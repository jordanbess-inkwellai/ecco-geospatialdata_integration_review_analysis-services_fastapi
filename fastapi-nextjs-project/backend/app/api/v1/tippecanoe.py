from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
import os
import logging

from app.core.database import get_db
from app.services.tippecanoe_service import TippecanoeService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload-geojson")
async def upload_geojson(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None, description="Optional name for the file"),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a GeoJSON file for processing with Tippecanoe
    """
    try:
        result = await TippecanoeService.upload_geojson(file=file, name=name)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading GeoJSON: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading GeoJSON: {str(e)}")


@router.post("/generate-tiles")
async def generate_tiles(
    input_files: List[str] = Form(..., description="List of input GeoJSON file paths"),
    output_format: str = Form("pmtiles", description="Output format (pmtiles or mbtiles)"),
    output_name: str = Form(..., description="Name for the output file"),
    min_zoom: Optional[int] = Form(None, description="Minimum zoom level"),
    max_zoom: Optional[int] = Form(None, description="Maximum zoom level"),
    layer_name: Optional[str] = Form(None, description="Layer name"),
    simplification: Optional[float] = Form(None, description="Simplification factor"),
    drop_rate: Optional[float] = Form(None, description="Rate at which to drop features"),
    buffer_size: Optional[int] = Form(None, description="Buffer size in pixels"),
    db: AsyncSession = Depends(get_db)
):
    """
    Run Tippecanoe to generate vector tiles
    """
    try:
        # Parse additional arguments from form data
        additional_args = []
        
        # Add common Tippecanoe options
        additional_args.extend(["--force"])  # Overwrite output file if it exists
        additional_args.extend(["--read-parallel"])  # Read input files in parallel
        
        result = await TippecanoeService.run_tippecanoe(
            input_files=input_files,
            output_format=output_format,
            output_name=output_name,
            min_zoom=min_zoom,
            max_zoom=max_zoom,
            layer_name=layer_name,
            simplification=simplification,
            drop_rate=drop_rate,
            buffer_size=buffer_size,
            additional_args=additional_args
        )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating tiles: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating tiles: {str(e)}")


@router.post("/convert-to-gpkg")
async def convert_to_gpkg(
    source_path: str = Form(..., description="Path to the source tile file"),
    source_type: str = Form(..., description="Type of source file (pmtiles or mbtiles)"),
    output_name: Optional[str] = Form(None, description="Name for the output GeoPackage file"),
    zoom_levels: Optional[List[int]] = Form(None, description="List of zoom levels to include"),
    db: AsyncSession = Depends(get_db)
):
    """
    Convert MBTiles or PMTiles to GeoPackage
    """
    try:
        result = await TippecanoeService.convert_to_gpkg(
            source_path=source_path,
            source_type=source_type,
            output_name=output_name,
            zoom_levels=zoom_levels
        )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error converting to GeoPackage: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error converting to GeoPackage: {str(e)}")


@router.get("/download-gpkg/{name}")
async def download_gpkg(
    name: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Download a GeoPackage file
    """
    try:
        # Sanitize name
        safe_name = "".join(c if c.isalnum() or c in ['-', '_'] else '_' for c in name)
        file_path = os.path.join(TippecanoeService.GPKG_DIR, f"{safe_name}.gpkg")
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"GeoPackage file not found: {name}")
        
        return FileResponse(
            path=file_path,
            filename=f"{safe_name}.gpkg",
            media_type="application/geopackage+sqlite3"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading GeoPackage: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error downloading GeoPackage: {str(e)}")


@router.get("/list-geojson")
async def list_geojson(
    db: AsyncSession = Depends(get_db)
):
    """
    List all available GeoJSON files
    """
    try:
        geojson_files = []
        
        for filename in os.listdir(TippecanoeService.GEOJSON_DIR):
            if filename.endswith((".geojson", ".json")):
                file_path = os.path.join(TippecanoeService.GEOJSON_DIR, filename)
                
                # Get basic file info
                geojson_files.append({
                    "name": os.path.splitext(filename)[0],
                    "file_path": file_path,
                    "size_bytes": os.path.getsize(file_path)
                })
        
        return geojson_files
    except Exception as e:
        logger.error(f"Error listing GeoJSON files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing GeoJSON files: {str(e)}")


@router.get("/list-gpkg")
async def list_gpkg(
    db: AsyncSession = Depends(get_db)
):
    """
    List all available GeoPackage files
    """
    try:
        gpkg_files = []
        
        for filename in os.listdir(TippecanoeService.GPKG_DIR):
            if filename.endswith(".gpkg"):
                file_path = os.path.join(TippecanoeService.GPKG_DIR, filename)
                
                # Get metadata
                metadata = await TippecanoeService.extract_gpkg_metadata(file_path)
                
                gpkg_files.append({
                    "name": os.path.splitext(filename)[0],
                    "file_path": file_path,
                    "size_bytes": os.path.getsize(file_path),
                    "metadata": metadata
                })
        
        return gpkg_files
    except Exception as e:
        logger.error(f"Error listing GeoPackage files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing GeoPackage files: {str(e)}")
