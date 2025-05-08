from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any


class DatabaseConnectionSettings(BaseModel):
    """Schema for database connection settings"""
    
    host: str = Field(..., description="Database host")
    port: int = Field(5432, description="Database port")
    username: str = Field(..., description="Database username")
    password: str = Field(..., description="Database password")
    database: str = Field(..., description="Database name")
    
    @validator('port')
    def port_must_be_valid(cls, v):
        if v < 1 or v > 65535:
            raise ValueError('Port must be between 1 and 65535')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "host": "localhost",
                "port": 5432,
                "username": "postgres",
                "password": "postgres",
                "database": "geospatial"
            }
        }


class DatabaseConnectionResponse(BaseModel):
    """Schema for database connection response"""
    
    success: bool
    message: str
    connection_string: Optional[str] = None
