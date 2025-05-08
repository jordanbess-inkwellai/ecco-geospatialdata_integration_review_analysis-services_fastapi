from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, Body
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
import os
import logging
from pydantic import BaseModel

from app.core.database import get_db
from app.services.box_service import BoxService

router = APIRouter()
logger = logging.getLogger(__name__)


class BoxAuthRequest(BaseModel):
    client_id: str
    client_secret: str
    auth_code: Optional[str] = None
    refresh_token: Optional[str] = None


class BoxMetadataUpdateRequest(BaseModel):
    scope: str
    template_key: str
    metadata: Dict[str, Any]


@router.post("/authenticate")
async def authenticate(
    request: BoxAuthRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate with Box.com API
    """
    try:
        result = await BoxService.authenticate(
            client_id=request.client_id,
            client_secret=request.client_secret,
            auth_code=request.auth_code,
            refresh_token=request.refresh_token
        )
        return result
    except Exception as e:
        logger.error(f"Error authenticating with Box: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error authenticating with Box: {str(e)}")


@router.get("/folders/{folder_id}")
async def list_folder(
    folder_id: str = "0",
    access_token: str = Query(..., description="Box access token")
):
    """
    List files and folders in a Box.com folder
    """
    try:
        result = await BoxService.list_folder(folder_id=folder_id, access_token=access_token)
        return result
    except Exception as e:
        logger.error(f"Error listing folder: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing folder: {str(e)}")


@router.get("/files/{file_id}")
async def get_file_info(
    file_id: str,
    access_token: str = Query(..., description="Box access token")
):
    """
    Get information about a Box.com file
    """
    try:
        result = await BoxService.get_file_info(file_id=file_id, access_token=access_token)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting file info: {str(e)}")


@router.get("/files/{file_id}/metadata")
async def get_box_metadata(
    file_id: str,
    access_token: str = Query(..., description="Box access token")
):
    """
    Get Box.com metadata for a file
    """
    try:
        result = await BoxService.get_box_metadata(file_id=file_id, access_token=access_token)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Box metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting Box metadata: {str(e)}")


@router.post("/files/{file_id}/metadata")
async def update_box_metadata(
    file_id: str,
    request: BoxMetadataUpdateRequest,
    access_token: str = Query(..., description="Box access token")
):
    """
    Update Box.com metadata for a file
    """
    try:
        result = await BoxService.update_box_metadata(
            file_id=file_id,
            scope=request.scope,
            template_key=request.template_key,
            metadata=request.metadata,
            access_token=access_token
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating Box metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating Box metadata: {str(e)}")


@router.post("/files/{file_id}/download")
async def download_file(
    file_id: str,
    destination_path: Optional[str] = Body(None, description="Path to save the file"),
    access_token: str = Query(..., description="Box access token")
):
    """
    Download a file from Box.com
    """
    try:
        result = await BoxService.download_file(
            file_id=file_id,
            destination_path=destination_path,
            access_token=access_token
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")


@router.get("/files/{file_id}/scan")
async def scan_file_metadata(
    file_id: str,
    access_token: str = Query(..., description="Box access token")
):
    """
    Scan a file for metadata
    """
    try:
        result = await BoxService.scan_file_metadata(file_id=file_id, access_token=access_token)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scanning file metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error scanning file metadata: {str(e)}")


@router.post("/files/{file_id}/analyze")
async def analyze_file(
    file_id: str,
    access_token: str = Query(..., description="Box access token")
):
    """
    Analyze a file from Box.com
    """
    try:
        result = await BoxService.analyze_file(file_id=file_id, access_token=access_token)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing file: {str(e)}")


@router.post("/files/{file_id}/import-to-duckdb")
async def import_to_duckdb(
    file_id: str,
    db_name: str = Body(..., description="Name for the DuckDB database"),
    access_token: str = Query(..., description="Box access token")
):
    """
    Import a file from Box.com to DuckDB
    """
    try:
        result = await BoxService.import_to_duckdb(
            file_id=file_id,
            db_name=db_name,
            access_token=access_token
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing to DuckDB: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error importing to DuckDB: {str(e)}")
