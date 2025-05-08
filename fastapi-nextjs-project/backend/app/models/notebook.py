from sqlalchemy import Column, String, Integer, Boolean, JSON, Text, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel, Base
from datetime import datetime


class NotebookStatus(str, enum.Enum):
    """Enum for notebook execution status"""
    DRAFT = "draft"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class NotebookSchedule(str, enum.Enum):
    """Enum for notebook schedule types"""
    MANUAL = "manual"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class Notebook(Base, BaseModel):
    """Model for Jupyter notebooks"""
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Notebook content
    content = Column(Text, nullable=True)  # JSON string of notebook content
    file_path = Column(Text, nullable=True)  # Path to notebook file if stored on disk
    
    # Execution details
    status = Column(String(20), default=NotebookStatus.DRAFT, nullable=False)
    last_executed = Column(DateTime, nullable=True)
    execution_time = Column(Integer, nullable=True)  # in seconds
    error_message = Column(Text, nullable=True)
    
    # Parameters for papermill
    parameters = Column(JSON, nullable=True)
    
    # Scheduling
    schedule_type = Column(String(20), default=NotebookSchedule.MANUAL, nullable=False)
    schedule_config = Column(JSON, nullable=True)  # Cron expression or other scheduling details
    
    # Relationships
    data_source_id = Column(Integer, ForeignKey('datasource.id'), nullable=True)
    data_source = relationship("DataSource", back_populates="notebooks")
    executions = relationship("NotebookExecution", back_populates="notebook", cascade="all, delete-orphan")


class NotebookExecution(Base, BaseModel):
    """Model for notebook execution history"""
    
    # Execution details
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False)
    execution_time = Column(Integer, nullable=True)  # in seconds
    
    # Parameters used
    parameters = Column(JSON, nullable=True)
    
    # Results
    output_path = Column(Text, nullable=True)  # Path to output notebook
    error_message = Column(Text, nullable=True)
    
    # Relationships
    notebook_id = Column(Integer, ForeignKey('notebook.id'), nullable=False)
    notebook = relationship("Notebook", back_populates="executions")
    
    # Results as JSON
    results = Column(JSON, nullable=True)  # Store any results returned by the notebook
