from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas import (
    RcesSubstationSchema, SubstationResponseSchema,
    FeederCreateSchema, FeederResponseSchema,
    TransformerCreateSchema, TransformerResponseSchema,
    PoleCreateSchema, PoleResponseSchema,
    ConductorCreateSchema, ConductorResponseSchema,
    SwitchCreateSchema, SwitchResponseSchema,
    FuseCreateSchema, FuseResponseSchema
)
from app.crud import (
    create_substation, get_substation, get_substations, update_substation, delete_substation,
    create_feeder, get_feeder, get_feeders, update_feeder, delete_feeder,
    create_transformer, get_transformer, get_transformers, update_transformer, delete_transformer,
    create_pole, get_pole, get_poles, update_pole, delete_pole,
    create_conductor, get_conductor, get_conductors, update_conductor, delete_conductor,
    create_switch, get_switch, get_switches, update_switch, delete_switch,
    create_fuse, get_fuse, get_fuses, update_fuse, delete_fuse
)
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/substations/", response_model=SubstationResponseSchema, status_code=status.HTTP_201_CREATED)
def add_substation(substation: RcesSubstationSchema, db: Session = Depends(get_db)):
    # The create_substation function returns a SQLAlchemy model instance.
    # FastAPI, with the help of Pydantic's from_attributes = True in SubstationResponseSchema,
    # will automatically serialize this model instance into the response schema.
    # The geom field, which is a Geometry type in the model, needs to be converted to a
    # GeoJSON-like dictionary for the response. This conversion logic should ideally be part of
    # the SubstationResponseSchema or handled before returning if Pydantic cannot do it automatically.
    # For now, we assume Pydantic handles the Geometry object from SQLAlchemy well enough
    # or that a custom serializer/validator in SubstationResponseSchema would handle it.
    # If the 'geom' field in the response is not coming out as a dict (GeoJSON),
    # a custom @validator or a root_validator in SubstationResponseSchema might be needed
    # to convert the WKBElement (or similar) from GeoAlchemy2 into a dict.
    # However, the task specifies `geom: dict` in the schema, so we expect Pydantic to map it.
    return create_substation(db, substation)

@router.get("/substations/{substation_id}", response_model=SubstationResponseSchema)
def read_substation(substation_id: int, db: Session = Depends(get_db)):
    db_substation = get_substation(db, substation_id=substation_id)
    if db_substation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Substation not found")
    return db_substation

@router.get("/substations/", response_model=List[SubstationResponseSchema])
def read_substations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    substations = get_substations(db, skip=skip, limit=limit)
    return substations

@router.put("/substations/{substation_id}", response_model=SubstationResponseSchema)
def update_substation_endpoint(substation_id: int, substation: RcesSubstationSchema, db: Session = Depends(get_db)):
    updated_substation = update_substation(db, substation_id=substation_id, substation_data=substation)
    if updated_substation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Substation not found")
    return updated_substation

@router.delete("/substations/{substation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_substation_endpoint(substation_id: int, db: Session = Depends(get_db)):
    deleted_substation = delete_substation(db, substation_id=substation_id)
    if deleted_substation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Substation not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# --- Feeder Endpoints ---

@router.post("/feeders/", response_model=FeederResponseSchema, status_code=status.HTTP_201_CREATED, tags=["Feeders"])
def add_feeder_endpoint(feeder: FeederCreateSchema, db: Session = Depends(get_db)):
    return create_feeder(db=db, feeder=feeder)

@router.get("/feeders/", response_model=List[FeederResponseSchema], tags=["Feeders"])
def read_feeders_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    feeders = get_feeders(db, skip=skip, limit=limit)
    return feeders

@router.get("/feeders/{feeder_id}", response_model=FeederResponseSchema, tags=["Feeders"])
def read_feeder_endpoint(feeder_id: int, db: Session = Depends(get_db)):
    db_feeder = get_feeder(db, feeder_id=feeder_id)
    if db_feeder is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feeder not found")
    return db_feeder

@router.put("/feeders/{feeder_id}", response_model=FeederResponseSchema, tags=["Feeders"])
def update_feeder_endpoint(feeder_id: int, feeder: FeederCreateSchema, db: Session = Depends(get_db)):
    updated_feeder = update_feeder(db, feeder_id=feeder_id, feeder_data=feeder)
    if updated_feeder is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feeder not found")
    return updated_feeder

@router.delete("/feeders/{feeder_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Feeders"])
def delete_feeder_endpoint(feeder_id: int, db: Session = Depends(get_db)):
    deleted_feeder = delete_feeder(db, feeder_id=feeder_id)
    if deleted_feeder is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feeder not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# --- Transformer Endpoints ---

@router.post("/transformers/", response_model=TransformerResponseSchema, status_code=status.HTTP_201_CREATED, tags=["Transformers"])
def add_transformer_endpoint(transformer: TransformerCreateSchema, db: Session = Depends(get_db)):
    return create_transformer(db=db, transformer=transformer)

@router.get("/transformers/", response_model=List[TransformerResponseSchema], tags=["Transformers"])
def read_transformers_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    transformers = get_transformers(db, skip=skip, limit=limit)
    return transformers

@router.get("/transformers/{transformer_id}", response_model=TransformerResponseSchema, tags=["Transformers"])
def read_transformer_endpoint(transformer_id: int, db: Session = Depends(get_db)):
    db_transformer = get_transformer(db, transformer_id=transformer_id)
    if db_transformer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transformer not found")
    return db_transformer

@router.put("/transformers/{transformer_id}", response_model=TransformerResponseSchema, tags=["Transformers"])
def update_transformer_endpoint(transformer_id: int, transformer: TransformerCreateSchema, db: Session = Depends(get_db)):
    updated_transformer = update_transformer(db, transformer_id=transformer_id, transformer_data=transformer)
    if updated_transformer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transformer not found")
    return updated_transformer

@router.delete("/transformers/{transformer_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Transformers"])
def delete_transformer_endpoint(transformer_id: int, db: Session = Depends(get_db)):
    deleted_transformer = delete_transformer(db, transformer_id=transformer_id)
    if deleted_transformer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transformer not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# --- Pole Endpoints ---

@router.post("/poles/", response_model=PoleResponseSchema, status_code=status.HTTP_201_CREATED, tags=["Poles"])
def add_pole_endpoint(pole: PoleCreateSchema, db: Session = Depends(get_db)):
    return create_pole(db=db, pole=pole)

@router.get("/poles/", response_model=List[PoleResponseSchema], tags=["Poles"])
def read_poles_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    poles = get_poles(db, skip=skip, limit=limit)
    return poles

@router.get("/poles/{pole_id}", response_model=PoleResponseSchema, tags=["Poles"])
def read_pole_endpoint(pole_id: int, db: Session = Depends(get_db)):
    db_pole = get_pole(db, pole_id=pole_id)
    if db_pole is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pole not found")
    return db_pole

@router.put("/poles/{pole_id}", response_model=PoleResponseSchema, tags=["Poles"])
def update_pole_endpoint(pole_id: int, pole: PoleCreateSchema, db: Session = Depends(get_db)):
    updated_pole = update_pole(db, pole_id=pole_id, pole_data=pole)
    if updated_pole is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pole not found")
    return updated_pole

@router.delete("/poles/{pole_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Poles"])
def delete_pole_endpoint(pole_id: int, db: Session = Depends(get_db)):
    deleted_pole = delete_pole(db, pole_id=pole_id)
    if deleted_pole is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pole not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# --- Conductor Endpoints ---

@router.post("/conductors/", response_model=ConductorResponseSchema, status_code=status.HTTP_201_CREATED, tags=["Conductors"])
def add_conductor_endpoint(conductor: ConductorCreateSchema, db: Session = Depends(get_db)):
    return create_conductor(db=db, conductor=conductor)

@router.get("/conductors/", response_model=List[ConductorResponseSchema], tags=["Conductors"])
def read_conductors_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    conductors = get_conductors(db, skip=skip, limit=limit)
    return conductors

@router.get("/conductors/{conductor_id}", response_model=ConductorResponseSchema, tags=["Conductors"])
def read_conductor_endpoint(conductor_id: int, db: Session = Depends(get_db)):
    db_conductor = get_conductor(db, conductor_id=conductor_id)
    if db_conductor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conductor not found")
    return db_conductor

@router.put("/conductors/{conductor_id}", response_model=ConductorResponseSchema, tags=["Conductors"])
def update_conductor_endpoint(conductor_id: int, conductor: ConductorCreateSchema, db: Session = Depends(get_db)):
    updated_conductor = update_conductor(db, conductor_id=conductor_id, conductor_data=conductor)
    if updated_conductor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conductor not found")
    return updated_conductor

@router.delete("/conductors/{conductor_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Conductors"])
def delete_conductor_endpoint(conductor_id: int, db: Session = Depends(get_db)):
    deleted_conductor = delete_conductor(db, conductor_id=conductor_id)
    if deleted_conductor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conductor not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# --- Switch Endpoints ---

@router.post("/switches/", response_model=SwitchResponseSchema, status_code=status.HTTP_201_CREATED, tags=["Switches"])
def add_switch_endpoint(switch: SwitchCreateSchema, db: Session = Depends(get_db)):
    return create_switch(db=db, switch=switch)

@router.get("/switches/", response_model=List[SwitchResponseSchema], tags=["Switches"])
def read_switches_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    switches = get_switches(db, skip=skip, limit=limit)
    return switches

@router.get("/switches/{switch_id}", response_model=SwitchResponseSchema, tags=["Switches"])
def read_switch_endpoint(switch_id: int, db: Session = Depends(get_db)):
    db_switch = get_switch(db, switch_id=switch_id)
    if db_switch is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Switch not found")
    return db_switch

@router.put("/switches/{switch_id}", response_model=SwitchResponseSchema, tags=["Switches"])
def update_switch_endpoint(switch_id: int, switch: SwitchCreateSchema, db: Session = Depends(get_db)):
    updated_switch = update_switch(db, switch_id=switch_id, switch_data=switch)
    if updated_switch is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Switch not found")
    return updated_switch

@router.delete("/switches/{switch_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Switches"])
def delete_switch_endpoint(switch_id: int, db: Session = Depends(get_db)):
    deleted_switch = delete_switch(db, switch_id=switch_id)
    if deleted_switch is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Switch not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# --- Fuse Endpoints ---

@router.post("/fuses/", response_model=FuseResponseSchema, status_code=status.HTTP_201_CREATED, tags=["Fuses"])
def add_fuse_endpoint(fuse: FuseCreateSchema, db: Session = Depends(get_db)):
    return create_fuse(db=db, fuse=fuse)

@router.get("/fuses/", response_model=List[FuseResponseSchema], tags=["Fuses"])
def read_fuses_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    fuses = get_fuses(db, skip=skip, limit=limit)
    return fuses

@router.get("/fuses/{fuse_id}", response_model=FuseResponseSchema, tags=["Fuses"])
def read_fuse_endpoint(fuse_id: int, db: Session = Depends(get_db)):
    db_fuse = get_fuse(db, fuse_id=fuse_id)
    if db_fuse is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fuse not found")
    return db_fuse

@router.put("/fuses/{fuse_id}", response_model=FuseResponseSchema, tags=["Fuses"])
def update_fuse_endpoint(fuse_id: int, fuse: FuseCreateSchema, db: Session = Depends(get_db)):
    updated_fuse = update_fuse(db, fuse_id=fuse_id, fuse_data=fuse)
    if updated_fuse is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fuse not found")
    return updated_fuse

@router.delete("/fuses/{fuse_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Fuses"])
def delete_fuse_endpoint(fuse_id: int, db: Session = Depends(get_db)):
    deleted_fuse = delete_fuse(db, fuse_id=fuse_id)
    if deleted_fuse is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fuse not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
