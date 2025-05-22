from fastapi import FastAPI, APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
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
# NOTE: Dynamically created routes are stored in-memory and will be lost on application restart.
# For persistent dynamic routes, consider storing these definitions in a database.
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
    # SECURITY NOTE: This function registers a route that executes a user-defined SQL query.
    # Refer to the security note in the 'create_endpoint' function for implications.
    path = f"/api/custom/{name}"

    def dynamic_handler(request: Request, db: Session = Depends(get_db)):
        params: Dict[str, Any] = dict(request.query_params)
        try:
            result = db.execute(text(sql), params)
            return [dict(row._mapping) for row in result]
        except SQLAlchemyError as e: # More specific database-related errors
            # Log the error e for debugging if a logging mechanism is in place
            raise HTTPException(status_code=500, detail=f"Database error: {e}")
        except Exception as e: # Catch-all for other unexpected errors
            # Log the error e for debugging
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

    app.add_api_route(path, dynamic_handler, methods=["GET"], name=name)
    registered_routes[name] = sql

@router.post("/create-endpoint/")
def create_endpoint(req: EndpointRequest, db: Session = Depends(get_db)):
    # SECURITY NOTE: The user-provided SQL query in 'req.sql' is executed directly.
    # Ensure that only trusted users have access to this endpoint, as malicious SQL
    # could lead to data breaches or loss if not properly vetted.
    # Parameter binding is used, which helps prevent SQL injection for parameter values,
    # but does not protect against vulnerabilities in the SQL structure itself.
    if req.name in registered_routes:
        raise HTTPException(status_code=400, detail="Endpoint already exists")
    register_dynamic_route(req.name, req.sql)
    return {"message": f"Dynamic GET endpoint created at /api/custom/{req.name}"}

# Register router and root
app.include_router(router, prefix="/api", tags=["Dynamic SQL"])

@app.get("/")
def root():
    return {"message": "Electric Network API is running"}
