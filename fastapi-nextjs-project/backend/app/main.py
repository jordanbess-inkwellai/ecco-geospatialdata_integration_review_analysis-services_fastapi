from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
import logging
import os

# Import routers
from app.api.v1.fast_geospatial import router as fast_geospatial_router
from app.api.v1.fast_importer import router as fast_importer_router
from app.api.v1.fate_geo_feature import router as fate_geo_feature_router
from app.api.v1.fast_geo_table import router as fast_geo_table_router
from app.api.v1.fast_geo_suitability import router as fast_geo_suitability_router
from app.api.v1.integrated import router as integrated_router
from app.api.v1.erd import router as erd_router
from app.api.v1.tiles import router as tiles_router
from app.api.v1.tippecanoe import router as tippecanoe_router
from app.api.v1.box_integration import router as box_integration_router
from app.api.v1.geospatial_processing import router as geospatial_processing_router
from app.api.v1.esri_geodatabase import router as esri_geodatabase_router
from app.api.v1.rclone import router as rclone_router

# Import database initialization
from app.core.database import init_db
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Integrated Geospatial API",
    description="An integrated API for geospatial data management and analysis",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# Legacy routers (kept for backward compatibility)
app.include_router(fast_geospatial_router, prefix="/api/v1/geospatial", tags=["Legacy Geospatial"])
app.include_router(fast_importer_router, prefix="/api/v1/importer", tags=["Legacy Importer"])
app.include_router(fate_geo_feature_router, prefix="/api/v1/geo-feature", tags=["Legacy Geo Feature"])
app.include_router(fast_geo_table_router, prefix="/api/v1/geo-table", tags=["Legacy Geo Table"])
app.include_router(fast_geo_suitability_router, prefix="/api/v1/geo-suitability", tags=["Legacy Geo Suitability"])

# New integrated router
app.include_router(integrated_router, prefix="/api/v1/integrated", tags=["Integrated API"])

# ERD router
app.include_router(erd_router, prefix="/api/v1/erd", tags=["ERD Generation"])

# Tiles router
app.include_router(tiles_router, prefix="/api/v1/tiles", tags=["Tile Management"])

# Tippecanoe router
app.include_router(tippecanoe_router, prefix="/api/v1/tippecanoe", tags=["Tippecanoe Operations"])

# Box integration router
app.include_router(box_integration_router, prefix="/api/v1/box", tags=["Box.com Integration"])

# Geospatial processing router
app.include_router(geospatial_processing_router, prefix="/api/v1/geospatial-processing", tags=["Geospatial Processing"])

# ESRI Geodatabase router
app.include_router(esri_geodatabase_router, prefix="/api/v1/esri-geodatabase", tags=["ESRI Geodatabase Conversion"])

# Cloud SQL Monitor router
from app.api.v1.cloudsql_monitor import router as cloudsql_monitor_router
app.include_router(cloudsql_monitor_router, prefix="/api/v1/cloudsql", tags=["Cloud SQL Monitoring"])

# Kestra Integration router
from app.api.v1.kestra import router as kestra_router
app.include_router(kestra_router, prefix="/api/v1/kestra", tags=["Kestra Integration"])

# DLT-Kestra Integration router
from app.api.v1.dlt_kestra import router as dlt_kestra_router
app.include_router(dlt_kestra_router, prefix="/api/v1/dlt-kestra", tags=["DLT-Kestra Integration"])

# Rclone Integration router
app.include_router(rclone_router, prefix="/api/v1/rclone", tags=["Rclone Integration"])

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Integrated Geospatial API!",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "openapi_url": "/openapi.json",
    }

@app.on_event("startup")
async def startup_event():
    """
    Initialize the database on startup
    """
    logger.info("Initializing database...")
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        # Don't raise the exception - allow the app to start even if DB init fails
        # This allows users to configure the DB connection later