from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.elec_schemas import RcesSubstationSchema
from app.crud.elec_crud import create_substation

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/substations/")
def add_substation(substation: RcesSubstationSchema, db: Session = Depends(get_db)):
    return create_substation(db, substation)
