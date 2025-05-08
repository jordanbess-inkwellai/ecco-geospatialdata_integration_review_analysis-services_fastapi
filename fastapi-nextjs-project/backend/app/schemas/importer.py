from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from app.schemas.base import BaseSchema
from datetime import datetime
import json
from app.models.importer import ImportStatus


class ImportLogCreate(BaseModel):
    """Schema for creating import log"""
    
    level: str = Field(..., description="Log level (INFO, WARNING, ERROR, etc.)")
    message: str = Field(..., description="Log message")
    timestamp: Optional[datetime] = Field(None, description="Timestamp of the log")


class ImportLogResponse(BaseSchema):
    """Schema for import log response"""
    
    level: str
    message: str
    timestamp: datetime
    import_job_id: int


class ImportJobCreate(BaseModel):
    """Schema for creating import job"""
    
    name: str = Field(..., description="Name of the import job")
    description: Optional[str] = Field(None, description="Description of the import job")
    source_type: str = Field(..., description="Type of source (file, url, database, etc.)")
    source_path: str = Field(..., description="Path to the source (file path, URL, etc.)")
    destination_schema: Optional[str] = Field(None, description="Schema name for the destination")
    destination_table: str = Field(..., description="Table name for the destination")
    format: str = Field(..., description="Format of the data (GeoJSON, Shapefile, CSV, etc.)")
    options: Optional[Dict[str, Any]] = Field(None, description="Additional options for the import")


class ImportJobUpdate(BaseModel):
    """Schema for updating import job"""
    
    name: Optional[str] = Field(None, description="Name of the import job")
    description: Optional[str] = Field(None, description="Description of the import job")
    status: Optional[str] = Field(None, description="Status of the import job")
    status_message: Optional[str] = Field(None, description="Status message")
    options: Optional[Dict[str, Any]] = Field(None, description="Additional options for the import")


class ImportJobResponse(BaseSchema):
    """Schema for import job response"""
    
    name: str
    description: Optional[str] = None
    source_type: str
    source_path: str
    destination_schema: Optional[str] = None
    destination_table: str
    format: str
    status: str
    status_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    options: Optional[Dict[str, Any]] = None
    logs: Optional[List[ImportLogResponse]] = None
    
    @classmethod
    def from_orm(cls, obj):
        # Convert options from JSON string to dict if it exists
        if obj.options and isinstance(obj.options, str):
            obj.options = json.loads(obj.options)
        return super().from_orm(obj)
