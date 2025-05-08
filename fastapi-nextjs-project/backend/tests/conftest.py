import os
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from fastapi.testclient import TestClient
import duckdb
import tempfile
import shutil

from app.core.database import Base, get_db
from app.main import app
from app.models.metadata import (
    MetadataDataset, 
    MetadataKeyword, 
    MetadataContact, 
    MetadataAttribute,
    MetadataHarvestJob
)

# Test database URL
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL", 
    "postgresql+asyncpg://postgres:postgres@localhost:5432/test_postgis_microservices"
)

# Create async engine for testing
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    echo=False
)

# Create async session for testing
TestingSessionLocal = sessionmaker(
    test_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# DuckDB test database path
DUCKDB_TEST_PATH = os.path.join(tempfile.gettempdir(), "test_duckdb.db")


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def setup_database() -> AsyncGenerator:
    """Set up the test database."""
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Drop all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(setup_database) -> AsyncGenerator:
    """Create a fresh database session for each test."""
    async with TestingSessionLocal() as session:
        yield session
        # Roll back all changes
        await session.rollback()


@pytest.fixture
async def client(db_session) -> AsyncGenerator:
    """Create a test client with a database session."""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def duckdb_connection():
    """Create a DuckDB connection for testing."""
    # Remove existing test database if it exists
    if os.path.exists(DUCKDB_TEST_PATH):
        os.remove(DUCKDB_TEST_PATH)
    
    # Create a new DuckDB database
    conn = duckdb.connect(DUCKDB_TEST_PATH)
    
    # Load spatial extension
    conn.execute("INSTALL spatial;")
    conn.execute("LOAD spatial;")
    
    # Load httpfs extension for remote data access
    conn.execute("INSTALL httpfs;")
    conn.execute("LOAD httpfs;")
    
    yield conn
    
    # Close connection
    conn.close()
    
    # Remove test database
    if os.path.exists(DUCKDB_TEST_PATH):
        os.remove(DUCKDB_TEST_PATH)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_geojson(temp_dir):
    """Create a sample GeoJSON file for testing."""
    geojson_content = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "name": "Test Point",
                    "value": 42
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [0, 0]
                }
            },
            {
                "type": "Feature",
                "properties": {
                    "name": "Test Polygon",
                    "value": 100
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [0, 0],
                            [1, 0],
                            [1, 1],
                            [0, 1],
                            [0, 0]
                        ]
                    ]
                }
            }
        ]
    }
    
    import json
    file_path = os.path.join(temp_dir, "test.geojson")
    with open(file_path, "w") as f:
        json.dump(geojson_content, f)
    
    return file_path
