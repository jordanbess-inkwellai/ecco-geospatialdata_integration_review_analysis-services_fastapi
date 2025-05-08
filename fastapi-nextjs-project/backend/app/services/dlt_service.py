import os
import json
import logging
from typing import Dict, List, Any, Optional, Union
import asyncio
from datetime import datetime

# Import DLT
import dlt
from dlt.common.typing import TDataItem, TDataItems
from dlt.common.configuration import configure_source
from dlt.common.destination import Destination
from dlt.common.schema import Schema
from dlt.common.pipeline import Pipeline

logger = logging.getLogger(__name__)

class DLTService:
    """
    Service for data loading using DLT (Data Load Tool)
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the DLT Service
        
        Args:
            config_path: Optional path to DLT configuration file
        """
        self.config_path = config_path or os.environ.get("DLT_CONFIG_PATH")
        self.pipelines: Dict[str, Pipeline] = {}
    
    async def create_pipeline(
        self, 
        pipeline_name: str, 
        destination: Union[str, Dict[str, Any], Destination],
        dataset_name: Optional[str] = None,
        full_refresh: bool = False,
        progress_bar: bool = True
    ) -> Dict[str, Any]:
        """
        Create a new DLT pipeline
        
        Args:
            pipeline_name: Name of the pipeline
            destination: Destination configuration or name
            dataset_name: Optional dataset name
            full_refresh: Whether to perform a full refresh
            progress_bar: Whether to show a progress bar
            
        Returns:
            Pipeline information
        """
        try:
            # Create the pipeline
            pipeline = dlt.pipeline(
                pipeline_name=pipeline_name,
                destination=destination,
                dataset_name=dataset_name,
                full_refresh=full_refresh,
                progress_bar=progress_bar
            )
            
            # Store the pipeline
            self.pipelines[pipeline_name] = pipeline
            
            return {
                "pipeline_name": pipeline_name,
                "destination": str(destination),
                "dataset_name": dataset_name,
                "status": "created"
            }
        except Exception as e:
            logger.error(f"Error creating pipeline {pipeline_name}: {str(e)}")
            raise
    
    async def run_pipeline(
        self,
        pipeline_name: str,
        data_source: Any,
        source_name: Optional[str] = None,
        write_disposition: str = "merge",
        table_name: Optional[str] = None,
        schema: Optional[Schema] = None,
        primary_key: Optional[Union[str, List[str]]] = None,
        merge_key: Optional[Union[str, List[str]]] = None
    ) -> Dict[str, Any]:
        """
        Run a DLT pipeline with the given data source
        
        Args:
            pipeline_name: Name of the pipeline to run
            data_source: Data source to load (can be a generator, list, or DLT source)
            source_name: Optional name for the source
            write_disposition: How to write data (append, replace, merge)
            table_name: Optional table name
            schema: Optional schema definition
            primary_key: Optional primary key(s)
            merge_key: Optional merge key(s)
            
        Returns:
            Pipeline run information
        """
        try:
            # Get the pipeline
            pipeline = self.pipelines.get(pipeline_name)
            if not pipeline:
                raise ValueError(f"Pipeline {pipeline_name} not found. Create it first.")
            
            # Run the pipeline
            load_info = pipeline.run(
                data_source,
                source_name=source_name,
                write_disposition=write_disposition,
                table_name=table_name,
                schema=schema,
                primary_key=primary_key,
                merge_key=merge_key
            )
            
            # Convert load info to a serializable format
            result = {
                "pipeline_name": pipeline_name,
                "load_id": load_info.load_id,
                "load_package": load_info.load_package,
                "destination_name": load_info.destination_name,
                "dataset_name": load_info.dataset_name,
                "table_name": load_info.table_name,
                "status": load_info.status,
                "metrics": {
                    "inserted_rows": load_info.metrics.inserted_rows,
                    "updated_rows": load_info.metrics.updated_rows,
                    "deleted_rows": load_info.metrics.deleted_rows,
                    "schema_events": load_info.metrics.schema_events
                },
                "start_time": load_info.start_time.isoformat() if load_info.start_time else None,
                "end_time": load_info.end_time.isoformat() if load_info.end_time else None
            }
            
            return result
        except Exception as e:
            logger.error(f"Error running pipeline {pipeline_name}: {str(e)}")
            raise
    
    async def load_data_to_postgres(
        self,
        data: Union[List[Dict[str, Any]], TDataItems],
        table_name: str,
        schema_name: Optional[str] = "public",
        connection_string: Optional[str] = None,
        primary_key: Optional[Union[str, List[str]]] = None,
        write_disposition: str = "merge"
    ) -> Dict[str, Any]:
        """
        Load data directly to PostgreSQL
        
        Args:
            data: Data to load
            table_name: Target table name
            schema_name: PostgreSQL schema name
            connection_string: PostgreSQL connection string
            primary_key: Primary key(s) for the table
            write_disposition: How to write data (append, replace, merge)
            
        Returns:
            Load information
        """
        try:
            # Use environment variable if connection string not provided
            if not connection_string:
                connection_string = os.environ.get("POSTGRES_CONNECTION_STRING")
                if not connection_string:
                    raise ValueError("PostgreSQL connection string not provided")
            
            # Create a pipeline for PostgreSQL
            pipeline_name = f"postgres_{table_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Configure the destination
            postgres_destination = {
                "type": "postgres",
                "connection_string": connection_string,
                "schema": schema_name
            }
            
            # Create and run the pipeline
            await self.create_pipeline(
                pipeline_name=pipeline_name,
                destination=postgres_destination,
                dataset_name=schema_name
            )
            
            result = await self.run_pipeline(
                pipeline_name=pipeline_name,
                data_source=data,
                table_name=table_name,
                primary_key=primary_key,
                write_disposition=write_disposition
            )
            
            return result
        except Exception as e:
            logger.error(f"Error loading data to PostgreSQL table {table_name}: {str(e)}")
            raise
    
    async def load_data_to_duckdb(
        self,
        data: Union[List[Dict[str, Any]], TDataItems],
        table_name: str,
        database_path: Optional[str] = None,
        primary_key: Optional[Union[str, List[str]]] = None,
        write_disposition: str = "merge"
    ) -> Dict[str, Any]:
        """
        Load data directly to DuckDB
        
        Args:
            data: Data to load
            table_name: Target table name
            database_path: Path to DuckDB database file
            primary_key: Primary key(s) for the table
            write_disposition: How to write data (append, replace, merge)
            
        Returns:
            Load information
        """
        try:
            # Use default path if not provided
            if not database_path:
                database_path = os.environ.get("DUCKDB_PATH", "data/analytics.duckdb")
            
            # Create a pipeline for DuckDB
            pipeline_name = f"duckdb_{table_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Configure the destination
            duckdb_destination = {
                "type": "duckdb",
                "database": database_path
            }
            
            # Create and run the pipeline
            await self.create_pipeline(
                pipeline_name=pipeline_name,
                destination=duckdb_destination
            )
            
            result = await self.run_pipeline(
                pipeline_name=pipeline_name,
                data_source=data,
                table_name=table_name,
                primary_key=primary_key,
                write_disposition=write_disposition
            )
            
            return result
        except Exception as e:
            logger.error(f"Error loading data to DuckDB table {table_name}: {str(e)}")
            raise
    
    async def load_data_to_parquet(
        self,
        data: Union[List[Dict[str, Any]], TDataItems],
        file_name: str,
        directory: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Load data to Parquet files
        
        Args:
            data: Data to load
            file_name: Base name for the Parquet file
            directory: Directory to store Parquet files
            
        Returns:
            Load information
        """
        try:
            # Use default directory if not provided
            if not directory:
                directory = os.environ.get("PARQUET_DIRECTORY", "data/parquet")
            
            # Ensure directory exists
            os.makedirs(directory, exist_ok=True)
            
            # Create a pipeline for Parquet
            pipeline_name = f"parquet_{file_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Configure the destination
            parquet_destination = {
                "type": "filesystem",
                "format": "parquet",
                "path": directory
            }
            
            # Create and run the pipeline
            await self.create_pipeline(
                pipeline_name=pipeline_name,
                destination=parquet_destination
            )
            
            result = await self.run_pipeline(
                pipeline_name=pipeline_name,
                data_source=data,
                table_name=file_name,
                write_disposition="replace"  # Always replace for files
            )
            
            return result
        except Exception as e:
            logger.error(f"Error loading data to Parquet file {file_name}: {str(e)}")
            raise
    
    async def extract_from_api(
        self,
        api_source: str,
        credentials: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        destination_type: str = "postgres",
        destination_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract data from a supported API source and load to destination
        
        Args:
            api_source: Name of the API source (e.g., 'github', 'stripe', etc.)
            credentials: API credentials
            config: Source configuration
            destination_type: Type of destination (postgres, duckdb, etc.)
            destination_config: Destination configuration
            
        Returns:
            Pipeline run information
        """
        try:
            # Configure the source
            source_config = configure_source(
                api_source,
                credentials=credentials,
                config=config
            )
            
            # Get the source
            source = getattr(dlt.sources, api_source)
            if not source:
                raise ValueError(f"API source {api_source} not supported by DLT")
            
            # Create source instance
            source_instance = source(**source_config)
            
            # Configure destination
            if destination_type == "postgres":
                dest_config = destination_config or {}
                connection_string = dest_config.get("connection_string") or os.environ.get("POSTGRES_CONNECTION_STRING")
                schema = dest_config.get("schema", "public")
                
                destination = {
                    "type": "postgres",
                    "connection_string": connection_string,
                    "schema": schema
                }
            elif destination_type == "duckdb":
                dest_config = destination_config or {}
                database_path = dest_config.get("database_path") or os.environ.get("DUCKDB_PATH", "data/analytics.duckdb")
                
                destination = {
                    "type": "duckdb",
                    "database": database_path
                }
            else:
                raise ValueError(f"Destination type {destination_type} not supported")
            
            # Create pipeline
            pipeline_name = f"{api_source}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            await self.create_pipeline(
                pipeline_name=pipeline_name,
                destination=destination
            )
            
            # Run pipeline
            result = await self.run_pipeline(
                pipeline_name=pipeline_name,
                data_source=source_instance
            )
            
            return result
        except Exception as e:
            logger.error(f"Error extracting data from {api_source}: {str(e)}")
            raise
    
    async def extract_from_database(
        self,
        source_connection_string: str,
        query: str,
        destination_type: str = "postgres",
        destination_config: Optional[Dict[str, Any]] = None,
        table_name: Optional[str] = None,
        primary_key: Optional[Union[str, List[str]]] = None,
        write_disposition: str = "merge"
    ) -> Dict[str, Any]:
        """
        Extract data from a database using SQL and load to destination
        
        Args:
            source_connection_string: Connection string for source database
            query: SQL query to extract data
            destination_type: Type of destination (postgres, duckdb, etc.)
            destination_config: Destination configuration
            table_name: Target table name
            primary_key: Primary key(s) for the table
            write_disposition: How to write data (append, replace, merge)
            
        Returns:
            Pipeline run information
        """
        try:
            # Configure the SQL source
            sql_source = dlt.sources.sql(
                connection_string=source_connection_string,
                query=query
            )
            
            # Configure destination
            if destination_type == "postgres":
                dest_config = destination_config or {}
                connection_string = dest_config.get("connection_string") or os.environ.get("POSTGRES_CONNECTION_STRING")
                schema = dest_config.get("schema", "public")
                
                destination = {
                    "type": "postgres",
                    "connection_string": connection_string,
                    "schema": schema
                }
            elif destination_type == "duckdb":
                dest_config = destination_config or {}
                database_path = dest_config.get("database_path") or os.environ.get("DUCKDB_PATH", "data/analytics.duckdb")
                
                destination = {
                    "type": "duckdb",
                    "database": database_path
                }
            else:
                raise ValueError(f"Destination type {destination_type} not supported")
            
            # Create pipeline
            source_type = source_connection_string.split("://")[0] if "://" in source_connection_string else "database"
            pipeline_name = f"{source_type}_extract_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            await self.create_pipeline(
                pipeline_name=pipeline_name,
                destination=destination
            )
            
            # Run pipeline
            result = await self.run_pipeline(
                pipeline_name=pipeline_name,
                data_source=sql_source,
                table_name=table_name,
                primary_key=primary_key,
                write_disposition=write_disposition
            )
            
            return result
        except Exception as e:
            logger.error(f"Error extracting data from database: {str(e)}")
            raise
