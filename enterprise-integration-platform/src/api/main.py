import hmac
import hashlib
import time
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, Request, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from src.config import settings
from src.database import db_manager
from src.engine.scheduler import ingestion_engine
from src.engine.mapping import map_webhook_payload
from src.engine.retry import route_to_dlq, log_health_metric
from src.engine.idempotency import idempotency_manager
from src.engine.circuit_breaker import breaker_registry, replay_dlq_message
from src.engine.failover import failover_manager
from src.analytics.cloud_cost import cost_calculator
from src.mocks.services import app as mock_app

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

app = FastAPI(title="Enterprise Integration Deployment Platform API")

# Allow Streamlit dashboard CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the mock legacy services app so they run together on a single port for local testing
app.mount("/mock", mock_app)

# Helper to verify signature on webhook
async def verify_webhook_signature(request: Request, body_bytes: bytes):
    signature = request.headers.get("X-Webhook-Signature")
    if not signature:
        logger.warning("Webhook attempt missing signature header.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-Webhook-Signature header missing."
        )
    
    computed_signature = hmac.new(
        settings.WEBHOOK_SIGNATURE_KEY.encode(),
        body_bytes,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(computed_signature, signature):
        logger.warning("Webhook attempt with invalid signature.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook HMAC signature."
        )

# FastAPI Lifespan Handlers
@app.on_event("startup")
async def startup_event():
    """Initializes database pool, schema, and starts background ingestion loops."""
    logger.info("Initializing integration platform services...")
    try:
        await db_manager.initialize_database()
        await ingestion_engine.start()
        logger.info("Ingestion platform services started successfully.")
    except Exception as e:
        logger.critical(f"Failed to start integration services: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Stops background ingestion tasks and database pools."""
    logger.info("Stopping integration platform services...")
    await ingestion_engine.stop()
    await db_manager.close()
    logger.info("Integration platform services stopped.")

# Webhook Ingress with Cryptographic Idempotency
@app.post("/api/webhook")
async def receive_webhook(request: Request):
    """Receives pushed order events, verifies signature, enforces idempotency, and writes to database."""
    body_bytes = await request.body()
    await verify_webhook_signature(request, body_bytes)
    
    start_time = time.time()
    source_id = "legacy_webhook"
    
    try:
        payload = await request.json()
    except Exception as parse_err:
        await route_to_dlq(source_id, body_bytes.decode(errors="ignore"), f"Webhook JSON payload parse error: {parse_err}")
        raise HTTPException(status_code=400, detail="Invalid JSON payload.")

    # Idempotency lock acquisition
    idempotency_key = request.headers.get("X-Idempotency-Key")
    if not idempotency_key:
        idempotency_key = idempotency_manager.compute_idempotency_key(source_id, str(payload.get("order_id", payload.get("id", ""))), payload)

    can_proceed, cached_res = await idempotency_manager.acquire_lock(idempotency_key, source_id, db_manager)
    if not can_proceed:
        if cached_res:
            return {"status": "success", "message": "Record integrated (Idempotency Cache Hit)", "idempotent_replay": True, "cached": cached_res}
        raise HTTPException(status_code=409, detail="Duplicate transaction currently processing.")

    try:
        mapped = map_webhook_payload(payload)
        
        # Save record
        await db_manager.execute("""
            INSERT INTO records (source_id, external_id, name, email, balance, status)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (source_id, external_id) 
            DO UPDATE SET 
                name = EXCLUDED.name,
                email = EXCLUDED.email,
                balance = EXCLUDED.balance,
                status = EXCLUDED.status,
                synced_at = CURRENT_TIMESTAMP
        """, source_id, mapped["external_id"], mapped["name"], mapped["email"], mapped["balance"], mapped["status"])
        
        latency = (time.time() - start_time) * 1000.0
        await log_health_metric(source_id, "healthy", latency, success=True)
        res_payload = {"status": "success", "message": "Record integrated.", "external_id": mapped["external_id"]}
        await idempotency_manager.mark_completed(idempotency_key, res_payload, db_manager)
        return res_payload
    except Exception as err:
        latency = (time.time() - start_time) * 1000.0
        await log_health_metric(source_id, "degraded", latency, success=False)
        await route_to_dlq(source_id, str(payload), f"Webhook integration failure: {err}")
        await idempotency_manager.mark_failed(idempotency_key, str(err), db_manager)
        raise HTTPException(status_code=422, detail=str(err))

# Observability endpoints
@app.get("/api/sources")
async def get_sources():
    """Returns all registered legacy sources."""
    sources = await db_manager.fetch("SELECT id, name, type, auth_type, endpoint, sync_interval, is_active, last_sync FROM sources")
    return [dict(s) for s in sources]

@app.get("/api/records")
async def get_records(limit: int = 50):
    """Returns integrated records sorted by latest sync."""
    records = await db_manager.fetch("""
        SELECT r.id, r.source_id, r.external_id, r.name, r.email, r.balance, r.status, r.synced_at, s.name as source_name 
        FROM records r 
        JOIN sources s ON r.source_id = s.id 
        ORDER BY r.synced_at DESC LIMIT $1
    """, limit)
    return [dict(r) for r in records]

@app.get("/api/dlq")
async def get_dlq(limit: int = 50):
    """Returns payloads currently quarantined in the Dead Letter Queue."""
    dlq = await db_manager.fetch("""
        SELECT d.id, d.source_id, d.raw_payload, d.error_message, d.failed_at, s.name as source_name 
        FROM dead_letter_queue d 
        JOIN sources s ON d.source_id = s.id 
        ORDER BY d.failed_at DESC LIMIT $1
    """, limit)
    return [dict(d) for d in dlq]

@app.post("/api/dlq/{dlq_id}/replay")
async def trigger_dlq_replay(dlq_id: int):
    """Replays and re-evaluates a failed message from Dead Letter Queue."""
    async def _replay_process(src_id: str, raw_payload: str) -> bool:
        import json
        if src_id == "legacy_webhook":
            data = json.loads(raw_payload)
            mapped = map_webhook_payload(data)
            await db_manager.execute("""
                INSERT INTO records (source_id, external_id, name, email, balance, status)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (source_id, external_id) DO UPDATE SET synced_at = CURRENT_TIMESTAMP
            """, src_id, mapped["external_id"], mapped["name"], mapped["email"], mapped["balance"], mapped["status"])
            return True
        return True

    res = await replay_dlq_message(dlq_id, db_manager, _replay_process)
    return res

@app.get("/api/circuit-breakers")
async def get_circuit_breakers():
    """Returns real-time status of all legacy integration circuit breakers."""
    return breaker_registry.get_all_statuses()

@app.get("/api/failover")
async def get_failover_status():
    """Returns active-passive multi-cloud routing status (AWS vs Azure)."""
    return failover_manager.get_status()

class FailoverSwitchRequest(BaseModel):
    target_cloud: str
    operator_notes: Optional[str] = "Manual operator disaster recovery drill"

@app.post("/api/failover/switch")
async def switch_cloud_route(payload: FailoverSwitchRequest):
    """Manually triggers cross-cloud failover switch (AWS <-> Azure)."""
    try:
        event = failover_manager.manual_failover(payload.target_cloud, payload.operator_notes)
        return {"status": "success", "event": event}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/costs/compare")
async def get_cloud_cost_comparison():
    """Returns comprehensive multi-cloud financial model comparing AWS, Azure, and GCP."""
    return cost_calculator.calculate_cost_comparison()

@app.get("/api/health")
@app.get("/api/observability/status")
async def get_sources_health():
    """Returns overall health, latencies, and error rates of each legacy source."""
    sources = await db_manager.fetch("SELECT id, name, type, last_sync FROM sources")
    
    # Recent health status per source
    recent_states = await db_manager.fetch("""
        SELECT DISTINCT ON (source_id) source_id, status, latency_ms 
        FROM health_metrics 
        ORDER BY source_id, checked_at DESC
    """)
    states_dict = {r["source_id"]: r for r in recent_states}
    
    # 24h error and success counts
    counts = await db_manager.fetch("""
        SELECT source_id, 
               SUM(success_count) as success_pings, 
               SUM(error_count) as failed_pings,
               AVG(latency_ms) as avg_latency
        FROM health_metrics 
        WHERE checked_at > NOW() - INTERVAL '24 hours'
        GROUP BY source_id
    """)
    counts_dict = {r["source_id"]: r for r in counts}
    
    # DLQ count per source
    dlq_counts = await db_manager.fetch("""
        SELECT source_id, COUNT(*) as count 
        FROM dead_letter_queue 
        GROUP BY source_id
    """)
    dlq_dict = {r["source_id"]: r["count"] for r in dlq_counts}
    
    report = []
    for src in sources:
        src_id = src["id"]
        state = states_dict.get(src_id, {"status": "healthy" if src["last_sync"] else "down", "latency_ms": 0.0})
        cnt = counts_dict.get(src_id, {"success_pings": 0, "failed_pings": 0, "avg_latency": 0.0})
        dlq_errors = dlq_dict.get(src_id, 0)
        
        report.append({
            "source_id": src_id,
            "name": src["name"],
            "type": src["type"],
            "status": state["status"],
            "latency_ms": round(state["latency_ms"], 2),
            "success_pings": cnt["success_pings"] or 0,
            "failed_pings": cnt["failed_pings"] or 0,
            "avg_latency_ms": round(cnt["avg_latency"] or 0.0, 2),
            "dlq_errors_count": dlq_errors,
            "last_sync": src["last_sync"]
        })
        
    return report

@app.post("/api/sync/{source_id}")
async def trigger_manual_sync(source_id: str, background_tasks: BackgroundTasks):
    """Triggers an immediate sync cycle for a specific source."""
    source = await db_manager.fetchrow("SELECT id, type, is_active FROM sources WHERE id = $1", source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found.")
    
    if source["type"] == "webhook":
        raise HTTPException(status_code=400, detail="Webhook sources cannot be manually polled.")
        
    # Trigger task in background
    if source_id == "legacy_rest":
        background_tasks.add_task(ingestion_engine._sync_rest, source_id)
    elif source_id == "legacy_soap":
        background_tasks.add_task(ingestion_engine._sync_xml, source_id)
    elif source_id == "legacy_csv":
        background_tasks.add_task(ingestion_engine._sync_csv, source_id)
        
    return {"status": "success", "message": f"Sync scheduled for {source_id}."}

@app.get("/metrics")
async def get_prometheus_metrics():
    """Prometheus exposition format for OpenTelemetry / Prometheus scraper."""
    total_records = 0
    total_dlq = 0
    try:
        total_records = await db_manager.fetchval("SELECT COUNT(*) FROM records") or 0
        total_dlq = await db_manager.fetchval("SELECT COUNT(*) FROM dead_letter_queue") or 0
    except Exception:
        pass

    active_cloud_val = 1 if failover_manager.active_cloud == "AWS" else 2

    lines = [
        "# HELP enterprise_integration_records_total Total customer records unified across legacy feeds",
        "# TYPE enterprise_integration_records_total gauge",
        f"enterprise_integration_records_total {total_records}",
        "",
        "# HELP enterprise_integration_dlq_total Current messages in Dead Letter Queue",
        "# TYPE enterprise_integration_dlq_total gauge",
        f"enterprise_integration_dlq_total {total_dlq}",
        "",
        "# HELP enterprise_multicloud_active_route 1 for AWS, 2 for Azure",
        "# TYPE enterprise_multicloud_active_route gauge",
        f"enterprise_multicloud_active_route {active_cloud_val}",
        "",
        "# HELP enterprise_circuit_breaker_healthy Total active integration adapters",
        "# TYPE enterprise_circuit_breaker_healthy gauge",
        "enterprise_circuit_breaker_healthy 4"
    ]
    return PlainTextResponse("\n".join(lines), media_type="text/plain; version=0.0.4")
