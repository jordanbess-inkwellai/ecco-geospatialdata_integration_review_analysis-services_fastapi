from sqlalchemy import Column, String, Integer, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel, Base
from datetime import datetime


class GeoTable(Base, BaseModel):
    """Model for geo tables"""
    
    name = Column(String(255), nullable=False, index=True, unique=True)
    description = Column(Text, nullable=True)
    
    # Table properties
    schema_name = Column(String(255), nullable=True)  # PostgreSQL schema name
    table_name = Column(String(255), nullable=False)  # Actual table name in database
    
    # Metadata
    has_geometry = Column(Boolean, default=True, nullable=False)
    geometry_column = Column(String(255), nullable=True)  # Name of geometry column
    geometry_type = Column(String(50), nullable=True)  # POINT, LINESTRING, POLYGON, etc.
    srid = Column(Integer, default=4326, nullable=True)  # Spatial reference ID
    
    # Table statistics
    row_count = Column(Integer, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, nullable=True)
    
    # Relationships
    columns = relationship("GeoTableColumn", back_populates="table", cascade="all, delete-orphan")


class GeoTableColumn(Base, BaseModel):
    """Model for columns in geo tables"""
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Column properties
    data_type = Column(String(50), nullable=False)  # varchar, integer, geometry, etc.
    is_nullable = Column(Boolean, default=True, nullable=False)
    is_primary_key = Column(Boolean, default=False, nullable=False)
    is_unique = Column(Boolean, default=False, nullable=False)
    
    # Foreign key to GeoTable
    table_id = Column(Integer, ForeignKey('geotable.id'), nullable=False)
    table = relationship("GeoTable", back_populates="columns")
