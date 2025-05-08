# PostGIS Microservices QGIS Plugin

This QGIS plugin integrates with the PostGIS Microservices API and NextJS application, providing access to geospatial data management, DuckDB operations, Tippecanoe vector tile generation, workflow management with Kestra, and database monitoring.

## Features

- **Database Connection**: Connect to PostgreSQL/PostGIS and DuckDB databases
- **DuckDB Operations**: Run SQL queries on DuckDB databases, import data, and export results
- **Tippecanoe Vector Tiles**: Generate vector tiles from GeoJSON and Shapefile data
- **Workflow Management**: Manage and monitor Kestra workflows
- **Database Monitoring**: Monitor PostgreSQL/PostGIS database performance and status

## Installation

1. Download the plugin from the repository
2. Extract the `postgis_microservices_plugin` folder to your QGIS plugins directory:
   - Windows: `C:\Users\{username}\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins`
   - macOS: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins`
   - Linux: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins`
3. Enable the plugin in QGIS: `Plugins > Manage and Install Plugins > Installed > PostGIS Microservices`

## Configuration

1. Set up the API URL in the plugin settings
2. Create database connections for PostgreSQL/PostGIS and DuckDB
3. Configure monitoring for your databases

## Usage

### Database Connection

1. Click the "Database Connection" button in the plugin toolbar
2. Create a new connection or select an existing one
3. Test the connection to ensure it works

### DuckDB Operations

1. Click the "DuckDB Operations" button in the plugin toolbar
2. Select a DuckDB database
3. Write and execute SQL queries
4. Export results or add them to the map

### Tippecanoe Vector Tiles

1. Click the "Tippecanoe Vector Tiles" button in the plugin toolbar
2. Add input files from layers or file system
3. Configure output options
4. Generate vector tiles

### Workflow Management

1. Click the "Workflow Management" button in the plugin toolbar
2. Browse available workflows
3. Run, monitor, and manage workflow executions

### Database Monitoring

1. Click the "Database Monitoring" button in the plugin toolbar
2. Add databases to monitor
3. View performance metrics, connections, and PostGIS statistics

## Requirements

- QGIS 3.0 or later
- PostGIS Microservices API running and accessible
- Internet connection to access the API

## License

This plugin is licensed under the GPL v2 license.

## Support

For support, please open an issue on the GitHub repository or contact the author at your.email@example.com.
