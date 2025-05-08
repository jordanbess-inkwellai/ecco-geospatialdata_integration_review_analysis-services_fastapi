from sqlalchemy import Column, String, Integer, Boolean, JSON, Text, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel, Base
from datetime import datetime


class ImportStatus(str, enum.Enum):
    """Enum for import job status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ImportMode(str, enum.Enum):
    """Enum for import modes"""
    CREATE = "create"  # Create new table
    APPEND = "append"  # Append to existing table
    REPLACE = "replace"  # Replace existing table
    UPSERT = "upsert"  # Update existing records, insert new ones


class ImportSourceType(str, enum.Enum):
    """Enum for import source types"""
    DATABASE = "database"  # Another database
    FILE = "file"  # File upload
    URL = "url"  # Remote URL
    FDW = "fdw"  # Foreign Data Wrapper
    QUERY = "query"  # SQL query


class ImportJob(Base, BaseModel):
    """Model for data import jobs"""
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Import details
    source_type = Column(String(50), nullable=False)
    import_mode = Column(String(20), default=ImportMode.CREATE, nullable=False)
    
    # Source details
    source_data_source_id = Column(Integer, ForeignKey('datasource.id'), nullable=True)
    source_table = Column(String(255), nullable=True)
    source_query = Column(Text, nullable=True)
    source_file_path = Column(Text, nullable=True)
    source_url = Column(String(1024), nullable=True)
    
    # Target details
    target_data_source_id = Column(Integer, ForeignKey('datasource.id'), nullable=False)
    target_schema = Column(String(255), nullable=True)
    target_table = Column(String(255), nullable=False)
    
    # Configuration
    column_mapping = Column(JSON, nullable=True)  # Map source columns to target columns
    transformation_rules = Column(JSON, nullable=True)  # Rules for transforming data
    filter_conditions = Column(Text, nullable=True)  # SQL WHERE clause for filtering
    batch_size = Column(Integer, default=1000, nullable=False)
    
    # For upsert mode
    key_columns = Column(JSON, nullable=True)  # Columns to use as keys for upsert
    
    # Status
    status = Column(String(20), default=ImportStatus.PENDING, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Statistics
    total_rows = Column(Integer, nullable=True)
    processed_rows = Column(Integer, nullable=True)
    success_rows = Column(Integer, nullable=True)
    error_rows = Column(Integer, nullable=True)
    
    # Relationships
    target_table_obj = relationship("DataSourceTable", foreign_keys=[target_data_source_id], backref="import_jobs")
    logs = relationship("ImportLog", back_populates="import_job", cascade="all, delete-orphan")
    
    # For Kestra integration
    kestra_flow_id = Column(String(255), nullable=True)
    kestra_execution_id = Column(String(255), nullable=True)


class ImportLog(Base, BaseModel):
    """Model for import job logs"""
    
    level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR, etc.
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Additional details
    details = Column(JSON, nullable=True)
    
    # Relationships
    import_job_id = Column(Integer, ForeignKey('importjob.id'), nullable=False)
    import_job = relationship("ImportJob", back_populates="logs")


class FDWMapping(Base, BaseModel):
    """Model for Foreign Data Wrapper mappings"""
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # FDW details
    fdw_type = Column(String(50), nullable=False)  # postgres_fdw, ogr_fdw, etc.
    server_name = Column(String(255), nullable=False)
    
    # Source details
    source_data_source_id = Column(Integer, ForeignKey('datasource.id'), nullable=False)
    source_schema = Column(String(255), nullable=True)
    source_table = Column(String(255), nullable=True)
    
    # Target details
    target_schema = Column(String(255), nullable=False)
    target_table = Column(String(255), nullable=False)
    
    # Configuration
    options = Column(JSON, nullable=True)  # FDW-specific options
    column_mapping = Column(JSON, nullable=True)  # Map source columns to target columns
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    last_refreshed = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Relationships
    source_data_source = relationship("DataSource", foreign_keys=[source_data_source_id])


class AnalyticsView(Base, BaseModel):
    """Model for analytics views"""
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # View details
    view_type = Column(String(50), nullable=False)  # materialized, regular, etc.
    schema_name = Column(String(255), nullable=True)
    view_name = Column(String(255), nullable=False)
    
    # Query
    query = Column(Text, nullable=False)
    
    # For materialized views
    is_materialized = Column(Boolean, default=False, nullable=False)
    refresh_schedule = Column(String(50), nullable=True)  # manual, daily, etc.
    last_refreshed = Column(DateTime, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Relationships
    data_source_id = Column(Integer, ForeignKey('datasource.id'), nullable=False)
    data_source = relationship("DataSource")
    
    # For Kestra integration
    kestra_flow_id = Column(String(255), nullable=True)
