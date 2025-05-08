from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Union
from enum import Enum

class OdbcConnectionRequest(BaseModel):
    """Schema for connecting to an ODBC data source."""
    
    connection_string: str = Field(..., description="ODBC connection string")
    name: str = Field(..., description="Name to use for the connection")
    db_path: Optional[str] = Field(None, description="Path to the DuckDB database file")
    
    class Config:
        schema_extra = {
            "example": {
                "connection_string": "Driver={SQL Server};Server=myserver;Database=mydatabase;Trusted_Connection=yes;",
                "name": "sqlserver",
                "db_path": None
            }
        }

class OdbcQueryRequest(BaseModel):
    """Schema for executing a query on an ODBC data source."""
    
    connection_name: str = Field(..., description="Name of the ODBC connection")
    query: str = Field(..., description="SQL query to execute")
    params: Optional[Dict[str, Any]] = Field(None, description="Query parameters")
    db_path: Optional[str] = Field(None, description="Path to the DuckDB database file")
    
    class Config:
        schema_extra = {
            "example": {
                "connection_name": "sqlserver",
                "query": "SELECT * FROM mydatabase.dbo.mytable",
                "params": None,
                "db_path": None
            }
        }

class OdbcImportTableRequest(BaseModel):
    """Schema for importing a table from an ODBC data source."""
    
    connection_name: str = Field(..., description="Name of the ODBC connection")
    source_query: str = Field(..., description="SQL query to execute on the ODBC data source")
    target_table: str = Field(..., description="Name of the table to create in DuckDB")
    db_path: Optional[str] = Field(None, description="Path to the DuckDB database file")
    
    class Config:
        schema_extra = {
            "example": {
                "connection_name": "sqlserver",
                "source_query": "SELECT * FROM mydatabase.dbo.mytable",
                "target_table": "imported_table",
                "db_path": None
            }
        }

class OdbcConnectionInfo(BaseModel):
    """Schema for ODBC connection information."""
    
    name: str = Field(..., description="Name of the ODBC connection")
    connection_string: str = Field(..., description="ODBC connection string (sensitive parts masked)")
    driver: Optional[str] = Field(None, description="ODBC driver name")
    server: Optional[str] = Field(None, description="Server name")
    database: Optional[str] = Field(None, description="Database name")
    
class OdbcConnectionsResponse(BaseModel):
    """Schema for listing ODBC connections."""
    
    connections: List[OdbcConnectionInfo] = Field(..., description="List of ODBC connections")
