from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import Dict, List, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import os
import json
import shutil
from app.core.database import get_db
from app.services.data_processing_service import DataProcessingService

router = APIRouter()
data_processing_service = DataProcessingService()

@router.get("/operations", response_model=Dict[str, List[Dict[str, Any]]])
async def get_operations():
    """
    Get a list of available data processing operations.
    
    Returns:
        Dictionary of operation categories and their operations
    """
    return data_processing_service.get_available_operations()

@router.post("/upload", response_model=Dict[str, Any])
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file for processing.
    
    Args:
        file: Uploaded file
        
    Returns:
        File information
    """
    try:
        # Save the uploaded file
        file_path = await data_processing_service.save_upload_file(file)
        
        # Get information about the file
        file_info = data_processing_service.get_file_info(file_path)
        
        # Add the file path to the response
        file_info["file_path"] = file_path
        file_info["file_name"] = file.filename
        
        return file_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@router.post("/convert-vector", response_model=Dict[str, Any])
async def convert_vector(
    background_tasks: BackgroundTasks,
    input_path: str = Form(...),
    output_format: str = Form(...)
):
    """
    Convert a vector file to another format.
    
    Args:
        background_tasks: FastAPI background tasks
        input_path: Path to the input file
        output_format: Output format (shp, geojson, gpkg, kml)
        
    Returns:
        Information about the converted file
    """
    try:
        # Convert the vector file
        output_path = data_processing_service.convert_vector(input_path, output_format)
        
        # Get information about the output file
        output_info = data_processing_service.get_file_info(output_path)
        
        # Add the output path to the response
        output_info["file_path"] = output_path
        output_info["file_name"] = os.path.basename(output_path)
        
        # Schedule cleanup of the input and output files
        background_tasks.add_task(cleanup_files, [input_path, output_path])
        
        return output_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting vector file: {str(e)}")

@router.post("/reproject-vector", response_model=Dict[str, Any])
async def reproject_vector(
    background_tasks: BackgroundTasks,
    input_path: str = Form(...),
    target_crs: str = Form(...)
):
    """
    Reproject a vector file to another coordinate reference system.
    
    Args:
        background_tasks: FastAPI background tasks
        input_path: Path to the input file
        target_crs: Target CRS (e.g., 'EPSG:4326')
        
    Returns:
        Information about the reprojected file
    """
    try:
        # Reproject the vector file
        output_path = data_processing_service.reproject_vector(input_path, target_crs)
        
        # Get information about the output file
        output_info = data_processing_service.get_file_info(output_path)
        
        # Add the output path to the response
        output_info["file_path"] = output_path
        output_info["file_name"] = os.path.basename(output_path)
        
        # Schedule cleanup of the input and output files
        background_tasks.add_task(cleanup_files, [input_path, output_path])
        
        return output_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reprojecting vector file: {str(e)}")

@router.post("/reproject-raster", response_model=Dict[str, Any])
async def reproject_raster(
    background_tasks: BackgroundTasks,
    input_path: str = Form(...),
    target_crs: str = Form(...)
):
    """
    Reproject a raster file to another coordinate reference system.
    
    Args:
        background_tasks: FastAPI background tasks
        input_path: Path to the input file
        target_crs: Target CRS (e.g., 'EPSG:4326')
        
    Returns:
        Information about the reprojected file
    """
    try:
        # Reproject the raster file
        output_path = data_processing_service.reproject_raster(input_path, target_crs)
        
        # Get information about the output file
        output_info = data_processing_service.get_file_info(output_path)
        
        # Add the output path to the response
        output_info["file_path"] = output_path
        output_info["file_name"] = os.path.basename(output_path)
        
        # Schedule cleanup of the input and output files
        background_tasks.add_task(cleanup_files, [input_path, output_path])
        
        return output_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reprojecting raster file: {str(e)}")

@router.post("/clip-vector", response_model=Dict[str, Any])
async def clip_vector(
    background_tasks: BackgroundTasks,
    input_path: str = Form(...),
    clip_geometry: str = Form(...)
):
    """
    Clip a vector file with a geometry.
    
    Args:
        background_tasks: FastAPI background tasks
        input_path: Path to the input file
        clip_geometry: GeoJSON geometry to clip with (as a string)
        
    Returns:
        Information about the clipped file
    """
    try:
        # Parse the clip geometry
        clip_geom = json.loads(clip_geometry)
        
        # Clip the vector file
        output_path = data_processing_service.clip_vector(input_path, clip_geom)
        
        # Get information about the output file
        output_info = data_processing_service.get_file_info(output_path)
        
        # Add the output path to the response
        output_info["file_path"] = output_path
        output_info["file_name"] = os.path.basename(output_path)
        
        # Schedule cleanup of the input and output files
        background_tasks.add_task(cleanup_files, [input_path, output_path])
        
        return output_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clipping vector file: {str(e)}")

@router.post("/clip-raster", response_model=Dict[str, Any])
async def clip_raster(
    background_tasks: BackgroundTasks,
    input_path: str = Form(...),
    clip_geometry: str = Form(...)
):
    """
    Clip a raster file with a geometry.
    
    Args:
        background_tasks: FastAPI background tasks
        input_path: Path to the input file
        clip_geometry: GeoJSON geometry to clip with (as a string)
        
    Returns:
        Information about the clipped file
    """
    try:
        # Parse the clip geometry
        clip_geom = json.loads(clip_geometry)
        
        # Clip the raster file
        output_path = data_processing_service.clip_raster(input_path, clip_geom)
        
        # Get information about the output file
        output_info = data_processing_service.get_file_info(output_path)
        
        # Add the output path to the response
        output_info["file_path"] = output_path
        output_info["file_name"] = os.path.basename(output_path)
        
        # Schedule cleanup of the input and output files
        background_tasks.add_task(cleanup_files, [input_path, output_path])
        
        return output_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clipping raster file: {str(e)}")

@router.post("/buffer-vector", response_model=Dict[str, Any])
async def buffer_vector(
    background_tasks: BackgroundTasks,
    input_path: str = Form(...),
    distance: float = Form(...)
):
    """
    Buffer a vector file.
    
    Args:
        background_tasks: FastAPI background tasks
        input_path: Path to the input file
        distance: Buffer distance in the units of the input file's CRS
        
    Returns:
        Information about the buffered file
    """
    try:
        # Buffer the vector file
        output_path = data_processing_service.buffer_vector(input_path, distance)
        
        # Get information about the output file
        output_info = data_processing_service.get_file_info(output_path)
        
        # Add the output path to the response
        output_info["file_path"] = output_path
        output_info["file_name"] = os.path.basename(output_path)
        
        # Schedule cleanup of the input and output files
        background_tasks.add_task(cleanup_files, [input_path, output_path])
        
        return output_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error buffering vector file: {str(e)}")

@router.post("/dissolve-vector", response_model=Dict[str, Any])
async def dissolve_vector(
    background_tasks: BackgroundTasks,
    input_path: str = Form(...),
    dissolve_field: Optional[str] = Form(None)
):
    """
    Dissolve a vector file.
    
    Args:
        background_tasks: FastAPI background tasks
        input_path: Path to the input file
        dissolve_field: Field to dissolve by (optional)
        
    Returns:
        Information about the dissolved file
    """
    try:
        # Dissolve the vector file
        output_path = data_processing_service.dissolve_vector(input_path, dissolve_field)
        
        # Get information about the output file
        output_info = data_processing_service.get_file_info(output_path)
        
        # Add the output path to the response
        output_info["file_path"] = output_path
        output_info["file_name"] = os.path.basename(output_path)
        
        # Schedule cleanup of the input and output files
        background_tasks.add_task(cleanup_files, [input_path, output_path])
        
        return output_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error dissolving vector file: {str(e)}")

@router.get("/download/{file_name}", response_class=FileResponse)
async def download_file(file_name: str, background_tasks: BackgroundTasks):
    """
    Download a processed file.
    
    Args:
        file_name: Name of the file to download
        background_tasks: FastAPI background tasks
        
    Returns:
        File response
    """
    try:
        # Construct the file path
        file_path = os.path.join(data_processing_service.upload_dir, file_name)
        
        # Check if the file exists
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File not found: {file_name}")
        
        # Schedule cleanup of the file
        background_tasks.add_task(cleanup_files, [file_path])
        
        return FileResponse(
            path=file_path,
            filename=file_name,
            background=background_tasks
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")

async def cleanup_files(file_paths: List[str], delay: int = 3600):
    """
    Clean up files after a delay.
    
    Args:
        file_paths: List of file paths to clean up
        delay: Delay in seconds before cleaning up (default: 1 hour)
    """
    import asyncio
    
    # Wait for the specified delay
    await asyncio.sleep(delay)
    
    # Clean up the files
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
        except Exception as e:
            print(f"Error cleaning up file {file_path}: {str(e)}")
