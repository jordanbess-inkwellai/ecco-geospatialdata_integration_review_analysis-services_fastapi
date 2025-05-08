from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from app.schemas.base import BaseSchema
from app.schemas.geospatial import GeometrySchema
import json


class GeoFeatureCreate(BaseModel):
    """Schema for creating geo feature"""
    
    name: str = Field(..., description="Name of the feature")
    description: Optional[str] = Field(None, description="Description of the feature")
    geometry: GeometrySchema = Field(..., description="GeoJSON geometry")
    properties: Optional[Dict[str, Any]] = Field(None, description="GeoJSON properties")
    geospatial_data_id: Optional[int] = Field(None, description="ID of the parent geospatial data")
    feature_type: Optional[str] = Field(None, description="Type of feature (point, line, polygon, etc.)")
    latitude: Optional[float] = Field(None, description="Latitude (for point features)")
    longitude: Optional[float] = Field(None, description="Longitude (for point features)")
    area: Optional[float] = Field(None, description="Area (for polygon features)")
    perimeter: Optional[float] = Field(None, description="Perimeter (for polygon features)")


class GeoFeatureUpdate(BaseModel):
    """Schema for updating geo feature"""
    
    name: Optional[str] = Field(None, description="Name of the feature")
    description: Optional[str] = Field(None, description="Description of the feature")
    geometry: Optional[GeometrySchema] = Field(None, description="GeoJSON geometry")
    properties: Optional[Dict[str, Any]] = Field(None, description="GeoJSON properties")
    geospatial_data_id: Optional[int] = Field(None, description="ID of the parent geospatial data")
    feature_type: Optional[str] = Field(None, description="Type of feature (point, line, polygon, etc.)")
    latitude: Optional[float] = Field(None, description="Latitude (for point features)")
    longitude: Optional[float] = Field(None, description="Longitude (for point features)")
    area: Optional[float] = Field(None, description="Area (for polygon features)")
    perimeter: Optional[float] = Field(None, description="Perimeter (for polygon features)")


class GeoFeatureResponse(BaseSchema):
    """Schema for geo feature response"""
    
    name: str
    description: Optional[str] = None
    geometry: Dict[str, Any]
    properties: Optional[Dict[str, Any]] = None
    geospatial_data_id: Optional[int] = None
    feature_type: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    area: Optional[float] = None
    perimeter: Optional[float] = None
    
    @classmethod
    def from_orm(cls, obj):
        # Convert properties from JSON string to dict if it exists
        if obj.properties and isinstance(obj.properties, str):
            obj.properties = json.loads(obj.properties)
        return super().from_orm(obj)
