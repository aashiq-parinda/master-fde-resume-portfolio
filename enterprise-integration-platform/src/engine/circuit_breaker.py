import time
import asyncio
import random
import logging
from typing import Dict, Any, Optional, Callable

logger = logging.getLogger("circuit_breaker")

class CircuitState:
    CLOSED = "CLOSED"      # Normal healthy operation
    OPEN = "OPEN"          # Failing, fast-rejecting requests
    HALF_OPEN = "HALF_OPEN"# Testing recovery with canary probes

class CircuitBreaker:
    """
    Production-grade Circuit Breaker protecting legacy integrations from cascading failures.
    Enforces automatic fail-fast trip, cooldown timeout, and canary probing.
    """
    def __init__(
        self,
        name: str,
        failure_threshold: int = 3,
        recovery_timeout_seconds: float = 10.0,
        half_open_success_threshold: int = 1
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds
        self.half_open_success_threshold = half_open_success_threshold

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.last_state_change: float = time.time()

    def can_execute(self) -> bool:
        """Determines if the integration endpoint can be invoked."""
        now = time.time()

        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has elapsed
            if now - self.last_failure_time >= self.recovery_timeout_seconds:
                logger.info(f"Circuit Breaker [{self.name}] recovery timeout elapsed. Transitioning OPEN -> HALF_OPEN.")
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = now
                self.success_count = 0
                return True
            return False

        if self.state == CircuitState.HALF_OPEN:
            # Allow limited canary requests
            return True

        return False

    def record_success(self):
        """Records a successful network invocation."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.half_open_success_threshold:
                logger.info(f"Circuit Breaker [{self.name}] canary successful. Resetting HALF_OPEN -> CLOSED.")
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.last_state_change = time.time()
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0

    def record_failure(self, error: Exception):
        """Records an execution error and trips circuit if threshold exceeded."""
        now = time.time()
        self.failure_count += 1
        self.last_failure_time = now

        if self.state == CircuitState.HALF_OPEN:
            logger.warning(f"Circuit Breaker [{self.name}] canary probe failed ({error}). Tripping HALF_OPEN -> OPEN.")
            self.state = CircuitState.OPEN
            self.last_state_change = now
        elif self.state == CircuitState.CLOSED:
            if self.failure_count >= self.failure_threshold:
                logger.error(f"Circuit Breaker [{self.name}] reached {self.failure_count} failures. Tripping CLOSED -> OPEN.")
                self.state = CircuitState.OPEN
                self.last_state_change = now

    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "state": self.state,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time,
            "state_uptime_seconds": round(time.time() - self.last_state_change, 2)
        }

class CircuitBreakerRegistry:
    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}

    def get(self, name: str) -> CircuitBreaker:
        if name not in self.breakers:
            self.breakers[name] = CircuitBreaker(name=name)
        return self.breakers[name]

    def get_all_statuses(self) -> Dict[str, Any]:
        return {name: cb.get_status() for name, cb in self.breakers.items()}

breaker_registry = CircuitBreakerRegistry()

def calculate_full_jitter_delay(attempt: int, base_delay: float = 1.0, max_delay: float = 30.0) -> float:
    """Calculates exponential backoff with full jitter to avoid thundering herds."""
    exp_backoff = min(max_delay, base_delay * (2 ** (attempt - 1)))
    return random.uniform(0.1, exp_backoff)

async def replay_dlq_message(dlq_id: int, db_manager: Any, process_fn: Callable) -> Dict[str, Any]:
    """
    Replays a failed message from Dead Letter Queue table.
    If schema mapping/ingestion succeeds, marks as reprocessed or deletes from DLQ.
    """
    row = await db_manager.fetchrow("""
        SELECT id, source_id, raw_payload, error_message
        FROM dead_letter_queue
        WHERE id = $1
    """, dlq_id)

    if not row:
        return {"status": "error", "message": f"DLQ entry #{dlq_id} not found."}

    source_id = row["source_id"]
    raw_payload = row["raw_payload"]

    try:
        # Re-run processing function
        success = await process_fn(source_id, raw_payload)
        if success:
            await db_manager.execute("DELETE FROM dead_letter_queue WHERE id = $1", dlq_id)
            logger.info(f"Successfully replayed and resolved DLQ record #{dlq_id} for source {source_id}.")
            return {"status": "success", "message": f"DLQ #{dlq_id} reprocessed successfully."}
        else:
            return {"status": "failed", "message": f"Replay re-evaluation failed for DLQ #{dlq_id}."}
    except Exception as e:
        logger.error(f"Replay attempt failed for DLQ #{dlq_id}: {e}")
        return {"status": "error", "message": str(e)}
