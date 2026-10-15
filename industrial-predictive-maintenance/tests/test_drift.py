import pytest
import numpy as np
from src.analytics.drift import calculate_psi, compute_empirical_ks_stat, SensorDriftDetector

def test_psi_stable_distribution():
    np.random.seed(42)
    expected = np.random.normal(loc=50.0, scale=5.0, size=500)
    actual = np.random.normal(loc=50.2, scale=5.1, size=500)
    psi = calculate_psi(expected, actual)
    # Identical or near-identical distributions have PSI < 0.10
    assert psi < 0.10

def test_psi_drifting_distribution():
    np.random.seed(42)
    expected = np.random.normal(loc=50.0, scale=5.0, size=500)
    actual = np.random.normal(loc=65.0, scale=8.0, size=500) # Substantial shift
    psi = calculate_psi(expected, actual)
    assert psi >= 0.25

def test_ks_statistic():
    np.random.seed(42)
    ref = np.random.normal(0, 1, 300)
    prod = np.random.normal(0, 1, 300)
    ks = compute_empirical_ks_stat(ref, prod)
    assert ks < 0.20

    prod_shifted = np.random.normal(3, 1, 300)
    ks_shifted = compute_empirical_ks_stat(ref, prod_shifted)
    assert ks_shifted > 0.80

def test_sensor_drift_detector_lifecycle():
    baseline_records = [
        {"vibration": 2.2, "temperature": 65.0, "rpm": 1800.0, "pressure": 45.0}
        for _ in range(50)
    ]
    detector = SensorDriftDetector(baseline_records, window_size=50)

    # Ingest shifted readings
    for _ in range(40):
        detector.add_reading({"vibration": 5.5, "temperature": 95.0, "rpm": 1400.0, "pressure": 80.0})

    report = detector.evaluate_drift()
    assert report["overall_status"] in ["MODERATE_DRIFT", "CRITICAL_DRIFT"]
    assert "sensor_reports" in report
