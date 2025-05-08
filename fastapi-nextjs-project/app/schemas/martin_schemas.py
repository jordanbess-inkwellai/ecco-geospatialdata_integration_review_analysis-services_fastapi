from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Union
from enum import Enum

class SourceType(str, Enum):
    """Enum for source types."""
    VECTOR = "vector"
    RASTER = "raster"
    TERRAIN = "terrain"

class TileFormat(str, Enum):
    """Enum for tile formats."""
    PBF = "pbf"
    MVT = "mvt"
    PNG = "png"
    JPG = "jpg"
    WEBP = "webp"

class ServerStatusResponse(BaseModel):
    """Schema for server status response."""
    
    status: str = Field(..., description="Server status")
    version: str = Field(..., description="Server version")
    url: str = Field(..., description="Server URL")
    error: Optional[str] = Field(None, description="Error message")

class TableMetadata(BaseModel):
    """Schema for table metadata."""
    
    name: str = Field(..., description="Table name")
    schema: str = Field(..., description="Schema name")
    geometry_column: str = Field(..., description="Geometry column name")
    srid: int = Field(..., description="SRID")
    geometry_type: str = Field(..., description="Geometry type")
    id_column: Optional[str] = Field(None, description="ID column name")
    properties: Dict[str, Any] = Field(..., description="Table properties")

class TileJSON(BaseModel):
    """Schema for TileJSON."""
    
    tilejson: str = Field(..., description="TileJSON version")
    name: str = Field(..., description="Layer name")
    description: Optional[str] = Field(None, description="Layer description")
    version: str = Field(..., description="Layer version")
    attribution: Optional[str] = Field(None, description="Attribution")
    scheme: str = Field(..., description="Tile scheme")
    tiles: List[str] = Field(..., description="Tile URLs")
    minzoom: int = Field(..., description="Minimum zoom level")
    maxzoom: int = Field(..., description="Maximum zoom level")
    bounds: List[float] = Field(..., description="Layer bounds")
    center: List[float] = Field(..., description="Layer center")
    vector_layers: Optional[List[Dict[str, Any]]] = Field(None, description="Vector layers")

class FileInfo(BaseModel):
    """Schema for file information."""
    
    name: str = Field(..., description="File name")
    path: str = Field(..., description="File path")
    size: int = Field(..., description="File size")
    modified: str = Field(..., description="Last modified date")
    url: str = Field(..., description="File URL")

class StyleInfo(BaseModel):
    """Schema for style information."""
    
    name: str = Field(..., description="Style name")
    file_name: str = Field(..., description="File name")
    path: str = Field(..., description="File path")
    size: int = Field(..., description="File size")
    modified: str = Field(..., description="Last modified date")
    version: str = Field(..., description="Style version")
    url: str = Field(..., description="Style URL")

class UploadResult(BaseModel):
    """Schema for upload result."""
    
    status: str = Field(..., description="Upload status")
    name: Optional[str] = Field(None, description="File name")
    path: Optional[str] = Field(None, description="File path")
    url: Optional[str] = Field(None, description="File URL")
    error: Optional[str] = Field(None, description="Error message")
    file_name: Optional[str] = Field(None, description="Original file name")
    version: Optional[str] = Field(None, description="Style version")

class DeleteResult(BaseModel):
    """Schema for delete result."""
    
    status: str = Field(..., description="Delete status")
    name: Optional[str] = Field(None, description="File name")
    error: Optional[str] = Field(None, description="Error message")

class CreatePMTilesRequest(BaseModel):
    """Schema for creating PMTiles from GeoJSON."""
    
    geojson_data: Dict[str, Any] = Field(..., description="GeoJSON data")
    output_name: str = Field(..., description="Output file name")
    min_zoom: int = Field(0, description="Minimum zoom level")
    max_zoom: int = Field(14, description="Maximum zoom level")

class CreateStyleRequest(BaseModel):
    """Schema for creating a style from a source."""
    
    source_url: str = Field(..., description="Source URL")
    source_type: SourceType = Field(..., description="Source type")
    source_name: str = Field(..., description="Source name")
    output_name: str = Field(..., description="Output file name")
