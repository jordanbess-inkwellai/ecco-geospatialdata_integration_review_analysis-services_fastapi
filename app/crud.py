from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.elec_models import Substation, Feeder, Transformer, Pole, Conductor, Switch, Fuse
from app.schemas import (
    RcesSubstationSchema, FeederCreateSchema, TransformerCreateSchema, PoleCreateSchema,
    ConductorCreateSchema, SwitchCreateSchema, FuseCreateSchema
)
from typing import Optional, List

def create_substation(db: Session, substation: RcesSubstationSchema) -> Substation:
    """
    Create a new substation in the database.
    """
    db_substation = Substation(
        substation_name=substation.substation_name,
        voltage_level_kv=substation.voltage_level_kv,
        status=substation.status,
        geom=func.ST_GeomFromText(substation.geom, 4326)  # Assuming WKT string input
    )
    db.add(db_substation)
    db.commit()
    db.refresh(db_substation)
    return db_substation

# Fuse CRUD functions
def create_fuse(db: Session, fuse: FuseCreateSchema) -> Fuse:
    db_fuse = Fuse(
        conductor_id=fuse.conductor_id,
        fuse_rating_amps=fuse.fuse_rating_amps,
        operational_status=fuse.operational_status,
        geom=func.ST_GeomFromText(fuse.geom, 4326)
    )
    db.add(db_fuse)
    db.commit()
    db.refresh(db_fuse)
    return db_fuse

def get_fuse(db: Session, fuse_id: int) -> Optional[Fuse]:
    return db.query(Fuse).filter(Fuse.fuse_id == fuse_id).first()

def get_fuses(db: Session, skip: int = 0, limit: int = 100) -> List[Fuse]:
    return db.query(Fuse).offset(skip).limit(limit).all()

def update_fuse(db: Session, fuse_id: int, fuse_data: FuseCreateSchema) -> Optional[Fuse]:
    db_fuse = db.query(Fuse).filter(Fuse.fuse_id == fuse_id).first()
    if not db_fuse:
        return None

    db_fuse.conductor_id = fuse_data.conductor_id
    db_fuse.fuse_rating_amps = fuse_data.fuse_rating_amps
    db_fuse.operational_status = fuse_data.operational_status
    if fuse_data.geom:
        db_fuse.geom = func.ST_GeomFromText(fuse_data.geom, 4326)
    
    db.add(db_fuse)
    db.commit()
    db.refresh(db_fuse)
    return db_fuse

def delete_fuse(db: Session, fuse_id: int) -> Optional[Fuse]:
    db_fuse = db.query(Fuse).filter(Fuse.fuse_id == fuse_id).first()
    if not db_fuse:
        return None
    
    db.delete(db_fuse)
    db.commit()
    return db_fuse

# Switch CRUD functions
def create_switch(db: Session, switch: SwitchCreateSchema) -> Switch:
    db_switch = Switch(
        conductor_id=switch.conductor_id,
        switch_type=switch.switch_type,
        operational_status=switch.operational_status,
        geom=func.ST_GeomFromText(switch.geom, 4326)
    )
    db.add(db_switch)
    db.commit()
    db.refresh(db_switch)
    return db_switch

def get_switch(db: Session, switch_id: int) -> Optional[Switch]:
    return db.query(Switch).filter(Switch.switch_id == switch_id).first()

def get_switches(db: Session, skip: int = 0, limit: int = 100) -> List[Switch]:
    return db.query(Switch).offset(skip).limit(limit).all()

def update_switch(db: Session, switch_id: int, switch_data: SwitchCreateSchema) -> Optional[Switch]:
    db_switch = db.query(Switch).filter(Switch.switch_id == switch_id).first()
    if not db_switch:
        return None

    db_switch.conductor_id = switch_data.conductor_id
    db_switch.switch_type = switch_data.switch_type
    db_switch.operational_status = switch_data.operational_status
    if switch_data.geom:
        db_switch.geom = func.ST_GeomFromText(switch_data.geom, 4326)
    
    db.add(db_switch)
    db.commit()
    db.refresh(db_switch)
    return db_switch

def delete_switch(db: Session, switch_id: int) -> Optional[Switch]:
    db_switch = db.query(Switch).filter(Switch.switch_id == switch_id).first()
    if not db_switch:
        return None
    
    db.delete(db_switch)
    db.commit()
    return db_switch

# Conductor CRUD functions
def create_conductor(db: Session, conductor: ConductorCreateSchema) -> Conductor:
    db_conductor = Conductor(
        start_pole_id=conductor.start_pole_id,
        end_pole_id=conductor.end_pole_id,
        conductor_type=conductor.conductor_type,
        voltage_rating_kv=conductor.voltage_rating_kv,
        geom=func.ST_GeomFromText(conductor.geom, 4326)
    )
    db.add(db_conductor)
    db.commit()
    db.refresh(db_conductor)
    return db_conductor

def get_conductor(db: Session, conductor_id: int) -> Optional[Conductor]:
    return db.query(Conductor).filter(Conductor.conductor_id == conductor_id).first()

def get_conductors(db: Session, skip: int = 0, limit: int = 100) -> List[Conductor]:
    return db.query(Conductor).offset(skip).limit(limit).all()

def update_conductor(db: Session, conductor_id: int, conductor_data: ConductorCreateSchema) -> Optional[Conductor]:
    db_conductor = db.query(Conductor).filter(Conductor.conductor_id == conductor_id).first()
    if not db_conductor:
        return None

    db_conductor.start_pole_id = conductor_data.start_pole_id
    db_conductor.end_pole_id = conductor_data.end_pole_id
    db_conductor.conductor_type = conductor_data.conductor_type
    db_conductor.voltage_rating_kv = conductor_data.voltage_rating_kv
    if conductor_data.geom:
        db_conductor.geom = func.ST_GeomFromText(conductor_data.geom, 4326)
    
    db.add(db_conductor)
    db.commit()
    db.refresh(db_conductor)
    return db_conductor

def delete_conductor(db: Session, conductor_id: int) -> Optional[Conductor]:
    db_conductor = db.query(Conductor).filter(Conductor.conductor_id == conductor_id).first()
    if not db_conductor:
        return None
    
    db.delete(db_conductor)
    db.commit()
    return db_conductor

# Pole CRUD functions
def create_pole(db: Session, pole: PoleCreateSchema) -> Pole:
    db_pole = Pole(
        transformer_id=pole.transformer_id,
        material_type=pole.material_type,
        height_meters=pole.height_meters,
        installation_year=pole.installation_year,
        geom=func.ST_GeomFromText(pole.geom, 4326)
    )
    db.add(db_pole)
    db.commit()
    db.refresh(db_pole)
    return db_pole

def get_pole(db: Session, pole_id: int) -> Optional[Pole]:
    return db.query(Pole).filter(Pole.pole_id == pole_id).first()

def get_poles(db: Session, skip: int = 0, limit: int = 100) -> List[Pole]:
    return db.query(Pole).offset(skip).limit(limit).all()

def update_pole(db: Session, pole_id: int, pole_data: PoleCreateSchema) -> Optional[Pole]:
    db_pole = db.query(Pole).filter(Pole.pole_id == pole_id).first()
    if not db_pole:
        return None

    db_pole.transformer_id = pole_data.transformer_id
    db_pole.material_type = pole_data.material_type
    db_pole.height_meters = pole_data.height_meters
    db_pole.installation_year = pole_data.installation_year
    if pole_data.geom:
        db_pole.geom = func.ST_GeomFromText(pole_data.geom, 4326)
    
    db.add(db_pole)
    db.commit()
    db.refresh(db_pole)
    return db_pole

def delete_pole(db: Session, pole_id: int) -> Optional[Pole]:
    db_pole = db.query(Pole).filter(Pole.pole_id == pole_id).first()
    if not db_pole:
        return None
    
    db.delete(db_pole)
    db.commit()
    return db_pole

# Transformer CRUD functions
def create_transformer(db: Session, transformer: TransformerCreateSchema) -> Transformer:
    db_transformer = Transformer(
        transformer_name=transformer.transformer_name,
        feeder_id=transformer.feeder_id,
        capacity_kva=transformer.capacity_kva,
        status=transformer.status,
        geom=func.ST_GeomFromText(transformer.geom, 4326)
    )
    db.add(db_transformer)
    db.commit()
    db.refresh(db_transformer)
    return db_transformer

def get_transformer(db: Session, transformer_id: int) -> Optional[Transformer]:
    return db.query(Transformer).filter(Transformer.transformer_id == transformer_id).first()

def get_transformers(db: Session, skip: int = 0, limit: int = 100) -> List[Transformer]:
    return db.query(Transformer).offset(skip).limit(limit).all()

def update_transformer(db: Session, transformer_id: int, transformer_data: TransformerCreateSchema) -> Optional[Transformer]:
    db_transformer = db.query(Transformer).filter(Transformer.transformer_id == transformer_id).first()
    if not db_transformer:
        return None

    db_transformer.transformer_name = transformer_data.transformer_name
    db_transformer.feeder_id = transformer_data.feeder_id
    db_transformer.capacity_kva = transformer_data.capacity_kva
    db_transformer.status = transformer_data.status
    if transformer_data.geom:
        db_transformer.geom = func.ST_GeomFromText(transformer_data.geom, 4326)
    
    db.add(db_transformer)
    db.commit()
    db.refresh(db_transformer)
    return db_transformer

def delete_transformer(db: Session, transformer_id: int) -> Optional[Transformer]:
    db_transformer = db.query(Transformer).filter(Transformer.transformer_id == transformer_id).first()
    if not db_transformer:
        return None
    
    db.delete(db_transformer)
    db.commit()
    return db_transformer

# Feeder CRUD functions
def create_feeder(db: Session, feeder: FeederCreateSchema) -> Feeder:
    db_feeder = Feeder(
        feeder_name=feeder.feeder_name,
        substation_id=feeder.substation_id,
        voltage_level_kv=feeder.voltage_level_kv,
        geom=func.ST_GeomFromText(feeder.geom, 4326)
    )
    db.add(db_feeder)
    db.commit()
    db.refresh(db_feeder)
    return db_feeder

def get_feeder(db: Session, feeder_id: int) -> Optional[Feeder]:
    return db.query(Feeder).filter(Feeder.feeder_id == feeder_id).first()

def get_feeders(db: Session, skip: int = 0, limit: int = 100) -> List[Feeder]:
    return db.query(Feeder).offset(skip).limit(limit).all()

def update_feeder(db: Session, feeder_id: int, feeder_data: FeederCreateSchema) -> Optional[Feeder]:
    db_feeder = db.query(Feeder).filter(Feeder.feeder_id == feeder_id).first()
    if not db_feeder:
        return None

    db_feeder.feeder_name = feeder_data.feeder_name
    db_feeder.substation_id = feeder_data.substation_id
    db_feeder.voltage_level_kv = feeder_data.voltage_level_kv
    if feeder_data.geom:
        db_feeder.geom = func.ST_GeomFromText(feeder_data.geom, 4326)
    
    db.add(db_feeder)
    db.commit()
    db.refresh(db_feeder)
    return db_feeder

def delete_feeder(db: Session, feeder_id: int) -> Optional[Feeder]:
    db_feeder = db.query(Feeder).filter(Feeder.feeder_id == feeder_id).first()
    if not db_feeder:
        return None
    
    db.delete(db_feeder)
    db.commit()
    return db_feeder

def delete_substation(db: Session, substation_id: int) -> Optional[Substation]:
    """
    Delete a substation by its ID.
    """
    db_substation = db.query(Substation).filter(Substation.substation_id == substation_id).first()
    if not db_substation:
        return None
    
    db.delete(db_substation)
    db.commit()
    # The object is expired from the session after commit, but can still be returned
    # if accessed before the session is closed or if it was explicitly expired.
    # For a DELETE operation, returning the object might be useful for logging or confirmation.
    return db_substation

def get_substation(db: Session, substation_id: int) -> Optional[Substation]:
    """
    Retrieve a substation by its ID.
    """
    return db.query(Substation).filter(Substation.substation_id == substation_id).first()

def get_substations(db: Session, skip: int = 0, limit: int = 100) -> List[Substation]:
    """
    Retrieve a list of substations with pagination.
    """
    return db.query(Substation).offset(skip).limit(limit).all()

def update_substation(db: Session, substation_id: int, substation_data: RcesSubstationSchema) -> Optional[Substation]:
    """
    Update an existing substation.
    """
    db_substation = db.query(Substation).filter(Substation.substation_id == substation_id).first()
    if not db_substation:
        return None

    db_substation.substation_name = substation_data.substation_name
    db_substation.voltage_level_kv = substation_data.voltage_level_kv
    db_substation.status = substation_data.status
    if substation_data.geom: # Assuming geom is a WKT string
        db_substation.geom = func.ST_GeomFromText(substation_data.geom, 4326)
    
    db.add(db_substation) # or db.merge(db_substation) if you prefer
    db.commit()
    db.refresh(db_substation)
    return db_substation
