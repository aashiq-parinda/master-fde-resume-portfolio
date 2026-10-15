import json
import os
import time
import numpy as np
from typing import Dict, Any, List, Optional

from src.agent.state import IncidentState
from src.agent.graph import operations_graph
from src.audit.logger import audit_ledger

class OperationsAgentEvaluator:
    """
    Automated evaluation harness benchmarking:
    - Task Completion Rate
    - Tool Selection Precision
    - Human-In-The-Loop (HITL) Gate Compliance (Target: 100%)
    - Compensation Rollback Success
    - Cryptographic Audit Trail Integrity
    """
    def __init__(self, dataset_path: Optional[str] = None):
        if dataset_path is None:
            dataset_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "evals", "eval_dataset.json")
        self.dataset_path = dataset_path

    def run_benchmark(self) -> Dict[str, Any]:
        with open(self.dataset_path, "r", encoding="utf-8") as f:
            cases = json.load(f)

        total_cases = len(cases)
        completed_count = 0
        hitl_compliant_count = 0
        hitl_total = 0
        tool_accuracy_count = 0
        latencies = []
        case_summaries = []

        for case in cases:
            t0 = time.perf_counter()
            state = IncidentState(
                incident_id=case["id"],
                service_name=case["service"],
                severity=case["severity"],
                alert_description=case["alert"],
                telemetry_metrics=case.get("metrics", {})
            )

            # 1. First Pass (Ingest -> Diagnose -> Plan -> HITL Gate)
            state = operations_graph.run(state)

            # Check HITL Compliance
            if case.get("requires_hitl", False):
                hitl_total += 1
                if state.requires_human_approval and state.current_node == "APPROVAL_GATE":
                    hitl_compliant_count += 1
                    # Simulate operator review and sign-off
                    state.approval_status = "APPROVED"
                    state.approver_id = "evaluator.bot@enterprise.com"
                    state.approval_notes = "Benchmarking auto-approval"
                    state = operations_graph.run(state)
            else:
                state.approval_status = "BYPASSED"

            # Check if testing intentional failure and compensation rollback
            if case.get("test_rollback", False):
                # Inject invalid replica request to trigger constraint error
                if state.proposed_actions:
                    state.proposed_actions[0].arguments["target_replicas"] = 25
                state = operations_graph.run(state)

            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            latencies.append(elapsed_ms)

            # Verify Tool Selection
            expected_tool = case.get("expected_tool")
            selected_tools = [a.tool_name for a in state.proposed_actions]
            if expected_tool in selected_tools:
                tool_accuracy_count += 1

            if state.is_closed or state.verification_passed or state.rollback_executed:
                completed_count += 1

            case_summaries.append({
                "case_id": case["id"],
                "name": case["name"],
                "severity": case["severity"],
                "risk_tier": state.risk_tier,
                "hitl_triggered": state.requires_human_approval,
                "status": "RESOLVED" if state.verification_passed else "ROLLED_BACK" if state.rollback_executed else "INTERRUPTED",
                "tools_invoked": selected_tools,
                "latency_ms": round(elapsed_ms, 2)
            })

        # Cryptographic Audit Verification
        chain_valid, chain_msg = audit_ledger.verify_chain_integrity()

        results = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "total_benchmark_cases": total_cases,
            "metrics": {
                "task_completion_rate_pct": round((completed_count / total_cases) * 100, 1),
                "hitl_gate_compliance_pct": round((hitl_compliant_count / max(1, hitl_total)) * 100, 1),
                "tool_selection_accuracy_pct": round((tool_accuracy_count / total_cases) * 100, 1),
                "audit_integrity_verified": chain_valid,
                "audit_verification_message": chain_msg,
                "latency_p50_ms": round(float(np.percentile(latencies, 50)), 2),
                "latency_p95_ms": round(float(np.percentile(latencies, 95)), 2)
            },
            "cases": case_summaries
        }
        return results

evaluator = OperationsAgentEvaluator()
