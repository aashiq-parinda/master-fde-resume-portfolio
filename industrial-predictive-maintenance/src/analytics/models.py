import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from typing import Dict, Any, Tuple, Optional
from src.utils.logger import get_logger, telemetry

logger = get_logger("analytics")

class MaintenancePredictor:
    """
    Combines Isolation Forest ML model and statistical threshold analysis
    to detect sensor anomalies, compute failure probabilities,
    and predict maintenance windows.
    """
    def __init__(self):
        # Store individual Isolation Forest models per machine
        self.models: Dict[str, IsolationForest] = {}
        # Baselines for statistical thresholds if models aren't trained yet
        # Mean & Std for: [vibration, temperature, rpm, pressure]
        self.baselines = {
            "M-101": {"mean": [1.8, 55.0, 1500.0, 30.0], "std": [0.2, 1.5, 20.0, 2.0]},
            "M-102": {"mean": [2.2, 65.0, 1800.0, 45.0], "std": [0.25, 2.5, 30.0, 3.0]},
            "M-103": {"mean": [1.5, 50.0, 1200.0, 90.0], "std": [0.15, 1.2, 15.0, 5.0]},
            "M-104": {"mean": [2.5, 75.0, 3000.0, 60.0], "std": [0.3, 3.0, 50.0, 4.0]},
            "M-105": {"mean": [1.2, 45.0, 800.0, 15.0], "std": [0.1, 1.0, 10.0, 1.5]}
        }

    def _get_z_scores(self, machine_id: str, reading: dict) -> Dict[str, float]:
        """Helper to calculate z-scores of current sensor values against baseline."""
        baseline = self.baselines.get(machine_id)
        if not baseline:
            return {k: 0.0 for k in ["vibration", "temperature", "rpm", "pressure"]}
        
        means = baseline["mean"]
        stds = baseline["std"]
        
        return {
            "vibration": (reading["vibration"] - means[0]) / stds[0],
            "temperature": (reading["temperature"] - means[1]) / stds[1],
            "rpm": (reading["rpm"] - means[2]) / stds[2],
            "pressure": (reading["pressure"] - means[3]) / stds[3]
        }

    def train_isolation_forest(self, machine_id: str, history: list) -> bool:
        """
        Fits/retrains an IsolationForest model on a list of historical readings.
        Requires at least 30 historical records to establish a reliable baseline.
        """
        if len(history) < 30:
            logger.debug(f"Insufficient history ({len(history)}/30) to train Isolation Forest for {machine_id}")
            return False

        try:
            # Convert history to DataFrame
            df = pd.DataFrame(history)
            features = ["vibration", "temperature", "rpm", "pressure"]
            X = df[features].values
            
            # Train model with low contamination (assuming mostly healthy data in recent window)
            model = IsolationForest(contamination=0.08, random_state=42)
            model.fit(X)
            self.models[machine_id] = model
            logger.info(f"Retrained Isolation Forest model successfully for {machine_id} using {len(history)} events.")
            return True
        except Exception as e:
            logger.error(f"Failed to train Isolation Forest for {machine_id}: {e}")
            telemetry.record_error()
            return False

    def predict(self, machine_id: str, current_reading: dict, history: list) -> Tuple[dict, float, Optional[float]]:
        """
        Evaluates a single reading.
        Returns:
            - sensor_statuses: dict representing whether each sensor is 'normal' or 'anomalous'
            - failure_probability: float (0.0 to 1.0)
            - estimated_window_hours: float or None
        """
        # 1. Statistical Threshold Anomaly Detection (Z-Score based)
        z_scores = self._get_z_scores(machine_id, current_reading)
        sensor_statuses = {}
        
        # Consider a single sensor anomalous if its z-score absolute value is greater than 3.0
        for sensor, z in z_scores.items():
            sensor_statuses[f"{sensor}_status"] = "anomalous" if abs(z) > 3.0 else "normal"
            
        is_stat_anomaly = any(status == "anomalous" for status in sensor_statuses.values())

        # 2. ML Isolation Forest Anomaly Detection
        is_ml_anomaly = False
        anomaly_score = 0.0
        
        model = self.models.get(machine_id)
        if model:
            try:
                features = [
                    current_reading["vibration"],
                    current_reading["temperature"],
                    current_reading["rpm"],
                    current_reading["pressure"]
                ]
                X_pred = np.array([features])
                # predict returns -1 for anomalies, 1 for normal
                pred = model.predict(X_pred)[0]
                is_ml_anomaly = (pred == -1)
                # score_samples returns the anomaly score (lower is more anomalous)
                anomaly_score = float(model.score_samples(X_pred)[0])
            except Exception as e:
                logger.error(f"Isolation Forest prediction error for {machine_id}: {e}")
                telemetry.record_error()
        
        # Determine overall anomaly flag: Combine statistical and ML triggers
        is_anomalous = is_stat_anomaly or is_ml_anomaly

        # 3. Calculate Failure Probability & Maintenance Window
        # Failure probability is modeled based on the magnitude of the worst z-score drift
        # focusing primarily on positive drifts in temperature and vibration (common failure indicators)
        max_drift_z = max(
            z_scores["vibration"], 
            z_scores["temperature"], 
            abs(z_scores["pressure"]), 
            abs(z_scores["rpm"])
        )
        
        if is_anomalous:
            # Scale probability between 50% and 99% based on the magnitude of the z-score drift
            # A z-score of 3.0 maps to ~50%, a z-score of 8.0 maps to 99%
            failure_prob = 0.5 + (0.49 * (min(max(max_drift_z, 3.0), 8.0) - 3.0) / 5.0)
            
            # Estimate recommended maintenance window in hours based on failure probability
            # 99% failure maps to 6 hours, 50% failure maps to 48 hours
            est_window = 48.0 - (42.0 * (failure_prob - 0.5) / 0.49)
            est_window = round(max(4.0, est_window), 1)
        else:
            # Under normal operation, baseline probability is low and based on subtle drifts
            failure_prob = 0.01 + (0.09 * (min(max(max_drift_z, 0.0), 3.0) / 3.0))
            est_window = None

        return sensor_statuses, round(failure_prob, 3), est_window

predictor = MaintenancePredictor()
