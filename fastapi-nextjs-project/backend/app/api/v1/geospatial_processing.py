from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, Body
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
import os
import logging
from pydantic import BaseModel

from app.core.database import get_db
from app.services.geospatial_processing_service import GeospatialProcessingService

router = APIRouter()
logger = logging.getLogger(__name__)


class DuckDBQueryRequest(BaseModel):
    query: str
    export_format: Optional[str] = None
    export_path: Optional[str] = None


class TippecanoeRequest(BaseModel):
    input_dir: str
    output_format: str = "pmtiles"
    output_dir: Optional[str] = None
    min_zoom: Optional[int] = None
    max_zoom: Optional[int] = None
    layer_name: Optional[str] = None
    simplification: Optional[float] = None
    drop_rate: Optional[float] = None
    buffer_size: Optional[int] = None
    additional_args: Optional[List[str]] = None


class KestraWorkflowRequest(BaseModel):
    workflow_name: str
    input_dir: str
    output_format: str = "pmtiles"
    output_dir: Optional[str] = None
    min_zoom: Optional[int] = None
    max_zoom: Optional[int] = None
    simplification: Optional[float] = None
    drop_rate: Optional[float] = None
    buffer_size: Optional[int] = None
    schedule: Optional[str] = None


@router.post("/import-to-duckdb")
async def import_to_duckdb(
    input_files: List[str] = Body(..., description="List of input file paths"),
    db_name: str = Body(..., description="Name for the DuckDB database"),
    spatial_index: bool = Body(True, description="Whether to create spatial indexes"),
    overwrite: bool = Body(False, description="Whether to overwrite existing tables"),
    db: AsyncSession = Depends(get_db)
):
    """
    Import geospatial files into DuckDB for fast inspection and querying
    """
    try:
        result = await GeospatialProcessingService.import_to_duckdb(
            input_files=input_files,
            db_name=db_name,
            spatial_index=spatial_index,
            overwrite=overwrite
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing to DuckDB: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error importing to DuckDB: {str(e)}")


@router.post("/query-duckdb/{db_name}")
async def query_duckdb(
    db_name: str,
    request: DuckDBQueryRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Execute a query on a DuckDB database
    """
    try:
        result = await GeospatialProcessingService.query_duckdb(
            db_name=db_name,
            query=request.query,
            export_format=request.export_format,
            export_path=request.export_path
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying DuckDB: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error querying DuckDB: {str(e)}")


@router.post("/batch-tippecanoe")
async def batch_tippecanoe(
    request: TippecanoeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Run Tippecanoe on a batch of GeoJSON files
    """
    try:
        result = await GeospatialProcessingService.batch_tippecanoe(
            input_dir=request.input_dir,
            output_format=request.output_format,
            output_dir=request.output_dir,
            min_zoom=request.min_zoom,
            max_zoom=request.max_zoom,
            layer_name=request.layer_name,
            simplification=request.simplification,
            drop_rate=request.drop_rate,
            buffer_size=request.buffer_size,
            additional_args=request.additional_args
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running batch Tippecanoe: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error running batch Tippecanoe: {str(e)}")


@router.post("/generate-kestra-workflow")
async def generate_kestra_workflow(
    request: KestraWorkflowRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a Kestra.io workflow for batch Tippecanoe processing
    """
    try:
        result = await GeospatialProcessingService.generate_kestra_workflow(
            workflow_name=request.workflow_name,
            input_dir=request.input_dir,
            output_format=request.output_format,
            output_dir=request.output_dir,
            min_zoom=request.min_zoom,
            max_zoom=request.max_zoom,
            simplification=request.simplification,
            drop_rate=request.drop_rate,
            buffer_size=request.buffer_size,
            schedule=request.schedule
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating Kestra workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating Kestra workflow: {str(e)}")


@router.get("/download-workflow/{workflow_name}")
async def download_workflow(
    workflow_name: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Download a generated Kestra workflow file
    """
    try:
        # Sanitize workflow name
        safe_name = "".join(c if c.isalnum() or c in ['-', '_'] else '_' for c in workflow_name)
        workflow_path = os.path.join(GeospatialProcessingService.TEMP_DIR, f"{safe_name}.yml")
        
        if not os.path.exists(workflow_path):
            raise HTTPException(status_code=404, detail=f"Workflow file not found: {workflow_name}")
        
        return FileResponse(
            path=workflow_path,
            filename=f"{safe_name}.yml",
            media_type="application/x-yaml"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error downloading workflow: {str(e)}")


@router.get("/list-duckdb")
async def list_duckdb(
    db: AsyncSession = Depends(get_db)
):
    """
    List all available DuckDB databases
    """
    try:
        duckdb_dir = GeospatialProcessingService.DUCKDB_DIR
        databases = []
        
        for filename in os.listdir(duckdb_dir):
            if filename.endswith('.duckdb'):
                file_path = os.path.join(duckdb_dir, filename)
                
                # Get basic file info
                databases.append({
                    "name": os.path.splitext(filename)[0],
                    "file_path": file_path,
                    "size_bytes": os.path.getsize(file_path)
                })
        
        return databases
    except Exception as e:
        logger.error(f"Error listing DuckDB databases: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing DuckDB databases: {str(e)}")


@router.get("/duckdb-info/{db_name}")
async def duckdb_info(
    db_name: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get information about a DuckDB database
    """
    try:
        # Sanitize database name
        safe_name = "".join(c if c.isalnum() or c in ['-', '_'] else '_' for c in db_name)
        db_path = os.path.join(GeospatialProcessingService.DUCKDB_DIR, f"{safe_name}.duckdb")
        
        # Check if database exists
        if not os.path.exists(db_path):
            raise HTTPException(status_code=404, detail=f"Database not found: {db_name}")
        
        import duckdb
        
        # Connect to DuckDB
        conn = duckdb.connect(db_path)
        
        # Load extensions
        conn.execute("INSTALL spatial;")
        conn.execute("LOAD spatial;")
        
        # Get tables
        tables = conn.execute("SHOW TABLES").fetchall()
        table_names = [table[0] for table in tables]
        
        # Get table info
        table_info = []
        for table in table_names:
            # Get row count
            row_count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            
            # Get columns
            columns = conn.execute(f"PRAGMA table_info({table})").fetchall()
            column_info = []
            for col in columns:
                column_info.append({
                    "name": col[1],
                    "type": col[2],
                    "notnull": col[3],
                    "default": col[4],
                    "pk": col[5]
                })
            
            # Check for geometry column
            has_geometry = False
            for col in columns:
                if col[2].upper() == 'GEOMETRY':
                    has_geometry = True
                    break
            
            # Get sample data
            sample = conn.execute(f"SELECT * FROM {table} LIMIT 5").fetchdf()
            sample_json = sample.to_dict(orient='records')
            
            table_info.append({
                "name": table,
                "row_count": row_count,
                "column_count": len(columns),
                "columns": column_info,
                "has_geometry": has_geometry,
                "sample_data": sample_json
            })
        
        # Close connection
        conn.close()
        
        return {
            "database_name": safe_name,
            "database_path": db_path,
            "size_bytes": os.path.getsize(db_path),
            "table_count": len(table_names),
            "tables": table_info
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting DuckDB info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting DuckDB info: {str(e)}")


@router.delete("/duckdb/{db_name}")
async def delete_duckdb(
    db_name: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a DuckDB database
    """
    try:
        # Sanitize database name
        safe_name = "".join(c if c.isalnum() or c in ['-', '_'] else '_' for c in db_name)
        db_path = os.path.join(GeospatialProcessingService.DUCKDB_DIR, f"{safe_name}.duckdb")
        
        # Check if database exists
        if not os.path.exists(db_path):
            raise HTTPException(status_code=404, detail=f"Database not found: {db_name}")
        
        # Delete the database file
        os.remove(db_path)
        
        return {
            "success": True,
            "database_name": safe_name,
            "database_path": db_path
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting DuckDB database: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting DuckDB database: {str(e)}")
