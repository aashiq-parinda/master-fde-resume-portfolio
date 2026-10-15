import logging
from typing import Dict, Any, List
from datetime import date
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from src.config import settings
from src.database import db_manager
from src.summarizer.engine import generate_pre_visit_summary

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

app = FastAPI(title="Healthcare Patient Intake Summarization Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class PatientIntakeCreate(BaseModel):
    patient_name: str = Field(..., example="Rohan Malhotra")
    date_of_birth: date = Field(..., example="1988-05-15")
    raw_symptoms: str = Field(..., example="I have severe pain in the lower right abdomen since this morning. It hurts to touch, and I feel nauseous.")

@app.on_event("startup")
async def startup_event():
    """Starts the database connection pool and initializes tables/seeds."""
    logger.info("Initializing Healthcare Summarization Platform services...")
    try:
        await db_manager.initialize_database()
        logger.info("Healthcare Summarization Platform services started.")
    except Exception as e:
        logger.critical(f"Failed to start healthcare services: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Closes database connection pools."""
    logger.info("Stopping Healthcare Summarization Platform services...")
    await db_manager.close()
    logger.info("Healthcare Summarization Platform services stopped.")

# Clinical Ingress
@app.post("/api/intakes", status_code=status.HTTP_201_CREATED)
async def create_patient_intake(payload: PatientIntakeCreate):
    """Submits a patient intake, triggers RAG matching, LLM summarization, and safety filter checks."""
    try:
        # 1. Insert patient intake record
        intake_id = await db_manager.fetchval("""
            INSERT INTO patient_intakes (patient_name, date_of_birth, raw_symptoms)
            VALUES ($1, $2, $3)
            RETURNING id
        """, payload.patient_name, payload.date_of_birth, payload.raw_symptoms)
        
        # 2. Trigger automated pre-visit summary pipeline (RAG + safety filter)
        summary = await generate_pre_visit_summary(intake_id, payload.patient_name, payload.raw_symptoms)
        
        return {
            "status": "success",
            "intake_id": intake_id,
            "patient_name": payload.patient_name,
            "triage_recommendation": summary["triage_recommendation"],
            "safety_attempts_triggered": summary["safety_attempts"],
            "summary_text": summary["summary_text"],
            "intake_status": summary["status"]
        }
    except Exception as e:
        logger.error(f"Failed to process patient intake: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the intake: {str(e)}"
        )

@app.get("/api/intakes")
async def get_intakes(limit: int = 50):
    """Fetches recently submitted patient intakes."""
    intakes = await db_manager.fetch("""
        SELECT id, patient_name, date_of_birth, raw_symptoms, status, created_at
        FROM patient_intakes
        ORDER BY created_at DESC
        LIMIT $1
    """, limit)
    return [dict(i) for i in intakes]

@app.get("/api/summaries")
async def get_summaries(limit: int = 50):
    """Fetches visit summaries with triage recommendations."""
    summaries = await db_manager.fetch("""
        SELECT v.id, v.intake_id, p.patient_name, v.summary_text, v.red_flags_extracted, 
               v.triage_recommendation, v.safety_attempts, v.generated_at
        FROM visit_summaries v
        JOIN patient_intakes p ON v.intake_id = p.id
        ORDER BY v.generated_at DESC
        LIMIT $1
    """, limit)
    return [dict(s) for s in summaries]

@app.get("/api/safety-logs")
async def get_safety_logs(limit: int = 50):
    """Fetches safety logs showing diagnostic terms and syntaxes that were blocked."""
    logs = await db_manager.fetch("""
        SELECT s.id, s.intake_id, p.patient_name, s.blocked_output, s.violation_reason, s.timestamp
        FROM safety_logs s
        JOIN patient_intakes p ON s.intake_id = p.id
        ORDER BY s.timestamp DESC
        LIMIT $1
    """, limit)
    return [dict(l) for l in logs]

@app.get("/api/traces")
async def get_traces(limit: int = 50):
    """Fetches recent execution traces."""
    from src.tracing.tracer import trace_repo
    return trace_repo.get_all(limit=limit)

@app.get("/api/traces/{trace_id}")
async def get_trace_by_id(trace_id: str):
    """Fetches full span breakdown for a specific execution trace."""
    from src.tracing.tracer import trace_repo
    t = trace_repo.get_by_id(trace_id)
    if not t:
        raise HTTPException(status_code=404, detail="Trace not found.")
    return t

@app.get("/api/guidelines")
async def get_guidelines():
    """Returns clinical guidelines corpus."""
    from src.summarizer.engine import get_guidelines_corpus
    return get_guidelines_corpus()

class RetrievalInspectRequest(BaseModel):
    query: str

@app.post("/api/retrieval/inspect")
async def inspect_retrieval(payload: RetrievalInspectRequest):
    """Inspects dense, sparse, RRF, and cross-encoder reranked candidates for a query."""
    from src.summarizer.engine import retrieve_and_rerank_guidelines
    reranked, telemetry = await retrieve_and_rerank_guidelines(payload.query)
    return {
        "query": payload.query,
        "reranked_candidates": reranked,
        "telemetry": telemetry
    }

@app.post("/api/evals/run")
async def trigger_evals():
    """Runs the clinical safety and RAG benchmark evaluation suite."""
    from evals.run_evals import run_evaluation_suite
    results = await run_evaluation_suite()
    return results

