import pytest
import asyncio
from src.engine.idempotency import IdempotencyManager

@pytest.mark.asyncio
async def test_idempotency_key_generation_and_caching():
    mgr = IdempotencyManager()
    payload = {"order_id": 901, "customer": "Rohan", "total": 1500.0}
    
    key1 = mgr.compute_idempotency_key("webhook", "ORD-901", payload)
    key2 = mgr.compute_idempotency_key("webhook", "ORD-901", payload)
    assert key1 == key2 # Deterministic SHA-256 hash
    
    # First attempt: lock acquired
    can_proceed, cached = await mgr.acquire_lock(key1, "webhook")
    assert can_proceed is True
    assert cached is None
    
    # Mark completed with result
    result = {"status": "success", "external_id": "ORD-901"}
    await mgr.mark_completed(key1, result)
    
    # Second duplicate attempt: should hit cache
    can_proceed_dup, cached_dup = await mgr.acquire_lock(key1, "webhook")
    assert can_proceed_dup is False
    assert cached_dup == result
