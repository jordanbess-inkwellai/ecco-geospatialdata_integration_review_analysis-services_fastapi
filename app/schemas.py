from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class RcesSubstationSchema(BaseModel):
    substation_name: str
    voltage_level_kv: float
    status: Optional[str] = 'Active'
    geom: str  # WKT string, e.g., "POINT(-71.060316 42.358429)"

    class Config:
        from_attributes = True # Replaces orm_mode for Pydantic V2
        schema_extra = {
            "example": {
                "substation_name": "Central Substation",
                "voltage_level_kv": 115.0,
                "status": "Active",
                "geom": "POINT(-71.060316 42.358429)"
            }
        }

class SubstationResponseSchema(BaseModel):
    substation_id: int
    substation_name: str
    voltage_level_kv: float
    status: str
    geom: Dict[str, Any]  # GeoJSON representation, e.g., {"type": "Point", "coordinates": [lon, lat]}
    created_at: datetime

    class Config:
        from_attributes = True

class FuseCreateSchema(BaseModel):
    conductor_id: Optional[int] = None
    fuse_rating_amps: Optional[int] = None
    operational_status: Optional[str] = 'Operational'
    geom: str  # WKT string, e.g., "POINT(lon lat)"

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "conductor_id": 1,
                "fuse_rating_amps": 100,
                "operational_status": "Operational",
                "geom": "POINT(-71.060316 42.358429)"
            }
        }

class FuseResponseSchema(BaseModel):
    fuse_id: int
    conductor_id: Optional[int] = None
    fuse_rating_amps: Optional[int] = None
    operational_status: str
    geom: Dict[str, Any]  # GeoJSON representation
    created_at: datetime

    class Config:
        from_attributes = True

class SwitchCreateSchema(BaseModel):
    conductor_id: Optional[int] = None
    switch_type: Optional[str] = None
    operational_status: Optional[str] = 'Closed'
    geom: str  # WKT string, e.g., "POINT(lon lat)"

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "conductor_id": 1,
                "switch_type": "Load Break",
                "operational_status": "Closed",
                "geom": "POINT(-71.060316 42.358429)"
            }
        }

class SwitchResponseSchema(BaseModel):
    switch_id: int
    conductor_id: Optional[int] = None
    switch_type: Optional[str] = None
    operational_status: str
    geom: Dict[str, Any]  # GeoJSON representation
    created_at: datetime

    class Config:
        from_attributes = True

class ConductorCreateSchema(BaseModel):
    start_pole_id: Optional[int] = None
    end_pole_id: Optional[int] = None
    conductor_type: Optional[str] = None
    voltage_rating_kv: Optional[float] = None
    geom: str  # WKT string, e.g., "LINESTRING(lon1 lat1, lon2 lat2)"

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "start_pole_id": 1,
                "end_pole_id": 2,
                "conductor_type": "ACSR",
                "voltage_rating_kv": 13.8,
                "geom": "LINESTRING(30 10, 10 30, 40 40)"
            }
        }

class ConductorResponseSchema(BaseModel):
    conductor_id: int
    start_pole_id: Optional[int] = None
    end_pole_id: Optional[int] = None
    conductor_type: Optional[str] = None
    voltage_rating_kv: Optional[float] = None
    geom: Dict[str, Any]  # GeoJSON representation
    created_at: datetime

    class Config:
        from_attributes = True

class PoleCreateSchema(BaseModel):
    transformer_id: Optional[int] = None
    material_type: Optional[str] = None
    height_meters: Optional[float] = None
    installation_year: Optional[int] = None
    geom: str  # WKT string, e.g., "POINT(lon lat)"

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "transformer_id": 1,
                "material_type": "Wood",
                "height_meters": 10.5,
                "installation_year": 2020,
                "geom": "POINT(-71.060316 42.358429)"
            }
        }

class PoleResponseSchema(BaseModel):
    pole_id: int
    transformer_id: Optional[int] = None
    material_type: Optional[str] = None
    height_meters: Optional[float] = None
    installation_year: Optional[int] = None
    geom: Dict[str, Any]  # GeoJSON representation
    created_at: datetime

    class Config:
        from_attributes = True

class TransformerCreateSchema(BaseModel):
    transformer_name: str
    feeder_id: int
    capacity_kva: float
    status: Optional[str] = 'Active'
    geom: str  # WKT string, e.g., "POINT(lon lat)"

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "transformer_name": "TX-477",
                "feeder_id": 1,
                "capacity_kva": 500,
                "status": "Active",
                "geom": "POINT(-71.060316 42.358429)"
            }
        }

class TransformerResponseSchema(BaseModel):
    transformer_id: int
    transformer_name: str
    feeder_id: int
    capacity_kva: float
    status: str
    geom: Dict[str, Any]  # GeoJSON representation
    created_at: datetime

    class Config:
        from_attributes = True

class FeederCreateSchema(BaseModel):
    feeder_name: str
    substation_id: int
    voltage_level_kv: Optional[float] = None
    geom: str  # WKT string, e.g., "LINESTRING(lon1 lat1, lon2 lat2)"

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "feeder_name": "Feeder F12",
                "substation_id": 1,
                "voltage_level_kv": 13.8,
                "geom": "LINESTRING(30 10, 10 30, 40 40)"
            }
        }

class FeederResponseSchema(BaseModel):
    feeder_id: int
    feeder_name: str
    substation_id: int
    voltage_level_kv: Optional[float] = None
    geom: Dict[str, Any]  # GeoJSON representation
    created_at: datetime

    class Config:
        from_attributes = True
