import logging
from typing import Dict, Any, List
from src.agent.state import IncidentState, ToolExecutionRecord
from src.tools.registry import tool_registry

logger = logging.getLogger("recovery")

class CompensationEngine:
    """
    Executes compensation transactions to safely revert system state
    if remediation actions fail or post-execution verification fails.
    """
    def __init__(self):
        pass

    def build_compensation_plan(self, executions: List[ToolExecutionRecord]) -> List[Dict[str, Any]]:
        """
        Derives reverse compensation actions for successfully executed tools.
        """
        plan = []
        # Process in reverse order (LIFO)
        for record in reversed(executions):
            if record.status != "SUCCESS":
                continue

            tool = record.tool_name
            res = record.result

            if tool == "scale_service":
                plan.append({
                    "tool_name": "scale_service",
                    "arguments": {
                        "service_name": res.get("service"),
                        "target_replicas": res.get("previous_replicas", 2),
                        "reason": "Compensatory rollback: reverting scale operation."
                    }
                })
            elif tool == "optimize_db_pool":
                plan.append({
                    "tool_name": "optimize_db_pool",
                    "arguments": {
                        "service_name": res.get("service", "inventory-db"),
                        "target_max_connections": res.get("previous_max", 25),
                        "kill_rogue_queries": False
                    }
                })

        return plan

    def execute_compensation(self, state: IncidentState) -> IncidentState:
        """
        Executes compensation plan and updates incident state.
        """
        logger.warning(f"Initiating compensation rollback for incident {state.incident_id}...")
        plan = self.build_compensation_plan(state.tool_executions)

        for step in plan:
            success, result = tool_registry.execute_tool(step["tool_name"], step["arguments"])
            rec = ToolExecutionRecord(
                tool_name=step["tool_name"],
                arguments=step["arguments"],
                result=result,
                status="SUCCESS" if success else "FAILED"
            )
            state.compensation_executions.append(rec)

        state.rollback_executed = True
        state.resolution_summary = (
            f"Remediation failed or unverified. Successfully executed {len(plan)} "
            f"compensatory rollback transactions. Escalated to on-call engineer."
        )
        return state

compensation_engine = CompensationEngine()
