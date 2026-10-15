import hashlib
import json
import time
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timezone

class AuditRecord:
    def __init__(
        self,
        sequence: int,
        prev_hash: str,
        incident_id: str,
        event_type: str,
        node: str,
        actor: str,
        payload: Dict[str, Any],
        timestamp: Optional[str] = None
    ):
        self.sequence = sequence
        self.prev_hash = prev_hash
        self.incident_id = incident_id
        self.event_type = event_type
        self.node = node
        self.actor = actor
        self.payload = payload
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()
        self.hash = self._compute_hash()

    def _compute_hash(self) -> str:
        serialized = json.dumps(self.payload, sort_keys=True)
        raw = f"{self.sequence}|{self.prev_hash}|{self.incident_id}|{self.event_type}|{self.node}|{self.actor}|{self.timestamp}|{serialized}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sequence": self.sequence,
            "hash": self.hash,
            "prev_hash": self.prev_hash,
            "incident_id": self.incident_id,
            "event_type": self.event_type,
            "node": self.node,
            "actor": self.actor,
            "timestamp": self.timestamp,
            "payload": self.payload
        }

class ImmutableAuditLedger:
    """
    Cryptographically chained, tamper-evident audit ledger.
    Guarantees immutable provenance of all AI agent thoughts, tool calls,
    human operator approvals, and recovery rollbacks.
    """
    GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

    def __init__(self):
        self.chain: List[AuditRecord] = []

    def record_event(
        self,
        incident_id: str,
        event_type: str,
        node: str,
        actor: str,
        payload: Dict[str, Any]
    ) -> AuditRecord:
        """Appends new event to cryptographic hash chain."""
        seq = len(self.chain) + 1
        prev_h = self.chain[-1].hash if self.chain else self.GENESIS_HASH
        rec = AuditRecord(
            sequence=seq,
            prev_hash=prev_h,
            incident_id=incident_id,
            event_type=event_type,
            node=node,
            actor=actor,
            payload=payload
        )
        self.chain.append(rec)
        return rec

    def verify_chain_integrity(self) -> Tuple[bool, Optional[str]]:
        """
        Validates cryptographic hash chain integrity.
        Returns: (is_valid: bool, error_message: Optional[str])
        """
        for i, rec in enumerate(self.chain):
            # Check previous hash pointer
            expected_prev = self.chain[i - 1].hash if i > 0 else self.GENESIS_HASH
            if rec.prev_hash != expected_prev:
                return False, f"Broken chain link at sequence #{rec.sequence}: prev_hash mismatch."

            # Check self hash computation
            recalculated = rec._compute_hash()
            if rec.hash != recalculated:
                return False, f"Tampered record detected at sequence #{rec.sequence}: hash mismatch."

        return True, "Chain integrity verified. All records immutable and authentic."

    def get_incident_audit_trail(self, incident_id: str) -> List[Dict[str, Any]]:
        return [r.to_dict() for r in self.chain if r.incident_id == incident_id]

    def get_all_records(self, limit: int = 100) -> List[Dict[str, Any]]:
        return [r.to_dict() for r in reversed(self.chain[-limit:])]

audit_ledger = ImmutableAuditLedger()
