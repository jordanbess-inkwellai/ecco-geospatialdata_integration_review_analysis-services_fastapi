import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import json
import asyncio
from unittest.mock import patch, MagicMock

from app.main import app
from app.core.database import get_db

# Create a test database
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Override the get_db dependency
async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

# Create a test client
client = TestClient(app)

def test_list_processes():
    """Test listing all processes."""
    response = client.get("/api/v1/processes")
    assert response.status_code == 200
    
    data = response.json()
    assert "processes" in data
    assert isinstance(data["processes"], list)
    
    # Check that we have some processes
    assert len(data["processes"]) > 0
    
    # Check that each process has the required fields
    for process in data["processes"]:
        assert "id" in process
        assert "title" in process
        assert "description" in process

def test_get_process():
    """Test getting a specific process."""
    # First, get the list of processes
    response = client.get("/api/v1/processes")
    processes = response.json()["processes"]
    
    # Get the first process ID
    process_id = processes[0]["id"]
    
    # Get the process details
    response = client.get(f"/api/v1/processes/{process_id}")
    assert response.status_code == 200
    
    process = response.json()
    assert process["id"] == process_id
    assert "title" in process
    assert "description" in process
    assert "inputs" in process
    assert "outputs" in process

def test_get_nonexistent_process():
    """Test getting a process that doesn't exist."""
    response = client.get("/api/v1/processes/nonexistent")
    assert response.status_code == 404
    
    error = response.json()
    assert "detail" in error
    assert "not found" in error["detail"].lower()

@pytest.mark.asyncio
async def test_execute_buffer_process():
    """Test executing the buffer process."""
    # Mock the database session to return a valid result
    async def mock_execute(*args, **kwargs):
        result = MagicMock()
        result.fetchone.return_value = MagicMock(
            buffered_geometry='{"type":"Polygon","coordinates":[[[0,0],[1,0],[1,1],[0,1],[0,0]]]}'
        )
        return result
    
    # Create a mock session
    mock_session = MagicMock()
    mock_session.execute = mock_execute
    
    # Override the get_db dependency for this test
    async def override_get_db_for_test():
        yield mock_session
    
    app.dependency_overrides[get_db] = override_get_db_for_test
    
    # Define test inputs
    inputs = {
        "geometry": {"type": "Point", "coordinates": [0, 0]},
        "distance": 100
    }
    
    # Execute the process
    response = client.post("/api/v1/processes/buffer/execution", json=inputs)
    
    # Reset the dependency override
    app.dependency_overrides[get_db] = override_get_db
    
    # Check the response
    assert response.status_code == 200
    
    result = response.json()
    assert "result" in result
    assert "buffered_geometry" in result["result"]
    assert result["result"]["buffered_geometry"]["type"] == "Polygon"

def test_execute_process_with_invalid_inputs():
    """Test executing a process with invalid inputs."""
    # Define invalid inputs (missing required parameter)
    inputs = {
        "geometry": {"type": "Point", "coordinates": [0, 0]}
        # Missing distance parameter
    }
    
    # Execute the process
    response = client.post("/api/v1/processes/buffer/execution", json=inputs)
    
    # Check the response
    assert response.status_code == 500
    
    error = response.json()
    assert "detail" in error
    assert "error" in error["detail"].lower()

def test_execute_nonexistent_process():
    """Test executing a process that doesn't exist."""
    # Define test inputs
    inputs = {
        "test_input": "value"
    }
    
    # Execute the process
    response = client.post("/api/v1/processes/nonexistent/execution", json=inputs)
    
    # Check the response
    assert response.status_code == 404
    
    error = response.json()
    assert "detail" in error
    assert "not found" in error["detail"].lower()
