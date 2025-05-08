from fastapi import APIRouter, Depends, HTTPException, Body, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
import logging
import json
from datetime import datetime

from app.core.database import get_db
from app.services.dlt_kestra_service import DLTKestraService
from app.services.kestra_service import KestraService
from app.core.security import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize services
kestra_service = KestraService()
dlt_kestra_service = DLTKestraService(kestra_service)


@router.post("/workflows/generate")
async def generate_dlt_workflow(
    workflow_name: str = Body(...),
    source_type: str = Body(...),
    destination_type: str = Body(...),
    source_config: Dict[str, Any] = Body(...),
    destination_config: Dict[str, Any] = Body(...),
    schedule: Optional[str] = Body(None),
    namespace: str = Body("default"),
    description: Optional[str] = Body(None),
    tags: Optional[List[str]] = Body(None),
    python_version: str = Body("3.10"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Generate a Kestra workflow YAML for a DLT pipeline
    """
    try:
        workflow = await dlt_kestra_service.generate_dlt_workflow(
            workflow_name=workflow_name,
            source_type=source_type,
            destination_type=destination_type,
            source_config=source_config,
            destination_config=destination_config,
            schedule=schedule,
            namespace=namespace,
            description=description,
            tags=tags,
            python_version=python_version
        )
        return workflow
    except Exception as e:
        logger.error(f"Error generating DLT workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating DLT workflow: {str(e)}")


@router.post("/workflows/create")
async def create_dlt_workflow(
    workflow_name: str = Body(...),
    source_type: str = Body(...),
    destination_type: str = Body(...),
    source_config: Dict[str, Any] = Body(...),
    destination_config: Dict[str, Any] = Body(...),
    schedule: Optional[str] = Body(None),
    namespace: str = Body("default"),
    description: Optional[str] = Body(None),
    tags: Optional[List[str]] = Body(None),
    python_version: str = Body("3.10"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Create a DLT workflow in Kestra
    """
    try:
        workflow = await dlt_kestra_service.create_dlt_workflow(
            workflow_name=workflow_name,
            source_type=source_type,
            destination_type=destination_type,
            source_config=source_config,
            destination_config=destination_config,
            schedule=schedule,
            namespace=namespace,
            description=description,
            tags=tags,
            python_version=python_version
        )
        return workflow
    except Exception as e:
        logger.error(f"Error creating DLT workflow in Kestra: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating DLT workflow in Kestra: {str(e)}")


@router.post("/workflows/run")
async def run_dlt_workflow(
    workflow_id: str = Body(...),
    namespace: str = Body("default"),
    source_credentials: Dict[str, Any] = Body(...),
    destination_credentials: Dict[str, Any] = Body(...),
    slack_webhook_url: Optional[str] = Body(None),
    current_user: Dict = Depends(get_current_user)
):
    """
    Run a DLT workflow in Kestra
    """
    try:
        execution = await dlt_kestra_service.run_dlt_workflow(
            workflow_id=workflow_id,
            namespace=namespace,
            source_credentials=source_credentials,
            destination_credentials=destination_credentials,
            slack_webhook_url=slack_webhook_url
        )
        return execution
    except Exception as e:
        logger.error(f"Error running DLT workflow in Kestra: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error running DLT workflow in Kestra: {str(e)}")


@router.post("/templates/postgres-to-postgres")
async def create_postgres_to_postgres_workflow(
    workflow_name: str = Body(...),
    source_connection: str = Body(...),
    source_query: str = Body(...),
    destination_connection: str = Body(...),
    destination_schema: str = Body("public"),
    destination_table: str = Body(...),
    primary_key: Optional[str] = Body(None),
    schedule: Optional[str] = Body(None),
    namespace: str = Body("default"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Create a workflow for Postgres to Postgres data transfer
    """
    try:
        # Configure source
        source_config = {
            "connection_string": source_connection,
            "query": source_query
        }
        
        # Configure destination
        destination_config = {
            "connection_string": destination_connection,
            "schema": destination_schema,
            "table_name": destination_table,
            "primary_key": primary_key,
            "write_disposition": "merge"
        }
        
        # Create the workflow
        workflow = await dlt_kestra_service.create_dlt_workflow(
            workflow_name=workflow_name,
            source_type="postgres",
            destination_type="postgres",
            source_config=source_config,
            destination_config=destination_config,
            schedule=schedule,
            namespace=namespace,
            description=f"Transfer data from PostgreSQL to PostgreSQL using DLT",
            tags=["postgres", "dlt", "data-transfer"]
        )
        
        return workflow
    except Exception as e:
        logger.error(f"Error creating Postgres to Postgres workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating workflow: {str(e)}")


@router.post("/templates/api-to-duckdb")
async def create_api_to_duckdb_workflow(
    workflow_name: str = Body(...),
    api_url: str = Body(...),
    api_method: str = Body("GET"),
    api_headers: Optional[Dict[str, str]] = Body(None),
    api_params: Optional[Dict[str, Any]] = Body(None),
    duckdb_path: str = Body("data/analytics.duckdb"),
    table_name: str = Body(...),
    schedule: Optional[str] = Body(None),
    namespace: str = Body("default"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Create a workflow for API to DuckDB data transfer
    """
    try:
        # Configure source
        source_config = {
            "url": api_url,
            "method": api_method,
            "headers": api_headers or {},
            "params": api_params or {}
        }
        
        # Configure destination
        destination_config = {
            "database": duckdb_path,
            "table_name": table_name,
            "write_disposition": "replace"
        }
        
        # Create the workflow
        workflow = await dlt_kestra_service.create_dlt_workflow(
            workflow_name=workflow_name,
            source_type="api",
            destination_type="duckdb",
            source_config=source_config,
            destination_config=destination_config,
            schedule=schedule,
            namespace=namespace,
            description=f"Load data from API to DuckDB using DLT",
            tags=["api", "duckdb", "dlt"]
        )
        
        return workflow
    except Exception as e:
        logger.error(f"Error creating API to DuckDB workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating workflow: {str(e)}")


@router.post("/templates/github-to-postgres")
async def create_github_to_postgres_workflow(
    workflow_name: str = Body(...),
    github_token: str = Body(...),
    github_repo: str = Body(...),
    destination_connection: str = Body(...),
    destination_schema: str = Body("public"),
    schedule: Optional[str] = Body(None),
    namespace: str = Body("default"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Create a workflow for GitHub to Postgres data transfer
    """
    try:
        # Configure source
        source_config = {
            "access_token": github_token,
            "config": {
                "repository": github_repo
            }
        }
        
        # Configure destination
        destination_config = {
            "connection_string": destination_connection,
            "schema": destination_schema,
            "write_disposition": "merge"
        }
        
        # Create the workflow
        workflow = await dlt_kestra_service.create_dlt_workflow(
            workflow_name=workflow_name,
            source_type="github",
            destination_type="postgres",
            source_config=source_config,
            destination_config=destination_config,
            schedule=schedule,
            namespace=namespace,
            description=f"Load GitHub data to PostgreSQL using DLT",
            tags=["github", "postgres", "dlt"]
        )
        
        return workflow
    except Exception as e:
        logger.error(f"Error creating GitHub to Postgres workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating workflow: {str(e)}")


@router.post("/templates/postgres-to-parquet")
async def create_postgres_to_parquet_workflow(
    workflow_name: str = Body(...),
    source_connection: str = Body(...),
    source_query: str = Body(...),
    output_directory: str = Body("data/parquet"),
    file_name: str = Body(...),
    schedule: Optional[str] = Body(None),
    namespace: str = Body("default"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Create a workflow for Postgres to Parquet data export
    """
    try:
        # Configure source
        source_config = {
            "connection_string": source_connection,
            "query": source_query
        }
        
        # Configure destination
        destination_config = {
            "type": "filesystem",
            "format": "parquet",
            "path": output_directory,
            "table_name": file_name
        }
        
        # Create the workflow
        workflow = await dlt_kestra_service.create_dlt_workflow(
            workflow_name=workflow_name,
            source_type="postgres",
            destination_type="filesystem",
            source_config=source_config,
            destination_config=destination_config,
            schedule=schedule,
            namespace=namespace,
            description=f"Export PostgreSQL data to Parquet files using DLT",
            tags=["postgres", "parquet", "dlt", "export"]
        )
        
        return workflow
    except Exception as e:
        logger.error(f"Error creating Postgres to Parquet workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating workflow: {str(e)}")


@router.get("/source-types")
async def get_source_types(
    current_user: Dict = Depends(get_current_user)
):
    """
    Get available DLT source types
    """
    source_types = [
        {
            "id": "postgres",
            "name": "PostgreSQL",
            "description": "Extract data from PostgreSQL database",
            "config_schema": {
                "connection_string": "string",
                "query": "string"
            }
        },
        {
            "id": "mysql",
            "name": "MySQL",
            "description": "Extract data from MySQL database",
            "config_schema": {
                "connection_string": "string",
                "query": "string"
            }
        },
        {
            "id": "api",
            "name": "REST API",
            "description": "Extract data from a REST API",
            "config_schema": {
                "url": "string",
                "method": "string",
                "headers": "object",
                "params": "object"
            }
        },
        {
            "id": "github",
            "name": "GitHub",
            "description": "Extract data from GitHub",
            "config_schema": {
                "access_token": "string",
                "config": {
                    "repository": "string"
                }
            }
        },
        {
            "id": "stripe",
            "name": "Stripe",
            "description": "Extract data from Stripe",
            "config_schema": {
                "api_key": "string"
            }
        },
        {
            "id": "google_analytics",
            "name": "Google Analytics",
            "description": "Extract data from Google Analytics",
            "config_schema": {
                "credentials": "object",
                "property_id": "string"
            }
        },
        {
            "id": "salesforce",
            "name": "Salesforce",
            "description": "Extract data from Salesforce",
            "config_schema": {
                "username": "string",
                "password": "string",
                "security_token": "string",
                "domain": "string"
            }
        }
    ]
    
    return source_types


@router.get("/destination-types")
async def get_destination_types(
    current_user: Dict = Depends(get_current_user)
):
    """
    Get available DLT destination types
    """
    destination_types = [
        {
            "id": "postgres",
            "name": "PostgreSQL",
            "description": "Load data to PostgreSQL database",
            "config_schema": {
                "connection_string": "string",
                "schema": "string"
            }
        },
        {
            "id": "bigquery",
            "name": "BigQuery",
            "description": "Load data to Google BigQuery",
            "config_schema": {
                "credentials": "object",
                "dataset": "string"
            }
        },
        {
            "id": "duckdb",
            "name": "DuckDB",
            "description": "Load data to DuckDB database",
            "config_schema": {
                "database": "string"
            }
        },
        {
            "id": "redshift",
            "name": "Redshift",
            "description": "Load data to Amazon Redshift",
            "config_schema": {
                "connection_string": "string",
                "schema": "string"
            }
        },
        {
            "id": "filesystem",
            "name": "Filesystem",
            "description": "Load data to files (Parquet, CSV, etc.)",
            "config_schema": {
                "type": "string",
                "format": "string",
                "path": "string"
            }
        }
    ]
    
    return destination_types
