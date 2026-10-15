import pytest
from src.evals.evaluator import OperationsAgentEvaluator

def test_evaluator_benchmark_execution():
    evaluator = OperationsAgentEvaluator()
    res = evaluator.run_benchmark()

    assert "metrics" in res
    assert "cases" in res
    m = res["metrics"]
    assert m["task_completion_rate_pct"] > 80.0
    assert m["hitl_gate_compliance_pct"] == 100.0 # 100% compliance on high/critical
    assert m["tool_selection_accuracy_pct"] > 80.0
    assert m["audit_integrity_verified"] is True
