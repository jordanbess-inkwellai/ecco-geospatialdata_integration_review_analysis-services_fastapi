from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime

class BoxMetadata(BaseModel):
    """Schema for Box.com file metadata."""
    
    crs: Optional[str] = Field(None, description="Coordinate Reference System")
    geometryType: Optional[str] = Field(None, description="Type of geometry")
    featureCount: Optional[str] = Field(None, description="Number of features")
    boundingBox: Optional[str] = Field(None, description="Bounding box coordinates")
    attributes: Optional[str] = Field(None, description="List of attribute fields")
    lastUpdated: Optional[str] = Field(None, description="Date when metadata was last updated")
    dataFormat: Optional[str] = Field(None, description="Format of the geospatial data")
    
    class Config:
        extra = "allow"  # Allow additional fields

class BoxFileInfo(BaseModel):
    """Schema for Box.com file information."""
    
    id: str = Field(..., description="File ID")
    name: str = Field(..., description="File name")
    type: str = Field(..., description="Item type (file or folder)")
    size: Optional[int] = Field(None, description="File size in bytes")
    created_at: Optional[datetime] = Field(None, description="Creation date")
    modified_at: Optional[datetime] = Field(None, description="Last modification date")
    has_metadata: bool = Field(False, description="Whether the file has geospatial metadata")
    metadata: Optional[BoxMetadata] = Field(None, description="Geospatial metadata")
    local_path: Optional[str] = Field(None, description="Local path to the downloaded file")
    
    class Config:
        extra = "allow"  # Allow additional fields

class BoxFolderContents(BaseModel):
    """Schema for Box.com folder contents."""
    
    folder_id: str = Field(..., description="Folder ID")
    items: List[Dict[str, Any]] = Field(..., description="Items in the folder")

class BoxSearchQuery(BaseModel):
    """Schema for Box.com search query."""
    
    query: str = Field(..., description="Search query")
    file_extensions: Optional[List[str]] = Field(None, description="File extensions to filter by")
    metadata_query: Optional[Dict[str, Any]] = Field(None, description="Metadata query to filter by")
    limit: int = Field(100, description="Maximum number of results to return")

class BoxUploadResponse(BaseModel):
    """Schema for Box.com file upload response."""
    
    id: str = Field(..., description="File ID")
    name: str = Field(..., description="File name")
    type: str = Field(..., description="Item type (file)")
    size: int = Field(..., description="File size in bytes")
    created_at: datetime = Field(..., description="Creation date")
    modified_at: datetime = Field(..., description="Last modification date")
    metadata: Optional[BoxMetadata] = Field(None, description="Geospatial metadata")
    
    class Config:
        extra = "allow"  # Allow additional fields

class BoxSharedLinkResponse(BaseModel):
    """Schema for Box.com shared link response."""
    
    shared_link: str = Field(..., description="Shared link URL")
