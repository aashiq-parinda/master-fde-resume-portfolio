from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class ToolExecutionRecord(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    result: Dict[str, Any]
    status: str # SUCCESS, FAILED
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ProposedAction(BaseModel):
    action_id: str
    tool_name: str
    arguments: Dict[str, Any]
    rationale: str
    risk_level: str # LOW, MEDIUM, HIGH, CRITICAL

class IncidentState(BaseModel):
    """
    Typed State Graph Model for Enterprise Operations AI Agent.
    Tracks end-to-end incident ingestion, diagnosis, remediation proposal,
    HITL approval gates, tool execution, compensation rollback, and audit trail.
    """
    incident_id: str
    service_name: str
    severity: str = "SEV2" # SEV1, SEV2, SEV3
    alert_description: str
    telemetry_metrics: Dict[str, Any] = Field(default_factory=dict)
    
    # Reasoning & Plan
    diagnosis: Optional[str] = None
    proposed_actions: List[ProposedAction] = Field(default_factory=list)
    risk_tier: str = "LOW" # LOW, MEDIUM, HIGH, CRITICAL
    requires_human_approval: bool = False
    
    # Human-In-The-Loop Approval Gate
    approval_status: str = "PENDING" # PENDING, APPROVED, REJECTED, BYPASSED
    approver_id: Optional[str] = None
    approval_notes: Optional[str] = None
    approval_timestamp: Optional[str] = None

    # Graph Execution State
    current_node: str = "START"
    node_history: List[str] = Field(default_factory=list)
    tool_executions: List[ToolExecutionRecord] = Field(default_factory=list)
    
    # Error Recovery & Rollback
    error_occurred: bool = False
    error_message: Optional[str] = None
    rollback_required: bool = False
    rollback_executed: bool = False
    compensation_executions: List[ToolExecutionRecord] = Field(default_factory=list)

    # Verification & Resolution
    verification_passed: bool = False
    verification_notes: Optional[str] = None
    resolution_summary: Optional[str] = None
    is_closed: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
