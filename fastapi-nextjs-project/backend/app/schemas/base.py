from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class BaseSchema(BaseModel):
    """Base schema for all Pydantic models"""
    
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
