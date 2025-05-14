# app/models/elec_models.py
from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, Text, TIMESTAMP
from geoalchemy2 import Geometry
from app.database import Base

class Substation(Base):
    __tablename__ = 'substations'
    __table_args__ = {'schema': 'network'}
    substation_id = Column(Integer, primary_key=True)
    substation_name = Column(String(255), nullable=False)
    voltage_level_kv = Column(Numeric, nullable=False)
    status = Column(String(50), default='Active')
    geom = Column(Geometry('POINT', 4326), nullable=False)
    created_at = Column(TIMESTAMP)

class Feeder(Base):
    __tablename__ = 'feeders'
    __table_args__ = {'schema': 'network'}
    feeder_id = Column(Integer, primary_key=True)
    feeder_name = Column(String(255), nullable=False)
    substation_id = Column(Integer, ForeignKey('network.substations.substation_id', ondelete='CASCADE'), nullable=False)
    voltage_level_kv = Column(Numeric)
    geom = Column(Geometry('LINESTRING', 4326), nullable=False)
    created_at = Column(TIMESTAMP)

class Transformer(Base):
    __tablename__ = 'transformers'
    __table_args__ = {'schema': 'network'}
    transformer_id = Column(Integer, primary_key=True)
    transformer_name = Column(String(255), nullable=False)
    feeder_id = Column(Integer, ForeignKey('network.feeders.feeder_id', ondelete='CASCADE'), nullable=False)
    capacity_kva = Column(Numeric, nullable=False)
    status = Column(String(50), default='Active')
    geom = Column(Geometry('POINT', 4326), nullable=False)
    created_at = Column(TIMESTAMP)

class Pole(Base):
    __tablename__ = 'poles'
    __table_args__ = {'schema': 'network'}
    pole_id = Column(Integer, primary_key=True)
    transformer_id = Column(Integer, ForeignKey('network.transformers.transformer_id', ondelete='SET NULL'))
    material_type = Column(String(100))
    height_meters = Column(Numeric)
    installation_year = Column(Integer)
    geom = Column(Geometry('POINT', 4326), nullable=False)
    created_at = Column(TIMESTAMP)

class Conductor(Base):
    __tablename__ = 'conductors'
    __table_args__ = {'schema': 'network'}
    conductor_id = Column(Integer, primary_key=True)
    start_pole_id = Column(Integer, ForeignKey('network.poles.pole_id', ondelete='CASCADE'))
    end_pole_id = Column(Integer, ForeignKey('network.poles.pole_id', ondelete='CASCADE'))
    conductor_type = Column(String(100))
    voltage_rating_kv = Column(Numeric)
    geom = Column(Geometry('LINESTRING', 4326), nullable=False)
    created_at = Column(TIMESTAMP)

class Switch(Base):
    __tablename__ = 'switches'
    __table_args__ = {'schema': 'network'}
    switch_id = Column(Integer, primary_key=True)
    conductor_id = Column(Integer, ForeignKey('network.conductors.conductor_id', ondelete='CASCADE'))
    switch_type = Column(String(100))
    operational_status = Column(String(50), default='Closed')
    geom = Column(Geometry('POINT', 4326), nullable=False)
    created_at = Column(TIMESTAMP)

class Fuse(Base):
    __tablename__ = 'fuses'
    __table_args__ = {'schema': 'network'}
    fuse_id = Column(Integer, primary_key=True)
    conductor_id = Column(Integer, ForeignKey('network.conductors.conductor_id', ondelete='CASCADE'))
    fuse_rating_amps = Column(Integer)
    operational_status = Column(String(50), default='Operational')
    geom = Column(Geometry('POINT', 4326), nullable=False)
    created_at = Column(TIMESTAMP)

class Meter(Base):
    __tablename__ = 'meters'
    __table_args__ = {'schema': 'network'}
    meter_id = Column(Integer, primary_key=True)
    pole_id = Column(Integer, ForeignKey('network.poles.pole_id', ondelete='SET NULL'))
    meter_number = Column(String(255), unique=True, nullable=False)
    installation_date = Column(Date)
    geom = Column(Geometry('POINT', 4326), nullable=False)
    created_at = Column(TIMESTAMP)

class Customer(Base):
    __tablename__ = 'customers'
    __table_args__ = {'schema': 'network'}
    customer_id = Column(Integer, primary_key=True)
    customer_name = Column(String(255), nullable=False)
    address = Column(Text)
    contact_number = Column(String(20))
    meter_id = Column(Integer, ForeignKey('network.meters.meter_id', ondelete='SET NULL'))
    created_at = Column(TIMESTAMP)

class ServicePoint(Base):
    __tablename__ = 'service_points'
    __table_args__ = {'schema': 'network'}
    service_point_id = Column(Integer, primary_key=True)
    meter_id = Column(Integer, ForeignKey('network.meters.meter_id', ondelete='CASCADE'))
    service_status = Column(String(50), default='Active')
    geom = Column(Geometry('POINT', 4326), nullable=False)
    created_at = Column(TIMESTAMP)
