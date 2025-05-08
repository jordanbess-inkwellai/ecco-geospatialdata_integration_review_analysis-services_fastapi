import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.process_registry import ProcessRegistry
from app.services.process_executor import ProcessExecutor

@pytest.fixture
def mock_registry():
    """Create a mock process registry."""
    registry = MagicMock(spec=ProcessRegistry)
    return registry

@pytest.fixture
def executor(mock_registry):
    """Create a process executor with a mock registry."""
    return ProcessExecutor(mock_registry)

@pytest.mark.asyncio
async def test_execute_process(executor, mock_registry):
    """Test executing a process."""
    # Define a mock process function
    mock_process = AsyncMock()
    mock_process.return_value = {"result": "test"}
    
    # Configure the mock registry
    mock_registry.get_process_function.return_value = mock_process
    
    # Define test inputs and mock DB
    inputs = {"test_input": "value"}
    mock_db = MagicMock()
    
    # Execute the process
    result = await executor.execute("test_process", inputs, mock_db)
    
    # Check that the registry was called correctly
    mock_registry.get_process_function.assert_called_once_with("test_process")
    
    # Check that the process function was called correctly
    mock_process.assert_called_once_with(inputs, mock_db)
    
    # Check that the result is correct
    assert result == {"result": "test"}

@pytest.mark.asyncio
async def test_execute_nonexistent_process(executor, mock_registry):
    """Test executing a process that doesn't exist."""
    # Configure the mock registry
    mock_registry.get_process_function.return_value = None
    
    # Define test inputs and mock DB
    inputs = {"test_input": "value"}
    mock_db = MagicMock()
    
    # Execute the process and check that it raises an error
    with pytest.raises(ValueError, match="Process test_process not found"):
        await executor.execute("test_process", inputs, mock_db)
    
    # Check that the registry was called correctly
    mock_registry.get_process_function.assert_called_once_with("test_process")
