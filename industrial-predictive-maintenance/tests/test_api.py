import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient

# Mock database and streaming operations during module load / import
with patch("src.storage.db.db_manager.initialize_database", new_callable=AsyncMock), \
     patch("src.storage.db.db_manager.start_pool", new_callable=AsyncMock), \
     patch("src.queue.streaming.stream_manager.connect", new_callable=AsyncMock):
    from src.api.main import app

# Clear startup/shutdown handlers to prevent running background generator/consumer loops during testing
app.router.on_startup = []
app.router.on_shutdown = []

client = TestClient(app)


@pytest.fixture
def mock_db():
    with patch("src.api.main.db_manager", new_callable=MagicMock) as mock:
        yield mock

@pytest.fixture
def mock_assistant():
    with patch("src.api.main.ai_assistant", new_callable=MagicMock) as mock:
        yield mock

def test_get_observability_metrics():
    # Observability metrics should read from PipelineTelemetry (in-memory)
    response = client.get("/api/observability/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "events_processed" in data
    assert "uptime_seconds" in data
    assert "avg_latency_ms" in data

def test_get_machines_endpoint(mock_db):
    # Setup mock return value for db fetch
    mock_db.fetch = AsyncMock(return_value=[
        {
            "machine_id": "M-101",
            "name": "CNC Lathe",
            "model": "T-1000",
            "status": "healthy",
            "vibration": 1.8,
            "temperature": 55.0,
            "rpm": 1500.0,
            "pressure": 30.0,
            "timestamp": "2026-08-22T20:00:00Z",
            "failure_probability": 0.05,
            "estimated_window_hours": None
        }
    ])
    
    response = client.get("/api/machines")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["machine_id"] == "M-101"
    assert data[0]["status"] == "healthy"
    mock_db.fetch.assert_called_once()

def test_post_maintenance_log_success(mock_db):
    mock_db.fetchval = AsyncMock(return_value=True) # Machine exists
    mock_db.execute = AsyncMock(return_value="INSERT 1")
    
    payload = {
        "machine_id": "M-102",
        "action": "Swapped bearings",
        "notes": "Bearing wear was high."
    }
    
    response = client.post("/api/maintenance", json=payload)
    assert response.status_code == 201
    assert response.json()["status"] == "success"

def test_post_maintenance_log_not_found(mock_db):
    mock_db.fetchval = AsyncMock(return_value=None) # Machine doesn't exist
    
    payload = {
        "machine_id": "M-999",
        "action": "Break down check",
        "notes": "Testing error case."
    }
    
    response = client.post("/api/maintenance", json=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_query_assistant_endpoint(mock_db, mock_assistant):
    mock_db.fetch = AsyncMock(return_value=[]) # Mock current context
    mock_assistant.answer_query = AsyncMock(return_value="Machine is healthy.")
    
    payload = {"query": "What's wrong with M-101?"}
    response = client.post("/api/assistant/query", json=payload)
    
    assert response.status_code == 200
    assert response.json()["response"] == "Machine is healthy."
    mock_assistant.answer_query.assert_called_once()
