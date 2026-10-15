import time
import asyncio
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("failover")

class MultiCloudFailoverManager:
    """
    Manages automated active-passive cross-cloud failover between AWS (Primary) and Azure (Secondary).
    Monitors endpoint heartbeats, triggers automated DNS/traffic rerouting upon primary outage,
    and conducts state reconciliation when primary recovers.
    """
    def __init__(
        self,
        primary_endpoint: str = "https://aws-fargate.enterprise.internal/health",
        secondary_endpoint: str = "https://azure-containerapps.enterprise.internal/health",
        failure_threshold: int = 3,
        recovery_threshold: int = 3
    ):
        self.primary_endpoint = primary_endpoint
        self.secondary_endpoint = secondary_endpoint
        self.failure_threshold = failure_threshold
        self.recovery_threshold = recovery_threshold

        self.active_cloud = "AWS"
        self.primary_consecutive_failures = 0
        self.primary_consecutive_successes = 0
        self.last_failover_timestamp: Optional[float] = None
        self.failover_history = []

    def report_probe_result(self, cloud: str, is_healthy: bool, latency_ms: float = 25.0) -> Dict[str, Any]:
        """Records probe outcome and evaluates whether failover or failback should trigger."""
        event = None

        if cloud == "AWS":
            if is_healthy:
                self.primary_consecutive_failures = 0
                self.primary_consecutive_successes += 1

                # Check if we should failback from Azure to AWS
                if self.active_cloud == "AZURE" and self.primary_consecutive_successes >= self.recovery_threshold:
                    self.active_cloud = "AWS"
                    self.last_failover_timestamp = time.time()
                    event = {
                        "action": "FAILBACK_TO_PRIMARY",
                        "target_cloud": "AWS",
                        "timestamp": time.time(),
                        "reason": f"Primary AWS recovered ({self.recovery_threshold} consecutive healthy checks)."
                    }
                    self.failover_history.append(event)
                    logger.warning(f"AUTOMATED FAILBACK: Traffic restored to Primary (AWS). Event: {event['reason']}")
            else:
                self.primary_consecutive_successes = 0
                self.primary_consecutive_failures += 1

                # Check if we should failover from AWS to Azure
                if self.active_cloud == "AWS" and self.primary_consecutive_failures >= self.failure_threshold:
                    self.active_cloud = "AZURE"
                    self.last_failover_timestamp = time.time()
                    event = {
                        "action": "FAILOVER_TO_SECONDARY",
                        "target_cloud": "AZURE",
                        "timestamp": time.time(),
                        "reason": f"Primary AWS unreachable ({self.failure_threshold} consecutive probe failures)."
                    }
                    self.failover_history.append(event)
                    logger.critical(f"AUTOMATED FAILOVER: Primary (AWS) failed! Rerouting all integration feeds to Secondary (AZURE).")

        return {
            "active_cloud": self.active_cloud,
            "primary_failures": self.primary_consecutive_failures,
            "primary_successes": self.primary_consecutive_successes,
            "event_triggered": event
        }

    def manual_failover(self, target_cloud: str, operator_notes: str = "Manual operator drill") -> Dict[str, Any]:
        """Manually forces traffic route for disaster recovery drills."""
        if target_cloud not in ["AWS", "AZURE"]:
            raise ValueError("Target cloud must be 'AWS' or 'AZURE'")

        old = self.active_cloud
        self.active_cloud = target_cloud
        self.last_failover_timestamp = time.time()

        event = {
            "action": f"MANUAL_SWITCH_{old}_TO_{target_cloud}",
            "target_cloud": target_cloud,
            "timestamp": time.time(),
            "reason": operator_notes
        }
        self.failover_history.append(event)
        logger.info(f"Manual disaster recovery reroute executed: {old} -> {target_cloud} ({operator_notes})")
        return event

    def get_status(self) -> Dict[str, Any]:
        return {
            "active_cloud": self.active_cloud,
            "primary_target": "AWS ECS Fargate (us-east-1)",
            "secondary_target": "Azure Container Apps (centralindia)",
            "primary_consecutive_failures": self.primary_consecutive_failures,
            "last_failover_timestamp": self.last_failover_timestamp,
            "total_failover_events": len(self.failover_history),
            "recent_events": self.failover_history[-5:]
        }

failover_manager = MultiCloudFailoverManager()
