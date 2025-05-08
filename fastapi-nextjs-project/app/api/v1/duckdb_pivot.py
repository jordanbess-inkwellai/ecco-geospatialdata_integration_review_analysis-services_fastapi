from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any, Optional
import json

from app.core.duckdb_config import duckdb_config
from app.services.duckdb_service import duckdb_service
from app.schemas.duckdb_pivot_schemas import PivotTableRequest, PivotTableResponse

router = APIRouter(tags=["DuckDB Pivot Table"], prefix="/duckdb/pivot")

@router.post("/table", response_model=PivotTableResponse)
async def create_pivot_table(request: PivotTableRequest):
    """
    Create a pivot table from a query result.
    
    Args:
        request: Pivot table request
        
    Returns:
        Pivot table data and column names
    """
    try:
        # Get a DuckDB connection
        conn = duckdb_service.get_connection(request.db_path)
        
        # Check if the pivot_table extension is loaded
        if "pivot_table" not in duckdb_service.extensions:
            raise HTTPException(status_code=500, detail="Pivot table extension is not loaded")
        
        # Prepare the value column parameter
        if isinstance(request.value_column, str):
            value_param = f"'{request.value_column}'"
        else:
            # Convert dictionary to JSON string
            value_param = json.dumps(request.value_column)
        
        # Prepare the column names parameter
        column_names_param = ""
        if request.column_names:
            column_names_param = f", {json.dumps(request.column_names)}"
        
        # Create the pivot table query
        pivot_query = f"""
            SELECT * FROM pivot(
                ({request.query}),
                '{request.pivot_column}',
                '{request.row_identifier}',
                {value_param}{column_names_param}
            )
        """
        
        # Execute the query
        result = conn.execute(pivot_query).fetchdf()
        
        # Convert to list of dictionaries
        data = result.to_dict(orient="records")
        
        # Get column names
        columns = list(result.columns)
        
        return {
            "data": data,
            "columns": columns
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating pivot table: {str(e)}")

@router.post("/table/preview", response_model=PivotTableResponse)
async def preview_pivot_table(request: PivotTableRequest):
    """
    Preview a pivot table from a query result with a limit of 10 rows.
    
    Args:
        request: Pivot table request
        
    Returns:
        Pivot table data and column names (limited to 10 rows)
    """
    try:
        # Modify the query to limit the results
        if "LIMIT" not in request.query.upper():
            request.query = f"SELECT * FROM ({request.query}) LIMIT 10"
        
        # Call the create_pivot_table function
        return await create_pivot_table(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error previewing pivot table: {str(e)}")

@router.get("/status", response_model=Dict[str, Any])
async def get_pivot_table_status():
    """
    Get the status of the pivot table extension.
    
    Returns:
        Status information
    """
    try:
        # Get a DuckDB connection
        conn = duckdb_service.get_connection()
        
        # Check if the pivot_table extension is loaded
        is_loaded = "pivot_table" in duckdb_service.extensions
        
        # Get the version of the pivot_table extension if loaded
        version = None
        if is_loaded:
            try:
                version_result = conn.execute("SELECT pivot_table_version()").fetchone()
                if version_result:
                    version = version_result[0]
            except:
                pass
        
        return {
            "loaded": is_loaded,
            "version": version,
            "available": "pivot_table" in duckdb_config.extensions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting pivot table status: {str(e)}")
