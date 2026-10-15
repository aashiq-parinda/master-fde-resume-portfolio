import pytest
from src.agent.state import IncidentState
from src.agent.graph import operations_graph

def test_autonomous_traffic_spike_triage_and_scale():
    state = IncidentState(
        incident_id="TEST-01",
        service_name="order-processor",
        severity="SEV2",
        alert_description="High CPU load of 88% due to sudden traffic burst. Request latency spiking.",
        telemetry_metrics={"cpu_pct": 88.0, "replicas": 2}
    )

    state = operations_graph.run(state)

    assert "traffic surge" in state.diagnosis.lower()
    assert state.risk_tier == "MEDIUM"
    assert state.requires_human_approval is False # Medium risk auto-remediates
    assert state.verification_passed is True
    assert state.is_closed is True
    assert len(state.tool_executions) > 0
    assert state.tool_executions[0].tool_name == "scale_service"
    assert state.tool_executions[0].status == "SUCCESS"
