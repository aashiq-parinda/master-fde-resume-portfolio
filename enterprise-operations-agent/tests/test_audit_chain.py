import pytest
from src.audit.logger import ImmutableAuditLedger

def test_cryptographic_hash_chain_integrity():
    ledger = ImmutableAuditLedger()

    r1 = ledger.record_event("INC-101", "INGEST", "NODE_1", "SYSTEM", {"metric": 10})
    r2 = ledger.record_event("INC-101", "DIAGNOSE", "NODE_2", "AGENT", {"diag": "leak"})
    r3 = ledger.record_event("INC-101", "EXECUTE", "NODE_3", "AGENT", {"action": "restart"})

    assert r2.prev_hash == r1.hash
    assert r3.prev_hash == r2.hash

    valid, msg = ledger.verify_chain_integrity()
    assert valid is True

def test_tamper_detection_invalidates_chain():
    ledger = ImmutableAuditLedger()
    ledger.record_event("INC-202", "START", "N1", "SYSTEM", {"data": "clean"})
    r2 = ledger.record_event("INC-202", "EXEC", "N2", "AGENT", {"data": "normal"})

    # Malicious actor tampers with record payload
    r2.payload["data"] = "TAMPERED_MALICIOUS_LOG"

    valid, msg = ledger.verify_chain_integrity()
    assert valid is False
    assert "tampered" in msg.lower()
