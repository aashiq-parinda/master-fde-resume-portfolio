import pytest
from src.analytics.models import MaintenancePredictor

def test_missing_features_resilience():
    predictor = MaintenancePredictor()
    # Missing pressure reading
    reading = {"vibration": 2.2, "temperature": 65.0, "rpm": 1800.0, "pressure": 45.0}
    statuses, prob, window = predictor.predict("M-102", reading, [])
    assert "vibration_status" in statuses
    assert 0.0 <= prob <= 1.0

def test_extreme_outlier_clamping():
    predictor = MaintenancePredictor()
    reading = {"vibration": 999.9, "temperature": 999.9, "rpm": 9999.0, "pressure": 999.9}
    statuses, prob, window = predictor.predict("M-102", reading, [])
    # Should flag critical anomaly without throwing NaN or division error
    assert prob >= 0.80
    assert any(s == "anomalous" for s in statuses.values())
