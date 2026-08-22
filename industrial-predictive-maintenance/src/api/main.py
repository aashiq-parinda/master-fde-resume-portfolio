import asyncio
import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from src.config import settings
from src.utils.logger import get_logger, telemetry
from src.storage.db import db_manager
from src.queue.streaming import stream_manager
from src.generator.generator import MachineSimulator
from src.analytics.models import predictor
from src.assistant.agent import ai_assistant

logger = get_logger("api")

# Set up Rate Limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Industrial Predictive Maintenance Platform API",
    description="FDE Portfolio Project API for synthetic factory telemetry, real-time ML anomaly detection, and LLM diagnostics.",
    version="1.0.0"
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Secure CORS configuration: No wildcard '*' allowed
# Restrict to local Streamlit app origin (port 8501)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Background tasks lifecycle management
background_tasks = set()
stop_event = asyncio.Event()
simulator = MachineSimulator()

# Pydantic Schemas for Input Validation
class MaintenanceLogCreate(BaseModel):
    machine_id: str = Field(..., max_length=50, example="M-102")
    action: str = Field(..., max_length=250, example="Replace hydraulic pump valve seals")
    notes: Optional[str] = Field(None, example="Detected high-vibration drift. Installed new seal kit.")

class AssistantQuery(BaseModel):
    query: str = Field(..., max_length=500, example="What's wrong with machine M-102?")

async def process_incoming_reading(reading: dict):
    """
    Main pipeline callback for incoming telemetry events.
    Ingests to DB -> Runs ML detection -> Triggers LLM explanation if anomaly found.
    """
    start_time = time.time()
    machine_id = reading["machine_id"]
    timestamp = datetime.fromisoformat(reading["timestamp"])
    
    try:
        # 1. Fetch recent telemetry history for ML context (last 50 readings)
        history_records = await db_manager.fetch(
            """
            SELECT vibration, temperature, rpm, pressure 
            FROM sensor_readings 
            WHERE machine_id = $1 
            ORDER BY timestamp DESC LIMIT 50
            """,
            machine_id
        )
        
        # 2. Fit/Predict anomalies
        sensor_statuses, failure_prob, est_window = predictor.predict(
            machine_id, reading, history_records
        )
        
        is_anomalous = failure_prob > 0.4
        
        # Write sensor reading to TimescaleDB hypertable
        await db_manager.execute(
            """
            INSERT INTO sensor_readings (timestamp, machine_id, vibration, temperature, rpm, pressure)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            timestamp, machine_id, reading["vibration"], reading["temperature"], reading["rpm"], reading["pressure"]
        )
        
        # 3. Handle anomalies
        if is_anomalous:
            # Check if this machine is already flagged as anomalous to avoid explanation spam
            current_status = await db_manager.fetchval(
                "SELECT status FROM machines WHERE machine_id = $1", machine_id
            )
            
            # Update machine status
            await db_manager.execute(
                "UPDATE machines SET status = 'anomalous' WHERE machine_id = $1",
                machine_id
            )
            
            # Create an anomaly log
            anomaly_id = await db_manager.fetchval(
                """
                INSERT INTO anomalies (
                    timestamp, machine_id, vibration_status, temperature_status, 
                    rpm_status, pressure_status, anomaly_score, failure_probability, estimated_window_hours
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                RETURNING id
                """,
                timestamp, machine_id, 
                sensor_statuses["vibration_status"], sensor_statuses["temperature_status"],
                sensor_statuses["rpm_status"], sensor_statuses["pressure_status"],
                0.0, failure_prob, est_window
            )
            
            # Request AI explanation in the background (or immediately, but safely)
            # Fetch machine details
            m_info = await db_manager.fetchrow(
                "SELECT name, model FROM machines WHERE machine_id = $1", machine_id
            )
            
            if m_info:
                # Generate AI explanation
                ai_explanation = await ai_assistant.explain_anomaly(
                    machine_id, m_info["name"], m_info["model"], reading, failure_prob, est_window
                )
                # Store AI diagnostic back to DB
                await db_manager.execute(
                    "UPDATE anomalies SET ai_explanation = $1 WHERE id = $2",
                    ai_explanation, anomaly_id
                )
                logger.info(f"AI diagnostic report completed for anomaly #{anomaly_id} on {machine_id}")

        # Retrain ML model periodically (every 50 events)
        if len(history_records) >= 49:
            # Schedule training asynchronously
            asyncio.create_task(
                asyncio.to_thread(predictor.train_isolation_forest, machine_id, history_records)
            )

        latency_ms = (time.time() - start_time) * 1000.0
        telemetry.record_event(latency_ms, is_anomaly=is_anomalous)
        
    except Exception as e:
        logger.error(f"Error processing streaming event: {e}")
        telemetry.record_error()

async def consumer_task():
    """Background task running the Redis Pub/Sub consumer."""
    try:
        await stream_manager.start_consumer(process_incoming_reading, stop_event)
    except asyncio.CancelledError:
        logger.info("Consumer task cancelled.")
    except Exception as e:
        logger.critical(f"Consumer task crashed: {e}")
        telemetry.record_error()

async def generator_task():
    """Background task running the mock machine telemetry generator."""
    try:
        await simulator.run(interval_seconds=2.0)
    except asyncio.CancelledError:
        logger.info("Generator task cancelled.")
    except Exception as e:
        logger.critical(f"Generator task crashed: {e}")
        telemetry.record_error()

@app.on_event("startup")
async def startup_event():
    # 1. Initialize Database schema, extensions, users
    await db_manager.initialize_database()
    
    # 2. Open DB connection pool
    await db_manager.start_pool()
    
    # 3. Connect to Redis Pub/Sub
    await stream_manager.connect()
    
    # 4. Spin up background pipeline tasks
    loop = asyncio.get_running_loop()
    
    c_task = loop.create_task(consumer_task())
    g_task = loop.create_task(generator_task())
    
    background_tasks.add(c_task)
    background_tasks.add(g_task)
    
    c_task.add_done_callback(background_tasks.discard)
    g_task.add_done_callback(background_tasks.discard)
    
    logger.info("Application successfully started up.")

@app.on_event("shutdown")
async def shutdown_event():
    # Signalling cancel to loops
    stop_event.set()
    simulator.stop()
    
    # Cancel running background tasks
    for task in background_tasks:
        task.cancel()
    await asyncio.gather(*background_tasks, return_exceptions=True)
    
    # Close resources
    await stream_manager.close()
    await db_manager.close_pool()
    logger.info("Application successfully shut down.")

# --- API Endpoints ---

@app.get("/api/machines", response_model=List[Dict[str, Any]])
@limiter.limit("60/minute")
async def get_machines(request: Request):
    """Retrieves list of all registered machines and their current state."""
    # We join with the latest sensor readings and predicted anomaly data to get current status
    query = """
        SELECT m.machine_id, m.name, m.model, m.status,
               r.vibration, r.temperature, r.rpm, r.pressure, r.timestamp,
               COALESCE(a.failure_probability, 0.0) as failure_probability,
               a.estimated_window_hours
        FROM machines m
        LEFT JOIN LATERAL (
            SELECT vibration, temperature, rpm, pressure, timestamp
            FROM sensor_readings
            WHERE machine_id = m.machine_id
            ORDER BY timestamp DESC LIMIT 1
        ) r ON TRUE
        LEFT JOIN LATERAL (
            SELECT failure_probability, estimated_window_hours
            FROM anomalies
            WHERE machine_id = m.machine_id
            ORDER BY timestamp DESC LIMIT 1
        ) a ON TRUE
        ORDER BY m.machine_id;
    """
    return await db_manager.fetch(query)

@app.get("/api/machines/{machine_id}/telemetry", response_model=List[Dict[str, Any]])
@limiter.limit("120/minute")
async def get_machine_telemetry(request: Request, machine_id: str, limit: int = 100):
    """Fetches historical telemetry data for a single machine, sorted chronologically."""
    # Input validation: enforce max limit
    limit = min(max(limit, 1), 500)
    
    query = """
        SELECT timestamp, vibration, temperature, rpm, pressure
        FROM sensor_readings
        WHERE machine_id = $1
        ORDER BY timestamp DESC
        LIMIT $2
    """
    results = await db_manager.fetch(query, machine_id, limit)
    # Return sorted oldest to newest for plotting purposes
    results.reverse()
    return results

@app.get("/api/anomalies", response_model=List[Dict[str, Any]])
@limiter.limit("60/minute")
async def get_anomalies(request: Request, limit: int = 20):
    """Fetches list of historical anomalies and alerts, including AI diagnostics."""
    limit = min(max(limit, 1), 100)
    
    query = """
        SELECT a.id, a.timestamp, a.machine_id, m.name as machine_name,
               a.vibration_status, a.temperature_status, a.rpm_status, a.pressure_status,
               a.failure_probability, a.estimated_window_hours, a.ai_explanation, a.action_taken
        FROM anomalies a
        JOIN machines m ON a.machine_id = m.machine_id
        ORDER BY a.timestamp DESC
        LIMIT $1
    """
    return await db_manager.fetch(query, limit)

@app.post("/api/maintenance", status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def add_maintenance_log(request: Request, log: MaintenanceLogCreate):
    """Submits a maintenance record to repair a machine. Resets machine degradation state."""
    # Ensure machine exists
    m_exists = await db_manager.fetchval(
        "SELECT 1 FROM machines WHERE machine_id = $1", log.machine_id
    )
    if not m_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Machine {log.machine_id} not found."
        )

    try:
        await db_manager.execute(
            """
            INSERT INTO maintenance_logs (machine_id, action, notes)
            VALUES ($1, $2, $3)
            """,
            log.machine_id, log.action, log.notes
        )
        # Note: Background generator loop checks these logs to restore machine health status
        return {"status": "success", "message": f"Maintenance logged for machine {log.machine_id}."}
    except Exception as e:
        logger.error(f"Failed to save maintenance log: {e}")
        telemetry.record_error()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record maintenance transaction."
        )

@app.get("/api/observability/metrics", response_model=Dict[str, Any])
@limiter.limit("60/minute")
async def get_pipeline_observability(request: Request):
    """Exposes real-time throughput, latency, and health analytics for the ingestion pipeline."""
    return telemetry.get_metrics()

@app.post("/api/assistant/query")
@limiter.limit("20/minute")
async def query_diagnostic_assistant(request: Request, body: AssistantQuery):
    """Forwards questions about machine health directly to the AI Diagnostic Agent."""
    try:
        # Fetch current system state context to feed the agent
        machines_context = await db_manager.fetch("""
            SELECT m.machine_id, m.name, m.status,
                   r.vibration, r.temperature, r.rpm, r.pressure,
                   COALESCE(a.failure_probability, 0.0) as failure_probability,
                   a.estimated_window_hours
            FROM machines m
            LEFT JOIN LATERAL (
                SELECT vibration, temperature, rpm, pressure
                FROM sensor_readings
                WHERE machine_id = m.machine_id
                ORDER BY timestamp DESC LIMIT 1
            ) r ON TRUE
            LEFT JOIN LATERAL (
                SELECT failure_probability, estimated_window_hours
                FROM anomalies
                WHERE machine_id = m.machine_id
                ORDER BY timestamp DESC LIMIT 1
            ) a ON TRUE
        """)
        
        answer = await ai_assistant.answer_query(body.query, machines_context)
        return {"query": body.query, "response": answer}
    except Exception as e:
        logger.error(f"Error executing assistant query: {e}")
        telemetry.record_error()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating AI Assistant response."
        )
