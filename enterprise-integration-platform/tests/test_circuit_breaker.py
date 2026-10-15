import pytest
import time
from src.engine.circuit_breaker import CircuitBreaker, CircuitState, calculate_full_jitter_delay

def test_circuit_breaker_trip_and_canary_recovery():
    cb = CircuitBreaker(name="test_api", failure_threshold=2, recovery_timeout_seconds=0.05)
    
    assert cb.state == CircuitState.CLOSED
    assert cb.can_execute() is True
    
    # 1st failure
    cb.record_failure(Exception("Timeout 1"))
    assert cb.state == CircuitState.CLOSED
    
    # 2nd failure -> Tripped to OPEN
    cb.record_failure(Exception("Timeout 2"))
    assert cb.state == CircuitState.OPEN
    assert cb.can_execute() is False
    
    # Wait for recovery timeout
    time.sleep(0.06)
    
    # Next call transitions to HALF_OPEN
    assert cb.can_execute() is True
    assert cb.state == CircuitState.HALF_OPEN
    
    # Canary succeeds -> Resets to CLOSED
    cb.record_success()
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 0

def test_full_jitter_delay():
    for attempt in range(1, 5):
        d = calculate_full_jitter_delay(attempt, base_delay=1.0, max_delay=10.0)
        assert 0.1 <= d <= 10.0
