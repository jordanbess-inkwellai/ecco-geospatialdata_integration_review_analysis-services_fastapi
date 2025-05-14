from fastapi import FastAPI, APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any
from app.database import SessionLocal, Base, engine

app = FastAPI(
    title="Electric Network API",
    description="API for querying electric infrastructure dynamically.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Create tables (if managed via SQLAlchemy)
Base.metadata.create_all(bind=engine)

# Dynamic routing setup
router = APIRouter()
registered_routes = {}

class EndpointRequest(BaseModel):
    name: str
    sql: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def register_dynamic_route(name: str, sql: str):
    path = f"/api/custom/{name}"

    async def dynamic_handler(request: Request, db: Session = Depends(get_db)):
        params: Dict[str, Any] = dict(request.query_params)
        try:
            result = db.execute(text(sql), params)
            return [dict(row._mapping) for row in result]
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    app.add_api_route(path, dynamic_handler, methods=["GET"], name=name)
    registered_routes[name] = sql

@router.post("/create-endpoint/")
def create_endpoint(req: EndpointRequest, db: Session = Depends(get_db)):
    if req.name in registered_routes:
        raise HTTPException(status_code=400, detail="Endpoint already exists")
    register_dynamic_route(req.name, req.sql)
    return {"message": f"Dynamic GET endpoint created at /api/custom/{req.name}"}

# Register router and root
app.include_router(router, prefix="/api", tags=["Dynamic SQL"])

@app.get("/")
def root():
    return {"message": "Electric Network API is running"}
