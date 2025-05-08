from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, Path, Body, File, UploadFile, Form
from fastapi.responses import JSONResponse, FileResponse
from typing import Dict, List, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import os
import json
import pandas as pd
import geopandas as gpd
from datetime import datetime

from app.core.database import get_db
from app.core.duckdb_config import duckdb_config
from app.services.duckdb_service import duckdb_service
from app.schemas.duckdb_schemas import (
    ExecuteQueryRequest,
    CreateTableFromFileRequest,
    ExportTableRequest,
    GetTableSchemaRequest,
    GetTablesRequest,
    GetTablePreviewRequest,
    GetTableStatisticsRequest,
    CreateDatabaseRequest,
    DeleteDatabaseRequest,
    ConnectToDatabaseRequest,
    SpatialQueryRequest,
    ReprojectGeometryRequest,
    ConvertToPostGISRequest,
    OutputFormat,
    DatabaseType
)

router = APIRouter()

@router.get("/status", response_model=Dict[str, Any])
async def get_duckdb_status():
    """
    Get the status of the DuckDB integration.

    Returns:
        Status information
    """
    return {
        "data_dir": duckdb_config.data_dir,
        "temp_dir": duckdb_config.temp_dir,
        "memory_limit": duckdb_config.memory_limit,
        "extensions": duckdb_config.extensions,
        "s3_configured": duckdb_config.is_s3_configured,
        "azure_configured": duckdb_config.is_azure_configured,
        "gcs_configured": duckdb_config.is_gcs_configured,
        "postgres_configured": duckdb_config.is_postgres_configured,
        "mysql_configured": duckdb_config.is_mysql_configured,
        "sqlite_configured": duckdb_config.is_sqlite_configured
    }

@router.post("/query", response_model=List[Dict[str, Any]])
async def execute_query(request: ExecuteQueryRequest):
    """
    Execute a SQL query.

    Args:
        request: Query request

    Returns:
        Query results
    """
    try:
        results = duckdb_service.execute_query(
            request.query,
            request.db_path,
            request.params
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing query: {str(e)}")

@router.post("/tables", response_model=Dict[str, str])
async def create_table_from_file(request: CreateTableFromFileRequest):
    """
    Create a table from a file.

    Args:
        request: Create table request

    Returns:
        Success message
    """
    try:
        success = duckdb_service.create_table_from_file(
            request.file_path,
            request.table_name,
            request.db_path,
            request.use_hostfs
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to create table from file")

        return {"message": f"Table {request.table_name} created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating table from file: {str(e)}")

@router.post("/tables/upload", response_model=Dict[str, str])
async def create_table_from_uploaded_file(
    table_name: str = Form(...),
    db_path: Optional[str] = Form(None),
    file: UploadFile = File(...)
):
    """
    Create a table from an uploaded file.

    Args:
        table_name: Name of the table to create
        db_path: Path to the database file (optional)
        file: Uploaded file

    Returns:
        Success message
    """
    try:
        success = duckdb_service.create_table_from_uploaded_file(
            file.file,
            file.filename,
            table_name,
            db_path
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to create table from uploaded file")

        return {"message": f"Table {table_name} created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating table from uploaded file: {str(e)}")

@router.post("/tables/export", response_model=Dict[str, str])
async def export_table(request: ExportTableRequest):
    """
    Export a table to a file.

    Args:
        request: Export table request

    Returns:
        Path to the exported file
    """
    try:
        output_path = duckdb_service.export_table(
            request.table_name,
            request.output_format.value,
            request.output_path,
            request.db_path
        )

        if not output_path:
            raise HTTPException(status_code=500, detail="Failed to export table")

        return {"file_path": output_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting table: {str(e)}")

@router.post("/tables/export/download", response_class=FileResponse)
async def export_table_and_download(
    table_name: str = Form(...),
    output_format: str = Form(...),
    db_path: Optional[str] = Form(None)
):
    """
    Export a table to a file and download it.

    Args:
        table_name: Name of the table to export
        output_format: Output format
        db_path: Path to the database file (optional)

    Returns:
        Exported file for download
    """
    try:
        # Validate the output format
        try:
            format_enum = OutputFormat(output_format)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid output format: {output_format}")

        # Export the table
        output_path = duckdb_service.export_table(
            table_name,
            format_enum.value,
            None,
            db_path
        )

        if not output_path:
            raise HTTPException(status_code=500, detail="Failed to export table")

        # Return the file for download
        return FileResponse(
            path=output_path,
            filename=os.path.basename(output_path),
            media_type="application/octet-stream"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting table: {str(e)}")

@router.get("/tables/{table_name}/schema", response_model=List[Dict[str, Any]])
async def get_table_schema(
    table_name: str,
    db_path: Optional[str] = Query(None)
):
    """
    Get the schema of a table.

    Args:
        table_name: Name of the table
        db_path: Path to the database file (optional)

    Returns:
        Table schema
    """
    try:
        schema = duckdb_service.get_table_schema(table_name, db_path)
        return schema
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting table schema: {str(e)}")

@router.get("/tables", response_model=List[str])
async def get_tables(
    db_path: Optional[str] = Query(None)
):
    """
    Get a list of tables in the database.

    Args:
        db_path: Path to the database file (optional)

    Returns:
        List of table names
    """
    try:
        tables = duckdb_service.get_tables(db_path)
        return tables
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting tables: {str(e)}")

@router.get("/tables/{table_name}/preview", response_model=List[Dict[str, Any]])
async def get_table_preview(
    table_name: str,
    limit: int = Query(10),
    db_path: Optional[str] = Query(None)
):
    """
    Get a preview of a table.

    Args:
        table_name: Name of the table
        limit: Maximum number of rows to return
        db_path: Path to the database file (optional)

    Returns:
        Table preview
    """
    try:
        preview = duckdb_service.get_table_preview(table_name, limit, db_path)
        return preview
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting table preview: {str(e)}")

@router.get("/tables/{table_name}/statistics", response_model=Dict[str, Any])
async def get_table_statistics(
    table_name: str,
    db_path: Optional[str] = Query(None)
):
    """
    Get statistics for a table.

    Args:
        table_name: Name of the table
        db_path: Path to the database file (optional)

    Returns:
        Table statistics
    """
    try:
        statistics = duckdb_service.get_table_statistics(table_name, db_path)
        return statistics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting table statistics: {str(e)}")

@router.post("/databases", response_model=Dict[str, str])
async def create_database(request: CreateDatabaseRequest):
    """
    Create a new DuckDB database.

    Args:
        request: Create database request

    Returns:
        Path to the database file
    """
    try:
        db_path = duckdb_service.create_database(request.db_name)
        return {"db_path": db_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating database: {str(e)}")

@router.delete("/databases", response_model=Dict[str, str])
async def delete_database(request: DeleteDatabaseRequest):
    """
    Delete a DuckDB database.

    Args:
        request: Delete database request

    Returns:
        Success message
    """
    try:
        success = duckdb_service.delete_database(request.db_path)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete database")

        return {"message": f"Database {request.db_path} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting database: {str(e)}")

@router.post("/connect", response_model=Dict[str, str])
async def connect_to_database(request: ConnectToDatabaseRequest):
    """
    Connect to a database.

    Args:
        request: Connect to database request

    Returns:
        Success message
    """
    try:
        success = False

        if request.db_type == DatabaseType.POSTGRES:
            success = duckdb_service.connect_to_postgres(request.connection_string, request.db_path)
        elif request.db_type == DatabaseType.MYSQL:
            success = duckdb_service.connect_to_mysql(request.connection_string, request.db_path)
        elif request.db_type == DatabaseType.SQLITE:
            success = duckdb_service.connect_to_sqlite(request.connection_string, request.db_path)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported database type: {request.db_type}")

        if not success:
            raise HTTPException(status_code=500, detail=f"Failed to connect to {request.db_type} database")

        return {"message": f"Connected to {request.db_type} database successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to database: {str(e)}")

@router.post("/spatial/query", response_model=Dict[str, Any])
async def spatial_query(request: SpatialQueryRequest):
    """
    Execute a spatial query.

    Args:
        request: Spatial query request

    Returns:
        Query results as GeoJSON
    """
    try:
        gdf = duckdb_service.spatial_query(request.query, request.db_path)

        # Convert to GeoJSON
        geojson = gdf.to_json()

        return json.loads(geojson)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing spatial query: {str(e)}")

@router.post("/spatial/reproject", response_model=Dict[str, str])
async def reproject_geometry(request: ReprojectGeometryRequest):
    """
    Reproject a geometry column.

    Args:
        request: Reproject geometry request

    Returns:
        Success message
    """
    try:
        success = duckdb_service.reproject_geometry(
            request.table_name,
            request.geometry_column,
            request.source_srid,
            request.target_srid,
            request.db_path
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to reproject geometry")

        return {"message": f"Geometry column {request.geometry_column} reprojected successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reprojecting geometry: {str(e)}")

@router.post("/spatial/to-postgis", response_model=Dict[str, str])
async def convert_to_postgis(request: ConvertToPostGISRequest):
    """
    Convert a table to PostGIS SQL.

    Args:
        request: Convert to PostGIS request

    Returns:
        PostGIS SQL
    """
    try:
        sql = duckdb_service.convert_to_postgis(
            request.table_name,
            request.geometry_column,
            request.srid,
            request.db_path
        )

        return {"sql": sql}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting to PostGIS: {str(e)}")

@router.post("/spatial/to-postgis/download", response_class=FileResponse)
async def convert_to_postgis_and_download(
    table_name: str = Form(...),
    geometry_column: str = Form(...),
    srid: int = Form(...),
    db_path: Optional[str] = Form(None)
):
    """
    Convert a table to PostGIS SQL and download it.

    Args:
        table_name: Name of the table
        geometry_column: Name of the geometry column
        srid: SRID of the geometry
        db_path: Path to the database file (optional)

    Returns:
        PostGIS SQL file for download
    """
    try:
        # Convert to PostGIS SQL
        sql = duckdb_service.convert_to_postgis(
            table_name,
            geometry_column,
            srid,
            db_path
        )

        # Create a temporary file
        output_dir = os.path.join(duckdb_config.data_dir, 'exports')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{table_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.sql")

        # Write the SQL to the file
        with open(output_path, 'w') as f:
            f.write(sql)

        # Return the file for download
        return FileResponse(
            path=output_path,
            filename=os.path.basename(output_path),
            media_type="application/sql"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting to PostGIS: {str(e)}")
