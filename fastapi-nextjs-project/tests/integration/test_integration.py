import os
import sys
import pytest
import json
import tempfile
import shutil
from pathlib import Path
from fastapi.testclient import TestClient

# Add the parent directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.main import app
from app.core.config import settings
from app.services.duckdb_service import duckdb_service
from app.services.martin_service import martin_service
from app.services.kestra_service import kestra_service

client = TestClient(app)

# Test data
TEST_GEOJSON = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"name": "Test Point"},
            "geometry": {"type": "Point", "coordinates": [0, 0]}
        }
    ]
}

@pytest.fixture(scope="module")
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture(scope="module")
def test_db_path(temp_dir):
    """Create a test DuckDB database."""
    db_path = os.path.join(temp_dir, "test.duckdb")
    conn = duckdb_service.get_connection(db_path)
    
    # Create a test table
    conn.execute("CREATE TABLE test_table (id INTEGER, name VARCHAR, value DOUBLE)")
    conn.execute("INSERT INTO test_table VALUES (1, 'test1', 1.1), (2, 'test2', 2.2), (3, 'test3', 3.3)")
    
    # Create a test spatial table
    conn.execute("CREATE TABLE test_spatial (id INTEGER, name VARCHAR, geometry VARCHAR)")
    conn.execute("INSERT INTO test_spatial VALUES (1, 'point', 'POINT(0 0)'), (2, 'line', 'LINESTRING(0 0, 1 1)')")
    
    yield db_path
    
    # Clean up
    duckdb_service.close_connection(db_path)

@pytest.fixture(scope="module")
def test_workflow():
    """Create a test workflow definition."""
    return {
        "id": "test_workflow",
        "namespace": "default",
        "tasks": [
            {
                "id": "hello",
                "type": "io.kestra.core.tasks.scripts.Bash",
                "commands": ["echo 'Hello, World!'"]
            }
        ]
    }

@pytest.fixture(scope="module")
def test_style():
    """Create a test MapLibre style."""
    return {
        "version": 8,
        "name": "Test Style",
        "sources": {
            "test-source": {
                "type": "vector",
                "url": "http://localhost:3000/tilejson/test.json"
            }
        },
        "layers": [
            {
                "id": "test-layer",
                "type": "fill",
                "source": "test-source",
                "source-layer": "test",
                "paint": {
                    "fill-color": "#ff0000",
                    "fill-opacity": 0.5
                }
            }
        ]
    }

# DuckDB Integration Tests
class TestDuckDBIntegration:
    def test_duckdb_status(self):
        """Test the DuckDB status endpoint."""
        response = client.get("/api/v1/duckdb/status")
        assert response.status_code == 200
        data = response.json()
        assert "data_dir" in data
        assert "extensions" in data
    
    def test_duckdb_query(self, test_db_path):
        """Test executing a query with DuckDB."""
        response = client.post(
            "/api/v1/duckdb/query",
            json={
                "query": "SELECT * FROM test_table ORDER BY id",
                "db_path": test_db_path
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["id"] == 1
        assert data[0]["name"] == "test1"
        assert data[0]["value"] == 1.1
    
    def test_duckdb_spatial_query(self, test_db_path):
        """Test executing a spatial query with DuckDB."""
        response = client.post(
            "/api/v1/duckdb/query",
            json={
                "query": "SELECT * FROM test_spatial WHERE geometry LIKE 'POINT%'",
                "db_path": test_db_path
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == 1
        assert data[0]["name"] == "point"
        assert data[0]["geometry"] == "POINT(0 0)"
    
    def test_duckdb_table_schema(self, test_db_path):
        """Test getting a table schema from DuckDB."""
        response = client.get(
            f"/api/v1/duckdb/tables/test_table/schema?db_path={test_db_path}"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["name"] == "id"
        assert data[0]["type"] == "INTEGER"
        assert data[1]["name"] == "name"
        assert data[1]["type"] == "VARCHAR"
        assert data[2]["name"] == "value"
        assert data[2]["type"] == "DOUBLE"
    
    def test_duckdb_table_preview(self, test_db_path):
        """Test getting a table preview from DuckDB."""
        response = client.get(
            f"/api/v1/duckdb/tables/test_table/preview?limit=2&db_path={test_db_path}"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["id"] == 1
        assert data[0]["name"] == "test1"
        assert data[0]["value"] == 1.1

# Kestra Workflow Integration Tests
@pytest.mark.skipif(not kestra_service.is_configured, reason="Kestra is not configured")
class TestKestraIntegration:
    def test_kestra_status(self):
        """Test the Kestra status endpoint."""
        response = client.get("/api/v1/workflows/status")
        assert response.status_code == 200
        data = response.json()
        assert "configured" in data
    
    def test_kestra_create_flow(self, test_workflow):
        """Test creating a workflow."""
        # Skip if Kestra is not available
        if not kestra_service.is_configured:
            pytest.skip("Kestra is not configured")
        
        # Delete the workflow if it already exists
        try:
            client.delete(f"/api/v1/workflows/flows/{test_workflow['namespace']}/{test_workflow['id']}")
        except:
            pass
        
        # Create the workflow
        response = client.post(
            "/api/v1/workflows/flows",
            json=test_workflow
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_workflow["id"]
        assert data["namespace"] == test_workflow["namespace"]
        
        # Clean up
        client.delete(f"/api/v1/workflows/flows/{test_workflow['namespace']}/{test_workflow['id']}")
    
    def test_kestra_execute_flow(self, test_workflow):
        """Test executing a workflow."""
        # Skip if Kestra is not available
        if not kestra_service.is_configured:
            pytest.skip("Kestra is not configured")
        
        # Create the workflow
        client.post(
            "/api/v1/workflows/flows",
            json=test_workflow
        )
        
        # Execute the workflow
        response = client.post(
            "/api/v1/workflows/flows/execute",
            json={
                "namespace": test_workflow["namespace"],
                "flow_id": test_workflow["id"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "executionId" in data
        
        # Clean up
        client.delete(f"/api/v1/workflows/flows/{test_workflow['namespace']}/{test_workflow['id']}")

# Martin MapLibre Integration Tests
@pytest.mark.skipif(not martin_service.get_server_status()["status"] == "ok", reason="Martin server is not available")
class TestMartinIntegration:
    def test_martin_status(self):
        """Test the Martin status endpoint."""
        response = client.get("/api/v1/martin/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "url" in data
    
    def test_martin_tables(self):
        """Test getting available tables from Martin."""
        response = client.get("/api/v1/martin/tables")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_martin_styles(self):
        """Test getting available styles from Martin."""
        response = client.get("/api/v1/martin/styles")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_martin_pmtiles(self):
        """Test getting available PMTiles from Martin."""
        response = client.get("/api/v1/martin/pmtiles")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_martin_create_style(self, test_style):
        """Test creating a style from a source."""
        # Skip if Martin is not available
        if not martin_service.get_server_status()["status"] == "ok":
            pytest.skip("Martin server is not available")
        
        # Create a temporary file for the style
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            f.write(json.dumps(test_style).encode())
            style_path = f.name
        
        try:
            # Upload the style
            with open(style_path, "rb") as f:
                files = {"file": (os.path.basename(style_path), f, "application/json")}
                response = client.post("/api/v1/martin/styles/upload", files=files)
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "success"
                assert "name" in data
                
                # Clean up
                client.delete(f"/api/v1/martin/styles/{os.path.basename(style_path)}")
        finally:
            # Remove the temporary file
            os.unlink(style_path)

# Cross-Component Integration Tests
class TestCrossComponentIntegration:
    def test_duckdb_to_martin(self, test_db_path, temp_dir):
        """Test converting DuckDB data to PMTiles for Martin."""
        # Skip if Martin or Tippecanoe is not available
        if not martin_service.get_server_status()["status"] == "ok" or not martin_service.is_tippecanoe_available:
            pytest.skip("Martin server or Tippecanoe is not available")
        
        # Export GeoJSON from DuckDB
        response = client.post(
            "/api/v1/duckdb/spatial/query",
            json={
                "query": "SELECT id, name, geometry FROM test_spatial",
                "db_path": test_db_path
            }
        )
        assert response.status_code == 200
        geojson_data = response.json()
        
        # Create PMTiles from GeoJSON
        response = client.post(
            "/api/v1/martin/pmtiles/create",
            json={
                "geojson_data": geojson_data,
                "output_name": "test_integration.pmtiles",
                "min_zoom": 0,
                "max_zoom": 5
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["name"] == "test_integration.pmtiles"
        
        # Clean up
        client.delete("/api/v1/martin/pmtiles/test_integration.pmtiles")
    
    def test_workflow_with_duckdb(self, test_db_path):
        """Test a workflow that uses DuckDB."""
        # Skip if Kestra is not available
        if not kestra_service.is_configured:
            pytest.skip("Kestra is not configured")
        
        # Create a workflow that uses DuckDB
        workflow = {
            "id": "test_duckdb_workflow",
            "namespace": "default",
            "tasks": [
                {
                    "id": "query_duckdb",
                    "type": "io.kestra.core.tasks.scripts.Python",
                    "script": f"""
import duckdb
import json

# Connect to DuckDB
conn = duckdb.connect('{test_db_path}')

# Execute a query
result = conn.execute("SELECT * FROM test_table ORDER BY id").fetchall()

# Convert to JSON
output = []
for row in result:
    output.append({{"id": row[0], "name": row[1], "value": row[2]}})

# Print the result
print(json.dumps(output))
                    """
                }
            ]
        }
        
        # Create the workflow
        client.post(
            "/api/v1/workflows/flows",
            json=workflow
        )
        
        # Execute the workflow
        response = client.post(
            "/api/v1/workflows/flows/execute",
            json={
                "namespace": workflow["namespace"],
                "flow_id": workflow["id"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "executionId" in data
        
        # Clean up
        client.delete(f"/api/v1/workflows/flows/{workflow['namespace']}/{workflow['id']}")
