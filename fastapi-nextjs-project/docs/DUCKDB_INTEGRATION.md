# DuckDB Integration

This document provides information about the DuckDB integration in the MCP Server application.

## Overview

The DuckDB integration allows users to:

1. Create and manage DuckDB databases
2. Import data from various file formats (CSV, Parquet, JSON, Excel, Shapefile, GeoPackage, GeoJSON)
3. Execute SQL queries on the data
4. Visualize query results in tables, charts, and maps
5. Export data to various formats
6. Connect to external databases (PostgreSQL, MySQL, SQLite)
7. Perform spatial analysis on geospatial data
8. Access local files and directories via SQL using the HostFS extension

## Setup and Configuration

### Prerequisites

To use the DuckDB integration, you need:

1. DuckDB Python package installed
2. Required DuckDB extensions (httpfs, spatial, postgres, mysql, sqlite, excel, odbc, hostfs, pivot_table, nanodbc)

### Configuration

The DuckDB integration is configured using environment variables:

```
# DuckDB settings
DUCKDB_DATA_DIR=/path/to/duckdb/data
DUCKDB_MEMORY_LIMIT=4GB
DUCKDB_TEMP_DIR=/path/to/duckdb/temp
DUCKDB_DEFAULT_OUTPUT_FORMAT=json

# HostFS settings
HOSTFS_ALLOWED_DIRS=/path/to/data,/path/to/uploads,/path/to/exports

# Cloud storage settings
S3_REGION=us-west-2
S3_ACCESS_KEY_ID=your_access_key
S3_SECRET_ACCESS_KEY=your_secret_key

AZURE_STORAGE_ACCOUNT=your_storage_account
AZURE_STORAGE_KEY=your_storage_key

GCS_PROJECT_ID=your_project_id
GCS_CREDENTIALS_PATH=/path/to/credentials.json

# Connection settings
POSTGRES_CONNECTION_STRING=postgresql://user:password@host:port/database
MYSQL_CONNECTION_STRING=mysql://user:password@host:port/database
SQLITE_CONNECTION_STRING=/path/to/database.sqlite
```

## Query Editor

The query editor is a web-based interface for executing SQL queries against DuckDB databases. It allows you to:

1. Write and execute SQL queries
2. View query results in a table
3. Visualize query results in charts and maps
4. Export query results to various formats

### SQL Syntax

DuckDB supports standard SQL syntax with some extensions for geospatial data:

```sql
-- Select all columns from a table
SELECT * FROM my_table;

-- Filter rows
SELECT * FROM my_table WHERE column_name = 'value';

-- Join tables
SELECT a.*, b.column_name
FROM table_a a
JOIN table_b b ON a.id = b.id;

-- Aggregate data
SELECT column_name, COUNT(*) as count
FROM my_table
GROUP BY column_name;

-- Spatial queries
SELECT ST_AsText(geometry_column) as wkt_geometry
FROM my_table
WHERE ST_Within(geometry_column, ST_GeomFromText('POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))'));
```

## Data Import

The DuckDB integration supports importing data from various file formats:

1. CSV
2. Parquet
3. JSON
4. Excel
5. Shapefile
6. GeoPackage
7. GeoJSON

### Import Methods

There are several ways to import data:

1. Upload a file through the web interface
2. Import a file from the server's file system
3. Import data from a URL
4. Import data from cloud storage (S3, Azure, GCS)

### Import Example

```sql
-- Import a CSV file
CREATE TABLE my_table AS SELECT * FROM read_csv('/path/to/file.csv', auto_detect=TRUE);

-- Import a Parquet file
CREATE TABLE my_table AS SELECT * FROM read_parquet('/path/to/file.parquet');

-- Import a GeoJSON file
CREATE TABLE my_table AS SELECT * FROM ST_Read('/path/to/file.geojson');
```

## Data Export

The DuckDB integration supports exporting data to various formats:

1. CSV
2. Parquet
3. JSON
4. GeoJSON
5. Shapefile
6. GeoPackage

### Export Methods

There are several ways to export data:

1. Download a file through the web interface
2. Export a file to the server's file system
3. Export data to cloud storage (S3, Azure, GCS)

### Export Example

```sql
-- Export to CSV
COPY my_table TO '/path/to/file.csv' (FORMAT CSV, HEADER);

-- Export to Parquet
COPY my_table TO '/path/to/file.parquet' (FORMAT PARQUET);

-- Export to JSON
COPY my_table TO '/path/to/file.json' (FORMAT JSON);
```

## Spatial Analysis

The DuckDB integration supports spatial analysis through the spatial extension:

1. Spatial functions (ST_Area, ST_Distance, ST_Intersection, etc.)
2. Spatial predicates (ST_Within, ST_Intersects, ST_Contains, etc.)
3. Spatial transformations (ST_Transform, ST_Simplify, ST_Buffer, etc.)
4. Spatial aggregations (ST_Union, ST_Collect, etc.)

## Local File Access with HostFS

The DuckDB integration includes support for accessing local files and directories using the HostFS extension. This allows you to:

1. List files and directories
2. Read file contents
3. Get file metadata
4. Check if files exist
5. Create directories
6. Remove files and directories

For security reasons, HostFS can only access directories that have been explicitly allowed. By default, the following directories are allowed:

1. The DuckDB data directory
2. The DuckDB temporary directory
3. The application's data directory
4. The application's uploads directory

Additional directories can be allowed by setting the `HOSTFS_ALLOWED_DIRS` environment variable.

### HostFS Example

```sql
-- List all files in a directory
SELECT * FROM hostfs_list_directory('/path/to/directory');

-- Read a CSV file
SELECT * FROM read_csv_auto(hostfs_file_path('/path/to/file.csv'));

-- Get file metadata
SELECT * FROM hostfs_file_info('/path/to/file.txt');
```

For more information and example SQL queries, see the [DuckDB HostFS documentation](./duckdb_hostfs.md).

## Pivot Table Extension

The DuckDB integration includes support for creating pivot tables using the Pivot Table extension. This allows you to:

1. Transform data from rows to columns
2. Create summary tables for data analysis
3. Generate cross-tabulations of data
4. Simplify complex aggregation queries

### Pivot Table Example

```sql
-- Basic pivot table
SELECT * FROM pivot(
    SELECT category, product, sales FROM sales_data,
    'category', -- The column to use for new column names
    'product',  -- The column to use for row identifiers
    'sales'     -- The column to aggregate
);

-- Pivot table with multiple aggregations
SELECT * FROM pivot(
    SELECT region, product, sales, quantity FROM sales_data,
    'region',
    'product',
    {'sales': 'sum', 'quantity': 'sum'}
);

-- Pivot table with custom column names
SELECT * FROM pivot(
    SELECT date_part('month', order_date) AS month, product, sales FROM sales_data,
    'month',
    'product',
    'sales',
    {'1': 'January', '2': 'February', '3': 'March'}
);
```

For more information, see the [DuckDB Pivot Table Extension documentation](https://duckdb.org/community_extensions/extensions/pivot_table.html).

## Nanodbc Extension

The DuckDB integration includes support for connecting to any ODBC database using the Nanodbc extension. This allows you to:

1. Connect to a wide variety of databases through ODBC
2. Query external databases directly from DuckDB
3. Join data between DuckDB and external databases
4. Import data from external databases into DuckDB
5. Export data from DuckDB to external databases

### Nanodbc Example

```sql
-- Connect to an ODBC data source
ATTACH 'Driver={SQL Server};Server=myserver;Database=mydatabase;Trusted_Connection=yes;' AS sqlserver (TYPE ODBC);

-- Query data from the ODBC data source
SELECT * FROM sqlserver.mydatabase.dbo.mytable;

-- Join data between DuckDB and the ODBC data source
SELECT d.*, s.column1, s.column2
FROM duckdb_table d
JOIN sqlserver.mydatabase.dbo.mytable s ON d.id = s.id;

-- Import data from the ODBC data source into DuckDB
CREATE TABLE imported_data AS
SELECT * FROM sqlserver.mydatabase.dbo.mytable;

-- Use parameterized queries with the ODBC data source
PREPARE stmt AS SELECT * FROM sqlserver.mydatabase.dbo.mytable WHERE id = $1;
EXECUTE stmt(42);
```

For more information, see the [DuckDB Nanodbc Extension documentation](https://duckdb.org/community_extensions/extensions/nanodbc.html).

### Spatial Example

```sql
-- Calculate the area of polygons
SELECT id, ST_Area(geometry_column) as area
FROM my_table;

-- Find points within a distance of a location
SELECT id, name
FROM points
WHERE ST_DWithin(geometry_column, ST_Point(-122.4194, 37.7749), 1000);

-- Reproject geometries
SELECT id, ST_Transform(geometry_column, 4326, 3857) as web_mercator_geometry
FROM my_table;
```

## External Database Connections

The DuckDB integration supports connecting to external databases:

1. PostgreSQL
2. MySQL
3. SQLite

### Connection Example

```sql
-- Connect to PostgreSQL
ATTACH 'postgresql://user:password@host:port/database' AS postgres (TYPE POSTGRES);

-- Query PostgreSQL tables
SELECT * FROM postgres.table_name;

-- Join DuckDB and PostgreSQL tables
SELECT a.*, b.column_name
FROM my_table a
JOIN postgres.table_name b ON a.id = b.id;
```

## API Endpoints

The following API endpoints are available for the DuckDB integration:

### Status and Information

- `GET /api/v1/duckdb/status` - Get the status of the DuckDB integration

### Query Execution

- `POST /api/v1/duckdb/query` - Execute a SQL query

### Table Management

- `POST /api/v1/duckdb/tables` - Create a table from a file
- `POST /api/v1/duckdb/tables/upload` - Create a table from an uploaded file
- `POST /api/v1/duckdb/tables/export` - Export a table to a file
- `POST /api/v1/duckdb/tables/export/download` - Export a table to a file and download it
- `GET /api/v1/duckdb/tables/{table_name}/schema` - Get the schema of a table
- `GET /api/v1/duckdb/tables` - Get a list of tables in the database
- `GET /api/v1/duckdb/tables/{table_name}/preview` - Get a preview of a table
- `GET /api/v1/duckdb/tables/{table_name}/statistics` - Get statistics for a table

### Database Management

- `POST /api/v1/duckdb/databases` - Create a new DuckDB database
- `DELETE /api/v1/duckdb/databases` - Delete a DuckDB database

### External Database Connections

- `POST /api/v1/duckdb/connect` - Connect to an external database

### Spatial Analysis

- `POST /api/v1/duckdb/spatial/query` - Execute a spatial query
- `POST /api/v1/duckdb/spatial/reproject` - Reproject a geometry column
- `POST /api/v1/duckdb/spatial/to-postgis` - Convert a table to PostGIS SQL
- `POST /api/v1/duckdb/spatial/to-postgis/download` - Convert a table to PostGIS SQL and download it

## Frontend Components

The frontend includes the following components for DuckDB integration:

- `DuckDBQueryEditor` - A component for executing SQL queries
- `DataTable` - A component for displaying query results in a table
- `DataChart` - A component for visualizing query results in charts
- `DataMap` - A component for visualizing geospatial query results on a map

## Usage

### Creating a Database

1. Navigate to the DuckDB page
2. Click the "New Database" button
3. Enter a name for the database
4. Click "Create"

### Importing Data

1. Navigate to the DuckDB page
2. Select a database
3. Click the "Upload File" button
4. Select a file to upload
5. Enter a name for the table
6. Click "Upload"

### Executing a Query

1. Navigate to the DuckDB page
2. Select a database
3. Enter a SQL query in the query editor
4. Click "Execute"
5. View the results in the table, chart, or map tab

### Exporting Data

1. Navigate to the DuckDB page
2. Select a database
3. Execute a query to get the data you want to export
4. Click the "Export" button
5. Select an export format
6. Click "Export"

## Troubleshooting

### Connection Issues

If you're having trouble connecting to DuckDB:

1. Check that the DuckDB data directory exists and is writable
2. Verify that the required DuckDB extensions are installed
3. Check the server logs for error messages

### Query Execution Issues

If a query fails to execute:

1. Check the SQL syntax
2. Verify that the tables and columns referenced in the query exist
3. Check for data type issues
4. Look for error messages in the response

### Import/Export Issues

If you're having trouble importing or exporting data:

1. Check that the file format is supported
2. Verify that the file is not corrupted
3. Check that the file size is not too large
4. Look for error messages in the response

## Limitations

The current implementation has the following limitations:

1. Limited support for complex spatial operations
2. No support for user-defined functions
3. Limited support for large datasets
4. No support for real-time data updates
