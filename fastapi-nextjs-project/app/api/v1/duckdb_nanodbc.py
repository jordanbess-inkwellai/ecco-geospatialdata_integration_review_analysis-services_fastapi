from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any, Optional
import re

from app.core.duckdb_config import duckdb_config
from app.services.duckdb_service import duckdb_service
from app.schemas.duckdb_nanodbc_schemas import (
    OdbcConnectionRequest,
    OdbcQueryRequest,
    OdbcImportTableRequest,
    OdbcConnectionsResponse,
    OdbcConnectionInfo
)

router = APIRouter(tags=["DuckDB Nanodbc"], prefix="/duckdb/odbc")

@router.post("/connect", response_model=Dict[str, str])
async def connect_to_odbc(request: OdbcConnectionRequest):
    """
    Connect to an ODBC data source.
    
    Args:
        request: ODBC connection request
        
    Returns:
        Success message
    """
    try:
        # Get a DuckDB connection
        conn = duckdb_service.get_connection(request.db_path)
        
        # Check if the nanodbc extension is loaded
        if "nanodbc" not in duckdb_service.extensions:
            raise HTTPException(status_code=500, detail="Nanodbc extension is not loaded")
        
        # Connect to the ODBC data source
        conn.execute(f"ATTACH '{request.connection_string}' AS {request.name} (TYPE ODBC)")
        
        return {"message": f"Connected to ODBC data source as {request.name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to ODBC data source: {str(e)}")

@router.post("/query", response_model=List[Dict[str, Any]])
async def execute_odbc_query(request: OdbcQueryRequest):
    """
    Execute a query on an ODBC data source.
    
    Args:
        request: ODBC query request
        
    Returns:
        Query results
    """
    try:
        # Execute the query
        result = duckdb_service.execute_query(
            query=request.query,
            db_path=request.db_path,
            params=request.params
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing ODBC query: {str(e)}")

@router.post("/import", response_model=Dict[str, str])
async def import_odbc_table(request: OdbcImportTableRequest):
    """
    Import a table from an ODBC data source.
    
    Args:
        request: ODBC import table request
        
    Returns:
        Success message
    """
    try:
        # Get a DuckDB connection
        conn = duckdb_service.get_connection(request.db_path)
        
        # Create the table from the ODBC query
        conn.execute(f"CREATE TABLE {request.target_table} AS SELECT * FROM ({request.source_query})")
        
        return {"message": f"Table {request.target_table} created successfully from ODBC data source"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error importing table from ODBC data source: {str(e)}")

@router.get("/connections", response_model=OdbcConnectionsResponse)
async def list_odbc_connections():
    """
    List all ODBC connections.
    
    Returns:
        List of ODBC connections
    """
    try:
        # Get connections from configuration
        connections = []
        
        # Add predefined connections from environment variables
        for name, connection_string in duckdb_config.odbc_connections.items():
            # Mask sensitive information in the connection string
            masked_connection_string = mask_connection_string(connection_string)
            
            # Extract driver, server, and database information
            driver = extract_connection_info(connection_string, "Driver")
            server = extract_connection_info(connection_string, "Server")
            database = extract_connection_info(connection_string, "Database")
            
            connections.append({
                "name": name,
                "connection_string": masked_connection_string,
                "driver": driver,
                "server": server,
                "database": database
            })
        
        return {"connections": connections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing ODBC connections: {str(e)}")

@router.get("/status", response_model=Dict[str, Any])
async def get_nanodbc_status():
    """
    Get the status of the Nanodbc extension.
    
    Returns:
        Status information
    """
    try:
        # Get a DuckDB connection
        conn = duckdb_service.get_connection()
        
        # Check if the nanodbc extension is loaded
        is_loaded = "nanodbc" in duckdb_service.extensions
        
        # Get the version of the nanodbc extension if loaded
        version = None
        if is_loaded:
            try:
                version_result = conn.execute("SELECT nanodbc_version()").fetchone()
                if version_result:
                    version = version_result[0]
            except:
                pass
        
        # Get ODBC driver paths
        driver_paths = duckdb_config.odbc_driver_paths
        
        return {
            "loaded": is_loaded,
            "version": version,
            "available": "nanodbc" in duckdb_config.extensions,
            "driver_paths": driver_paths,
            "connections": len(duckdb_config.odbc_connections)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting Nanodbc status: {str(e)}")

def mask_connection_string(connection_string: str) -> str:
    """
    Mask sensitive information in an ODBC connection string.
    
    Args:
        connection_string: ODBC connection string
        
    Returns:
        Masked connection string
    """
    # Mask password
    masked = re.sub(r"(Pwd|Password)=([^;]*)", r"\1=********", connection_string, flags=re.IGNORECASE)
    
    # Mask other potentially sensitive information
    masked = re.sub(r"(UID|User ID)=([^;]*)", r"\1=********", masked, flags=re.IGNORECASE)
    masked = re.sub(r"(PWD|Password)=([^;]*)", r"\1=********", masked, flags=re.IGNORECASE)
    masked = re.sub(r"(Auth)=([^;]*)", r"\1=********", masked, flags=re.IGNORECASE)
    
    return masked

def extract_connection_info(connection_string: str, key: str) -> Optional[str]:
    """
    Extract information from an ODBC connection string.
    
    Args:
        connection_string: ODBC connection string
        key: Key to extract
        
    Returns:
        Extracted value or None if not found
    """
    match = re.search(f"{key}=({{[^}}]*}}|[^;]*)", connection_string, re.IGNORECASE)
    if match:
        value = match.group(1)
        # Remove curly braces if present
        if value.startswith("{") and value.endswith("}"):
            value = value[1:-1]
        return value
    return None
