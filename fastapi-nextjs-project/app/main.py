from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import api_router
from app.api.v1.ogc_api_processes import router as ogc_processes_router

app = FastAPI(
    title="MCP Server API",
    description="""
    MCP Server API provides geospatial data management and analysis capabilities.
    
    ## OGC API Processes
    
    The API includes OGC API Processes endpoints for spatial analysis and search:
    
    * `/api/v1/processes` - List all available processes
    * `/api/v1/processes/{processId}` - Get details about a specific process
    * `/api/v1/processes/{processId}/execution` - Execute a process
    
    These endpoints allow you to perform spatial analysis and search operations in a standardized way.
    """,
    version="1.0.0",
    openapi_url="/api/v1/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(api_router, prefix="/api/v1")
app.include_router(
    ogc_processes_router,
    prefix="/api/v1/processes",
    tags=["OGC API Processes"]
)

@app.get("/")
async def root():
    """
    Root endpoint
    
    Returns:
        Welcome message
    """
    return {"message": "Welcome to the MCP Server API"}
