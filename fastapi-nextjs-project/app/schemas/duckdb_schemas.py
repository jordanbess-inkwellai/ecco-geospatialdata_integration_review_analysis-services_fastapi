from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Union
from enum import Enum

class OutputFormat(str, Enum):
    """Enum for output formats."""
    CSV = "csv"
    PARQUET = "parquet"
    JSON = "json"
    GEOJSON = "geojson"
    SHAPEFILE = "shp"
    GEOPACKAGE = "gpkg"

class ColumnType(str, Enum):
    """Enum for column types."""
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    DOUBLE = "DOUBLE"
    VARCHAR = "VARCHAR"
    TEXT = "TEXT"
    BOOLEAN = "BOOLEAN"
    DATE = "DATE"
    TIMESTAMP = "TIMESTAMP"
    GEOMETRY = "GEOMETRY"

class DatabaseType(str, Enum):
    """Enum for database types."""
    POSTGRES = "postgres"
    MYSQL = "mysql"
    SQLITE = "sqlite"

class TableColumn(BaseModel):
    """Schema for a table column."""

    name: str = Field(..., description="Column name")
    type: str = Field(..., description="Column type")
    nullable: bool = Field(True, description="Whether the column is nullable")
    description: Optional[str] = Field(None, description="Column description")

class TableSchema(BaseModel):
    """Schema for a table schema."""

    name: str = Field(..., description="Table name")
    columns: List[TableColumn] = Field(..., description="Table columns")
    description: Optional[str] = Field(None, description="Table description")

class ExecuteQueryRequest(BaseModel):
    """Schema for executing a query."""

    query: str = Field(..., description="SQL query to execute")
    db_path: Optional[str] = Field(None, description="Path to the database file")
    params: Optional[Dict[str, Any]] = Field(None, description="Query parameters")

class CreateTableFromFileRequest(BaseModel):
    """Schema for creating a table from a file."""

    file_path: str = Field(..., description="Path to the file")
    table_name: str = Field(..., description="Name of the table to create")
    db_path: Optional[str] = Field(None, description="Path to the database file")
    use_hostfs: Optional[bool] = Field(False, description="Whether to use HostFS to access the file")

class ExportTableRequest(BaseModel):
    """Schema for exporting a table."""

    table_name: str = Field(..., description="Name of the table to export")
    output_format: OutputFormat = Field(..., description="Output format")
    output_path: Optional[str] = Field(None, description="Path to the output file")
    db_path: Optional[str] = Field(None, description="Path to the database file")

class GetTableSchemaRequest(BaseModel):
    """Schema for getting a table schema."""

    table_name: str = Field(..., description="Name of the table")
    db_path: Optional[str] = Field(None, description="Path to the database file")

class GetTablesRequest(BaseModel):
    """Schema for getting a list of tables."""

    db_path: Optional[str] = Field(None, description="Path to the database file")

class GetTablePreviewRequest(BaseModel):
    """Schema for getting a table preview."""

    table_name: str = Field(..., description="Name of the table")
    limit: int = Field(10, description="Maximum number of rows to return")
    db_path: Optional[str] = Field(None, description="Path to the database file")

class GetTableStatisticsRequest(BaseModel):
    """Schema for getting table statistics."""

    table_name: str = Field(..., description="Name of the table")
    db_path: Optional[str] = Field(None, description="Path to the database file")

class CreateDatabaseRequest(BaseModel):
    """Schema for creating a database."""

    db_name: str = Field(..., description="Name of the database")

class DeleteDatabaseRequest(BaseModel):
    """Schema for deleting a database."""

    db_path: str = Field(..., description="Path to the database file")

class ConnectToDatabaseRequest(BaseModel):
    """Schema for connecting to a database."""

    connection_string: str = Field(..., description="Database connection string")
    db_type: DatabaseType = Field(..., description="Database type")
    db_path: Optional[str] = Field(None, description="Path to the DuckDB database file")

class SpatialQueryRequest(BaseModel):
    """Schema for executing a spatial query."""

    query: str = Field(..., description="SQL query to execute")
    db_path: Optional[str] = Field(None, description="Path to the database file")

class ReprojectGeometryRequest(BaseModel):
    """Schema for reprojecting a geometry column."""

    table_name: str = Field(..., description="Name of the table")
    geometry_column: str = Field(..., description="Name of the geometry column")
    source_srid: int = Field(..., description="Source SRID")
    target_srid: int = Field(..., description="Target SRID")
    db_path: Optional[str] = Field(None, description="Path to the database file")

class ConvertToPostGISRequest(BaseModel):
    """Schema for converting a table to PostGIS."""

    table_name: str = Field(..., description="Name of the table")
    geometry_column: str = Field(..., description="Name of the geometry column")
    srid: int = Field(..., description="SRID of the geometry")
    db_path: Optional[str] = Field(None, description="Path to the database file")

class ColumnStatistics(BaseModel):
    """Schema for column statistics."""

    name: str = Field(..., description="Column name")
    type: str = Field(..., description="Column type")
    null_count: int = Field(..., description="Number of null values")
    min: Optional[float] = Field(None, description="Minimum value (numeric columns only)")
    max: Optional[float] = Field(None, description="Maximum value (numeric columns only)")
    mean: Optional[float] = Field(None, description="Mean value (numeric columns only)")
    std: Optional[float] = Field(None, description="Standard deviation (numeric columns only)")
    min_length: Optional[int] = Field(None, description="Minimum length (string columns only)")
    max_length: Optional[int] = Field(None, description="Maximum length (string columns only)")
    mean_length: Optional[float] = Field(None, description="Mean length (string columns only)")

class TableStatistics(BaseModel):
    """Schema for table statistics."""

    row_count: int = Field(..., description="Number of rows")
    column_count: int = Field(..., description="Number of columns")
    columns: List[ColumnStatistics] = Field(..., description="Column statistics")
