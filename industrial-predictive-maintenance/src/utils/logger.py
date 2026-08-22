import logging
import time
from typing import Dict, Any

# Configure logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

class PipelineTelemetry:
    """
    In-memory storage for pipeline metrics & telemetry.
    Allows basic observability of event processing latency, error counts, and volume.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PipelineTelemetry, cls).__new__(cls)
            cls._instance.metrics = {
                "events_processed": 0,
                "anomalies_detected": 0,
                "processing_time_total_ms": 0.0,
                "errors_count": 0,
                "start_time": time.time()
            }
        return cls._instance

    def record_event(self, latency_ms: float, is_anomaly: bool = False):
        self.metrics["events_processed"] += 1
        self.metrics["processing_time_total_ms"] += latency_ms
        if is_anomaly:
            self.metrics["anomalies_detected"] += 1

    def record_error(self):
        self.metrics["errors_count"] += 1

    def get_metrics(self) -> Dict[str, Any]:
        uptime_seconds = time.time() - self.metrics["start_time"]
        avg_latency_ms = (
            self.metrics["processing_time_total_ms"] / self.metrics["events_processed"]
            if self.metrics["events_processed"] > 0
            else 0.0
        )
        return {
            "uptime_seconds": round(uptime_seconds, 2),
            "events_processed": self.metrics["events_processed"],
            "anomalies_detected": self.metrics["anomalies_detected"],
            "avg_latency_ms": round(avg_latency_ms, 3),
            "errors_count": self.metrics["errors_count"],
            "throughput_events_per_sec": round(self.metrics["events_processed"] / max(uptime_seconds, 1.0), 3)
        }

telemetry = PipelineTelemetry()
