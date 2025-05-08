from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, text
from typing import List, Dict, Any, Optional
from app.core.database import get_db, init_db
from app.models import (
    GeospatialData, GeospatialLayer, GeoFeature,
    GeoTable, GeoTableColumn, GeoSuitability, SuitabilityCriterion,
    ImportJob, ImportLog
)
from app.schemas import (
    DatabaseConnectionSettings, DatabaseConnectionResponse,
    GeospatialDataCreate, GeospatialDataUpdate, GeospatialDataResponse,
    GeospatialLayerCreate, GeospatialLayerUpdate, GeospatialLayerResponse,
    GeoFeatureCreate, GeoFeatureUpdate, GeoFeatureResponse,
    GeoTableCreate, GeoTableUpdate, GeoTableResponse,
    GeoSuitabilityCreate, GeoSuitabilityUpdate, GeoSuitabilityResponse,
    ImportJobCreate, ImportJobUpdate, ImportJobResponse
)
from geoalchemy2.functions import ST_AsGeoJSON
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import shape, mapping
import json
import logging
from datetime import datetime

router = APIRouter()

# Database connection endpoints
@router.post("/database/connect", response_model=DatabaseConnectionResponse)
async def connect_database(settings: DatabaseConnectionSettings):
    """
    Test and save database connection settings
    """
    try:
        # Test connection
        connection_string = f"postgresql://{settings.username}:{settings.password}@{settings.host}:{settings.port}/{settings.database}"
        
        # Update environment variables or settings
        # This is a simplified example - in a real app, you'd want to securely store these
        from app.core.config import settings as app_settings
        app_settings.POSTGRES_HOST = settings.host
        app_settings.POSTGRES_PORT = str(settings.port)
        app_settings.POSTGRES_USER = settings.username
        app_settings.POSTGRES_PASSWORD = settings.password
        app_settings.POSTGRES_DB = settings.database
        
        # Initialize database with PostGIS
        await init_db()
        
        return DatabaseConnectionResponse(
            success=True,
            message="Successfully connected to the database",
            connection_string=connection_string
        )
    except Exception as e:
        return DatabaseConnectionResponse(
            success=False,
            message=f"Failed to connect to the database: {str(e)}"
        )

# Geospatial data endpoints
@router.post("/geospatial/data", response_model=GeospatialDataResponse)
async def create_geospatial_data(
    data: GeospatialDataCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create new geospatial data
    """
    try:
        # Convert GeoJSON to WKT
        geom_shape = shape(data.geometry.dict())
        wkb_element = from_shape(geom_shape, srid=4326)
        
        # Convert properties to JSON string if provided
        properties_json = json.dumps(data.properties) if data.properties else None
        
        # Create new geospatial data
        new_data = GeospatialData(
            name=data.name,
            description=data.description,
            geometry=wkb_element,
            properties=properties_json,
            source=data.source,
            data_type=data.data_type
        )
        
        db.add(new_data)
        await db.commit()
        await db.refresh(new_data)
        
        # Convert WKB geometry to GeoJSON for response
        stmt = select(
            new_data.id,
            new_data.name,
            new_data.description,
            func.ST_AsGeoJSON(new_data.geometry).label('geometry'),
            new_data.properties,
            new_data.source,
            new_data.data_type,
            new_data.created_at,
            new_data.updated_at
        ).where(new_data.id == new_data.id)
        
        result = await db.execute(stmt)
        row = result.fetchone()
        
        # Create response
        response = GeospatialDataResponse(
            id=row.id,
            name=row.name,
            description=row.description,
            geometry=json.loads(row.geometry),
            properties=json.loads(row.properties) if row.properties else None,
            source=row.source,
            data_type=row.data_type,
            created_at=row.created_at,
            updated_at=row.updated_at
        )
        
        return response
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create geospatial data: {str(e)}")

@router.get("/geospatial/data", response_model=List[GeospatialDataResponse])
async def get_geospatial_data(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all geospatial data
    """
    try:
        stmt = select(
            GeospatialData.id,
            GeospatialData.name,
            GeospatialData.description,
            func.ST_AsGeoJSON(GeospatialData.geometry).label('geometry'),
            GeospatialData.properties,
            GeospatialData.source,
            GeospatialData.data_type,
            GeospatialData.created_at,
            GeospatialData.updated_at
        ).offset(skip).limit(limit)
        
        result = await db.execute(stmt)
        rows = result.fetchall()
        
        # Create response
        response = []
        for row in rows:
            response.append(GeospatialDataResponse(
                id=row.id,
                name=row.name,
                description=row.description,
                geometry=json.loads(row.geometry),
                properties=json.loads(row.properties) if row.properties else None,
                source=row.source,
                data_type=row.data_type,
                created_at=row.created_at,
                updated_at=row.updated_at
            ))
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get geospatial data: {str(e)}")

@router.get("/geospatial/data/{data_id}", response_model=GeospatialDataResponse)
async def get_geospatial_data_by_id(
    data_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get geospatial data by ID
    """
    try:
        stmt = select(
            GeospatialData.id,
            GeospatialData.name,
            GeospatialData.description,
            func.ST_AsGeoJSON(GeospatialData.geometry).label('geometry'),
            GeospatialData.properties,
            GeospatialData.source,
            GeospatialData.data_type,
            GeospatialData.created_at,
            GeospatialData.updated_at
        ).where(GeospatialData.id == data_id)
        
        result = await db.execute(stmt)
        row = result.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail=f"Geospatial data with ID {data_id} not found")
        
        # Create response
        response = GeospatialDataResponse(
            id=row.id,
            name=row.name,
            description=row.description,
            geometry=json.loads(row.geometry),
            properties=json.loads(row.properties) if row.properties else None,
            source=row.source,
            data_type=row.data_type,
            created_at=row.created_at,
            updated_at=row.updated_at
        )
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get geospatial data: {str(e)}")

# Add more endpoints for other microservices (GeoFeature, GeoTable, GeoSuitability, Importer)
# This is a starting point - you would add similar CRUD operations for each entity

# Spatial queries endpoints
@router.get("/spatial/within", response_model=List[GeospatialDataResponse])
async def get_data_within_geometry(
    geometry: str = Query(..., description="GeoJSON geometry string"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all geospatial data within the given geometry
    """
    try:
        # Parse GeoJSON geometry
        geom_dict = json.loads(geometry)
        geom_shape = shape(geom_dict)
        wkb_element = from_shape(geom_shape, srid=4326)
        
        # Query data within geometry
        stmt = select(
            GeospatialData.id,
            GeospatialData.name,
            GeospatialData.description,
            func.ST_AsGeoJSON(GeospatialData.geometry).label('geometry'),
            GeospatialData.properties,
            GeospatialData.source,
            GeospatialData.data_type,
            GeospatialData.created_at,
            GeospatialData.updated_at
        ).where(
            func.ST_Within(GeospatialData.geometry, wkb_element)
        )
        
        result = await db.execute(stmt)
        rows = result.fetchall()
        
        # Create response
        response = []
        for row in rows:
            response.append(GeospatialDataResponse(
                id=row.id,
                name=row.name,
                description=row.description,
                geometry=json.loads(row.geometry),
                properties=json.loads(row.properties) if row.properties else None,
                source=row.source,
                data_type=row.data_type,
                created_at=row.created_at,
                updated_at=row.updated_at
            ))
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query data within geometry: {str(e)}")

@router.get("/spatial/buffer", response_model=Dict[str, Any])
async def buffer_geometry(
    geometry: str = Query(..., description="GeoJSON geometry string"),
    distance: float = Query(..., description="Buffer distance in meters"),
    db: AsyncSession = Depends(get_db)
):
    """
    Buffer a geometry by a given distance
    """
    try:
        # Parse GeoJSON geometry
        geom_dict = json.loads(geometry)
        geom_shape = shape(geom_dict)
        wkb_element = from_shape(geom_shape, srid=4326)
        
        # Buffer geometry
        stmt = select(
            func.ST_AsGeoJSON(
                func.ST_Transform(
                    func.ST_Buffer(
                        func.ST_Transform(wkb_element, 3857),
                        distance
                    ),
                    4326
                )
            ).label('buffered_geometry')
        )
        
        result = await db.execute(stmt)
        row = result.fetchone()
        
        # Create response
        return {
            "original_geometry": geom_dict,
            "buffered_geometry": json.loads(row.buffered_geometry),
            "distance": distance
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to buffer geometry: {str(e)}")

# Add more spatial query endpoints as needed
