from fastapi import APIRouter, Depends, HTTPException, Request, FastAPI
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any
from app.database import SessionLocal

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

@router.post("/create-endpoint/")
def create_endpoint(req: EndpointRequest, db: Session = Depends(get_db)):
    return register_route(req.name, req.sql, router)

def register_route(name: str, sql: str, app_or_router):
    if name in registered_routes:
        raise HTTPException(status_code=400, detail="Endpoint already exists")

    path = f"/api/custom/{name}"

    async def dynamic_handler(request: Request, db: Session = Depends(get_db)):
        params: Dict[str, Any] = dict(request.query_params)
        try:
            result = db.execute(text(sql), params)
            return [dict(row) for row in result]
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    app_or_router.add_api_route(path, dynamic_handler, methods=["GET"])
    registered_routes[name] = sql
    return {"message": f"Dynamic GET endpoint created at {path}"}

# ✅ Re-register routes on startup
def init_dynamic_routes(app: FastAPI):
    for name, sql in registered_routes.items():
        register_route(name, sql, app)
