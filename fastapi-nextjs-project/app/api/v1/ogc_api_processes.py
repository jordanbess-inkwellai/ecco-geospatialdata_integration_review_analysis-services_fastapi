from fastapi import APIRouter, Depends, Body, Request
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import time
import asyncio
from app.core.database import get_db
from app.services.ogc_processes_service import OGCProcessesService
from app.core.exceptions import (
    ProcessNotFoundException,
    ProcessExecutionException,
    ValidationException,
    DatabaseException,
    TimeoutException
)
from app.core.validators import validate_process_inputs

router = APIRouter()
processes_service = OGCProcessesService()

@router.get("/", response_model=Dict[str, Any])
async def list_processes():
    """
    List all available processes

    Returns:
        Dictionary with list of processes
    """
    processes = processes_service.get_all_processes()
    return {
        "processes": processes
    }

@router.get("/{process_id}", response_model=Dict[str, Any])
async def get_process(process_id: str):
    """
    Get details about a specific process

    Args:
        process_id: Process ID

    Returns:
        Process details

    Raises:
        ProcessNotFoundException: If the process is not found
    """
    process = processes_service.get_process(process_id)
    if not process:
        raise ProcessNotFoundException(process_id)
    return process

@router.post("/{process_id}/execution", response_model=Dict[str, Any])
async def execute_process(
    request: Request,
    process_id: str,
    inputs: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Execute a process with the provided inputs

    Args:
        request: FastAPI request object
        process_id: Process ID
        inputs: Process inputs
        db: Database session

    Returns:
        Process result

    Raises:
        ProcessNotFoundException: If the process is not found
        ValidationException: If the inputs are invalid
        ProcessExecutionException: If the process execution fails
        TimeoutException: If the process times out
        DatabaseException: If a database error occurs
    """
    # Get the process definition
    process = processes_service.get_process(process_id)
    if not process:
        raise ProcessNotFoundException(process_id)

    # Validate inputs
    try:
        validated_inputs = validate_process_inputs(process, inputs)
    except ValidationException as e:
        raise e

    # Set a timeout for the process execution
    timeout = 300  # 5 minutes default timeout

    # Check for timeout in query parameters
    timeout_param = request.query_params.get("timeout")
    if timeout_param:
        try:
            timeout = int(timeout_param)
            # Limit timeout to a reasonable range
            timeout = max(1, min(timeout, 3600))  # Between 1 second and 1 hour
        except ValueError:
            pass

    # Execute the process with timeout
    try:
        start_time = time.time()

        # Create a task for the process execution
        task = asyncio.create_task(
            processes_service.execute_process(process_id, validated_inputs, db)
        )

        # Wait for the task to complete with timeout
        result = await asyncio.wait_for(task, timeout=timeout)

        execution_time = time.time() - start_time

        return {
            "result": result,
            "execution_time": execution_time
        }
    except asyncio.TimeoutError:
        raise TimeoutException(process_id)
    except ValidationException as e:
        raise e
    except DatabaseException as e:
        raise e
    except Exception as e:
        raise ProcessExecutionException(process_id, str(e))

@router.exception_handler(ProcessNotFoundException)
async def process_not_found_exception_handler(request: Request, exc: ProcessNotFoundException):
    """Handle ProcessNotFoundException."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@router.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    """Handle ValidationException."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@router.exception_handler(ProcessExecutionException)
async def process_execution_exception_handler(request: Request, exc: ProcessExecutionException):
    """Handle ProcessExecutionException."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@router.exception_handler(TimeoutException)
async def timeout_exception_handler(request: Request, exc: TimeoutException):
    """Handle TimeoutException."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@router.exception_handler(DatabaseException)
async def database_exception_handler(request: Request, exc: DatabaseException):
    """Handle DatabaseException."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
