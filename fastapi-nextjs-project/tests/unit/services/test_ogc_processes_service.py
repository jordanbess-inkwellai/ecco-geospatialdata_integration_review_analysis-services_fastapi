import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.ogc_processes_service import OGCProcessesService

@pytest.fixture
def mock_registry():
    """Create a mock process registry."""
    with patch('app.services.ogc_processes_service.ProcessRegistry') as mock:
        yield mock.return_value

@pytest.fixture
def mock_executor():
    """Create a mock process executor."""
    with patch('app.services.ogc_processes_service.ProcessExecutor') as mock:
        yield mock.return_value

@pytest.fixture
def service(mock_registry, mock_executor):
    """Create a service with mocked dependencies."""
    with patch('app.services.ogc_processes_service.ProcessRegistry', return_value=mock_registry), \
         patch('app.services.ogc_processes_service.ProcessExecutor', return_value=mock_executor), \
         patch('app.services.ogc_processes_service.register_all_processes'):
        service = OGCProcessesService()
        return service

def test_get_all_processes(service, mock_registry):
    """Test getting all processes."""
    # Configure the mock registry
    mock_registry.get_all_processes.return_value = [
        {"id": "test_process1", "title": "Test Process 1", "description": "Test process 1"},
        {"id": "test_process2", "title": "Test Process 2", "description": "Test process 2"}
    ]
    
    # Get all processes
    processes = service.get_all_processes()
    
    # Check that the registry was called
    mock_registry.get_all_processes.assert_called_once()
    
    # Check that the processes are returned
    assert len(processes) == 2
    assert processes[0]["id"] == "test_process1"
    assert processes[1]["id"] == "test_process2"

def test_get_process(service, mock_registry):
    """Test getting a specific process."""
    # Configure the mock registry
    mock_registry.get_process.return_value = {
        "id": "test_process",
        "title": "Test Process",
        "description": "Test process",
        "inputs": {},
        "outputs": {}
    }
    
    # Get the process
    process = service.get_process("test_process")
    
    # Check that the registry was called correctly
    mock_registry.get_process.assert_called_once_with("test_process")
    
    # Check that the process is returned
    assert process["id"] == "test_process"
    assert process["title"] == "Test Process"

@pytest.mark.asyncio
async def test_execute_process(service, mock_executor):
    """Test executing a process."""
    # Configure the mock executor
    mock_executor.execute.return_value = {"result": "test"}
    
    # Define test inputs and mock DB
    inputs = {"test_input": "value"}
    mock_db = MagicMock()
    
    # Execute the process
    result = await service.execute_process("test_process", inputs, mock_db)
    
    # Check that the executor was called correctly
    mock_executor.execute.assert_called_once_with("test_process", inputs, mock_db)
    
    # Check that the result is correct
    assert result == {"result": "test"}
