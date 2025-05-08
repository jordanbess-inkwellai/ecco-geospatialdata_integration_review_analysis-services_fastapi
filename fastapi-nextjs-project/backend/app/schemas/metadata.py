from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field


class KeywordBase(BaseModel):
    name: str
    thesaurus: Optional[str] = None


class KeywordCreate(KeywordBase):
    pass


class KeywordResponse(KeywordBase):
    id: int
    
    class Config:
        orm_mode = True


class ContactBase(BaseModel):
    name: str
    organization: Optional[str] = None
    position: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    website: Optional[str] = None


class ContactCreate(ContactBase):
    pass


class ContactResponse(ContactBase):
    id: int
    
    class Config:
        orm_mode = True


class ContactWithRole(ContactResponse):
    role: Optional[str] = "pointOfContact"


class AttributeBase(BaseModel):
    name: str
    description: Optional[str] = None
    data_type: Optional[str] = None
    unit: Optional[str] = None
    domain: Optional[Any] = None


class AttributeCreate(AttributeBase):
    pass


class AttributeResponse(AttributeBase):
    id: int
    dataset_id: int
    
    class Config:
        orm_mode = True


class DatasetBase(BaseModel):
    title: str
    description: Optional[str] = None
    abstract: Optional[str] = None
    resource_type: str = "dataset"
    resource_format: Optional[str] = None
    resource_size: Optional[int] = None
    resource_url: Optional[str] = None
    resource_path: Optional[str] = None
    bbox: Optional[List[float]] = None
    srid: Optional[int] = None
    temporal_start: Optional[datetime] = None
    temporal_end: Optional[datetime] = None
    metadata_language: str = "en"
    metadata_standard_name: Optional[str] = None
    metadata_standard_version: Optional[str] = None
    is_published: bool = False
    identifier: Optional[str] = None
    file_identifier: Optional[str] = None
    parent_identifier: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None


class DatasetCreate(DatasetBase):
    keywords: Optional[List[Union[str, KeywordCreate]]] = None
    contacts: Optional[List[Union[int, ContactCreate, Dict[str, Any]]]] = None
    attributes: Optional[List[AttributeCreate]] = None


class DatasetUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    abstract: Optional[str] = None
    resource_type: Optional[str] = None
    resource_format: Optional[str] = None
    resource_size: Optional[int] = None
    resource_url: Optional[str] = None
    resource_path: Optional[str] = None
    bbox: Optional[List[float]] = None
    srid: Optional[int] = None
    temporal_start: Optional[datetime] = None
    temporal_end: Optional[datetime] = None
    metadata_language: Optional[str] = None
    metadata_standard_name: Optional[str] = None
    metadata_standard_version: Optional[str] = None
    is_published: Optional[bool] = None
    identifier: Optional[str] = None
    file_identifier: Optional[str] = None
    parent_identifier: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    keywords: Optional[List[Union[str, KeywordCreate]]] = None
    contacts: Optional[List[Union[int, ContactCreate, Dict[str, Any]]]] = None
    attributes: Optional[List[AttributeCreate]] = None


class DatasetResponse(DatasetBase):
    id: int
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    harvested_from: Optional[str] = None
    harvested_at: Optional[datetime] = None
    keywords: List[KeywordResponse] = []
    contacts: List[ContactWithRole] = []
    attributes: List[AttributeResponse] = []
    
    class Config:
        orm_mode = True


class HarvestJobBase(BaseModel):
    source_type: str
    source_path: str
    config: Optional[Dict[str, Any]] = None


class HarvestJobCreate(HarvestJobBase):
    pass


class HarvestJobResponse(HarvestJobBase):
    id: int
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_records: int = 0
    processed_records: int = 0
    success_records: int = 0
    failed_records: int = 0
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    
    class Config:
        orm_mode = True
