from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, Path, Body
from typing import Dict, List, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.docetl_service import docetl_service

router = APIRouter()

@router.get("/status", response_model=Dict[str, Any])
async def get_docetl_status():
    """
    Get the status of the DocETL service.
    
    Returns:
        Status information
    """
    status = docetl_service.get_status()
    return status

@router.get("/pipelines", response_model=List[Dict[str, Any]])
async def get_pipelines():
    """
    Get a list of available pipelines.
    
    Returns:
        List of pipelines
    """
    pipelines = docetl_service.get_pipelines()
    return pipelines

@router.get("/pipelines/{pipeline_id}", response_model=Dict[str, Any])
async def get_pipeline(pipeline_id: str):
    """
    Get details for a specific pipeline.
    
    Args:
        pipeline_id: Pipeline ID
        
    Returns:
        Pipeline details
    """
    pipeline = docetl_service.get_pipeline(pipeline_id)
    
    if not pipeline:
        raise HTTPException(status_code=404, detail=f"Pipeline {pipeline_id} not found")
    
    return pipeline

@router.post("/pipelines/{pipeline_id}/run", response_model=Dict[str, Any])
async def run_pipeline(pipeline_id: str, parameters: Dict[str, Any] = Body({})):
    """
    Run a pipeline.
    
    Args:
        pipeline_id: Pipeline ID
        parameters: Pipeline parameters
        
    Returns:
        Pipeline run result
    """
    result = docetl_service.run_pipeline(pipeline_id, parameters)
    
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message", "Unknown error"))
    
    return result

@router.get("/pipelines/{pipeline_id}/runs", response_model=List[Dict[str, Any]])
async def get_pipeline_runs(pipeline_id: str):
    """
    Get a list of runs for a specific pipeline.
    
    Args:
        pipeline_id: Pipeline ID
        
    Returns:
        List of pipeline runs
    """
    runs = docetl_service.get_pipeline_runs(pipeline_id)
    return runs

@router.get("/pipelines/{pipeline_id}/runs/{run_id}", response_model=Dict[str, Any])
async def get_pipeline_run(pipeline_id: str, run_id: str):
    """
    Get details for a specific pipeline run.
    
    Args:
        pipeline_id: Pipeline ID
        run_id: Run ID
        
    Returns:
        Pipeline run details
    """
    run = docetl_service.get_pipeline_run(pipeline_id, run_id)
    
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found for pipeline {pipeline_id}")
    
    return run

@router.get("/pipelines/{pipeline_id}/runs/{run_id}/logs", response_model=List[Dict[str, Any]])
async def get_pipeline_run_logs(pipeline_id: str, run_id: str):
    """
    Get logs for a specific pipeline run.
    
    Args:
        pipeline_id: Pipeline ID
        run_id: Run ID
        
    Returns:
        Pipeline run logs
    """
    logs = docetl_service.get_pipeline_run_logs(pipeline_id, run_id)
    return logs

@router.post("/pipelines", response_model=Dict[str, Any])
async def create_pipeline(pipeline_config: Dict[str, Any] = Body(...)):
    """
    Create a new pipeline.
    
    Args:
        pipeline_config: Pipeline configuration
        
    Returns:
        Created pipeline
    """
    result = docetl_service.create_pipeline(pipeline_config)
    
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message", "Unknown error"))
    
    return result

@router.put("/pipelines/{pipeline_id}", response_model=Dict[str, Any])
async def update_pipeline(pipeline_id: str, pipeline_config: Dict[str, Any] = Body(...)):
    """
    Update an existing pipeline.
    
    Args:
        pipeline_id: Pipeline ID
        pipeline_config: Pipeline configuration
        
    Returns:
        Updated pipeline
    """
    result = docetl_service.update_pipeline(pipeline_id, pipeline_config)
    
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message", "Unknown error"))
    
    return result

@router.delete("/pipelines/{pipeline_id}", response_model=Dict[str, Any])
async def delete_pipeline(pipeline_id: str):
    """
    Delete a pipeline.
    
    Args:
        pipeline_id: Pipeline ID
        
    Returns:
        Deletion result
    """
    result = docetl_service.delete_pipeline(pipeline_id)
    
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message", "Unknown error"))
    
    return result

@router.get("/extractors", response_model=List[Dict[str, Any]])
async def get_extractors():
    """
    Get a list of available extractors.
    
    Returns:
        List of extractors
    """
    extractors = docetl_service.get_extractors()
    return extractors

@router.get("/transformers", response_model=List[Dict[str, Any]])
async def get_transformers():
    """
    Get a list of available transformers.
    
    Returns:
        List of transformers
    """
    transformers = docetl_service.get_transformers()
    return transformers

@router.get("/loaders", response_model=List[Dict[str, Any]])
async def get_loaders():
    """
    Get a list of available loaders.
    
    Returns:
        List of loaders
    """
    loaders = docetl_service.get_loaders()
    return loaders
