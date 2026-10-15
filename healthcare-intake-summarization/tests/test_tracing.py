import pytest
import time
from src.tracing.tracer import PipelineTrace, TraceRepository

def test_pipeline_tracing_spans_and_metrics():
    trace = PipelineTrace(intake_id=42, patient_name="Test Patient")
    trace.start_span("span_1")
    time.sleep(0.01)
    trace.end_span("span_1", status="OK", detail="span 1 done")
    
    trace.start_span("span_2")
    trace.end_span("span_2", status="OK")
    
    trace.finish()
    d = trace.to_dict()
    
    assert d["intake_id"] == 42
    assert d["total_duration_ms"] > 5.0
    assert len(d["spans"]) == 2
    assert d["spans"][0]["name"] == "span_1"
    assert d["spans"][0]["duration_ms"] > 5.0

def test_trace_repository_recording():
    repo = TraceRepository(capacity=5)
    t = PipelineTrace(intake_id=1, patient_name="A").finish()
    repo.record(t)
    assert len(repo.get_all()) == 1
    fetched = repo.get_by_id(t.trace_id)
    assert fetched is not None
    assert fetched["trace_id"] == t.trace_id
