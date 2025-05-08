from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import os
import json
from app.core.database import get_db
from app.core.config import settings
from app.services.ai_service import AIService

router = APIRouter()
ai_service = AIService()

@router.get("/status", response_model=Dict[str, Any])
async def get_ai_status():
    """
    Get the status of the AI service.
    
    Returns:
        Status information
    """
    return {
        "enabled": settings.ENABLE_AI_FEATURES,
        "initialized": ai_service.is_initialized if settings.ENABLE_AI_FEATURES else False,
        "model_type": ai_service.model_type if settings.ENABLE_AI_FEATURES else None,
        "available_models": list(settings.AI_MODEL_PATHS.keys())
    }

@router.post("/validate-data", response_model=Dict[str, Any])
async def validate_data(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    schema: Optional[str] = Form(None)
):
    """
    Validate data against a schema or infer data quality issues.
    
    Args:
        background_tasks: FastAPI background tasks
        file: Data file to validate
        schema: Optional schema to validate against (as JSON string)
        
    Returns:
        Validation results
    """
    if not settings.ENABLE_AI_FEATURES:
        return JSONResponse(
            status_code=400,
            content={"error": "AI features are not enabled"}
        )
    
    try:
        # Save the uploaded file
        upload_dir = settings.UPLOAD_DIR
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Parse schema if provided
        schema_dict = None
        if schema:
            try:
                schema_dict = json.loads(schema)
            except json.JSONDecodeError:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Invalid schema JSON"}
                )
        
        # Validate the data
        validation_results = ai_service.validate_data(file_path, schema_dict)
        
        # Schedule cleanup of the file
        background_tasks.add_task(cleanup_file, file_path)
        
        return validation_results
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error validating data: {str(e)}"}
        )

@router.post("/match-schema", response_model=Dict[str, Any])
async def match_schema(
    source_schema: Dict[str, Any],
    target_schema: Dict[str, Any]
):
    """
    Match source schema to target schema.
    
    Args:
        source_schema: Source schema
        target_schema: Target schema
        
    Returns:
        Schema mapping
    """
    if not settings.ENABLE_AI_FEATURES:
        return JSONResponse(
            status_code=400,
            content={"error": "AI features are not enabled"}
        )
    
    try:
        # Match the schemas
        mapping_results = ai_service.match_schema(source_schema, target_schema)
        
        return mapping_results
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error matching schemas: {str(e)}"}
        )

@router.post("/suggest-transformations", response_model=Dict[str, Any])
async def suggest_transformations(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    target_schema: Optional[str] = Form(None)
):
    """
    Suggest data transformations to match a target schema or improve data quality.
    
    Args:
        background_tasks: FastAPI background tasks
        file: Data file to transform
        target_schema: Optional target schema (as JSON string)
        
    Returns:
        Suggested transformations
    """
    if not settings.ENABLE_AI_FEATURES:
        return JSONResponse(
            status_code=400,
            content={"error": "AI features are not enabled"}
        )
    
    try:
        # Save the uploaded file
        upload_dir = settings.UPLOAD_DIR
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Parse target schema if provided
        schema_dict = None
        if target_schema:
            try:
                schema_dict = json.loads(target_schema)
            except json.JSONDecodeError:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Invalid schema JSON"}
                )
        
        # Suggest transformations
        transformation_results = ai_service.suggest_data_transformations(file_path, schema_dict)
        
        # Schedule cleanup of the file
        background_tasks.add_task(cleanup_file, file_path)
        
        return transformation_results
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error suggesting transformations: {str(e)}"}
        )

async def cleanup_file(file_path: str, delay: int = 3600):
    """
    Clean up a file after a delay.
    
    Args:
        file_path: Path to the file to clean up
        delay: Delay in seconds before cleaning up (default: 1 hour)
    """
    import asyncio
    
    # Wait for the specified delay
    await asyncio.sleep(delay)
    
    # Clean up the file
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Error cleaning up file {file_path}: {str(e)}")
