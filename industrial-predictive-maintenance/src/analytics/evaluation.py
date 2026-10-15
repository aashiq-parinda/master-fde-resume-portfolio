import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from sklearn.metrics import (
    precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score,
    confusion_matrix
)
from src.analytics.models import MaintenancePredictor

def generate_benchmark_telemetry(n_samples: int = 1000, anomaly_rate: float = 0.10, random_seed: int = 42) -> Tuple[pd.DataFrame, np.ndarray]:
    """
    Generates realistic industrial sensor telemetry with ground-truth anomaly labels.
    Simulates:
    - Normal steady-state operation
    - Bearing failure (high frequency vibration spikes)
    - Thermal runaway (gradual temperature escalation)
    - Pump cavitation (extreme pressure drops & surges)
    - Motor imbalance (RPM fluctuations)
    """
    np.random.seed(random_seed)
    n_anomalies = int(n_samples * anomaly_rate)
    n_normal = n_samples - n_anomalies

    # 1. Normal baseline telemetry
    normal_vibration = np.random.normal(loc=2.2, scale=0.25, size=n_normal)
    normal_temperature = np.random.normal(loc=65.0, scale=2.5, size=n_normal)
    normal_rpm = np.random.normal(loc=1800.0, scale=30.0, size=n_normal)
    normal_pressure = np.random.normal(loc=45.0, scale=3.0, size=n_normal)
    normal_labels = np.zeros(n_normal, dtype=int)

    # 2. Injected physical anomalies
    # Sub-case A: Bearing failure (35% of anomalies)
    nA = int(n_anomalies * 0.35)
    anom_A_vib = np.random.normal(loc=4.5, scale=0.6, size=nA) # Severe vibration
    anom_A_temp = np.random.normal(loc=78.0, scale=3.0, size=nA)
    anom_A_rpm = np.random.normal(loc=1750.0, scale=40.0, size=nA)
    anom_A_pres = np.random.normal(loc=44.0, scale=3.0, size=nA)

    # Sub-case B: Thermal runaway (35% of anomalies)
    nB = int(n_anomalies * 0.35)
    anom_B_vib = np.random.normal(loc=2.6, scale=0.3, size=nB)
    anom_B_temp = np.random.normal(loc=95.0, scale=4.0, size=nB) # Critical heat
    anom_B_rpm = np.random.normal(loc=1800.0, scale=30.0, size=nB)
    anom_B_pres = np.random.normal(loc=52.0, scale=4.0, size=nB)

    # Sub-case C: Cavitation & pressure surge (30% of anomalies)
    nC = n_anomalies - nA - nB
    anom_C_vib = np.random.normal(loc=3.8, scale=0.4, size=nC)
    anom_C_temp = np.random.normal(loc=68.0, scale=3.0, size=nC)
    anom_C_rpm = np.random.normal(loc=1600.0, scale=80.0, size=nC) # RPM drop
    anom_C_pres = np.random.normal(loc=85.0, scale=7.0, size=nC) # Surge

    anom_vibration = np.concatenate([anom_A_vib, anom_B_vib, anom_C_vib])
    anom_temperature = np.concatenate([anom_A_temp, anom_B_temp, anom_C_temp])
    anom_rpm = np.concatenate([anom_A_rpm, anom_B_rpm, anom_C_rpm])
    anom_pressure = np.concatenate([anom_A_pres, anom_B_pres, anom_C_pres])
    anom_labels = np.ones(n_anomalies, dtype=int)

    # Combine & shuffle
    vibration = np.concatenate([normal_vibration, anom_vibration])
    temperature = np.concatenate([normal_temperature, anom_temperature])
    rpm = np.concatenate([normal_rpm, anom_rpm])
    pressure = np.concatenate([normal_pressure, anom_pressure])
    y_true = np.concatenate([normal_labels, anom_labels])

    indices = np.arange(n_samples)
    np.random.shuffle(indices)

    df = pd.DataFrame({
        "vibration": vibration[indices],
        "temperature": temperature[indices],
        "rpm": rpm[indices],
        "pressure": pressure[indices]
    })
    y_true = y_true[indices]

    return df, y_true

class AnomalyEvaluator:
    """
    Benchmarking suite for Industrial Anomaly Detection algorithms.
    Evaluates Statistical Z-score, Isolation Forest, and Composite Ensemble.
    """
    def __init__(self, machine_id: str = "M-102"):
        self.machine_id = machine_id
        self.predictor = MaintenancePredictor()

    def fit_and_evaluate(self, df_telemetry: pd.DataFrame, y_true: np.ndarray, train_ratio: float = 0.5) -> Dict[str, Any]:
        n_train = int(len(df_telemetry) * train_ratio)
        df_train = df_telemetry.iloc[:n_train]
        df_test = df_telemetry.iloc[n_train:]
        y_test = y_true[n_train:]

        # Train Isolation Forest on normal baseline subset
        normal_train = df_train.to_dict(orient="records")
        self.predictor.train_isolation_forest(self.machine_id, normal_train)

        # Inference loop
        y_pred_stat = []
        y_pred_ml = []
        y_pred_ensemble = []
        prob_scores = []

        history_buffer = normal_train[-50:]

        for _, row in df_test.iterrows():
            reading = row.to_dict()
            statuses, prob, _ = self.predictor.predict(self.machine_id, reading, history_buffer)

            # Statistical model decision
            is_stat = any(s == "anomalous" for s in statuses.values())
            y_pred_stat.append(1 if is_stat else 0)

            # ML model decision
            # Prob > 0.40 indicates high ML anomaly likelihood
            y_pred_ml.append(1 if prob > 0.40 else 0)

            # Composite decision
            y_pred_ensemble.append(1 if prob > 0.35 or is_stat else 0)
            prob_scores.append(prob)

        y_pred_stat = np.array(y_pred_stat)
        y_pred_ml = np.array(y_pred_ml)
        y_pred_ensemble = np.array(y_pred_ensemble)
        prob_scores = np.array(prob_scores)

        def _compute_metrics(y_pred: np.ndarray, y_score: Optional[np.ndarray] = None) -> Dict[str, float]:
            prec = precision_score(y_test, y_pred, zero_division=0)
            rec = recall_score(y_test, y_pred, zero_division=0)
            f1 = f1_score(y_test, y_pred, zero_division=0)
            cm = confusion_matrix(y_test, y_pred)
            tn, fp, fn, tp = cm.ravel() if cm.shape == (2, 2) else (0, 0, 0, 0)
            fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0

            metrics = {
                "precision": round(float(prec), 4),
                "recall": round(float(rec), 4),
                "f1_score": round(float(f1), 4),
                "false_positive_rate": round(float(fpr), 4),
                "tp": int(tp), "fp": int(fp), "tn": int(tn), "fn": int(fn)
            }

            if y_score is not None and len(np.unique(y_test)) > 1:
                try:
                    metrics["roc_auc"] = round(float(roc_auc_score(y_test, y_score)), 4)
                    metrics["pr_auc"] = round(float(average_precision_score(y_test, y_score)), 4)
                except Exception:
                    metrics["roc_auc"] = 0.0
                    metrics["pr_auc"] = 0.0

            return metrics

        return {
            "test_sample_count": len(y_test),
            "anomaly_incidence": round(float(np.mean(y_test)), 4),
            "statistical_zscore_model": _compute_metrics(y_pred_stat),
            "isolation_forest_ml_model": _compute_metrics(y_pred_ml, prob_scores),
            "composite_ensemble_model": _compute_metrics(y_pred_ensemble, prob_scores)
        }
