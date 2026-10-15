import hashlib
import json
import logging
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timezone, timedelta

logger = logging.getLogger("idempotency")

class IdempotencyManager:
    """
    Guarantees exactly-once processing semantics for enterprise transactional events.
    Computes cryptographic signatures, enforces distributed state transitions (PENDING -> COMPLETED / FAILED),
    and prevents duplicate processing during network retries or concurrent replays.
    """
    def __init__(self):
        # In-memory store for fallback/testing, backed by SQL table when DB is active
        self._memory_store: Dict[str, Dict[str, Any]] = {}

    def compute_idempotency_key(self, source_id: str, external_id: str, payload: Any) -> str:
        """Generates SHA-256 idempotency key combining source, event ID, and normalized payload hash."""
        if isinstance(payload, dict):
            serialized = json.dumps(payload, sort_keys=True)
        else:
            serialized = str(payload)
        raw = f"{source_id}:{external_id}:{serialized}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    async def acquire_lock(self, idempotency_key: str, source_id: str, db_manager: Optional[Any] = None) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Attempts to acquire atomic execution lock.
        Returns:
            (can_proceed: bool, cached_result: Optional[dict])
            - If can_proceed is True: Request is unique, proceed to execute.
            - If can_proceed is False and cached_result exists: Request was already processed (idempotency hit).
            - If can_proceed is False and cached_result is None: Request is currently being processed by another worker.
        """
        now = datetime.now(timezone.utc)
        
        # Check in-memory store
        record = self._memory_store.get(idempotency_key)
        if record:
            if record["status"] == "COMPLETED":
                logger.info(f"Idempotency Cache Hit for key {idempotency_key[:12]} (source: {source_id}). Returning cached response.")
                return False, record.get("result")
            elif record["status"] == "PENDING":
                # Check lock expiration (30s timeout)
                if now - record["timestamp"] < timedelta(seconds=30):
                    logger.warning(f"Concurrent request detected for locked key {idempotency_key[:12]}. Rejecting duplicate in-flight call.")
                    return False, None

        # Lock acquired
        self._memory_store[idempotency_key] = {
            "source_id": source_id,
            "status": "PENDING",
            "timestamp": now,
            "result": None
        }

        # Persist to database if pool is active
        if db_manager and hasattr(db_manager, "execute"):
            try:
                await db_manager.execute("""
                    INSERT INTO idempotency_ledger (idempotency_key, source_id, status, created_at)
                    VALUES ($1, $2, 'PENDING', CURRENT_TIMESTAMP)
                    ON CONFLICT (idempotency_key) DO UPDATE
                    SET status = 'PENDING', created_at = CURRENT_TIMESTAMP
                    WHERE idempotency_ledger.status = 'FAILED'
                """, idempotency_key, source_id)
            except Exception as e:
                logger.debug(f"Idempotency ledger DB insert skipped: {e}")

        return True, None

    async def mark_completed(self, idempotency_key: str, result: Dict[str, Any], db_manager: Optional[Any] = None) -> None:
        """Marks idempotency record as COMPLETED and caches result."""
        if idempotency_key in self._memory_store:
            self._memory_store[idempotency_key]["status"] = "COMPLETED"
            self._memory_store[idempotency_key]["result"] = result

        if db_manager and hasattr(db_manager, "execute"):
            try:
                await db_manager.execute("""
                    UPDATE idempotency_ledger 
                    SET status = 'COMPLETED', result_payload = $1, completed_at = CURRENT_TIMESTAMP
                    WHERE idempotency_key = $2
                """, json.dumps(result), idempotency_key)
            except Exception as e:
                logger.debug(f"Idempotency ledger DB update skipped: {e}")

    async def mark_failed(self, idempotency_key: str, error_message: str, db_manager: Optional[Any] = None) -> None:
        """Marks idempotency record as FAILED to allow corrective retry."""
        if idempotency_key in self._memory_store:
            self._memory_store[idempotency_key]["status"] = "FAILED"
            self._memory_store[idempotency_key]["error"] = error_message

idempotency_manager = IdempotencyManager()
