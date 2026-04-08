import pytest
import os
import sys
import json

# Add parent directory to path to import main
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import create_flask_app, Database, TaskOrchestrator
from unittest.mock import MagicMock, AsyncMock

# Fixtures

@pytest.fixture
def mock_db():
    db = Database()
    # Use in-memory DB for tests
    db.conn = sqlite3.connect(":memory:")
    db.init_db()
    return db

@pytest.fixture
def mock_orchestrator():
    orch = TaskOrchestrator(None, None)
    orch.is_running = True
    return orch

@pytest.fixture
def client(mock_db, mock_orchestrator):
    app = create_flask_app(mock_db, mock_orchestrator)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Tests

def test_health_endpoint(client):
    """Test the health check endpoint returns 200."""
    rv = client.get('/health')
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert data['status'] == 'ok'
    assert 'service' in data

def test_status_endpoint(client, mock_db):
    """Test the status endpoint reflects database state."""
    # Add dummy data
    mock_db.log_task("test_task", {}, "pending")
    
    rv = client.get('/status')
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert 'database_stats' in data
    assert data['orchestrator_running'] == True

def test_trigger_task_endpoint(client):
    """Test triggering a task via API."""
    payload = {"task_type": "manual_test", "data": "123"}
    rv = client.post('/trigger', json=payload)
    
    assert rv.status_code == 202
    data = json.loads(rv.data)
    assert 'message' in data

def test_trigger_task_missing_type(client):
    """Test trigger endpoint validation."""
    rv = client.post('/trigger', json={"data": "123"})
    assert rv.status_code == 400

def test_database_log_task(mock_db):
    """Test database logging functionality."""
    mock_db.log_task("unit_test", {"id": 1}, "success")
    stats = mock_db.get_stats()
    assert "success" in stats
    assert stats["success"] == 1

if __name__ == '__main__':
    pytest.main()