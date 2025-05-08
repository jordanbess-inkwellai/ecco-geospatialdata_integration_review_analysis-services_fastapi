from sqlalchemy import Column, String, Integer, ForeignKey, Text, DateTime, Enum
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel, Base
from datetime import datetime


class ImportStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ImportJob(Base, BaseModel):
    """Model for import jobs"""
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Import source
    source_type = Column(String(50), nullable=False)  # file, url, database, etc.
    source_path = Column(String(255), nullable=False)  # File path, URL, etc.
    
    # Import destination
    destination_schema = Column(String(255), nullable=True)
    destination_table = Column(String(255), nullable=False)
    
    # Import format
    format = Column(String(50), nullable=False)  # GeoJSON, Shapefile, CSV, etc.
    
    # Import status
    status = Column(String(50), default=ImportStatus.PENDING, nullable=False)
    status_message = Column(Text, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Import options
    options = Column(Text, nullable=True)  # JSON string for additional options
    
    # Relationships
    logs = relationship("ImportLog", back_populates="import_job", cascade="all, delete-orphan")


class ImportLog(Base, BaseModel):
    """Model for import job logs"""
    
    level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR, etc.
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Foreign key to ImportJob
    import_job_id = Column(Integer, ForeignKey('importjob.id'), nullable=False)
    import_job = relationship("ImportJob", back_populates="logs")
