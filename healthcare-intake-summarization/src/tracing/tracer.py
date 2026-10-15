import time
import uuid
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger("tracer")

class TraceSpan:
    def __init__(self, name: str, parent_id: Optional[str] = None):
        self.span_id = str(uuid.uuid4())[:8]
        self.parent_id = parent_id
        self.name = name
        self.start_time = time.perf_counter()
        self.end_time: Optional[float] = None
        self.duration_ms: float = 0.0
        self.status: str = "RUNNING"
        self.metadata: Dict[str, Any] = {}
        self.error: Optional[str] = None

    def end(self, status: str = "OK", error: Optional[str] = None, **kwargs):
        self.end_time = time.perf_counter()
        self.duration_ms = round((self.end_time - self.start_time) * 1000, 2)
        self.status = status
        self.error = error
        self.metadata.update(kwargs)
        return self

    def to_dict(self) -> Dict[str, Any]:
        return {
            "span_id": self.span_id,
            "parent_id": self.parent_id,
            "name": self.name,
            "duration_ms": self.duration_ms,
            "status": self.status,
            "metadata": self.metadata,
            "error": self.error
        }

class PipelineTrace:
    def __init__(self, intake_id: Optional[int] = None, patient_name: Optional[str] = None):
        self.trace_id = f"trc-{uuid.uuid4().hex[:12]}"
        self.intake_id = intake_id
        self.patient_name = patient_name
        self.start_time = time.perf_counter()
        self.end_time: Optional[float] = None
        self.total_duration_ms: float = 0.0
        self.status: str = "RUNNING"
        self.spans: List[TraceSpan] = []
        self._active_spans: Dict[str, TraceSpan] = {}

    def start_span(self, name: str, parent_span_name: Optional[str] = None) -> TraceSpan:
        parent_id = self._active_spans[parent_span_name].span_id if parent_span_name and parent_span_name in self._active_spans else None
        span = TraceSpan(name=name, parent_id=parent_id)
        self.spans.append(span)
        self._active_spans[name] = span
        return span

    def end_span(self, name: str, status: str = "OK", error: Optional[str] = None, **kwargs):
        if name in self._active_spans:
            span = self._active_spans.pop(name)
            span.end(status=status, error=error, **kwargs)
            return span
        return None

    def finish(self, status: str = "COMPLETED") -> "PipelineTrace":
        self.end_time = time.perf_counter()
        self.total_duration_ms = round((self.end_time - self.start_time) * 1000, 2)
        self.status = status
        return self

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "intake_id": self.intake_id,
            "patient_name": self.patient_name,
            "total_duration_ms": self.total_duration_ms,
            "status": self.status,
            "spans": [s.to_dict() for s in self.spans]
        }

class TraceRepository:
    """In-memory ring buffer holding recent RAG execution traces."""
    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self.traces: List[Dict[str, Any]] = []

    def record(self, trace: PipelineTrace):
        d = trace.to_dict()
        self.traces.insert(0, d)
        if len(self.traces) > self.capacity:
            self.traces.pop()

    def get_all(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self.traces[:limit]

    def get_by_id(self, trace_id: str) -> Optional[Dict[str, Any]]:
        for t in self.traces:
            if t["trace_id"] == trace_id:
                return t
        return None

# Global singleton repository
trace_repo = TraceRepository()
