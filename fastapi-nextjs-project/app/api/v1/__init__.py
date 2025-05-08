from fastapi import APIRouter
from app.core.config import settings

api_router = APIRouter()

# Import and include other routers here
from .ogc_api_processes import router as ogc_processes_router
from .data_processing import router as data_processing_router
from .box_integration import router as box_integration_router
from .kestra_workflows import router as kestra_workflows_router
from .duckdb_analytics import router as duckdb_analytics_router
from .duckdb_pivot import router as duckdb_pivot_router
from .duckdb_nanodbc import router as duckdb_nanodbc_router
from .martin_maplibre import router as martin_maplibre_router
from .docetl import router as docetl_router
from .diagram import router as diagram_router

# Include routers
api_router.include_router(ogc_processes_router, prefix="/processes", tags=["OGC API Processes"])
api_router.include_router(data_processing_router, prefix="/data-processing", tags=["Data Processing"])
api_router.include_router(box_integration_router, prefix="/box", tags=["Box.com Integration"])
api_router.include_router(kestra_workflows_router, prefix="/workflows", tags=["Kestra Workflows"])
api_router.include_router(duckdb_analytics_router, prefix="/duckdb", tags=["DuckDB Analytics"])
api_router.include_router(duckdb_pivot_router, prefix="/api/v1", tags=["DuckDB Pivot Table"])
api_router.include_router(duckdb_nanodbc_router, prefix="/api/v1", tags=["DuckDB Nanodbc"])
api_router.include_router(martin_maplibre_router, prefix="/martin", tags=["Martin MapLibre"])
api_router.include_router(docetl_router, prefix="/docetl", tags=["DocETL"])
api_router.include_router(diagram_router, prefix="/diagrams", tags=["Database Diagrams"])

# Conditionally include AI service router if AI features are enabled
if settings.ENABLE_AI_FEATURES:
    from .ai_service import router as ai_service_router
    api_router.include_router(ai_service_router, prefix="/ai", tags=["AI Services"])
