import numpy as np
from typing import Dict, Any, List, Tuple

def calculate_psi(expected: np.ndarray, actual: np.ndarray, num_bins: int = 10) -> float:
    """
    Computes Population Stability Index (PSI) between baseline (expected) and production (actual) distributions.
    PSI = sum((Actual_pct - Expected_pct) * ln(Actual_pct / Expected_pct))
    """
    if len(expected) == 0 or len(actual) == 0:
        return 0.0

    # Determine bin edges from expected baseline distribution
    percentiles = np.linspace(0, 100, num_bins + 1)
    bin_edges = np.percentile(expected, percentiles)
    bin_edges[0] = -np.inf
    bin_edges[-1] = np.inf

    # Calculate frequencies
    expected_counts, _ = np.histogram(expected, bins=bin_edges)
    actual_counts, _ = np.histogram(actual, bins=bin_edges)

    expected_pct = expected_counts / len(expected)
    actual_pct = actual_counts / len(actual)

    # Apply Laplace smoothing to avoid division by zero or log(0)
    eps = 1e-4
    expected_pct = np.where(expected_pct == 0, eps, expected_pct)
    actual_pct = np.where(actual_pct == 0, eps, actual_pct)

    # Renormalize
    expected_pct /= np.sum(expected_pct)
    actual_pct /= np.sum(actual_pct)

    psi_val = np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct))
    return float(round(psi_val, 4))

def compute_empirical_ks_stat(ref: np.ndarray, prod: np.ndarray) -> float:
    """
    Computes Kolmogorov-Smirnov statistic (maximum vertical distance between empirical CDFs).
    """
    if len(ref) == 0 or len(prod) == 0:
        return 0.0

    combined = np.sort(np.concatenate([ref, prod]))
    cdf_ref = np.searchsorted(np.sort(ref), combined, side="right") / len(ref)
    cdf_prod = np.searchsorted(np.sort(prod), combined, side="right") / len(prod)
    ks_stat = np.max(np.abs(cdf_ref - cdf_prod))
    return float(round(ks_stat, 4))

class SensorDriftDetector:
    """
    Real-time sensor drift and distribution shift monitor.
    Monitors degradation, calibration loss, and thermal drift across industrial sensors.
    """
    def __init__(self, baseline_history: List[Dict[str, float]], window_size: int = 100):
        self.window_size = window_size
        self.sensors = ["vibration", "temperature", "rpm", "pressure"]
        self.baseline = {
            s: np.array([r[s] for r in baseline_history if s in r], dtype=np.float32)
            for s in self.sensors
        }
        self.current_window: Dict[str, List[float]] = {s: [] for s in self.sensors}

    def add_reading(self, reading: Dict[str, float]) -> None:
        """Appends reading to sliding window."""
        for s in self.sensors:
            if s in reading:
                self.current_window[s].append(reading[s])
                if len(self.current_window[s]) > self.window_size:
                    self.current_window[s].pop(0)

    def evaluate_drift(self) -> Dict[str, Any]:
        """
        Evaluates PSI and KS statistics for each sensor.
        Classifies status:
        - STABLE (PSI < 0.10)
        - MODERATE_DRIFT (0.10 <= PSI < 0.25)
        - CRITICAL_DRIFT (PSI >= 0.25)
        """
        report: Dict[str, Any] = {
            "overall_status": "STABLE",
            "needs_retraining": False,
            "sensor_reports": {}
        }

        max_psi = 0.0

        for s in self.sensors:
            ref = self.baseline.get(s, np.array([]))
            prod = np.array(self.current_window.get(s, []), dtype=np.float32)

            if len(prod) < 20 or len(ref) < 20:
                report["sensor_reports"][s] = {
                    "psi": 0.0,
                    "ks_statistic": 0.0,
                    "status": "INSUFFICIENT_DATA",
                    "sample_count": len(prod)
                }
                continue

            psi = calculate_psi(ref, prod)
            ks = compute_empirical_ks_stat(ref, prod)

            if psi >= 0.25:
                status = "CRITICAL_DRIFT"
            elif psi >= 0.10:
                status = "MODERATE_DRIFT"
            else:
                status = "STABLE"

            if psi > max_psi:
                max_psi = psi

            report["sensor_reports"][s] = {
                "psi": psi,
                "ks_statistic": ks,
                "status": status,
                "ref_mean": round(float(np.mean(ref)), 2),
                "prod_mean": round(float(np.mean(prod)), 2),
                "prod_std": round(float(np.std(prod)), 2)
            }

        if max_psi >= 0.25:
            report["overall_status"] = "CRITICAL_DRIFT"
            report["needs_retraining"] = True
            report["action"] = "Trigger immediate model retraining and recalibrate physical sensors."
        elif max_psi >= 0.10:
            report["overall_status"] = "MODERATE_DRIFT"
            report["needs_retraining"] = False
            report["action"] = "Schedule telemetry inspection and sensor cleaning."
        else:
            report["overall_status"] = "STABLE"
            report["needs_retraining"] = False
            report["action"] = "Sensors operating within normal baseline tolerance."

        return report
