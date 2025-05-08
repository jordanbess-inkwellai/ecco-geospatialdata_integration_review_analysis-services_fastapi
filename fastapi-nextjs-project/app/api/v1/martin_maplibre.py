from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, Path, Body, File, UploadFile, Form
from fastapi.responses import JSONResponse, Response, FileResponse
from typing import Dict, List, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import os
import json

from app.core.database import get_db
from app.core.martin_config import martin_config
from app.services.martin_service import martin_service
from app.schemas.martin_schemas import (
    ServerStatusResponse,
    TableMetadata,
    TileJSON,
    FileInfo,
    StyleInfo,
    UploadResult,
    DeleteResult,
    CreatePMTilesRequest,
    CreateStyleRequest,
    SourceType,
    TileFormat
)

router = APIRouter()

@router.get("/status", response_model=ServerStatusResponse)
async def get_martin_status():
    """
    Get the status of the Martin server.
    
    Returns:
        Server status information
    """
    status = martin_service.get_server_status()
    return status

@router.get("/tables", response_model=List[Dict[str, Any]])
async def get_available_tables():
    """
    Get a list of available tables from the Martin server.
    
    Returns:
        List of available tables
    """
    tables = martin_service.get_available_tables()
    return tables

@router.get("/tables/{table_name}/metadata", response_model=Dict[str, Any])
async def get_table_metadata(table_name: str):
    """
    Get metadata for a table.
    
    Args:
        table_name: Name of the table
        
    Returns:
        Table metadata
    """
    metadata = martin_service.get_table_metadata(table_name)
    
    if not metadata:
        raise HTTPException(status_code=404, detail=f"Table {table_name} not found")
    
    return metadata

@router.get("/tables/{table_name}/tilejson", response_model=Dict[str, Any])
async def get_table_tilejson(table_name: str):
    """
    Get TileJSON for a table.
    
    Args:
        table_name: Name of the table
        
    Returns:
        TileJSON metadata
    """
    tilejson = martin_service.get_table_tilejson(table_name)
    
    if not tilejson:
        raise HTTPException(status_code=404, detail=f"Table {table_name} not found")
    
    return tilejson

@router.get("/tables/{table_name}/tiles/{z}/{x}/{y}")
async def get_tile(
    table_name: str,
    z: int,
    x: int,
    y: int,
    format: TileFormat = Query(TileFormat.PBF, description="Tile format")
):
    """
    Get a tile for a table.
    
    Args:
        table_name: Name of the table
        z: Zoom level
        x: X coordinate
        y: Y coordinate
        format: Tile format
        
    Returns:
        Tile data
    """
    tile_data = martin_service.get_tile(table_name, z, x, y, format)
    
    if not tile_data:
        raise HTTPException(status_code=404, detail=f"Tile not found")
    
    # Set the appropriate content type based on the format
    content_type = "application/x-protobuf"
    
    if format == TileFormat.MVT:
        content_type = "application/vnd.mapbox-vector-tile"
    elif format == TileFormat.PNG:
        content_type = "image/png"
    elif format == TileFormat.JPG:
        content_type = "image/jpeg"
    elif format == TileFormat.WEBP:
        content_type = "image/webp"
    
    return Response(content=tile_data, media_type=content_type)

@router.get("/pmtiles", response_model=List[FileInfo])
async def get_available_pmtiles():
    """
    Get a list of available PMTiles.
    
    Returns:
        List of available PMTiles
    """
    pmtiles = martin_service.get_available_pmtiles()
    return pmtiles

@router.get("/mbtiles", response_model=List[FileInfo])
async def get_available_mbtiles():
    """
    Get a list of available MBTiles.
    
    Returns:
        List of available MBTiles
    """
    mbtiles = martin_service.get_available_mbtiles()
    return mbtiles

@router.get("/raster", response_model=List[FileInfo])
async def get_available_raster_tiles():
    """
    Get a list of available raster tiles.
    
    Returns:
        List of available raster tiles
    """
    raster_tiles = martin_service.get_available_raster_tiles()
    return raster_tiles

@router.get("/terrain", response_model=List[FileInfo])
async def get_available_terrain_tiles():
    """
    Get a list of available terrain tiles.
    
    Returns:
        List of available terrain tiles
    """
    terrain_tiles = martin_service.get_available_terrain_tiles()
    return terrain_tiles

@router.get("/styles", response_model=List[StyleInfo])
async def get_available_styles():
    """
    Get a list of available styles.
    
    Returns:
        List of available styles
    """
    styles = martin_service.get_available_styles()
    return styles

@router.post("/pmtiles/upload", response_model=UploadResult)
async def upload_pmtiles(file: UploadFile = File(...)):
    """
    Upload a PMTiles file.
    
    Args:
        file: PMTiles file
        
    Returns:
        Upload result
    """
    result = martin_service.upload_pmtiles(file.file, file.filename)
    
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
    
    return result

@router.post("/mbtiles/upload", response_model=UploadResult)
async def upload_mbtiles(file: UploadFile = File(...)):
    """
    Upload an MBTiles file.
    
    Args:
        file: MBTiles file
        
    Returns:
        Upload result
    """
    result = martin_service.upload_mbtiles(file.file, file.filename)
    
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
    
    return result

@router.post("/raster/upload", response_model=UploadResult)
async def upload_raster_tiles(file: UploadFile = File(...)):
    """
    Upload a raster tiles file.
    
    Args:
        file: Raster tiles file
        
    Returns:
        Upload result
    """
    result = martin_service.upload_raster_tiles(file.file, file.filename)
    
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
    
    return result

@router.post("/terrain/upload", response_model=UploadResult)
async def upload_terrain_tiles(file: UploadFile = File(...)):
    """
    Upload a terrain tiles file.
    
    Args:
        file: Terrain tiles file
        
    Returns:
        Upload result
    """
    result = martin_service.upload_terrain_tiles(file.file, file.filename)
    
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
    
    return result

@router.post("/styles/upload", response_model=UploadResult)
async def upload_style(file: UploadFile = File(...)):
    """
    Upload a style file.
    
    Args:
        file: Style file
        
    Returns:
        Upload result
    """
    result = martin_service.upload_style(file.file, file.filename)
    
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
    
    return result

@router.delete("/pmtiles/{file_name}", response_model=DeleteResult)
async def delete_pmtiles(file_name: str):
    """
    Delete a PMTiles file.
    
    Args:
        file_name: File name
        
    Returns:
        Delete result
    """
    result = martin_service.delete_pmtiles(file_name)
    
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
    
    return result

@router.delete("/mbtiles/{file_name}", response_model=DeleteResult)
async def delete_mbtiles(file_name: str):
    """
    Delete an MBTiles file.
    
    Args:
        file_name: File name
        
    Returns:
        Delete result
    """
    result = martin_service.delete_mbtiles(file_name)
    
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
    
    return result

@router.delete("/raster/{file_name}", response_model=DeleteResult)
async def delete_raster_tiles(file_name: str):
    """
    Delete a raster tiles file.
    
    Args:
        file_name: File name
        
    Returns:
        Delete result
    """
    result = martin_service.delete_raster_tiles(file_name)
    
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
    
    return result

@router.delete("/terrain/{file_name}", response_model=DeleteResult)
async def delete_terrain_tiles(file_name: str):
    """
    Delete a terrain tiles file.
    
    Args:
        file_name: File name
        
    Returns:
        Delete result
    """
    result = martin_service.delete_terrain_tiles(file_name)
    
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
    
    return result

@router.delete("/styles/{file_name}", response_model=DeleteResult)
async def delete_style(file_name: str):
    """
    Delete a style file.
    
    Args:
        file_name: File name
        
    Returns:
        Delete result
    """
    result = martin_service.delete_style(file_name)
    
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
    
    return result

@router.post("/pmtiles/create", response_model=UploadResult)
async def create_pmtiles_from_geojson(request: CreatePMTilesRequest):
    """
    Create PMTiles from GeoJSON data using Tippecanoe.
    
    Args:
        request: Create PMTiles request
        
    Returns:
        Creation result
    """
    result = martin_service.create_pmtiles_from_geojson(
        request.geojson_data,
        request.output_name,
        request.min_zoom,
        request.max_zoom
    )
    
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
    
    return result

@router.post("/styles/create", response_model=UploadResult)
async def create_style_from_source(request: CreateStyleRequest):
    """
    Create a MapLibre style from a source.
    
    Args:
        request: Create style request
        
    Returns:
        Creation result
    """
    result = martin_service.create_style_from_source(
        request.source_url,
        request.source_type,
        request.source_name,
        request.output_name
    )
    
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
    
    return result
