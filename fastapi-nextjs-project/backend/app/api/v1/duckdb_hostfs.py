from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Query, Body
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional, Union
import os
import tempfile
import shutil
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.duckdb_config import duckdb_config
from app.services.duckdb_service import duckdb_service

router = APIRouter(tags=["DuckDB HostFS"], prefix="/duckdb/hostfs")

class DirectoryInfo(BaseModel):
    """Information about a directory"""
    path: str = Field(..., description="Path of the directory")
    allowed: bool = Field(..., description="Whether the directory is allowed")
    files: List[Dict[str, Any]] = Field(..., description="List of files in the directory")

class FileInfo(BaseModel):
    """Information about a file"""
    name: str = Field(..., description="Name of the file")
    path: str = Field(..., description="Path of the file")
    size: int = Field(..., description="Size of the file in bytes")
    is_dir: bool = Field(..., description="Whether the file is a directory")
    last_modified: str = Field(..., description="Last modified time of the file")
    extension: Optional[str] = Field(None, description="File extension")

class CreateDirectoryRequest(BaseModel):
    """Request to create a directory"""
    path: str = Field(..., description="Path of the directory to create")

class AllowedDirectoriesResponse(BaseModel):
    """Response for listing allowed directories"""
    directories: List[str] = Field(..., description="List of allowed directories")

@router.get("/allowed-directories", response_model=AllowedDirectoriesResponse)
async def get_allowed_directories():
    """
    Get a list of directories that are allowed to be accessed by HostFS.
    
    Returns:
        A list of allowed directory paths.
    """
    # Get allowed directories from DuckDB service
    allowed_dirs = []
    
    # Add default allowed directories
    allowed_dirs.append(os.path.abspath(duckdb_config.data_dir))
    allowed_dirs.append(os.path.abspath(duckdb_config.temp_dir))
    allowed_dirs.append(os.path.abspath(os.path.join(os.getcwd(), "data")))
    allowed_dirs.append(os.path.abspath(os.path.join(os.getcwd(), "uploads")))
    
    # Add environment variable defined directories
    hostfs_allowed_dirs = os.environ.get("HOSTFS_ALLOWED_DIRS", "")
    if hostfs_allowed_dirs:
        allowed_dirs.extend([os.path.abspath(d.strip()) for d in hostfs_allowed_dirs.split(",")])
    
    # Filter out directories that don't exist
    allowed_dirs = [d for d in allowed_dirs if os.path.exists(d)]
    
    return {"directories": allowed_dirs}

@router.get("/list", response_model=DirectoryInfo)
async def list_directory(path: str = Query(..., description="Path to list")):
    """
    List the contents of a directory.
    
    Args:
        path: Path to list
        
    Returns:
        Directory information and contents
    """
    # Check if the directory is allowed
    allowed_dirs = (await get_allowed_directories())["directories"]
    is_allowed = False
    
    for allowed_dir in allowed_dirs:
        if path == allowed_dir or path.startswith(allowed_dir + os.sep):
            is_allowed = True
            break
    
    if not is_allowed:
        return {
            "path": path,
            "allowed": False,
            "files": []
        }
    
    # Check if the directory exists
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Directory not found: {path}")
    
    # Check if the path is a directory
    if not os.path.isdir(path):
        raise HTTPException(status_code=400, detail=f"Path is not a directory: {path}")
    
    # List the directory contents
    files = []
    
    try:
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            is_dir = os.path.isdir(item_path)
            
            # Get file extension if not a directory
            extension = None
            if not is_dir and '.' in item:
                extension = item.split('.')[-1].lower()
            
            files.append({
                "name": item,
                "path": item_path,
                "size": 0 if is_dir else os.path.getsize(item_path),
                "is_dir": is_dir,
                "last_modified": os.path.getmtime(item_path),
                "extension": extension
            })
        
        # Sort directories first, then files
        files.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
        
        return {
            "path": path,
            "allowed": True,
            "files": files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing directory: {str(e)}")

@router.get("/download")
async def download_file(path: str = Query(..., description="Path to download")):
    """
    Download a file.
    
    Args:
        path: Path to download
        
    Returns:
        The file as a streaming response
    """
    # Check if the file is allowed
    allowed_dirs = (await get_allowed_directories())["directories"]
    is_allowed = False
    
    for allowed_dir in allowed_dirs:
        if path.startswith(allowed_dir + os.sep):
            is_allowed = True
            break
    
    if not is_allowed:
        raise HTTPException(status_code=403, detail="Access to this file is not allowed")
    
    # Check if the file exists
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"File not found: {path}")
    
    # Check if the path is a file
    if not os.path.isfile(path):
        raise HTTPException(status_code=400, detail=f"Path is not a file: {path}")
    
    # Return the file
    return FileResponse(
        path=path,
        filename=os.path.basename(path),
        media_type="application/octet-stream"
    )

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    directory: str = Form(..., description="Directory to upload to")
):
    """
    Upload a file to a directory.
    
    Args:
        file: File to upload
        directory: Directory to upload to
        
    Returns:
        Success message
    """
    # Check if the directory is allowed
    allowed_dirs = (await get_allowed_directories())["directories"]
    is_allowed = False
    
    for allowed_dir in allowed_dirs:
        if directory == allowed_dir or directory.startswith(allowed_dir + os.sep):
            is_allowed = True
            break
    
    if not is_allowed:
        raise HTTPException(status_code=403, detail="Access to this directory is not allowed")
    
    # Check if the directory exists
    if not os.path.exists(directory):
        raise HTTPException(status_code=404, detail=f"Directory not found: {directory}")
    
    # Check if the path is a directory
    if not os.path.isdir(directory):
        raise HTTPException(status_code=400, detail=f"Path is not a directory: {directory}")
    
    # Save the file
    file_path = os.path.join(directory, file.filename)
    
    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        return {"success": True, "message": f"File uploaded successfully: {file.filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@router.post("/directory", response_model=Dict[str, Any])
async def create_directory(request: CreateDirectoryRequest):
    """
    Create a new directory.
    
    Args:
        request: Create directory request
        
    Returns:
        Success message
    """
    path = request.path
    
    # Check if the parent directory is allowed
    parent_dir = os.path.dirname(path)
    allowed_dirs = (await get_allowed_directories())["directories"]
    is_allowed = False
    
    for allowed_dir in allowed_dirs:
        if parent_dir == allowed_dir or parent_dir.startswith(allowed_dir + os.sep):
            is_allowed = True
            break
    
    if not is_allowed:
        raise HTTPException(status_code=403, detail="Access to this directory is not allowed")
    
    # Create the directory
    try:
        os.makedirs(path, exist_ok=True)
        return {"success": True, "message": f"Directory created successfully: {path}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating directory: {str(e)}")

@router.delete("/directory", response_model=Dict[str, Any])
async def delete_directory(
    path: str = Query(..., description="Path to delete"),
    recursive: bool = Query(False, description="Whether to delete recursively")
):
    """
    Delete a directory.
    
    Args:
        path: Path to delete
        recursive: Whether to delete recursively
        
    Returns:
        Success message
    """
    # Check if the directory is allowed
    allowed_dirs = (await get_allowed_directories())["directories"]
    is_allowed = False
    
    for allowed_dir in allowed_dirs:
        # Make sure we're not deleting an allowed directory itself
        if path == allowed_dir:
            raise HTTPException(status_code=403, detail="Cannot delete an allowed directory root")
        
        if path.startswith(allowed_dir + os.sep):
            is_allowed = True
            break
    
    if not is_allowed:
        raise HTTPException(status_code=403, detail="Access to this directory is not allowed")
    
    # Check if the directory exists
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Directory not found: {path}")
    
    # Check if the path is a directory
    if not os.path.isdir(path):
        raise HTTPException(status_code=400, detail=f"Path is not a directory: {path}")
    
    # Delete the directory
    try:
        if recursive:
            shutil.rmtree(path)
        else:
            os.rmdir(path)
        
        return {"success": True, "message": f"Directory deleted successfully: {path}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting directory: {str(e)}")

@router.delete("/file", response_model=Dict[str, Any])
async def delete_file(path: str = Query(..., description="Path to delete")):
    """
    Delete a file.
    
    Args:
        path: Path to delete
        
    Returns:
        Success message
    """
    # Check if the file is allowed
    allowed_dirs = (await get_allowed_directories())["directories"]
    is_allowed = False
    
    for allowed_dir in allowed_dirs:
        if path.startswith(allowed_dir + os.sep):
            is_allowed = True
            break
    
    if not is_allowed:
        raise HTTPException(status_code=403, detail="Access to this file is not allowed")
    
    # Check if the file exists
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"File not found: {path}")
    
    # Check if the path is a file
    if not os.path.isfile(path):
        raise HTTPException(status_code=400, detail=f"Path is not a file: {path}")
    
    # Delete the file
    try:
        os.remove(path)
        return {"success": True, "message": f"File deleted successfully: {path}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")
