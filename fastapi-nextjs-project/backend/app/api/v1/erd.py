from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
import os
import tempfile
import logging

from app.core.database import get_db
from app.services.erd_service import ERDService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/generate/{data_source_id}")
async def generate_erd(
    data_source_id: int,
    output_format: str = Query("png", description="Output format (png, pdf, dot)"),
    include_tables: Optional[List[str]] = Query(None, description="Tables to include"),
    exclude_tables: Optional[List[str]] = Query(None, description="Tables to exclude"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate ERD from a data source
    """
    try:
        result = await ERDService.generate_erd_from_datasource(
            data_source_id=data_source_id,
            output_format=output_format,
            include_tables=include_tables,
            exclude_tables=exclude_tables
        )
        
        return FileResponse(
            path=result["file_path"],
            filename=f"erd_{data_source_id}.{output_format}",
            media_type=f"image/{output_format}" if output_format in ["png", "jpg", "jpeg"] else "application/octet-stream"
        )
    except Exception as e:
        logger.error(f"Error generating ERD: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating ERD: {str(e)}")


@router.get("/models")
async def generate_erd_from_models(
    output_format: str = Query("png", description="Output format (png, pdf, dot)"),
    include_models: Optional[List[str]] = Query(None, description="Models to include"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate ERD from SQLAlchemy models
    """
    try:
        result = await ERDService.generate_erd_from_models(
            output_format=output_format,
            include_models=include_models
        )
        
        return FileResponse(
            path=result["file_path"],
            filename=f"erd_models.{output_format}",
            media_type=f"image/{output_format}" if output_format in ["png", "jpg", "jpeg"] else "application/octet-stream"
        )
    except Exception as e:
        logger.error(f"Error generating ERD from models: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating ERD from models: {str(e)}")


@router.get("/schema/{data_source_id}")
async def get_schema_as_json(
    data_source_id: int,
    include_tables: Optional[List[str]] = Query(None, description="Tables to include"),
    exclude_tables: Optional[List[str]] = Query(None, description="Tables to exclude"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get database schema as JSON for frontend visualization
    """
    try:
        result = await ERDService.get_schema_as_json(
            data_source_id=data_source_id,
            include_tables=include_tables,
            exclude_tables=exclude_tables
        )
        
        return result
    except Exception as e:
        logger.error(f"Error getting schema as JSON: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting schema as JSON: {str(e)}")
