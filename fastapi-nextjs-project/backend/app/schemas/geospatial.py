from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from app.schemas.base import BaseSchema
import json


class GeometrySchema(BaseModel):
    """Schema for GeoJSON geometry"""
    
    type: str
    coordinates: Union[List[float], List[List[float]], List[List[List[float]]], List[List[List[List[float]]]]]


class PropertiesSchema(BaseModel):
    """Schema for GeoJSON properties"""
    
    class Config:
        extra = "allow"


class GeospatialDataCreate(BaseModel):
    """Schema for creating geospatial data"""
    
    name: str = Field(..., description="Name of the geospatial data")
    description: Optional[str] = Field(None, description="Description of the geospatial data")
    geometry: GeometrySchema = Field(..., description="GeoJSON geometry")
    properties: Optional[Dict[str, Any]] = Field(None, description="GeoJSON properties")
    source: Optional[str] = Field(None, description="Source of the data")
    data_type: Optional[str] = Field(None, description="Type of data (point, line, polygon, etc.)")


class GeospatialDataUpdate(BaseModel):
    """Schema for updating geospatial data"""
    
    name: Optional[str] = Field(None, description="Name of the geospatial data")
    description: Optional[str] = Field(None, description="Description of the geospatial data")
    geometry: Optional[GeometrySchema] = Field(None, description="GeoJSON geometry")
    properties: Optional[Dict[str, Any]] = Field(None, description="GeoJSON properties")
    source: Optional[str] = Field(None, description="Source of the data")
    data_type: Optional[str] = Field(None, description="Type of data (point, line, polygon, etc.)")


class GeospatialDataResponse(BaseSchema):
    """Schema for geospatial data response"""
    
    name: str
    description: Optional[str] = None
    geometry: Dict[str, Any]
    properties: Optional[Dict[str, Any]] = None
    source: Optional[str] = None
    data_type: Optional[str] = None
    
    @classmethod
    def from_orm(cls, obj):
        # Convert properties from JSON string to dict if it exists
        if obj.properties and isinstance(obj.properties, str):
            obj.properties = json.loads(obj.properties)
        return super().from_orm(obj)


class GeospatialLayerCreate(BaseModel):
    """Schema for creating geospatial layer"""
    
    name: str = Field(..., description="Name of the layer")
    description: Optional[str] = Field(None, description="Description of the layer")
    visible: Optional[int] = Field(1, description="Visibility (0=hidden, 1=visible)")
    z_index: Optional[int] = Field(0, description="Z-index for layer ordering")
    opacity: Optional[float] = Field(1.0, description="Layer opacity (0-1)")
    style: Optional[Dict[str, Any]] = Field(None, description="Layer style properties")


class GeospatialLayerUpdate(BaseModel):
    """Schema for updating geospatial layer"""
    
    name: Optional[str] = Field(None, description="Name of the layer")
    description: Optional[str] = Field(None, description="Description of the layer")
    visible: Optional[int] = Field(None, description="Visibility (0=hidden, 1=visible)")
    z_index: Optional[int] = Field(None, description="Z-index for layer ordering")
    opacity: Optional[float] = Field(None, description="Layer opacity (0-1)")
    style: Optional[Dict[str, Any]] = Field(None, description="Layer style properties")


class GeospatialLayerResponse(BaseSchema):
    """Schema for geospatial layer response"""
    
    name: str
    description: Optional[str] = None
    visible: int
    z_index: int
    opacity: float
    style: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_orm(cls, obj):
        # Convert style from JSON string to dict if it exists
        if obj.style and isinstance(obj.style, str):
            obj.style = json.loads(obj.style)
        return super().from_orm(obj)
