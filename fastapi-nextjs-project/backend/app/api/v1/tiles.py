from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
import logging

from app.core.database import get_db
from app.services.tile_service import TileService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload")
async def upload_tile_file(
    file: UploadFile = File(...),
    tile_type: str = Form(..., description="Type of tile file (pmtiles or mbtiles)"),
    name: str = Form(..., description="Name for the tile source"),
    description: Optional[str] = Form(None, description="Description of the tile source"),
    attribution: Optional[str] = Form(None, description="Attribution for the tile source"),
    min_zoom: Optional[int] = Form(None, description="Minimum zoom level"),
    max_zoom: Optional[int] = Form(None, description="Maximum zoom level"),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a tile file (PMTiles or MBTiles)
    """
    try:
        # Validate file extension
        if tile_type == "pmtiles" and not file.filename.endswith(".pmtiles"):
            raise HTTPException(status_code=400, detail="File must have .pmtiles extension")
        if tile_type == "mbtiles" and not file.filename.endswith(".mbtiles"):
            raise HTTPException(status_code=400, detail="File must have .mbtiles extension")
        
        result = await TileService.upload_tile_file(
            file=file,
            tile_type=tile_type,
            name=name,
            description=description,
            attribution=attribution,
            min_zoom=min_zoom,
            max_zoom=max_zoom
        )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading tile file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading tile file: {str(e)}")


@router.get("/sources")
async def list_tile_sources(
    db: AsyncSession = Depends(get_db)
):
    """
    List all available tile sources
    """
    try:
        sources = await TileService.list_tile_sources()
        return sources
    except Exception as e:
        logger.error(f"Error listing tile sources: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing tile sources: {str(e)}")


@router.get("/sources/{name}")
async def get_tile_source(
    name: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get information about a specific tile source
    """
    try:
        source = await TileService.get_tile_source(name)
        return source
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tile source: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting tile source: {str(e)}")


@router.delete("/sources/{name}")
async def delete_tile_source(
    name: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a tile source
    """
    try:
        result = await TileService.delete_tile_source(name)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting tile source: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting tile source: {str(e)}")


@router.get("/terrain/elevation")
async def get_terrain_elevation(
    lng: float = Query(..., description="Longitude"),
    lat: float = Query(..., description="Latitude"),
    source: str = Query(..., description="Terrain source name"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get terrain elevation at a specific point
    """
    try:
        # This is a placeholder - in a real implementation, you would query the terrain data
        # For now, we'll return a mock elevation
        return {
            "elevation": 100.0,  # Mock elevation in meters
            "source": source,
            "coordinates": [lng, lat]
        }
    except Exception as e:
        logger.error(f"Error getting terrain elevation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting terrain elevation: {str(e)}")


@router.get("/terrain/profile")
async def get_terrain_profile(
    start_lng: float = Query(..., description="Start longitude"),
    start_lat: float = Query(..., description="Start latitude"),
    end_lng: float = Query(..., description="End longitude"),
    end_lat: float = Query(..., description="End latitude"),
    samples: int = Query(100, description="Number of samples"),
    source: str = Query(..., description="Terrain source name"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get terrain elevation profile between two points
    """
    try:
        # This is a placeholder - in a real implementation, you would query the terrain data
        # For now, we'll return a mock profile
        import numpy as np
        
        # Generate mock elevation profile
        distances = np.linspace(0, 1, samples)
        elevations = 100 + 50 * np.sin(distances * np.pi * 2)
        
        return {
            "profile": [
                {
                    "distance": float(d),
                    "elevation": float(e),
                    "coordinates": [
                        start_lng + (end_lng - start_lng) * d,
                        start_lat + (end_lat - start_lat) * d
                    ]
                }
                for d, e in zip(distances, elevations)
            ],
            "source": source,
            "start": [start_lng, start_lat],
            "end": [end_lng, end_lat],
            "samples": samples
        }
    except Exception as e:
        logger.error(f"Error getting terrain profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting terrain profile: {str(e)}")
