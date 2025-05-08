# Box.com Integration

This document provides information about the Box.com integration in the MCP Server application.

## Overview

The Box.com integration allows users to:

1. Browse files and folders in their Box.com account
2. Download files from Box.com
3. Import geospatial data files from Box.com into the application
4. Extract and view geospatial metadata from files
5. Create shared links for Box.com files
6. Search for files in Box.com

## Setup and Configuration

### Prerequisites

To use the Box.com integration, you need:

1. A Box.com account
2. A Box.com application with appropriate permissions

### Creating a Box.com Application

1. Go to the [Box Developer Console](https://developer.box.com/)
2. Create a new application
3. Select "Custom App" as the application type
4. Select "Server Authentication (with JWT)" or "OAuth 2.0 with JWT" as the authentication method
5. Configure the application with the following scopes:
   - Read and write all files and folders stored in Box
   - Manage users
   - Manage groups
   - Manage enterprise properties
   - Manage webhooks

### Configuration

The Box.com integration is configured using environment variables:

```
# Box.com API credentials
BOX_CLIENT_ID=your_client_id
BOX_CLIENT_SECRET=your_client_secret

# JWT configuration (for Server Authentication)
BOX_PRIVATE_KEY_PATH=/path/to/private_key.pem
BOX_PRIVATE_KEY_PASSWORD=your_private_key_password
BOX_ENTERPRISE_ID=your_enterprise_id

# OAuth2 configuration (for OAuth 2.0 with JWT)
BOX_REDIRECT_URI=https://your-app-url/api/v1/box/oauth2callback

# Metadata template settings
BOX_METADATA_TEMPLATE_SCOPE=enterprise
BOX_METADATA_TEMPLATE_NAME=geospatialMetadata

# Webhook settings
BOX_WEBHOOK_SIGNATURE_KEY=your_webhook_signature_key
```

## Geospatial Metadata

The integration automatically extracts and stores geospatial metadata for imported files. The metadata includes:

- Coordinate Reference System (CRS)
- Geometry Type
- Feature Count
- Bounding Box
- Attributes
- Data Format
- Last Updated

This metadata is stored in Box.com using a custom metadata template, making it searchable and filterable.

## API Endpoints

The following API endpoints are available for the Box.com integration:

### Status and Authentication

- `GET /api/v1/box/status` - Get the status of the Box.com integration
- `GET /api/v1/box/auth/url` - Get the OAuth2 authorization URL
- `GET /api/v1/box/oauth2callback` - Handle the OAuth2 callback

### File and Folder Operations

- `GET /api/v1/box/folders/{folder_id}` - Get the contents of a Box folder
- `GET /api/v1/box/files/{file_id}` - Get information about a Box file
- `GET /api/v1/box/files/{file_id}/download` - Download a file from Box
- `POST /api/v1/box/files/{file_id}/metadata` - Update the geospatial metadata for a file
- `POST /api/v1/box/search` - Search for files in Box
- `POST /api/v1/box/folders/{folder_id}/upload` - Upload a file to Box
- `POST /api/v1/box/files/{file_id}/share` - Create a shared link for a file
- `POST /api/v1/box/files/{file_id}/import` - Import a file from Box with metadata
- `POST /api/v1/box/webhook` - Handle Box.com webhook events

## Frontend Components

The frontend includes the following components for Box.com integration:

- `BoxBrowser` - A component for browsing Box.com files and folders
- `BoxIntegrationPage` - A page for the Box.com integration

## Usage

### Browsing Files

1. Navigate to the Box.com page in the application
2. If not authenticated, click the "Connect to Box.com" button
3. Browse through folders by clicking on them
4. Use the breadcrumb navigation to go back to previous folders
5. Use the search box to search for files

### Importing Files

1. Browse to the file you want to import
2. Click the "Import" button next to the file
3. The file will be downloaded and its metadata will be extracted
4. The imported file will be available in the application

### Viewing File Details

1. Click the "File Details" icon next to a file
2. A dialog will show the file details, including any geospatial metadata
3. From this dialog, you can:
   - Download the file
   - Create a shared link
   - Import the file

## Supported File Types

The Box.com integration supports various file types, including:

### Geospatial Data

- Shapefiles (.shp, .zip)
- GeoJSON (.geojson, .json)
- KML (.kml)
- GeoPackage (.gpkg)
- File Geodatabase (.gdb)

### Tabular Data

- CSV (.csv)
- Excel (.xlsx, .xls)
- Text (.txt)
- Tab-separated values (.tsv)

### Images

- JPEG (.jpg, .jpeg)
- PNG (.png)
- TIFF (.tif, .tiff)
- BMP (.bmp)

## Troubleshooting

### Authentication Issues

If you encounter authentication issues:

1. Check that your Box.com API credentials are correct
2. Verify that your application has the necessary scopes
3. Check the redirect URI configuration
4. Try reconnecting to Box.com

### File Import Issues

If you encounter issues importing files:

1. Check that the file format is supported
2. Verify that the file is not corrupted
3. Check the server logs for detailed error messages

## Security Considerations

The Box.com integration includes several security features:

1. OAuth2 authentication for secure access to Box.com
2. Temporary file storage for imported files
3. Automatic cleanup of temporary files
4. Webhook signature verification for secure webhooks

## Limitations

The current implementation has the following limitations:

1. File size limit of 100MB for uploads and downloads
2. Limited support for some specialized geospatial formats
3. No support for Box.com comments or tasks
4. No support for Box.com collaboration features
