import logging
from typing import Dict, Any, Tuple, Optional

try:
    from langsmith import traceable
except ImportError:
    def traceable(*args, **kwargs):
        def decorator(f):
            return f
        return decorator

logger = logging.getLogger("tools")

# Mock cluster operational state
CLUSTER_STATE = {
    "services": {
        "order-processor": {"replicas": 2, "cpu_pct": 88.0, "memory_mb": 750, "status": "HEALTHY"},
        "checkout-api": {"replicas": 3, "cpu_pct": 45.0, "memory_mb": 1850, "status": "MEMORY_LEAK"},
        "billing-gateway": {"replicas": 2, "cpu_pct": 30.0, "memory_mb": 512, "status": "HEALTHY"},
        "inventory-db": {"max_connections": 25, "active_connections": 25, "status": "POOL_EXHAUSTION"}
    },
    "cache": {
        "keys_count": 45000,
        "poisoned_keys": 120
    },
    "tickets": {},
    "pagerduty_alerts": []
}

class ToolRegistry:
    """
    Enterprise Operations Tool Registry.
    Exposes declarative tool calling definitions and execution handlers.
    """
    def __init__(self):
        self.definitions = [
            {
                "name": "scale_service",
                "description": "Adjusts container/pod replica count for a microservice under high traffic load.",
                "parameters": {
                    "service_name": {"type": "string", "required": True},
                    "target_replicas": {"type": "integer", "required": True, "minimum": 1, "maximum": 10},
                    "reason": {"type": "string", "required": True}
                }
            },
            {
                "name": "restart_pod",
                "description": "Gracefully restarts microservice containers with connection draining to resolve deadlocks or memory leaks.",
                "parameters": {
                    "service_name": {"type": "string", "required": True},
                    "drain_traffic": {"type": "boolean", "default": True},
                    "grace_period_seconds": {"type": "integer", "default": 30}
                }
            },
            {
                "name": "optimize_db_pool",
                "description": "Dynamically tunes database connection pool limits and terminates rogue queries running > 15s.",
                "parameters": {
                    "service_name": {"type": "string", "required": True},
                    "target_max_connections": {"type": "integer", "required": True, "minimum": 10, "maximum": 100},
                    "kill_rogue_queries": {"type": "boolean", "default": True}
                }
            },
            {
                "name": "flush_redis_cache",
                "description": "Evicts corrupted or poisoned cache keys matching a pattern to restore cache integrity.",
                "parameters": {
                    "pattern": {"type": "string", "required": True},
                    "async_flush": {"type": "boolean", "default": True}
                }
            },
            {
                "name": "update_incident_ticket",
                "description": "Updates ServiceNow / Jira incident ticket state and remediation logs.",
                "parameters": {
                    "ticket_id": {"type": "string", "required": True},
                    "status": {"type": "string", "enum": ["INVESTIGATING", "MITIGATING", "RESOLVED"]},
                    "notes": {"type": "string", "required": True}
                }
            },
            {
                "name": "notify_pagerduty",
                "description": "Dispatches operational notifications or alerts to on-call engineers.",
                "parameters": {
                    "incident_id": {"type": "string", "required": True},
                    "urgency": {"type": "string", "enum": ["LOW", "HIGH", "CRITICAL"]},
                    "message": {"type": "string", "required": True}
                }
            }
        ]

    @traceable(name="ToolRegistry.execute_tool", run_type="tool")
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Executes operational tool with parameter validation.
        Returns: (success: bool, result_payload: dict)
        """
        logger.info(f"Invoking Tool: [{tool_name}] with args: {arguments}")

        if tool_name == "scale_service":
            svc = arguments.get("service_name")
            target = arguments.get("target_replicas", 2)
            if target > 10:
                return False, {"error": "Target replicas exceeds maximum cluster safety limit of 10."}
            
            if svc in CLUSTER_STATE["services"]:
                prev = CLUSTER_STATE["services"][svc]["replicas"]
                CLUSTER_STATE["services"][svc]["replicas"] = target
                CLUSTER_STATE["services"][svc]["cpu_pct"] = max(20.0, CLUSTER_STATE["services"][svc]["cpu_pct"] / 2.0)
                return True, {
                    "action": "scale_service",
                    "service": svc,
                    "previous_replicas": prev,
                    "new_replicas": target,
                    "status": "SCALED_SUCCESSFULLY"
                }
            return False, {"error": f"Service '{svc}' not found in cluster."}

        elif tool_name == "restart_pod":
            svc = arguments.get("service_name")
            if svc in CLUSTER_STATE["services"]:
                CLUSTER_STATE["services"][svc]["memory_mb"] = 450 # Reset memory
                CLUSTER_STATE["services"][svc]["status"] = "HEALTHY"
                return True, {
                    "action": "restart_pod",
                    "service": svc,
                    "restarted_instances": CLUSTER_STATE["services"][svc]["replicas"],
                    "drain_completed": arguments.get("drain_traffic", True),
                    "status": "RESTARTED_ZERO_DOWNTIME"
                }
            return False, {"error": f"Service '{svc}' not found in cluster."}

        elif tool_name == "optimize_db_pool":
            svc = arguments.get("service_name", "inventory-db")
            target = arguments.get("target_max_connections", 50)
            kill_rogue = arguments.get("kill_rogue_queries", True)

            prev_max = CLUSTER_STATE["services"]["inventory-db"]["max_connections"]
            CLUSTER_STATE["services"]["inventory-db"]["max_connections"] = target
            CLUSTER_STATE["services"]["inventory-db"]["active_connections"] = 12
            CLUSTER_STATE["services"]["inventory-db"]["status"] = "HEALTHY"

            return True, {
                "action": "optimize_db_pool",
                "service": svc,
                "previous_max": prev_max,
                "new_max": target,
                "terminated_rogue_queries": 3 if kill_rogue else 0,
                "status": "POOL_OPTIMIZED"
            }

        elif tool_name == "flush_redis_cache":
            pattern = arguments.get("pattern", "*")
            cleared = CLUSTER_STATE["cache"]["poisoned_keys"]
            CLUSTER_STATE["cache"]["poisoned_keys"] = 0
            return True, {
                "action": "flush_redis_cache",
                "pattern": pattern,
                "evicted_keys": cleared,
                "status": "CACHE_CLEARED"
            }

        elif tool_name == "update_incident_ticket":
            t_id = arguments.get("ticket_id")
            st = arguments.get("status")
            notes = arguments.get("notes")
            CLUSTER_STATE["tickets"][t_id] = {"status": st, "notes": notes}
            return True, {
                "action": "update_incident_ticket",
                "ticket_id": t_id,
                "status": st
            }

        elif tool_name == "notify_pagerduty":
            inc_id = arguments.get("incident_id")
            urgency = arguments.get("urgency", "HIGH")
            msg = arguments.get("message")
            record = {"incident_id": inc_id, "urgency": urgency, "message": msg}
            CLUSTER_STATE["pagerduty_alerts"].append(record)
            return True, {
                "action": "notify_pagerduty",
                "incident_id": inc_id,
                "dispatched": True
            }

tool_registry = ToolRegistry()

def reset_cluster_state():
    CLUSTER_STATE["services"] = {
        "order-processor": {"replicas": 2, "cpu_pct": 88.0, "memory_mb": 750, "status": "HEALTHY"},
        "checkout-api": {"replicas": 3, "cpu_pct": 45.0, "memory_mb": 1850, "status": "MEMORY_LEAK"},
        "billing-gateway": {"replicas": 2, "cpu_pct": 30.0, "memory_mb": 512, "status": "HEALTHY"},
        "inventory-db": {"max_connections": 25, "active_connections": 25, "status": "POOL_EXHAUSTION"}
    }
    CLUSTER_STATE["cache"] = {"keys_count": 45000, "poisoned_keys": 120}
    CLUSTER_STATE["tickets"].clear()
    CLUSTER_STATE["pagerduty_alerts"].clear()

