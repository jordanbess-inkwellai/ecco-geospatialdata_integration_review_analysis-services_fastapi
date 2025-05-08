from sqlalchemy import Column, String, Integer, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.models.base import BaseModel, Base


class GeoFeature(Base, BaseModel):
    """Model for geo features"""
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Geometry column - can store any geometry type (point, line, polygon)
    geometry = Column(Geometry(geometry_type='GEOMETRY', srid=4326), nullable=False)
    
    # Properties stored as JSON in PostgreSQL
    properties = Column(Text, nullable=True)  # JSON string
    
    # Foreign key to GeospatialData
    geospatial_data_id = Column(Integer, ForeignKey('geospatialdata.id'), nullable=True)
    geospatial_data = relationship("GeospatialData", back_populates="features")
    
    # Feature type
    feature_type = Column(String(50), nullable=True)  # point, line, polygon, etc.
    
    # Additional properties for specific feature types
    # For points
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # For polygons
    area = Column(Float, nullable=True)
    perimeter = Column(Float, nullable=True)
