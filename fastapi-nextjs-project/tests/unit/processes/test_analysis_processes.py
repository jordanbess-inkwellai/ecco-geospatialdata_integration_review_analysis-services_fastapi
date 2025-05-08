import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy import text
from app.services.processes.analysis_processes import (
    buffer_process,
    intersection_process,
    distance_process,
    area_process,
    convex_hull_process,
    simplify_process,
    voronoi_process
)

@pytest.fixture
def mock_db():
    """Create a mock database session."""
    db = AsyncMock()
    return db

@pytest.fixture
def mock_result():
    """Create a mock query result."""
    result = MagicMock()
    return result

@pytest.mark.asyncio
async def test_buffer_process(mock_db, mock_result):
    """Test the buffer process."""
    # Configure the mock
    mock_db.execute.return_value = mock_result
    mock_result.fetchone.return_value = MagicMock(buffered_geometry='{"type":"Polygon","coordinates":[[[0,0],[1,0],[1,1],[0,1],[0,0]]]}')
    
    # Define test inputs
    inputs = {
        "geometry": {"type": "Point", "coordinates": [0, 0]},
        "distance": 100
    }
    
    # Execute the process
    result = await buffer_process(inputs, mock_db)
    
    # Check that the database was called correctly
    mock_db.execute.assert_called_once()
    args, kwargs = mock_db.execute.call_args
    assert isinstance(args[0], text)
    assert "ST_Buffer" in str(args[0])
    assert kwargs["geometry"] == json.dumps(inputs["geometry"])
    assert kwargs["distance"] == inputs["distance"]
    
    # Check that the result is correct
    assert "buffered_geometry" in result
    assert result["buffered_geometry"]["type"] == "Polygon"

@pytest.mark.asyncio
async def test_intersection_process(mock_db, mock_result):
    """Test the intersection process."""
    # Configure the mock
    mock_db.execute.return_value = mock_result
    mock_result.fetchone.return_value = MagicMock(intersection_geometry='{"type":"Polygon","coordinates":[[[0,0],[1,0],[1,1],[0,1],[0,0]]]}')
    
    # Define test inputs
    inputs = {
        "geometry_a": {"type": "Polygon", "coordinates": [[[0,0],[2,0],[2,2],[0,2],[0,0]]]},
        "geometry_b": {"type": "Polygon", "coordinates": [[[1,1],[3,1],[3,3],[1,3],[1,1]]]}
    }
    
    # Execute the process
    result = await intersection_process(inputs, mock_db)
    
    # Check that the database was called correctly
    mock_db.execute.assert_called_once()
    args, kwargs = mock_db.execute.call_args
    assert isinstance(args[0], text)
    assert "ST_Intersection" in str(args[0])
    assert kwargs["geometry_a"] == json.dumps(inputs["geometry_a"])
    assert kwargs["geometry_b"] == json.dumps(inputs["geometry_b"])
    
    # Check that the result is correct
    assert "intersection_geometry" in result
    assert result["intersection_geometry"]["type"] == "Polygon"

@pytest.mark.asyncio
async def test_distance_process(mock_db, mock_result):
    """Test the distance process."""
    # Configure the mock
    mock_db.execute.return_value = mock_result
    mock_result.fetchone.return_value = MagicMock(distance=100.0)
    
    # Define test inputs
    inputs = {
        "geometry_a": {"type": "Point", "coordinates": [0, 0]},
        "geometry_b": {"type": "Point", "coordinates": [1, 1]},
        "use_spheroid": True
    }
    
    # Execute the process
    result = await distance_process(inputs, mock_db)
    
    # Check that the database was called correctly
    mock_db.execute.assert_called_once()
    args, kwargs = mock_db.execute.call_args
    assert isinstance(args[0], text)
    assert "ST_Distance" in str(args[0])
    assert kwargs["geometry_a"] == json.dumps(inputs["geometry_a"])
    assert kwargs["geometry_b"] == json.dumps(inputs["geometry_b"])
    assert kwargs["use_spheroid"] == inputs["use_spheroid"]
    
    # Check that the result is correct
    assert "distance" in result
    assert result["distance"] == 100.0

@pytest.mark.asyncio
async def test_area_process(mock_db, mock_result):
    """Test the area process."""
    # Configure the mock
    mock_db.execute.return_value = mock_result
    mock_result.fetchone.return_value = MagicMock(area=100.0)
    
    # Define test inputs
    inputs = {
        "geometry": {"type": "Polygon", "coordinates": [[[0,0],[1,0],[1,1],[0,1],[0,0]]]}
    }
    
    # Execute the process
    result = await area_process(inputs, mock_db)
    
    # Check that the database was called correctly
    mock_db.execute.assert_called_once()
    args, kwargs = mock_db.execute.call_args
    assert isinstance(args[0], text)
    assert "ST_Area" in str(args[0])
    assert kwargs["geometry"] == json.dumps(inputs["geometry"])
    
    # Check that the result is correct
    assert "area" in result
    assert result["area"] == 100.0

@pytest.mark.asyncio
async def test_convex_hull_process(mock_db, mock_result):
    """Test the convex hull process."""
    # Configure the mock
    mock_db.execute.return_value = mock_result
    mock_result.fetchone.return_value = MagicMock(convex_hull='{"type":"Polygon","coordinates":[[[0,0],[1,0],[1,1],[0,1],[0,0]]]}')
    
    # Define test inputs
    inputs = {
        "geometry": {"type": "MultiPoint", "coordinates": [[0,0],[1,0],[1,1],[0,1]]}
    }
    
    # Execute the process
    result = await convex_hull_process(inputs, mock_db)
    
    # Check that the database was called correctly
    mock_db.execute.assert_called_once()
    args, kwargs = mock_db.execute.call_args
    assert isinstance(args[0], text)
    assert "ST_ConvexHull" in str(args[0])
    assert kwargs["geometry"] == json.dumps(inputs["geometry"])
    
    # Check that the result is correct
    assert "convex_hull" in result
    assert result["convex_hull"]["type"] == "Polygon"

@pytest.mark.asyncio
async def test_simplify_process(mock_db, mock_result):
    """Test the simplify process."""
    # Configure the mock
    mock_db.execute.return_value = mock_result
    mock_result.fetchone.return_value = MagicMock(simplified_geometry='{"type":"Polygon","coordinates":[[[0,0],[1,0],[1,1],[0,1],[0,0]]]}')
    
    # Define test inputs
    inputs = {
        "geometry": {"type": "Polygon", "coordinates": [[[0,0],[0.5,0.1],[1,0],[1,1],[0.5,0.9],[0,1],[0,0]]]},
        "tolerance": 0.2,
        "preserve_topology": True
    }
    
    # Execute the process
    result = await simplify_process(inputs, mock_db)
    
    # Check that the database was called correctly
    mock_db.execute.assert_called_once()
    args, kwargs = mock_db.execute.call_args
    assert isinstance(args[0], text)
    assert "ST_SimplifyPreserveTopology" in str(args[0])
    assert kwargs["geometry"] == json.dumps(inputs["geometry"])
    assert kwargs["tolerance"] == inputs["tolerance"]
    
    # Check that the result is correct
    assert "simplified_geometry" in result
    assert result["simplified_geometry"]["type"] == "Polygon"

@pytest.mark.asyncio
async def test_simplify_process_without_topology(mock_db, mock_result):
    """Test the simplify process without preserving topology."""
    # Configure the mock
    mock_db.execute.return_value = mock_result
    mock_result.fetchone.return_value = MagicMock(simplified_geometry='{"type":"Polygon","coordinates":[[[0,0],[1,0],[1,1],[0,1],[0,0]]]}')
    
    # Define test inputs
    inputs = {
        "geometry": {"type": "Polygon", "coordinates": [[[0,0],[0.5,0.1],[1,0],[1,1],[0.5,0.9],[0,1],[0,0]]]},
        "tolerance": 0.2,
        "preserve_topology": False
    }
    
    # Execute the process
    result = await simplify_process(inputs, mock_db)
    
    # Check that the database was called correctly
    mock_db.execute.assert_called_once()
    args, kwargs = mock_db.execute.call_args
    assert isinstance(args[0], text)
    assert "ST_Simplify" in str(args[0])
    assert kwargs["geometry"] == json.dumps(inputs["geometry"])
    assert kwargs["tolerance"] == inputs["tolerance"]
    
    # Check that the result is correct
    assert "simplified_geometry" in result
    assert result["simplified_geometry"]["type"] == "Polygon"

@pytest.mark.asyncio
async def test_voronoi_process(mock_db, mock_result):
    """Test the Voronoi process."""
    # Configure the mock
    mock_db.execute.return_value = mock_result
    mock_result.fetchone.return_value = MagicMock(voronoi_polygons='{"type":"GeometryCollection","geometries":[{"type":"Polygon","coordinates":[[[0,0],[1,0],[1,1],[0,1],[0,0]]]}]}')
    
    # Define test inputs
    inputs = {
        "points": {"type": "MultiPoint", "coordinates": [[0,0],[1,0],[1,1],[0,1]]},
        "tolerance": 0.0,
        "bounds": {"type": "Polygon", "coordinates": [[[-1,-1],[2,-1],[2,2],[-1,2],[-1,-1]]]}
    }
    
    # Execute the process
    result = await voronoi_process(inputs, mock_db)
    
    # Check that the database was called correctly
    mock_db.execute.assert_called_once()
    args, kwargs = mock_db.execute.call_args
    assert isinstance(args[0], text)
    assert "ST_VoronoiPolygons" in str(args[0])
    assert kwargs["point"] == json.dumps(inputs["points"])
    assert kwargs["tolerance"] == inputs["tolerance"]
    assert kwargs["bounds"] == json.dumps(inputs["bounds"])
    
    # Check that the result is correct
    assert "voronoi_polygons" in result
    assert result["voronoi_polygons"]["type"] == "GeometryCollection"
