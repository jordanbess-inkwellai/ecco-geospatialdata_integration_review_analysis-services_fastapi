# OGC API Processes Documentation

The MCP Server implements the OGC API Processes standard to provide standardized access to geospatial analysis and search capabilities.

## Endpoints

- `GET /api/v1/processes` - List all available processes
- `GET /api/v1/processes/{processId}` - Get details about a specific process
- `POST /api/v1/processes/{processId}/execution` - Execute a process

## Available Processes

### Spatial Analysis Processes

- **buffer** - Buffer a geometry by a specified distance
- **intersection** - Find the intersection of two geometries
- **distance** - Calculate the distance between two geometries
- **area** - Calculate the area of a geometry
- **convex_hull** - Generate a convex hull from a geometry
- **simplify** - Simplify a geometry using the Douglas-Peucker algorithm
- **voronoi** - Generate a Voronoi diagram from a set of points

### Spatial Search Processes

- **bbox_search** - Search for features within a bounding box
- **spatial_relationship_search** - Search for features with a specific spatial relationship to a geometry
- **nearest_neighbor** - Find the nearest neighbors to a geometry
- **attribute_spatial_filter** - Filter features by attribute and spatial criteria

### Raster Analysis Processes

- **raster_value_at_point** - Get the raster value at a point
- **raster_statistics** - Calculate statistics for a raster within a geometry
- **raster_contour** - Generate contour lines from a raster

### Network Analysis Processes

- **shortest_path** - Find the shortest path between two points using pgRouting
- **service_area** - Find the service area around a point using pgRouting

## Example Usage

### Buffer a Point

```json
POST /api/v1/processes/buffer/execution

{
  "geometry": {
    "type": "Point",
    "coordinates": [0, 0]
  },
  "distance": 100
}
```

### Search for Features in a Bounding Box

```json
POST /api/v1/processes/bbox_search/execution

{
  "bbox": [-122.5, 47.2, -122.3, 47.4],
  "table_name": "public.buildings",
  "limit": 10
}
```

## Client Integration

The OGC API Processes can be used from any HTTP client, including:

- The QGIS Plugin
- The NextJS PWA
- Marimo Notebooks
- Other OGC API Processes clients

## QGIS Plugin Integration

The QGIS plugin provides a user-friendly interface for discovering and executing OGC API Processes:

1. Click the "OGC API Processes" button in the toolbar
2. Browse the available processes
3. Select a process to view its details
4. Fill in the input parameters
5. Click "Execute Process" to run the process
6. View the results and add them to the map

## NextJS PWA Integration

The NextJS PWA provides a web-based interface for working with OGC API Processes:

1. Navigate to the "Analysis" section
2. Browse the available processes
3. Select a process to view its details
4. Fill in the input parameters
5. Click "Execute" to run the process
6. View the results on the map or download them

## Marimo Integration

Marimo notebooks can use the OGC API Processes through the Python requests library:

```python
import requests
import json

# Define the API endpoint
api_url = "http://localhost:8000/api/v1"

# Get the list of available processes
response = requests.get(f"{api_url}/processes")
processes = response.json()

# Get details about a specific process
process_id = "buffer"
response = requests.get(f"{api_url}/processes/{process_id}")
process_details = response.json()

# Execute a process
inputs = {
    "geometry": {
        "type": "Point",
        "coordinates": [0, 0]
    },
    "distance": 100
}
response = requests.post(f"{api_url}/processes/{process_id}/execution", json=inputs)
result = response.json()

# Display the result
print(json.dumps(result, indent=2))
```
