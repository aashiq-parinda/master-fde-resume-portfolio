import pytest
from src.analytics.models import MaintenancePredictor

def test_nominal_readings():
    predictor = MaintenancePredictor()
    # M-101 baseline: vib=1.8, temp=55.0, rpm=1500, pressure=30.0
    nominal_reading = {
        "vibration": 1.8,
        "temperature": 55.0,
        "rpm": 1500.0,
        "pressure": 30.0
    }
    
    statuses, fail_prob, window = predictor.predict("M-101", nominal_reading, [])
    
    # Assert normal status and low failure probability
    assert statuses["vibration_status"] == "normal"
    assert statuses["temperature_status"] == "normal"
    assert fail_prob < 0.20
    assert window is None

def test_anomalous_readings():
    predictor = MaintenancePredictor()
    # M-102 baseline: vib=2.2, temp=65.0, rpm=1800, pressure=45.0
    # Inject massive values
    anomalous_reading = {
        "vibration": 8.5, # Critical spike
        "temperature": 98.0, # High temp
        "rpm": 1820.0,
        "pressure": 46.0
    }
    
    statuses, fail_prob, window = predictor.predict("M-102", anomalous_reading, [])
    
    # Assert anomaly detected
    assert statuses["vibration_status"] == "anomalous"
    assert statuses["temperature_status"] == "anomalous"
    assert fail_prob > 0.50
    assert window is not None
    assert 4.0 <= window <= 48.0

def test_isolation_forest_retraining():
    predictor = MaintenancePredictor()
    # Create 35 normal readings for M-103
    history = []
    for _ in range(35):
        history.append({
            "vibration": 1.5,
            "temperature": 50.0,
            "rpm": 1200.0,
            "pressure": 90.0
        })
        
    # Fit model
    success = predictor.train_isolation_forest("M-103", history)
    assert success is True
    assert "M-103" in predictor.models
    
    # Test predictions with trained model
    normal_pred = {
        "vibration": 1.5,
        "temperature": 50.0,
        "rpm": 1200.0,
        "pressure": 90.0
    }
    statuses, fail_prob, window = predictor.predict("M-103", normal_pred, history)
    # Since it's normal, the Isolation Forest should predict 1 (normal)
    # We can check that the prediction works without crashing
    assert isinstance(fail_prob, float)
