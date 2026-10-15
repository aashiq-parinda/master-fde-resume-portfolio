import os
import uuid
import logging
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load LangSmith and agent environment variables
load_dotenv()

from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from src.agent.state import IncidentState
from src.agent.graph import operations_graph
from src.audit.logger import audit_ledger
from src.evals.evaluator import evaluator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

app = FastAPI(
    title="Enterprise Operations AI Agent API",
    description="Autonomous Site Reliability & Incident Triage Agent using State Graphs, Tool Calling, and HITL Governance.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory incident store
INCIDENTS_DB: Dict[str, IncidentState] = {}

class IncidentCreateRequest(BaseModel):
    service_name: str = Field(..., example="checkout-api")
    severity: str = Field("SEV2", example="SEV1")
    alert_description: str = Field(..., example="Pod memory reached 94%. Frequent GC pauses causing 504 gateway timeouts.")
    telemetry_metrics: Dict[str, Any] = Field(default_factory=dict, example={"memory_mb": 1850, "cpu_pct": 45.0})

class ApprovalRequest(BaseModel):
    approver_id: str = Field(..., example="lead.sre@enterprise.com")
    approval_notes: str = Field(..., example="Approved rolling restart after verifying canary traffic drain.")

class RejectionRequest(BaseModel):
    approver_id: str = Field(..., example="security.lead@enterprise.com")
    rejection_reason: str = Field(..., example="High traffic maintenance window in effect. Postpone until 02:00 UTC.")

@app.post("/api/incidents", status_code=status.HTTP_201_CREATED)
async def create_and_triage_incident(payload: IncidentCreateRequest):
    """
    Ingests an operational incident, kicks off State Graph triage (Ingest -> Diagnose -> Plan),
    and executes remediation or pauses at the Human Approval Gate.
    """
    inc_id = f"INC-{uuid.uuid4().hex[:6].upper()}"
    state = IncidentState(
        incident_id=inc_id,
        service_name=payload.service_name,
        severity=payload.severity,
        alert_description=payload.alert_description,
        telemetry_metrics=payload.telemetry_metrics
    )

    # Execute graph
    state = operations_graph.run(state)
    INCIDENTS_DB[inc_id] = state

    return {
        "incident_id": inc_id,
        "current_node": state.current_node,
        "diagnosis": state.diagnosis,
        "risk_tier": state.risk_tier,
        "requires_human_approval": state.requires_human_approval,
        "approval_status": state.approval_status,
        "is_closed": state.is_closed,
        "resolution_summary": state.resolution_summary
    }

@app.get("/api/incidents")
async def list_incidents(limit: int = 50):
    """Lists all operational incidents."""
    return [state.model_dump() for state in reversed(list(INCIDENTS_DB.values())[-limit:])]

@app.get("/api/incidents/{incident_id}")
async def get_incident(incident_id: str):
    """Fetches details, execution history, and audit trail of an incident."""
    if incident_id not in INCIDENTS_DB:
        raise HTTPException(status_code=404, detail="Incident not found.")
    state = INCIDENTS_DB[incident_id]
    audit_trail = audit_ledger.get_incident_audit_trail(incident_id)
    return {
        "incident": state.model_dump(),
        "audit_trail": audit_trail
    }

@app.post("/api/incidents/{incident_id}/approve")
async def approve_remediation(incident_id: str, payload: ApprovalRequest):
    """
    Submits Human Operator approval for a gated remediation action.
    Resumes State Graph execution from APPROVAL_GATE -> EXECUTE -> VERIFY -> FINALIZE.
    """
    if incident_id not in INCIDENTS_DB:
        raise HTTPException(status_code=404, detail="Incident not found.")
    state = INCIDENTS_DB[incident_id]

    if state.is_closed:
        raise HTTPException(status_code=400, detail="Incident is already closed.")

    # Record approval in state & audit ledger
    state.approval_status = "APPROVED"
    state.approver_id = payload.approver_id
    state.approval_notes = payload.approval_notes

    audit_ledger.record_event(
        incident_id=incident_id,
        event_type="HUMAN_APPROVAL_GRANTED",
        node="APPROVAL_GATE",
        actor=payload.approver_id,
        payload={"notes": payload.approval_notes}
    )

    # Resume graph execution
    state = operations_graph.run(state)
    INCIDENTS_DB[incident_id] = state

    return {
        "incident_id": incident_id,
        "status": "APPROVED_AND_EXECUTED",
        "current_node": state.current_node,
        "is_closed": state.is_closed,
        "resolution_summary": state.resolution_summary
    }

@app.post("/api/incidents/{incident_id}/reject")
async def reject_remediation(incident_id: str, payload: RejectionRequest):
    """
    Rejects the proposed remediation. Aborts execution and updates audit trail.
    """
    if incident_id not in INCIDENTS_DB:
        raise HTTPException(status_code=404, detail="Incident not found.")
    state = INCIDENTS_DB[incident_id]

    state.approval_status = "REJECTED"
    state.approver_id = payload.approver_id
    state.approval_notes = payload.rejection_reason

    audit_ledger.record_event(
        incident_id=incident_id,
        event_type="HUMAN_APPROVAL_REJECTED",
        node="APPROVAL_GATE",
        actor=payload.approver_id,
        payload={"reason": payload.rejection_reason}
    )

    state = operations_graph.run(state)
    INCIDENTS_DB[incident_id] = state

    return {
        "incident_id": incident_id,
        "status": "REJECTED_AND_ABORTED",
        "current_node": state.current_node,
        "is_closed": state.is_closed,
        "resolution_summary": state.resolution_summary
    }

@app.get("/api/audit-logs")
async def get_audit_logs(limit: int = 50):
    """Returns tamper-evident cryptographic audit ledger records and hash chain integrity."""
    chain_valid, msg = audit_ledger.verify_chain_integrity()
    records = audit_ledger.get_all_records(limit=limit)
    return {
        "chain_integrity_valid": chain_valid,
        "verification_message": msg,
        "records_count": len(audit_ledger.chain),
        "records": records
    }

@app.post("/api/evals/run")
async def run_benchmark_evaluations():
    """Triggers the automated operations agent benchmark evaluation harness."""
    results = evaluator.run_benchmark()
    return results

@app.get("/metrics")
async def get_prometheus_metrics():
    """Prometheus metrics endpoint."""
    total_incidents = len(INCIDENTS_DB)
    resolved_count = sum(1 for i in INCIDENTS_DB.values() if i.is_closed and i.verification_passed)
    pending_approval = sum(1 for i in INCIDENTS_DB.values() if i.approval_status == "PENDING" and i.requires_human_approval)
    audit_chain_valid, _ = audit_ledger.verify_chain_integrity()

    lines = [
        "# HELP operations_agent_incidents_total Total incidents ingested",
        "# TYPE operations_agent_incidents_total counter",
        f"operations_agent_incidents_total {total_incidents}",
        "",
        "# HELP operations_agent_resolved_total Total incidents resolved successfully",
        "# TYPE operations_agent_resolved_total counter",
        f"operations_agent_resolved_total {resolved_count}",
        "",
        "# HELP operations_agent_pending_hitl_approvals Current incidents awaiting human operator approval",
        "# TYPE operations_agent_pending_hitl_approvals gauge",
        f"operations_agent_pending_hitl_approvals {pending_approval}",
        "",
        "# HELP operations_agent_audit_chain_valid 1 if cryptographic ledger intact, 0 otherwise",
        "# TYPE operations_agent_audit_chain_valid gauge",
        f"operations_agent_audit_chain_valid {1 if audit_chain_valid else 0}"
    ]
    return PlainTextResponse("\n".join(lines), media_type="text/plain; version=0.0.4")
