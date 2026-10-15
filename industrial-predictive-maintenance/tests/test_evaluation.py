import pytest
import numpy as np
from src.analytics.evaluation import generate_benchmark_telemetry, AnomalyEvaluator

def test_generate_benchmark_telemetry():
    df, y_true = generate_benchmark_telemetry(n_samples=500, anomaly_rate=0.10)
    assert len(df) == 500
    assert len(y_true) == 500
    assert np.sum(y_true) == 50 # 10% of 500
    assert set(df.columns) == {"vibration", "temperature", "rpm", "pressure"}

def test_anomaly_evaluator_metrics():
    df, y_true = generate_benchmark_telemetry(n_samples=400, anomaly_rate=0.10)
    evaluator = AnomalyEvaluator(machine_id="M-102")
    results = evaluator.fit_and_evaluate(df, y_true)

    assert "statistical_zscore_model" in results
    assert "isolation_forest_ml_model" in results
    assert "composite_ensemble_model" in results

    ens = results["composite_ensemble_model"]
    assert "precision" in ens
    assert "recall" in ens
    assert "f1_score" in ens
    assert "false_positive_rate" in ens
    # Model should achieve reasonable detection performance on injected physical anomalies
    assert ens["recall"] > 0.60
    assert ens["f1_score"] > 0.50
