from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from app.schemas.base import BaseSchema
from datetime import datetime


class GeoTableColumnCreate(BaseModel):
    """Schema for creating geo table column"""
    
    name: str = Field(..., description="Name of the column")
    description: Optional[str] = Field(None, description="Description of the column")
    data_type: str = Field(..., description="Data type of the column")
    is_nullable: Optional[bool] = Field(True, description="Whether the column is nullable")
    is_primary_key: Optional[bool] = Field(False, description="Whether the column is a primary key")
    is_unique: Optional[bool] = Field(False, description="Whether the column has a unique constraint")


class GeoTableColumnUpdate(BaseModel):
    """Schema for updating geo table column"""
    
    name: Optional[str] = Field(None, description="Name of the column")
    description: Optional[str] = Field(None, description="Description of the column")
    data_type: Optional[str] = Field(None, description="Data type of the column")
    is_nullable: Optional[bool] = Field(None, description="Whether the column is nullable")
    is_primary_key: Optional[bool] = Field(None, description="Whether the column is a primary key")
    is_unique: Optional[bool] = Field(None, description="Whether the column has a unique constraint")


class GeoTableColumnResponse(BaseSchema):
    """Schema for geo table column response"""
    
    name: str
    description: Optional[str] = None
    data_type: str
    is_nullable: bool
    is_primary_key: bool
    is_unique: bool
    table_id: int


class GeoTableCreate(BaseModel):
    """Schema for creating geo table"""
    
    name: str = Field(..., description="Name of the table")
    description: Optional[str] = Field(None, description="Description of the table")
    schema_name: Optional[str] = Field(None, description="Schema name in PostgreSQL")
    table_name: str = Field(..., description="Table name in PostgreSQL")
    has_geometry: Optional[bool] = Field(True, description="Whether the table has a geometry column")
    geometry_column: Optional[str] = Field(None, description="Name of the geometry column")
    geometry_type: Optional[str] = Field(None, description="Type of geometry (POINT, LINESTRING, POLYGON, etc.)")
    srid: Optional[int] = Field(4326, description="Spatial reference ID")
    columns: Optional[List[GeoTableColumnCreate]] = Field(None, description="Columns in the table")


class GeoTableUpdate(BaseModel):
    """Schema for updating geo table"""
    
    name: Optional[str] = Field(None, description="Name of the table")
    description: Optional[str] = Field(None, description="Description of the table")
    schema_name: Optional[str] = Field(None, description="Schema name in PostgreSQL")
    table_name: Optional[str] = Field(None, description="Table name in PostgreSQL")
    has_geometry: Optional[bool] = Field(None, description="Whether the table has a geometry column")
    geometry_column: Optional[str] = Field(None, description="Name of the geometry column")
    geometry_type: Optional[str] = Field(None, description="Type of geometry (POINT, LINESTRING, POLYGON, etc.)")
    srid: Optional[int] = Field(None, description="Spatial reference ID")


class GeoTableResponse(BaseSchema):
    """Schema for geo table response"""
    
    name: str
    description: Optional[str] = None
    schema_name: Optional[str] = None
    table_name: str
    has_geometry: bool
    geometry_column: Optional[str] = None
    geometry_type: Optional[str] = None
    srid: Optional[int] = None
    row_count: Optional[int] = None
    last_updated: Optional[datetime] = None
    columns: Optional[List[GeoTableColumnResponse]] = None
