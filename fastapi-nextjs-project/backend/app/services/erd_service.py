import os
import tempfile
from typing import List, Dict, Any, Optional
from sqlalchemy import MetaData, create_engine, inspect
from sqlalchemy.engine import Engine
from eralchemy2 import render_er
from sqlalchemy_schemadisplay import create_schema_graph
import networkx as nx
import json
import logging

from app.core.config import settings
from app.models.data_source import DataSource, DataSourceTable

logger = logging.getLogger(__name__)


class ERDService:
    """Service for generating Entity-Relationship Diagrams"""
    
    @staticmethod
    async def generate_erd_from_datasource(
        data_source_id: int,
        output_format: str = "png",
        include_tables: Optional[List[str]] = None,
        exclude_tables: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate ERD from a data source
        
        Args:
            data_source_id: ID of the data source
            output_format: Output format (png, pdf, dot, etc.)
            include_tables: List of tables to include (if None, include all)
            exclude_tables: List of tables to exclude
            
        Returns:
            Dictionary with file path and metadata
        """
        try:
            # Get data source from database
            # This is a placeholder - in a real implementation, you'd fetch from the database
            data_source = {
                "id": data_source_id,
                "name": "Sample Database",
                "connection_string": "postgresql://user:password@localhost:5432/database"
            }
            
            # Create engine
            engine = create_engine(data_source["connection_string"])
            
            # Generate ERD
            with tempfile.NamedTemporaryFile(suffix=f'.{output_format}', delete=False) as tmp:
                output_path = tmp.name
            
            # Use eralchemy2 to generate the ERD
            render_er(engine, output_path, include_tables=include_tables, exclude_tables=exclude_tables)
            
            return {
                "file_path": output_path,
                "format": output_format,
                "data_source_id": data_source_id,
                "data_source_name": data_source["name"]
            }
        
        except Exception as e:
            logger.error(f"Error generating ERD: {str(e)}")
            raise
    
    @staticmethod
    async def generate_erd_from_models(
        output_format: str = "png",
        include_models: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate ERD from SQLAlchemy models
        
        Args:
            output_format: Output format (png, pdf, dot, etc.)
            include_models: List of model names to include (if None, include all)
            
        Returns:
            Dictionary with file path and metadata
        """
        try:
            from app.models.base import Base
            
            # Generate ERD
            with tempfile.NamedTemporaryFile(suffix=f'.{output_format}', delete=False) as tmp:
                output_path = tmp.name
            
            # Create graph
            graph = create_schema_graph(
                metadata=Base.metadata,
                show_datatypes=True,
                show_indexes=True,
                rankdir='LR',  # Left to right
                concentrate=False
            )
            
            # Save graph
            graph.write_png(output_path)
            
            return {
                "file_path": output_path,
                "format": output_format,
                "source": "sqlalchemy_models"
            }
        
        except Exception as e:
            logger.error(f"Error generating ERD from models: {str(e)}")
            raise
    
    @staticmethod
    async def get_schema_as_json(
        data_source_id: int,
        include_tables: Optional[List[str]] = None,
        exclude_tables: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get database schema as JSON for frontend visualization
        
        Args:
            data_source_id: ID of the data source
            include_tables: List of tables to include (if None, include all)
            exclude_tables: List of tables to exclude
            
        Returns:
            Dictionary with nodes and edges for visualization
        """
        try:
            # Get data source from database
            # This is a placeholder - in a real implementation, you'd fetch from the database
            data_source = {
                "id": data_source_id,
                "name": "Sample Database",
                "connection_string": "postgresql://user:password@localhost:5432/database"
            }
            
            # Create engine
            engine = create_engine(data_source["connection_string"])
            
            # Get schema information
            inspector = inspect(engine)
            schema_name = None  # Use default schema
            
            # Get all tables
            tables = inspector.get_table_names(schema=schema_name)
            
            # Filter tables if needed
            if include_tables:
                tables = [t for t in tables if t in include_tables]
            if exclude_tables:
                tables = [t for t in tables if t not in exclude_tables]
            
            # Build nodes and edges
            nodes = []
            edges = []
            
            for table_name in tables:
                # Get columns
                columns = inspector.get_columns(table_name, schema=schema_name)
                column_info = [
                    {
                        "name": col["name"],
                        "type": str(col["type"]),
                        "nullable": col.get("nullable", True),
                        "default": str(col.get("default", ""))
                    }
                    for col in columns
                ]
                
                # Get primary keys
                pk_constraint = inspector.get_pk_constraint(table_name, schema=schema_name)
                primary_keys = pk_constraint.get("constrained_columns", [])
                
                # Add node for table
                nodes.append({
                    "id": table_name,
                    "type": "table",
                    "data": {
                        "label": table_name,
                        "columns": column_info,
                        "primary_keys": primary_keys
                    }
                })
                
                # Get foreign keys
                fk_constraints = inspector.get_foreign_keys(table_name, schema=schema_name)
                for fk in fk_constraints:
                    referred_table = fk.get("referred_table")
                    if referred_table in tables:  # Only add edge if both tables are included
                        for i, col in enumerate(fk.get("constrained_columns", [])):
                            referred_col = fk.get("referred_columns", [])[i] if i < len(fk.get("referred_columns", [])) else None
                            if referred_col:
                                edges.append({
                                    "id": f"{table_name}.{col}->{referred_table}.{referred_col}",
                                    "source": table_name,
                                    "target": referred_table,
                                    "sourceHandle": col,
                                    "targetHandle": referred_col,
                                    "data": {
                                        "label": fk.get("name", ""),
                                        "sourceColumn": col,
                                        "targetColumn": referred_col
                                    }
                                })
            
            return {
                "nodes": nodes,
                "edges": edges,
                "data_source_id": data_source_id,
                "data_source_name": data_source["name"]
            }
        
        except Exception as e:
            logger.error(f"Error getting schema as JSON: {str(e)}")
            raise
