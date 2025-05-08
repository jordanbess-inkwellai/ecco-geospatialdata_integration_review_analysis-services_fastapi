# Rclone Integration Documentation

## Overview

The Rclone integration provides a powerful way to connect to various cloud storage providers and remote file systems. This integration leverages [Rclone](https://rclone.org/), an open-source command-line program designed for managing files on cloud storage, to provide a seamless experience for accessing, transferring, and managing files across different storage platforms.

## Features

- **Multiple Storage Providers**: Connect to various cloud storage providers including Box, Google Drive, Dropbox, Amazon S3, Azure Blob Storage, and more.
- **File Operations**: Browse, upload, download, and manage files on remote storage.
- **Box.com Integration**: Special integration with Box.com for metadata extraction and advanced features.
- **Remote Geodatabase Support**: Convert ESRI Geodatabases directly from remote storage.
- **Synchronization**: Sync directories between local and remote storage.

## Prerequisites

Before using the Rclone integration, ensure you have:

1. **Rclone Installed**: The integration requires Rclone to be installed on the server. [Installation instructions](https://rclone.org/install/).
2. **Box SDK**: For Box.com integration, the Box SDK is required (already included in requirements.txt).
3. **Storage Provider Credentials**: You'll need appropriate credentials for each storage provider you want to connect to.

## Installation

### Server-side Setup

1. Install Rclone on your server:

```bash
# Linux/macOS
curl https://rclone.org/install.sh | sudo bash

# Windows (using PowerShell)
Invoke-Expression (New-Object System.Net.WebClient).DownloadString('https://rclone.org/install.ps1')
```

2. Verify the installation:

```bash
rclone version
```

3. Install the required Python packages:

```bash
pip install -r requirements.txt
```

### Configuration

The Rclone integration uses a configuration file to store remote configurations. By default, it uses the standard Rclone configuration file location:

- **Linux/macOS**: `~/.config/rclone/rclone.conf`
- **Windows**: `%USERPROFILE%\.config\rclone\rclone.conf`

You can configure remotes either through the web interface or directly using the Rclone command-line tool.

## Usage

### Web Interface

The web interface provides a user-friendly way to manage Rclone configurations and interact with remote storage:

1. **Rclone Configuration**: Navigate to `/rclone/config` to manage remote configurations.
2. **File Browser**: Navigate to `/rclone/browser` to browse and manage files on remote storage.
3. **Box.com Integration**: Navigate to `/rclone/box` for Box-specific features.

### API Endpoints

The following API endpoints are available for programmatic access:

#### Remote Management

- `GET /api/v1/rclone/remotes`: List all configured remotes
- `POST /api/v1/rclone/remotes`: Add a new remote
- `DELETE /api/v1/rclone/remotes/{name}`: Remove a remote

#### File Operations

- `GET /api/v1/rclone/files`: List files in a remote path
- `GET /api/v1/rclone/download`: Download a file from remote storage
- `POST /api/v1/rclone/upload`: Upload a file to remote storage
- `POST /api/v1/rclone/sync`: Sync directories between local and remote storage

#### Box.com Integration

- `POST /api/v1/rclone/box/auth`: Authenticate with Box.com
- `POST /api/v1/rclone/scan`: Scan files for metadata

#### Remote Geodatabase Operations

- `POST /api/v1/esri_geodatabase/convert-remote-geodatabase`: Convert a remote geodatabase
- `GET /api/v1/esri_geodatabase/download-remote-geodatabase`: Download a converted remote geodatabase

## Configuring Storage Providers

### Box.com

To configure Box.com:

1. Go to the Box Developer Console and create a new application
2. Set the application type to "Custom App" or "Enterprise Integration"
3. Enable OAuth 2.0 authentication
4. Add the redirect URI: `http://localhost:53682/`
5. Note your Client ID and Client Secret
6. In the web interface, navigate to `/rclone/box` and enter your credentials

### Amazon S3

To configure Amazon S3:

1. Create an IAM user with appropriate S3 permissions
2. Generate an access key and secret key
3. In the web interface, navigate to `/rclone/config` and add a new remote with type "s3"
4. Enter your access key and secret key

### Google Drive

To configure Google Drive:

1. Create a Google Cloud project
2. Enable the Google Drive API
3. Create OAuth 2.0 credentials
4. In the web interface, navigate to `/rclone/config` and add a new remote with type "drive"
5. Follow the authentication flow

## Working with Remote Geodatabases

The integration allows you to work with ESRI Geodatabases stored on remote storage:

1. **Browsing**: Use the file browser to locate geodatabase files on remote storage
2. **Converting**: Use the API to convert geodatabases to various formats:
   - GeoJSON
   - GeoPackage
   - PostGIS schema SQL
   - DuckDB

Example API call:

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/esri_geodatabase/convert-remote-geodatabase",
    json={
        "remote_path": "box:path/to/geodatabase.gdb",
        "output_format": "gpkg"
    }
)
result = response.json()
```

## Box.com Metadata Extraction

The Box.com integration includes special support for extracting metadata:

1. Navigate to `/rclone/box` in the web interface
2. Authenticate with Box.com
3. Use the "Scan Files" feature to extract metadata from files
4. View and analyze the extracted metadata

The metadata extraction process captures:

- File properties (name, size, creation date, etc.)
- Custom metadata fields defined in Box
- File descriptions and comments

## Troubleshooting

### Common Issues

1. **Authentication Failures**:
   - Ensure your credentials are correct
   - Check that the required permissions are granted
   - For OAuth flows, ensure redirect URIs are correctly configured

2. **File Operation Errors**:
   - Check file paths and permissions
   - Ensure the remote is correctly configured
   - Verify network connectivity

3. **Rclone Not Found**:
   - Ensure Rclone is installed and in the system PATH
   - Check the Rclone version (`rclone version`)

### Logs

The integration logs detailed information about operations:

- Backend logs are available in the standard application log
- Rclone command output is captured for debugging

## Security Considerations

1. **Credentials Storage**:
   - Rclone stores credentials in its configuration file
   - Ensure the configuration file has appropriate permissions
   - Consider using environment variables for sensitive credentials

2. **OAuth Tokens**:
   - OAuth tokens are stored in the Rclone configuration
   - Tokens are refreshed automatically when expired
   - Revoke tokens when no longer needed

3. **File Access**:
   - The integration provides access to all files the configured remotes can access
   - Implement appropriate access controls in your application

## Advanced Configuration

### Custom Rclone Path

You can specify a custom path to the Rclone executable by setting the `RCLONE_PATH` environment variable:

```bash
export RCLONE_PATH=/path/to/rclone
```

### Custom Configuration File

You can specify a custom configuration file by setting the `RCLONE_CONFIG` environment variable:

```bash
export RCLONE_CONFIG=/path/to/rclone.conf
```

### Temporary Directory

You can specify a custom temporary directory for downloads by setting the `RCLONE_TEMP_DIR` environment variable:

```bash
export RCLONE_TEMP_DIR=/path/to/temp
```

## API Reference

For a complete API reference, see the [API Documentation](./api_reference.md#rclone-api).

## Further Reading

- [Rclone Documentation](https://rclone.org/docs/)
- [Box Developer Documentation](https://developer.box.com/guides/)
- [ESRI Geodatabase Format](https://desktop.arcgis.com/en/arcmap/latest/manage-data/geodatabases/types-of-geodatabases.htm)
