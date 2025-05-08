from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from app.schemas.base import BaseSchema
from app.schemas.geospatial import GeometrySchema
import json


class SuitabilityCriterionCreate(BaseModel):
    """Schema for creating suitability criterion"""
    
    name: str = Field(..., description="Name of the criterion")
    description: Optional[str] = Field(None, description="Description of the criterion")
    weight: Optional[float] = Field(1.0, description="Weight of the criterion (0-1)")
    criterion_type: str = Field(..., description="Type of criterion (distance, overlay, buffer, etc.)")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Parameters for the criterion")


class SuitabilityCriterionUpdate(BaseModel):
    """Schema for updating suitability criterion"""
    
    name: Optional[str] = Field(None, description="Name of the criterion")
    description: Optional[str] = Field(None, description="Description of the criterion")
    weight: Optional[float] = Field(None, description="Weight of the criterion (0-1)")
    criterion_type: Optional[str] = Field(None, description="Type of criterion (distance, overlay, buffer, etc.)")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Parameters for the criterion")


class SuitabilityCriterionResponse(BaseSchema):
    """Schema for suitability criterion response"""
    
    name: str
    description: Optional[str] = None
    weight: float
    criterion_type: str
    parameters: Optional[Dict[str, Any]] = None
    suitability_id: int
    
    @classmethod
    def from_orm(cls, obj):
        # Convert parameters from JSON string to dict if it exists
        if obj.parameters and isinstance(obj.parameters, str):
            obj.parameters = json.loads(obj.parameters)
        return super().from_orm(obj)


class GeoSuitabilityCreate(BaseModel):
    """Schema for creating geo suitability"""
    
    name: str = Field(..., description="Name of the suitability analysis")
    description: Optional[str] = Field(None, description="Description of the suitability analysis")
    area_of_interest: GeometrySchema = Field(..., description="Area of interest for the analysis")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Parameters for the analysis")
    criteria: Optional[List[SuitabilityCriterionCreate]] = Field(None, description="Criteria for the analysis")


class GeoSuitabilityUpdate(BaseModel):
    """Schema for updating geo suitability"""
    
    name: Optional[str] = Field(None, description="Name of the suitability analysis")
    description: Optional[str] = Field(None, description="Description of the suitability analysis")
    area_of_interest: Optional[GeometrySchema] = Field(None, description="Area of interest for the analysis")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Parameters for the analysis")


class GeoSuitabilityResponse(BaseSchema):
    """Schema for geo suitability response"""
    
    name: str
    description: Optional[str] = None
    area_of_interest: Dict[str, Any]
    suitability_score: Optional[float] = None
    parameters: Optional[Dict[str, Any]] = None
    results: Optional[Dict[str, Any]] = None
    criteria: Optional[List[SuitabilityCriterionResponse]] = None
    
    @classmethod
    def from_orm(cls, obj):
        # Convert parameters and results from JSON string to dict if they exist
        if obj.parameters and isinstance(obj.parameters, str):
            obj.parameters = json.loads(obj.parameters)
        if obj.results and isinstance(obj.results, str):
            obj.results = json.loads(obj.results)
        return super().from_orm(obj)
