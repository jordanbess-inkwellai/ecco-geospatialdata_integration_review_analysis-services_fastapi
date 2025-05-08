from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, Table, JSON, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from geoalchemy2 import Geometry
from datetime import datetime

from app.core.database import Base

# Association table for many-to-many relationship between datasets and keywords
dataset_keyword = Table(
    'dataset_keyword',
    Base.metadata,
    Column('dataset_id', Integer, ForeignKey('metadata_dataset.id'), primary_key=True),
    Column('keyword_id', Integer, ForeignKey('metadata_keyword.id'), primary_key=True)
)

# Association table for many-to-many relationship between datasets and contacts
dataset_contact = Table(
    'dataset_contact',
    Base.metadata,
    Column('dataset_id', Integer, ForeignKey('metadata_dataset.id'), primary_key=True),
    Column('contact_id', Integer, ForeignKey('metadata_contact.id'), primary_key=True),
    Column('role', String(50))  # Role of the contact (e.g., owner, maintainer, publisher)
)


class MetadataKeyword(Base):
    """Keyword for metadata classification"""
    __tablename__ = 'metadata_keyword'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    thesaurus = Column(String(255), nullable=True)  # Optional thesaurus name
    
    # Relationships
    datasets = relationship("MetadataDataset", secondary=dataset_keyword, back_populates="keywords")
    
    def __repr__(self):
        return f"<MetadataKeyword(name='{self.name}')>"


class MetadataContact(Base):
    """Contact information for metadata"""
    __tablename__ = 'metadata_contact'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    organization = Column(String(255), nullable=True)
    position = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    website = Column(String(255), nullable=True)
    
    # Relationships
    datasets = relationship("MetadataDataset", secondary=dataset_contact, back_populates="contacts")
    
    def __repr__(self):
        return f"<MetadataContact(name='{self.name}')>"


class MetadataDataset(Base):
    """Metadata for geospatial datasets"""
    __tablename__ = 'metadata_dataset'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    abstract = Column(Text, nullable=True)
    
    # Resource information
    resource_type = Column(String(50), nullable=False)  # dataset, service, etc.
    resource_format = Column(String(50), nullable=True)  # GeoJSON, Shapefile, GeoTIFF, etc.
    resource_size = Column(Integer, nullable=True)  # Size in bytes
    resource_url = Column(String(255), nullable=True)  # URL to the resource
    resource_path = Column(String(255), nullable=True)  # Local path to the resource
    
    # Spatial information
    bbox = Column(ARRAY(Float, dimensions=1), nullable=True)  # [minx, miny, maxx, maxy]
    geometry = Column(Geometry('POLYGON', srid=4326), nullable=True)  # Spatial extent
    srid = Column(Integer, nullable=True)  # Spatial reference ID
    
    # Temporal information
    temporal_start = Column(DateTime, nullable=True)  # Start of temporal coverage
    temporal_end = Column(DateTime, nullable=True)  # End of temporal coverage
    
    # Metadata information
    metadata_language = Column(String(50), default='en')
    metadata_standard_name = Column(String(100), nullable=True)
    metadata_standard_version = Column(String(50), nullable=True)
    
    # Administrative information
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    is_published = Column(Boolean, default=False)
    
    # Identifiers
    identifier = Column(String(255), unique=True, nullable=True)  # Unique identifier (UUID, DOI, etc.)
    file_identifier = Column(String(255), nullable=True)  # File identifier from original metadata
    parent_identifier = Column(String(255), nullable=True)  # Parent identifier for hierarchical metadata
    
    # Additional properties
    properties = Column(JSONB, nullable=True)  # Additional properties as JSON
    
    # Harvesting information
    harvested_from = Column(String(255), nullable=True)  # Source of harvested metadata
    harvested_at = Column(DateTime, nullable=True)  # When the metadata was harvested
    
    # Relationships
    keywords = relationship("MetadataKeyword", secondary=dataset_keyword, back_populates="datasets")
    contacts = relationship("MetadataContact", secondary=dataset_contact, back_populates="datasets")
    attributes = relationship("MetadataAttribute", back_populates="dataset", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<MetadataDataset(title='{self.title}')>"


class MetadataAttribute(Base):
    """Attribute information for datasets"""
    __tablename__ = 'metadata_attribute'
    
    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey('metadata_dataset.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    data_type = Column(String(50), nullable=True)  # string, integer, float, date, etc.
    unit = Column(String(50), nullable=True)  # Unit of measurement
    domain = Column(JSON, nullable=True)  # Domain values or range
    
    # Relationships
    dataset = relationship("MetadataDataset", back_populates="attributes")
    
    def __repr__(self):
        return f"<MetadataAttribute(name='{self.name}')>"


class MetadataHarvestJob(Base):
    """Metadata harvesting job information"""
    __tablename__ = 'metadata_harvest_job'
    
    id = Column(Integer, primary_key=True, index=True)
    source_type = Column(String(50), nullable=False)  # file, directory, service, etc.
    source_path = Column(String(255), nullable=False)  # Path or URL to the source
    status = Column(String(50), default='pending')  # pending, running, completed, failed
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Job details
    total_records = Column(Integer, default=0)
    processed_records = Column(Integer, default=0)
    success_records = Column(Integer, default=0)
    failed_records = Column(Integer, default=0)
    
    # Error information
    error_message = Column(Text, nullable=True)
    error_details = Column(JSONB, nullable=True)
    
    # Job configuration
    config = Column(JSONB, nullable=True)  # Configuration for the harvesting job
    
    def __repr__(self):
        return f"<MetadataHarvestJob(source='{self.source_path}', status='{self.status}')>"
