import pytest
from src.agent.state import IncidentState
from src.agent.graph import operations_graph

def test_hitl_approval_interruption_and_resumption():
    state = IncidentState(
        incident_id="TEST-HITL-01",
        service_name="inventory-db",
        severity="SEV1",
        alert_description="Database connection pool saturation. 25/25 connections locked.",
        telemetry_metrics={"active_connections": 25, "max_connections": 25}
    )

    # 1. Initial run: should pause at APPROVAL_GATE
    state = operations_graph.run(state)
    assert state.current_node == "APPROVAL_GATE"
    assert state.requires_human_approval is True
    assert state.risk_tier == "CRITICAL"
    assert state.approval_status == "PENDING"
    assert state.is_closed is False
    assert len(state.tool_executions) == 0 # Has NOT executed yet!

    # 2. Operator submits approval
    state.approval_status = "APPROVED"
    state.approver_id = "lead.sre@enterprise.com"
    state.approval_notes = "Verified production impact. Authorized pool tuning."

    # 3. Resume graph
    state = operations_graph.run(state)
    assert state.current_node == "FINALIZE"
    assert state.is_closed is True
    assert state.verification_passed is True
    assert len(state.tool_executions) > 0
    assert state.tool_executions[0].tool_name == "optimize_db_pool"

def test_hitl_rejection_aborts_execution():
    state = IncidentState(
        incident_id="TEST-HITL-02",
        service_name="checkout-api",
        severity="SEV1",
        alert_description="Progressive memory leak. JVM heap saturation.",
        telemetry_metrics={"memory_mb": 1850}
    )

    state = operations_graph.run(state)
    assert state.current_node == "APPROVAL_GATE"

    # Operator rejects
    state.approval_status = "REJECTED"
    state.approver_id = "oncall.manager@enterprise.com"
    state.approval_notes = "Major transaction surge in progress. Postpone restart."

    state = operations_graph.run(state)
    assert state.is_closed is True
    assert len(state.tool_executions) == 0 # Aborted, zero destructive tools called
    assert "rejected" in state.resolution_summary.lower()
