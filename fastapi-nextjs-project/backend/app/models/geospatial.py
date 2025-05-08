from sqlalchemy import Column, String, Float, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.models.base import BaseModel, Base


class GeospatialData(Base, BaseModel):
    """Model for geospatial data"""
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Geometry column - can store any geometry type (point, line, polygon)
    geometry = Column(Geometry(geometry_type='GEOMETRY', srid=4326), nullable=False)
    
    # Properties stored as JSON in PostgreSQL
    properties = Column(Text, nullable=True)  # JSON string
    
    # Metadata
    source = Column(String(255), nullable=True)
    data_type = Column(String(50), nullable=True)  # point, line, polygon, etc.
    
    # Relationships
    features = relationship("GeoFeature", back_populates="geospatial_data", cascade="all, delete-orphan")


class GeospatialLayer(Base, BaseModel):
    """Model for geospatial layers"""
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Layer properties
    visible = Column(Integer, default=1, nullable=False)  # 0=hidden, 1=visible
    z_index = Column(Integer, default=0, nullable=False)
    opacity = Column(Float, default=1.0, nullable=False)
    
    # Style properties (can be extended)
    style = Column(Text, nullable=True)  # JSON string for styling
