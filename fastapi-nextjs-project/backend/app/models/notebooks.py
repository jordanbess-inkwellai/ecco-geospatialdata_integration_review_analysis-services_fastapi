from sqlalchemy import Column, String, Integer, Boolean, JSON, Text, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel, Base
from datetime import datetime


class NotebookType(str, enum.Enum):
    """Enum for notebook types"""
    JUPYTER = "jupyter"
    MARIMO = "marimo"
    JUPYTEXT = "jupytext"
    CUSTOM = "custom"


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
    """Model for notebooks (Jupyter, Marimo, etc.)"""
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Notebook details
    notebook_type = Column(String(20), default=NotebookType.JUPYTER, nullable=False)
    content = Column(Text, nullable=True)  # JSON string of notebook content
    file_path = Column(Text, nullable=True)  # Path to notebook file if stored on disk
    
    # Execution details
    status = Column(String(20), default=NotebookStatus.DRAFT, nullable=False)
    last_executed = Column(DateTime, nullable=True)
    execution_time = Column(Integer, nullable=True)  # in seconds
    error_message = Column(Text, nullable=True)
    
    # Parameters for papermill/marimo
    parameters = Column(JSON, nullable=True)
    
    # Scheduling
    schedule_type = Column(String(20), default=NotebookSchedule.MANUAL, nullable=False)
    schedule_config = Column(JSON, nullable=True)  # Cron expression or other scheduling details
    
    # Kestra integration
    kestra_flow_id = Column(String(255), nullable=True)
    
    # Relationships
    data_source_id = Column(Integer, ForeignKey('datasource.id'), nullable=True)
    data_source = relationship("DataSource", back_populates="notebooks")
    executions = relationship("NotebookExecution", back_populates="notebook", cascade="all, delete-orphan")
    
    # For Marimo apps
    is_published = Column(Boolean, default=False, nullable=False)
    published_url = Column(String(1024), nullable=True)
    access_token = Column(String(255), nullable=True)


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
    
    # For Kestra integration
    kestra_execution_id = Column(String(255), nullable=True)
    kestra_logs_url = Column(String(1024), nullable=True)


class MarimoApp(Base, BaseModel):
    """Model for Marimo apps"""
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # App details
    file_path = Column(Text, nullable=True)  # Path to .py file
    content = Column(Text, nullable=True)  # Python code content
    
    # Configuration
    config = Column(JSON, nullable=True)  # App configuration
    
    # Deployment
    is_deployed = Column(Boolean, default=False, nullable=False)
    deployment_url = Column(String(1024), nullable=True)
    deployment_config = Column(JSON, nullable=True)
    
    # Status
    last_modified = Column(DateTime, nullable=True)
    last_executed = Column(DateTime, nullable=True)
    
    # Relationships
    data_source_id = Column(Integer, ForeignKey('datasource.id'), nullable=True)
    data_source = relationship("DataSource", back_populates="marimo_apps")
    executions = relationship("MarimoExecution", back_populates="marimo_app", cascade="all, delete-orphan")


class MarimoExecution(Base, BaseModel):
    """Model for Marimo app execution history"""
    
    # Execution details
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False)
    execution_time = Column(Integer, nullable=True)  # in seconds
    
    # Parameters used
    parameters = Column(JSON, nullable=True)
    
    # Results
    output = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Relationships
    marimo_app_id = Column(Integer, ForeignKey('marimoapp.id'), nullable=False)
    marimo_app = relationship("MarimoApp", back_populates="executions")
    
    # For Kestra integration
    kestra_execution_id = Column(String(255), nullable=True)
