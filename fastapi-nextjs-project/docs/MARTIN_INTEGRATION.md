# Martin MapLibre Integration

This document provides information about the Martin MapLibre integration in the MCP Server application.

## Overview

The Martin MapLibre integration allows users to:

1. Visualize geospatial data from PostGIS databases using vector tiles
2. Upload and manage PMTiles, MBTiles, raster tiles, and terrain tiles
3. Create and customize MapLibre GL styles
4. Combine data from multiple sources in a single map
5. Export data to various formats

## Setup and Configuration

### Prerequisites

To use the Martin MapLibre integration, you need:

1. A running Martin server (https://martin.maplibre.org/)
2. PostGIS database with geospatial data
3. (Optional) Tippecanoe for creating PMTiles

### Configuration

The Martin integration is configured using environment variables:

```
# Martin server settings
MARTIN_SERVER_URL=http://localhost:3000

# Database connection settings
MARTIN_PG_CONNECTION_STRING=postgresql://postgres:postgres@localhost:5432/postgres

# Tile cache settings
MARTIN_CACHE_DIRECTORY=/path/to/cache

# Tile settings
MARTIN_DEFAULT_TILE_FORMAT=pbf

# PMTiles settings
MARTIN_PMTILES_DIRECTORY=/path/to/pmtiles

# MBTiles settings
MARTIN_MBTILES_DIRECTORY=/path/to/mbtiles

# Raster tiles settings
MARTIN_RASTER_DIRECTORY=/path/to/raster

# Terrain tiles settings
MARTIN_TERRAIN_DIRECTORY=/path/to/terrain

# Default style settings
MARTIN_DEFAULT_STYLE_DIRECTORY=/path/to/styles

# Tippecanoe settings
TIPPECANOE_PATH=tippecanoe
```

## Map Viewer

The map viewer is a web-based interface for visualizing geospatial data. It allows you to:

1. View data from PostGIS tables as vector tiles
2. View data from PMTiles, MBTiles, raster tiles, and terrain tiles
3. Customize the map style
4. Toggle layer visibility
5. Export data to various formats

### Supported Data Sources

The map viewer supports the following data sources:

1. PostGIS tables
2. PMTiles
3. MBTiles
4. Raster tiles (GeoTIFF)
5. Terrain tiles

### Supported Tile Formats

The map viewer supports the following tile formats:

1. Vector tiles (PBF, MVT)
2. Raster tiles (PNG, JPG, WebP)
3. Terrain tiles

## Style Editor

The style editor is a web-based interface for creating and customizing MapLibre GL styles. It allows you to:

1. Create new styles
2. Edit existing styles
3. Add and remove layers
4. Customize layer properties
5. Add and remove sources
6. Export styles to JSON

### Style Format

The style editor uses the MapLibre GL style specification, which is compatible with the Mapbox GL style specification. A style consists of:

1. Sources: Data sources for the map
2. Layers: Visual representations of the data
3. Metadata: Information about the style
4. Sprite: Icons and patterns
5. Glyphs: Font glyphs for text rendering

Example style:

```json
{
  "version": 8,
  "name": "My Style",
  "sources": {
    "my-source": {
      "type": "vector",
      "url": "http://localhost:3000/tilejson/my_table.json"
    }
  },
  "layers": [
    {
      "id": "my-layer",
      "type": "fill",
      "source": "my-source",
      "source-layer": "my_table",
      "paint": {
        "fill-color": "#ff0000",
        "fill-opacity": 0.5
      }
    }
  ]
}
```

## PMTiles

PMTiles is a single-file format for hosting map tiles. It is designed to be served from static storage, such as S3, without the need for a server.

### Creating PMTiles

You can create PMTiles using Tippecanoe:

```bash
tippecanoe -o output.pmtiles -z 14 input.geojson
```

### Uploading PMTiles

You can upload PMTiles through the web interface or using the API:

```bash
curl -X POST -F "file=@output.pmtiles" http://localhost:8000/api/v1/martin/pmtiles/upload
```

### Using PMTiles

Once uploaded, PMTiles can be used as a source in a MapLibre GL style:

```json
{
  "sources": {
    "my-pmtiles": {
      "type": "vector",
      "url": "http://localhost:3000/pmtiles/output.pmtiles"
    }
  }
}
```

## MBTiles

MBTiles is a specification for storing tiled map data in SQLite databases. It is designed to be portable and self-contained.

### Uploading MBTiles

You can upload MBTiles through the web interface or using the API:

```bash
curl -X POST -F "file=@output.mbtiles" http://localhost:8000/api/v1/martin/mbtiles/upload
```

### Using MBTiles

Once uploaded, MBTiles can be used as a source in a MapLibre GL style:

```json
{
  "sources": {
    "my-mbtiles": {
      "type": "vector",
      "url": "http://localhost:3000/mbtiles/output.mbtiles"
    }
  }
}
```

## Raster Tiles

Raster tiles are image-based tiles that can be used for satellite imagery, elevation data, or other raster datasets.

### Uploading Raster Tiles

You can upload raster tiles (GeoTIFF) through the web interface or using the API:

```bash
curl -X POST -F "file=@output.tif" http://localhost:8000/api/v1/martin/raster/upload
```

### Using Raster Tiles

Once uploaded, raster tiles can be used as a source in a MapLibre GL style:

```json
{
  "sources": {
    "my-raster": {
      "type": "raster",
      "url": "http://localhost:3000/raster/output.tif"
    }
  }
}
```

## Terrain Tiles

Terrain tiles are used for 3D terrain visualization.

### Uploading Terrain Tiles

You can upload terrain tiles through the web interface or using the API:

```bash
curl -X POST -F "file=@output.terrain" http://localhost:8000/api/v1/martin/terrain/upload
```

### Using Terrain Tiles

Once uploaded, terrain tiles can be used as a source in a MapLibre GL style:

```json
{
  "sources": {
    "my-terrain": {
      "type": "raster-dem",
      "url": "http://localhost:3000/terrain/output.terrain"
    }
  }
}
```

## API Endpoints

The following API endpoints are available for the Martin MapLibre integration:

### Status and Information

- `GET /api/v1/martin/status` - Get the status of the Martin server

### Tables

- `GET /api/v1/martin/tables` - Get a list of available tables
- `GET /api/v1/martin/tables/{table_name}/metadata` - Get metadata for a table
- `GET /api/v1/martin/tables/{table_name}/tilejson` - Get TileJSON for a table
- `GET /api/v1/martin/tables/{table_name}/tiles/{z}/{x}/{y}` - Get a tile for a table

### PMTiles

- `GET /api/v1/martin/pmtiles` - Get a list of available PMTiles
- `POST /api/v1/martin/pmtiles/upload` - Upload a PMTiles file
- `DELETE /api/v1/martin/pmtiles/{file_name}` - Delete a PMTiles file
- `POST /api/v1/martin/pmtiles/create` - Create PMTiles from GeoJSON data

### MBTiles

- `GET /api/v1/martin/mbtiles` - Get a list of available MBTiles
- `POST /api/v1/martin/mbtiles/upload` - Upload an MBTiles file
- `DELETE /api/v1/martin/mbtiles/{file_name}` - Delete an MBTiles file

### Raster Tiles

- `GET /api/v1/martin/raster` - Get a list of available raster tiles
- `POST /api/v1/martin/raster/upload` - Upload a raster tiles file
- `DELETE /api/v1/martin/raster/{file_name}` - Delete a raster tiles file

### Terrain Tiles

- `GET /api/v1/martin/terrain` - Get a list of available terrain tiles
- `POST /api/v1/martin/terrain/upload` - Upload a terrain tiles file
- `DELETE /api/v1/martin/terrain/{file_name}` - Delete a terrain tiles file

### Styles

- `GET /api/v1/martin/styles` - Get a list of available styles
- `POST /api/v1/martin/styles/upload` - Upload a style file
- `DELETE /api/v1/martin/styles/{file_name}` - Delete a style file
- `POST /api/v1/martin/styles/create` - Create a style from a source

## Frontend Components

The frontend includes the following components for Martin MapLibre integration:

- `MapViewer` - A component for viewing maps
- `MapLibreMap` - A component for rendering MapLibre GL maps
- `StyleEditor` - A component for editing MapLibre GL styles

## Usage

### Viewing a Map

1. Navigate to the Martin page
2. Select a style from the Styles tab
3. Toggle layer visibility as needed
4. Zoom and pan to explore the map

### Uploading PMTiles

1. Navigate to the Martin page
2. Select the Layers tab
3. Click the upload button in the PMTiles section
4. Select a PMTiles file to upload
5. Click Upload

### Creating a Style

1. Navigate to the Martin page
2. Select the Styles tab
3. Click the upload button
4. Select a style file to upload
5. Click Upload

### Editing a Style

1. Navigate to the Martin page
2. Select the Styles tab
3. Click the edit button for a style
4. Make changes to the style
5. Click Save

## Troubleshooting

### Connection Issues

If you're having trouble connecting to the Martin server:

1. Check that the Martin server is running
2. Verify the `MARTIN_SERVER_URL` environment variable
3. Check the server logs for error messages

### Tile Loading Issues

If tiles are not loading:

1. Check that the table exists in the database
2. Verify that the table has a geometry column
3. Check that the geometry column is indexed
4. Check that the table has a primary key

### Style Issues

If the style is not rendering correctly:

1. Check that the style is valid JSON
2. Verify that the sources exist
3. Check that the layers reference valid sources
4. Check that the layer types are appropriate for the data

## Limitations

The current implementation has the following limitations:

1. Limited support for 3D visualization
2. No support for client-side filtering
3. Limited support for complex styles
4. No support for real-time data updates
