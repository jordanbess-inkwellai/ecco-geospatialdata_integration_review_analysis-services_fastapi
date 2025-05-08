from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Query, Body
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional, Iterator
import os
import tempfile
import json
import shutil
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.services.rclone_service import rclone_service

# API models for documentation
class RemoteInfo(BaseModel):
    """Information about a remote"""
    name: str = Field(..., description="Name of the remote")
    type: str = Field(..., description="Type of remote (s3, box, drive, etc.)")

class FileInfo(BaseModel):
    """Information about a file"""
    Path: str = Field(..., description="Path of the file relative to the remote path")
    Name: str = Field(..., description="Name of the file")
    Size: int = Field(..., description="Size of the file in bytes")
    MimeType: str = Field(..., description="MIME type of the file")
    ModTime: str = Field(..., description="Modification time of the file")
    IsDir: bool = Field(..., description="Whether the file is a directory")

class RemoteListResponse(BaseModel):
    """Response for listing remotes"""
    success: bool = Field(..., description="Whether the operation was successful")
    remotes: List[str] = Field(..., description="List of remote names")
    error: Optional[str] = Field(None, description="Error message if operation failed")

class FileListResponse(BaseModel):
    """Response for listing files"""
    success: bool = Field(..., description="Whether the operation was successful")
    path: str = Field(..., description="Remote path that was listed")
    files: List[FileInfo] = Field(..., description="List of files")
    error: Optional[str] = Field(None, description="Error message if operation failed")

class FileDownloadParams(BaseModel):
    """Parameters for downloading a file"""
    path: str = Field(..., description="Remote path to download")

router = APIRouter(tags=["Rclone"], prefix="/rclone")

@router.get("/remotes", response_model=RemoteListResponse,
         summary="List remotes",
         description="List all configured remotes")
async def list_remotes():
    """
    List all configured remotes.

    Returns:
        A dictionary with a list of remote names.

    Example:
        ```json
        {
            "success": true,
            "remotes": ["s3", "box", "drive"]
        }
        ```
    """
    result = await rclone_service.list_remotes()

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to list remotes"))

    return result

@router.post("/remotes")
async def add_remote(
    name: str = Form(...),
    remote_type: str = Form(...),
    params: str = Form(...)
):
    """Add a new remote configuration"""
    try:
        # Parse parameters
        params_dict = json.loads(params)

        result = await rclone_service.add_remote(name, remote_type, params_dict)

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to add remote"))

        return result
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in params")

@router.delete("/remotes/{name}")
async def remove_remote(name: str):
    """Remove a remote configuration"""
    result = await rclone_service.remove_remote(name)

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to remove remote"))

    return result

@router.get("/files")
async def list_files(
    path: str = Query(..., description="Remote path in the format 'remote:path'"),
    recursive: bool = Query(False, description="Whether to list files recursively")
):
    """List files in a remote path"""
    result = await rclone_service.list_files(path, recursive)

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to list files"))

    return result

@router.post("/download")
async def download_file(
    path: str = Form(..., description="Remote path in the format 'remote:path/to/file'")
):
    """Download a file from a remote path"""
    result = await rclone_service.download_file(path)

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to download file"))

    # Return the file
    return FileResponse(
        path=result["local_path"],
        filename=os.path.basename(result["local_path"]),
        media_type="application/octet-stream"
    )

@router.post("/upload")
async def upload_file(
    remote_path: str = Form(..., description="Remote path in the format 'remote:path/to/file'"),
    file: UploadFile = File(...)
):
    """Upload a file to a remote path"""
    # Save the uploaded file
    temp_dir = tempfile.mkdtemp()
    local_path = os.path.join(temp_dir, file.filename)

    try:
        with open(local_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Upload the file
        result = await rclone_service.upload_file(local_path, remote_path)

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to upload file"))

        return result
    finally:
        # Clean up
        shutil.rmtree(temp_dir)

@router.post("/sync")
async def sync_directories(
    source_path: str = Form(..., description="Source path (local or remote)"),
    dest_path: str = Form(..., description="Destination path (local or remote)"),
    delete: bool = Form(False, description="Whether to delete files in destination that don't exist in source")
):
    """Sync directories"""
    result = await rclone_service.sync_directory(source_path, dest_path, delete)

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to sync directories"))

    return result

@router.get("/info/{remote}")
async def get_remote_info(remote: str):
    """Get information about a remote"""
    # Ensure remote ends with a colon
    if not remote.endswith(":"):
        remote += ":"

    result = await rclone_service.get_remote_info(remote)

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to get remote info"))

    return result

@router.post("/link")
async def create_public_link(
    path: str = Form(..., description="Remote path in the format 'remote:path/to/file'"),
    expire: Optional[str] = Form(None, description="Expiration time (e.g., '1d', '2h30m')")
):
    """Create a public link for a file"""
    result = await rclone_service.create_public_link(path, expire)

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to create public link"))

    return result

@router.post("/box/auth",
         summary="Box authentication",
         description="Authenticate with Box.com")
async def authenticate_with_box(
    client_id: str = Form(..., description="Box API client ID"),
    client_secret: str = Form(..., description="Box API client secret")
):
    """
    Authenticate with Box.com.

    Args:
        client_id: Box client ID
        client_secret: Box client secret

    Returns:
        A dictionary with information about the authentication.

    Example:
        ```json
        {
            "success": true,
            "message": "Box authentication successful",
            "remote": "box:"
        }
        ```
    """
    result = await rclone_service.box_auth(client_id, client_secret)

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to authenticate with Box"))

    return result


@router.post("/scan",
         summary="Scan files",
         description="Scan files for metadata")
async def scan_files(
    path: str = Form(..., description="Remote path to scan"),
    recursive: bool = Form(False, description="Whether to scan recursively")
):
    """
    Scan files for metadata.

    Args:
        path: Remote path to scan (e.g., "box:path")
        recursive: Whether to scan recursively

    Returns:
        A dictionary with information about the scanned files and their metadata.

    Example:
        ```json
        {
            "success": true,
            "remote_path": "box:path",
            "file_count": 2,
            "files": [
                {
                    "name": "file1.txt",
                    "path": "file1.txt",
                    "size": 1024,
                    "modified_time": "2023-01-01T12:00:00Z",
                    "metadata": {
                        "id": "123456",
                        "description": "Test file"
                    }
                }
            ]
        }
        ```
    """
    return await rclone_service.scan_files_for_metadata(path, recursive)


@router.post("/download-with-progress",
         summary="Download file with progress tracking",
         description="Download a file from remote storage with progress tracking")
async def download_file_with_progress(
    request: FileDownloadParams
):
    """
    Download a file from remote storage with progress tracking.

    This endpoint is designed to be used with frontend progress tracking.
    It returns the file as a streaming response that can be monitored for progress.

    Args:
        path: Remote path to download (e.g., "s3:bucket/path/file.txt")

    Returns:
        The file as a streaming response.
    """
    result = await rclone_service.download_file(request.path)

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))

    # Create a streaming response that can be monitored for progress
    def file_iterator(file_path: str, chunk_size: int = 8192) -> Iterator[bytes]:
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    # Get file info for content type detection
    filename = os.path.basename(result["local_path"])
    file_size = os.path.getsize(result["local_path"])

    # Determine content type
    content_type = "application/octet-stream"
    if '.' in filename:
        ext = filename.split('.')[-1].lower()
        if ext in ['jpg', 'jpeg']:
            content_type = "image/jpeg"
        elif ext == 'png':
            content_type = "image/png"
        elif ext == 'pdf':
            content_type = "application/pdf"
        elif ext in ['txt', 'csv']:
            content_type = "text/plain"
        elif ext in ['xlsx', 'xls']:
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif ext == 'zip':
            content_type = "application/zip"

    # Create streaming response
    return StreamingResponse(
        file_iterator(result["local_path"]),
        media_type=content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(file_size)
        }
    )
