from sqlalchemy import Column, String, Integer, Boolean, JSON, Text, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel, Base
from datetime import datetime


class GeoServerInstanceType(str, enum.Enum):
    """Enum for GeoServer instance types"""
    STANDALONE = "standalone"
    GEONODE = "geonode"
    CLOUD = "cloud"
    DOCKER = "docker"
    CUSTOM = "custom"


class GeoServerInstance(Base, BaseModel):
    """Model for GeoServer instances"""
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Connection details
    url = Column(String(1024), nullable=False)
    username = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    
    # Instance details
    instance_type = Column(String(50), default=GeoServerInstanceType.STANDALONE, nullable=False)
    version = Column(String(50), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    last_connected = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Relationships
    workspaces = relationship("GeoServerWorkspace", back_populates="geoserver", cascade="all, delete-orphan")


class GeoServerWorkspace(Base, BaseModel):
    """Model for GeoServer workspaces"""
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Namespace URI
    namespace_uri = Column(String(1024), nullable=True)
    
    # Status
    is_default = Column(Boolean, default=False, nullable=False)
    is_isolated = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    geoserver_id = Column(Integer, ForeignKey('geoserverinstance.id'), nullable=False)
    geoserver = relationship("GeoServerInstance", back_populates="workspaces")
    datastores = relationship("GeoServerDataStore", back_populates="workspace", cascade="all, delete-orphan")
    layers = relationship("GeoServerLayer", back_populates="workspace", cascade="all, delete-orphan")
    styles = relationship("GeoServerStyle", back_populates="workspace", cascade="all, delete-orphan")


class GeoServerDataStore(Base, BaseModel):
    """Model for GeoServer data stores"""
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Store details
    store_type = Column(String(50), nullable=False)  # shapefile, postgis, etc.
    connection_params = Column(JSON, nullable=True)
    
    # Status
    is_enabled = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    workspace_id = Column(Integer, ForeignKey('geoserverworkspace.id'), nullable=False)
    workspace = relationship("GeoServerWorkspace", back_populates="datastores")
    layers = relationship("GeoServerLayer", back_populates="datastore", cascade="all, delete-orphan")
    
    # Link to our data source if applicable
    data_source_id = Column(Integer, ForeignKey('datasource.id'), nullable=True)


class GeoServerLayer(Base, BaseModel):
    """Model for GeoServer layers"""
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Layer details
    layer_type = Column(String(50), nullable=False)  # vector, raster, etc.
    native_name = Column(String(255), nullable=True)
    title = Column(String(255), nullable=True)
    abstract = Column(Text, nullable=True)
    
    # Spatial details
    srs = Column(String(50), nullable=True)  # Spatial reference system
    bbox = Column(JSON, nullable=True)  # Bounding box
    
    # Status
    is_enabled = Column(Boolean, default=True, nullable=False)
    is_advertised = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    workspace_id = Column(Integer, ForeignKey('geoserverworkspace.id'), nullable=False)
    workspace = relationship("GeoServerWorkspace", back_populates="layers")
    datastore_id = Column(Integer, ForeignKey('geoserverdatastore.id'), nullable=True)
    datastore = relationship("GeoServerDataStore", back_populates="layers")
    default_style_id = Column(Integer, ForeignKey('geoserverstyle.id'), nullable=True)
    
    # Link to our data source table if applicable
    data_source_table_id = Column(Integer, ForeignKey('datasourcetable.id'), nullable=True)


class GeoServerStyle(Base, BaseModel):
    """Model for GeoServer styles"""
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Style details
    style_format = Column(String(50), nullable=False)  # SLD, CSS, etc.
    style_content = Column(Text, nullable=True)
    file_path = Column(String(1024), nullable=True)
    
    # Relationships
    workspace_id = Column(Integer, ForeignKey('geoserverworkspace.id'), nullable=True)
    workspace = relationship("GeoServerWorkspace", back_populates="styles")
    layers = relationship("GeoServerLayer", foreign_keys=[GeoServerLayer.default_style_id], backref="default_style")


class GeoNodeInstance(Base, BaseModel):
    """Model for GeoNode instances"""
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Connection details
    url = Column(String(1024), nullable=False)
    username = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)
    api_key = Column(String(255), nullable=True)
    
    # Instance details
    version = Column(String(50), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    last_connected = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Linked GeoServer
    geoserver_id = Column(Integer, ForeignKey('geoserverinstance.id'), nullable=True)
    
    # Relationships
    datasets = relationship("GeoNodeDataset", back_populates="geonode", cascade="all, delete-orphan")
    maps = relationship("GeoNodeMap", back_populates="geonode", cascade="all, delete-orphan")


class GeoNodeDataset(Base, BaseModel):
    """Model for GeoNode datasets"""
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Dataset details
    uuid = Column(String(255), nullable=True)
    title = Column(String(255), nullable=True)
    abstract = Column(Text, nullable=True)
    category = Column(String(255), nullable=True)
    keywords = Column(JSON, nullable=True)
    
    # Spatial details
    srs = Column(String(50), nullable=True)
    bbox = Column(JSON, nullable=True)
    
    # Status
    is_published = Column(Boolean, default=True, nullable=False)
    date_created = Column(DateTime, nullable=True)
    date_updated = Column(DateTime, nullable=True)
    
    # Relationships
    geonode_id = Column(Integer, ForeignKey('geonodeinstance.id'), nullable=False)
    geonode = relationship("GeoNodeInstance", back_populates="datasets")
    
    # Link to our data source table if applicable
    data_source_table_id = Column(Integer, ForeignKey('datasourcetable.id'), nullable=True)


class GeoNodeMap(Base, BaseModel):
    """Model for GeoNode maps"""
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Map details
    uuid = Column(String(255), nullable=True)
    title = Column(String(255), nullable=True)
    abstract = Column(Text, nullable=True)
    
    # Map configuration
    config = Column(JSON, nullable=True)
    
    # Status
    is_published = Column(Boolean, default=True, nullable=False)
    date_created = Column(DateTime, nullable=True)
    date_updated = Column(DateTime, nullable=True)
    
    # Relationships
    geonode_id = Column(Integer, ForeignKey('geonodeinstance.id'), nullable=False)
    geonode = relationship("GeoNodeInstance", back_populates="maps")
