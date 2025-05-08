# DuckDB HostFS Extension

The HostFS extension for DuckDB allows you to access local files and directories directly via SQL. This document provides information on how to use the HostFS extension in the MCP Server application.

## Overview

The HostFS extension provides SQL functions to:
- List files and directories
- Read file contents
- Get file metadata
- Check if files exist
- Create directories
- Remove files and directories

## Security Considerations

For security reasons, the HostFS extension requires explicit permission to access directories on the host system. In the MCP Server application, the following directories are allowed by default:

1. The DuckDB data directory
2. The DuckDB temporary directory
3. The application's data directory
4. The application's uploads directory

Additional directories can be allowed by setting the `HOSTFS_ALLOWED_DIRS` environment variable to a comma-separated list of directories.

## Example SQL Queries

### Listing Files in a Directory

```sql
-- List all files in a directory
SELECT * FROM hostfs_list_directory('/path/to/directory');

-- List all files in a directory recursively
SELECT * FROM hostfs_list_directory('/path/to/directory', true);

-- List all CSV files in a directory
SELECT * 
FROM hostfs_list_directory('/path/to/directory') 
WHERE name LIKE '%.csv';
```

### Reading File Contents

```sql
-- Read a text file
SELECT * FROM hostfs_read_text('/path/to/file.txt');

-- Read a CSV file
SELECT * FROM read_csv_auto(hostfs_file_path('/path/to/file.csv'));

-- Read a Parquet file
SELECT * FROM read_parquet(hostfs_file_path('/path/to/file.parquet'));

-- Read a JSON file
SELECT * FROM read_json_auto(hostfs_file_path('/path/to/file.json'));

-- Read an Excel file
SELECT * FROM read_excel(hostfs_file_path('/path/to/file.xlsx'));

-- Read a spatial file (Shapefile, GeoPackage, GeoJSON)
SELECT * FROM ST_Read(hostfs_file_path('/path/to/file.shp'));
```

### Getting File Metadata

```sql
-- Get file metadata
SELECT * FROM hostfs_file_info('/path/to/file.txt');

-- Check if a file exists
SELECT hostfs_file_exists('/path/to/file.txt');

-- Get file size
SELECT size FROM hostfs_file_info('/path/to/file.txt');

-- Get file modification time
SELECT last_modified FROM hostfs_file_info('/path/to/file.txt');
```

### Creating and Removing Directories

```sql
-- Create a directory
CALL hostfs_create_directory('/path/to/new_directory');

-- Remove a file
CALL hostfs_remove_file('/path/to/file.txt');

-- Remove a directory
CALL hostfs_remove_directory('/path/to/directory');

-- Remove a directory recursively
CALL hostfs_remove_directory('/path/to/directory', true);
```

### Working with Multiple Files

```sql
-- List all CSV files in a directory and read them
WITH files AS (
    SELECT name 
    FROM hostfs_list_directory('/path/to/directory') 
    WHERE name LIKE '%.csv'
)
SELECT * 
FROM files, 
     read_csv_auto(hostfs_file_path(concat('/path/to/directory/', name)));

-- Combine multiple CSV files into a single table
WITH files AS (
    SELECT name 
    FROM hostfs_list_directory('/path/to/directory') 
    WHERE name LIKE '%.csv'
)
SELECT * 
FROM files, 
     read_csv_auto(hostfs_file_path(concat('/path/to/directory/', name)))
UNION ALL
SELECT * 
FROM read_csv_auto(hostfs_file_path('/path/to/another_directory/file.csv'));
```

### Exporting Data

```sql
-- Export a query result to a CSV file
COPY (SELECT * FROM my_table) TO hostfs_file_path('/path/to/output.csv') (FORMAT CSV, HEADER);

-- Export a query result to a Parquet file
COPY (SELECT * FROM my_table) TO hostfs_file_path('/path/to/output.parquet') (FORMAT PARQUET);

-- Export a query result to a JSON file
COPY (SELECT * FROM my_table) TO hostfs_file_path('/path/to/output.json') (FORMAT JSON);
```

## Integration with Other Extensions

HostFS works well with other DuckDB extensions:

### Spatial Data

```sql
-- Read a spatial file and perform spatial operations
SELECT ST_Area(geometry) 
FROM ST_Read(hostfs_file_path('/path/to/file.shp'));

-- Reproject a spatial file
SELECT ST_Transform(geometry, 4326, 3857) 
FROM ST_Read(hostfs_file_path('/path/to/file.shp'));
```

### HTTP and HostFS

```sql
-- Download a file from the web and save it locally
CALL hostfs_write_text(
    '/path/to/output.csv',
    (SELECT * FROM http_get('https://example.com/data.csv'))
);

-- Read a file from the web, process it, and save it locally
COPY (
    SELECT * 
    FROM read_csv_auto('https://example.com/data.csv')
    WHERE value > 100
) TO hostfs_file_path('/path/to/filtered_data.csv') (FORMAT CSV, HEADER);
```

## API Integration

The HostFS extension is integrated with the DuckDB API in the MCP Server application. You can use the following API endpoints to work with local files:

- `POST /api/v1/duckdb/query` - Execute a SQL query that uses HostFS functions
- `POST /api/v1/duckdb/tables` - Create a table from a local file using HostFS
- `POST /api/v1/duckdb/tables/export` - Export a table to a local file using HostFS

## Environment Variables

The following environment variables can be used to configure HostFS:

- `HOSTFS_ALLOWED_DIRS` - Comma-separated list of additional directories to allow access to

Example:
```
HOSTFS_ALLOWED_DIRS=/data,/mnt/external,/home/user/documents
```

## Limitations

- HostFS can only access directories that have been explicitly allowed
- HostFS cannot access files outside of the allowed directories
- HostFS cannot modify system files or directories
- HostFS operations are subject to the permissions of the user running the application
