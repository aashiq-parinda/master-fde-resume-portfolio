import pytest
from src.agent.state import IncidentState, ProposedAction
from src.agent.graph import operations_graph

def test_tool_failure_triggers_compensation_rollback():
    state = IncidentState(
        incident_id="TEST-ROLLBACK-01",
        service_name="order-processor",
        severity="SEV2",
        alert_description="High CPU load traffic burst.",
        telemetry_metrics={"cpu_pct": 88.0, "replicas": 2}
    )

    state = operations_graph.run(state)

    # Now simulate an invalid state where target_replicas exceeds cluster limit
    state.current_node = "PLAN"
    state.proposed_actions = [
        ProposedAction(
            action_id="ACT-FAIL",
            tool_name="scale_service",
            arguments={"service_name": "order-processor", "target_replicas": 99}, # Exceeds limit of 10
            rationale="Unbounded scale test",
            risk_level="LOW"
        )
    ]

    state = operations_graph.execute_node(state)
    assert state.error_occurred is True

    state = operations_graph.verify_node(state)
    assert state.rollback_required is True

    state = operations_graph.rollback_node(state)
    assert state.rollback_executed is True
    assert "remediation failed" in state.resolution_summary.lower()
