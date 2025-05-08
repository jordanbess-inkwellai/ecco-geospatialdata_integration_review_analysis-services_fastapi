from sqlalchemy import Column, String, Integer, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.models.base import BaseModel, Base


class GeoSuitability(Base, BaseModel):
    """Model for geospatial suitability analysis"""
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Geometry column - area of interest for suitability analysis
    area_of_interest = Column(Geometry(geometry_type='POLYGON', srid=4326), nullable=False)
    
    # Suitability score (0-100)
    suitability_score = Column(Float, nullable=True)
    
    # Analysis parameters stored as JSON
    parameters = Column(Text, nullable=True)  # JSON string
    
    # Results stored as JSON
    results = Column(Text, nullable=True)  # JSON string
    
    # Relationships
    criteria = relationship("SuitabilityCriterion", back_populates="suitability", cascade="all, delete-orphan")


class SuitabilityCriterion(Base, BaseModel):
    """Model for suitability criteria"""
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Criterion properties
    weight = Column(Float, default=1.0, nullable=False)  # Importance weight (0-1)
    criterion_type = Column(String(50), nullable=False)  # distance, overlay, buffer, etc.
    
    # Parameters specific to this criterion
    parameters = Column(Text, nullable=True)  # JSON string
    
    # Foreign key to GeoSuitability
    suitability_id = Column(Integer, ForeignKey('geosuitability.id'), nullable=False)
    suitability = relationship("GeoSuitability", back_populates="criteria")
