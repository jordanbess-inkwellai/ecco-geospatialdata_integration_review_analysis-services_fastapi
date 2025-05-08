import pytest
from app.services.process_registry import ProcessRegistry

def test_register_process():
    """Test registering a process."""
    registry = ProcessRegistry()
    
    # Define a test process
    async def test_process(inputs, db):
        return {"result": "test"}
    
    # Register the process
    registry.register_process(
        process_id="test_process",
        process_func=test_process,
        description="Test process",
        inputs={
            "test_input": {
                "title": "Test Input",
                "description": "A test input",
                "schema": {"type": "string"},
                "required": True
            }
        },
        outputs={
            "result": {
                "title": "Result",
                "description": "The result",
                "schema": {"type": "string"}
            }
        }
    )
    
    # Check that the process was registered
    assert "test_process" in registry.processes
    
    # Check that the process has the correct properties
    process = registry.processes["test_process"]
    assert process["id"] == "test_process"
    assert process["title"] == "Test Process"
    assert process["description"] == "Test process"
    assert "test_input" in process["inputs"]
    assert "result" in process["outputs"]
    assert process["func"] == test_process

def test_get_process():
    """Test getting a process."""
    registry = ProcessRegistry()
    
    # Define a test process
    async def test_process(inputs, db):
        return {"result": "test"}
    
    # Register the process
    registry.register_process(
        process_id="test_process",
        process_func=test_process,
        description="Test process",
        inputs={},
        outputs={}
    )
    
    # Get the process
    process = registry.get_process("test_process")
    
    # Check that the process has the correct properties
    assert process["id"] == "test_process"
    assert process["title"] == "Test Process"
    assert process["description"] == "Test process"
    assert "func" not in process  # Function should not be included

def test_get_nonexistent_process():
    """Test getting a process that doesn't exist."""
    registry = ProcessRegistry()
    
    # Get a nonexistent process
    process = registry.get_process("nonexistent")
    
    # Check that the process is None
    assert process is None

def test_get_all_processes():
    """Test getting all processes."""
    registry = ProcessRegistry()
    
    # Define test processes
    async def test_process1(inputs, db):
        return {"result": "test1"}
    
    async def test_process2(inputs, db):
        return {"result": "test2"}
    
    # Register the processes
    registry.register_process(
        process_id="test_process1",
        process_func=test_process1,
        description="Test process 1",
        inputs={},
        outputs={}
    )
    
    registry.register_process(
        process_id="test_process2",
        process_func=test_process2,
        description="Test process 2",
        inputs={},
        outputs={}
    )
    
    # Get all processes
    processes = registry.get_all_processes()
    
    # Check that the processes are returned
    assert len(processes) == 2
    
    # Check that the processes have the correct properties
    process_ids = [p["id"] for p in processes]
    assert "test_process1" in process_ids
    assert "test_process2" in process_ids
    
    # Check that the processes don't include the function
    for process in processes:
        assert "func" not in process

def test_get_process_function():
    """Test getting a process function."""
    registry = ProcessRegistry()
    
    # Define a test process
    async def test_process(inputs, db):
        return {"result": "test"}
    
    # Register the process
    registry.register_process(
        process_id="test_process",
        process_func=test_process,
        description="Test process",
        inputs={},
        outputs={}
    )
    
    # Get the process function
    func = registry.get_process_function("test_process")
    
    # Check that the function is returned
    assert func == test_process

def test_get_nonexistent_process_function():
    """Test getting a function for a process that doesn't exist."""
    registry = ProcessRegistry()
    
    # Get a nonexistent process function
    func = registry.get_process_function("nonexistent")
    
    # Check that the function is None
    assert func is None
