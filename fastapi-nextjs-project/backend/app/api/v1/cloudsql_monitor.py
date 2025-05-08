from fastapi import APIRouter, Depends, HTTPException, Body, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
import logging
import json
from datetime import datetime

from app.core.database import get_db
from app.services.cloudsql_monitor_service import CloudSQLMonitorService
from app.core.security import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize Cloud SQL Monitor Service
cloudsql_monitor_service = CloudSQLMonitorService()


@router.post("/instances/status")
async def get_instance_status(
    instance_config: Dict[str, Any] = Body(...),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get status of a Cloud SQL instance
    
    Body:
    ```
    {
        "instance_connection_name": "project:region:instance",
        "database": "database_name",
        "user": "username",
        "password": "password",
        "ip_type": "PUBLIC" or "PRIVATE" (optional, default: "PUBLIC")
    }
    ```
    """
    try:
        # Validate required fields
        required_fields = ["instance_connection_name", "database", "user", "password"]
        for field in required_fields:
            if field not in instance_config:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Get instance status
        status = await cloudsql_monitor_service.get_instance_status(instance_config)
        return status
    except Exception as e:
        logger.error(f"Error getting instance status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting instance status: {str(e)}")


@router.post("/instances/metrics")
async def get_performance_metrics(
    instance_config: Dict[str, Any] = Body(...),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get performance metrics for a Cloud SQL instance
    
    Body:
    ```
    {
        "instance_connection_name": "project:region:instance",
        "database": "database_name",
        "user": "username",
        "password": "password",
        "ip_type": "PUBLIC" or "PRIVATE" (optional, default: "PUBLIC")
    }
    ```
    """
    try:
        # Validate required fields
        required_fields = ["instance_connection_name", "database", "user", "password"]
        for field in required_fields:
            if field not in instance_config:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Get performance metrics
        metrics = await cloudsql_monitor_service.get_performance_metrics(instance_config)
        return metrics
    except Exception as e:
        logger.error(f"Error getting performance metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting performance metrics: {str(e)}")


@router.post("/instances/table-sizes")
async def get_table_sizes(
    instance_config: Dict[str, Any] = Body(...),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get table sizes for a Cloud SQL instance
    
    Body:
    ```
    {
        "instance_connection_name": "project:region:instance",
        "database": "database_name",
        "user": "username",
        "password": "password",
        "ip_type": "PUBLIC" or "PRIVATE" (optional, default: "PUBLIC")
    }
    ```
    """
    try:
        # Validate required fields
        required_fields = ["instance_connection_name", "database", "user", "password"]
        for field in required_fields:
            if field not in instance_config:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Get table sizes
        table_sizes = await cloudsql_monitor_service.get_table_sizes(instance_config)
        return table_sizes
    except Exception as e:
        logger.error(f"Error getting table sizes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting table sizes: {str(e)}")


@router.post("/instances/postgis-stats")
async def get_postgis_stats(
    instance_config: Dict[str, Any] = Body(...),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get PostGIS statistics for a Cloud SQL instance
    
    Body:
    ```
    {
        "instance_connection_name": "project:region:instance",
        "database": "database_name",
        "user": "username",
        "password": "password",
        "ip_type": "PUBLIC" or "PRIVATE" (optional, default: "PUBLIC")
    }
    ```
    """
    try:
        # Validate required fields
        required_fields = ["instance_connection_name", "database", "user", "password"]
        for field in required_fields:
            if field not in instance_config:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Get PostGIS statistics
        postgis_stats = await cloudsql_monitor_service.get_postgis_stats(instance_config)
        return postgis_stats
    except Exception as e:
        logger.error(f"Error getting PostGIS statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting PostGIS statistics: {str(e)}")


@router.post("/instances/custom-query")
async def run_custom_query(
    instance_config: Dict[str, Any] = Body(...),
    query: str = Body(...),
    params: Optional[List] = Body(None),
    current_user: Dict = Depends(get_current_user)
):
    """
    Run a custom query on a Cloud SQL instance
    
    Body:
    ```
    {
        "instance_config": {
            "instance_connection_name": "project:region:instance",
            "database": "database_name",
            "user": "username",
            "password": "password",
            "ip_type": "PUBLIC" or "PRIVATE" (optional, default: "PUBLIC")
        },
        "query": "SELECT * FROM table WHERE column = %s",
        "params": ["value"]
    }
    ```
    """
    try:
        # Validate required fields
        required_fields = ["instance_connection_name", "database", "user", "password"]
        for field in required_fields:
            if field not in instance_config:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Run custom query
        results = await cloudsql_monitor_service.run_custom_query(instance_config, query, params)
        return results
    except Exception as e:
        logger.error(f"Error running custom query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error running custom query: {str(e)}")


@router.post("/instances/save-config")
async def save_instance_config(
    instance_config: Dict[str, Any] = Body(...),
    name: str = Body(...),
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Save a Cloud SQL instance configuration
    
    Body:
    ```
    {
        "name": "My Database",
        "instance_config": {
            "instance_connection_name": "project:region:instance",
            "database": "database_name",
            "user": "username",
            "password": "password",
            "ip_type": "PUBLIC" or "PRIVATE" (optional, default: "PUBLIC")
        }
    }
    ```
    """
    try:
        # Validate required fields
        required_fields = ["instance_connection_name", "database", "user", "password"]
        for field in required_fields:
            if field not in instance_config:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Save instance configuration
        # In a real implementation, this would save to a database
        # For this example, we'll just return success
        return {
            "status": "success",
            "message": f"Instance configuration saved: {name}",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error saving instance configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving instance configuration: {str(e)}")


@router.get("/instances/configs")
async def get_instance_configs(
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get saved Cloud SQL instance configurations
    """
    try:
        # In a real implementation, this would fetch from a database
        # For this example, we'll return mock data
        return [
            {
                "id": 1,
                "name": "Production Database",
                "instance_connection_name": "project:region:instance1",
                "database": "production",
                "user": "user1",
                "password": "********",  # Passwords should be masked
                "ip_type": "PRIVATE"
            },
            {
                "id": 2,
                "name": "Development Database",
                "instance_connection_name": "project:region:instance2",
                "database": "development",
                "user": "user2",
                "password": "********",  # Passwords should be masked
                "ip_type": "PUBLIC"
            }
        ]
    except Exception as e:
        logger.error(f"Error getting instance configurations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting instance configurations: {str(e)}")


@router.on_event("shutdown")
async def shutdown_event():
    """Close all connections on shutdown"""
    await cloudsql_monitor_service.close_connections()
