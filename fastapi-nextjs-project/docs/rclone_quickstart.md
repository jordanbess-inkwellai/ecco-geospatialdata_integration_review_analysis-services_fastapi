# Rclone Integration Quick Start Guide

This guide will help you quickly get started with the Rclone integration in our application.

## What is Rclone?

Rclone is a command-line program to manage files on cloud storage. It's like rsync for cloud storage, allowing you to sync files between your local system and various cloud storage providers.

## Getting Started

### 1. Access the Rclone Interface

In the application, navigate to the Rclone section using the sidebar menu:

- **File Browser**: Browse and manage files on remote storage
- **Configuration**: Manage remote storage connections
- **Box.com Integration**: Special features for Box.com

### 2. Configure a Remote

To connect to a cloud storage provider:

1. Go to the **Configuration** page
2. Click the **Add Remote** button
3. Enter a name for your remote
4. Select the remote type (e.g., Box, S3, Google Drive)
5. Enter the required parameters for the selected provider
6. Click **Add Remote**

### 3. Browse Files

Once you've configured a remote:

1. Go to the **File Browser** page
2. Click on your remote in the list
3. Navigate through directories by clicking on folders
4. Download files by clicking the menu next to a file and selecting "Download"
5. Upload files by clicking the "Upload" button

### 4. Box.com Integration

For Box.com users, we offer enhanced features:

1. Go to the **Box.com Integration** page
2. Click "Authenticate with Box" and enter your credentials
3. Once authenticated, you can scan files to extract metadata
4. View and analyze the extracted metadata

## Working with Geodatabases

Our application allows you to work with ESRI Geodatabases stored on remote storage:

1. Browse to a geodatabase file in the **File Browser**
2. Use the API to convert the geodatabase to various formats:
   - GeoJSON
   - GeoPackage
   - PostGIS schema SQL
   - DuckDB

Example conversion:

1. Navigate to the geodatabase in the file browser
2. Click the menu next to the file
3. Select "Convert Geodatabase"
4. Choose your desired output format
5. Click "Convert"

## Common Tasks

### Uploading Files

1. Navigate to the destination folder in the **File Browser**
2. Click the "Upload" button
3. Select a file from your local system
4. Click "Upload"

### Downloading Files

1. Navigate to the file in the **File Browser**
2. Click the menu next to the file
3. Select "Download"

### Syncing Directories

Use the API to sync directories between local and remote storage:

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/rclone/sync",
    json={
        "source_path": "local/path",
        "dest_path": "remote:path",
        "delete": True  # Delete files in dest that don't exist in source
    }
)
result = response.json()
```

## Supported Storage Providers

Our Rclone integration supports many cloud storage providers, including:

- **Box.com**: Enterprise content management
- **Amazon S3**: Object storage service
- **Google Drive**: File storage and synchronization
- **Dropbox**: File hosting service
- **Microsoft OneDrive**: File hosting service
- **Azure Blob Storage**: Microsoft's object storage solution
- **SFTP**: Secure File Transfer Protocol
- **WebDAV**: Web-based Distributed Authoring and Versioning

## Troubleshooting

### Can't Connect to Remote

- Verify your credentials are correct
- Check network connectivity
- Ensure the remote service is available

### File Operations Fail

- Check file permissions
- Verify the path is correct
- Ensure you have sufficient storage space

### Authentication Issues

- For OAuth providers, try re-authenticating
- Check that your API keys haven't expired
- Verify you have the necessary permissions

## Next Steps

For more detailed information, check out:

- [Full Rclone Integration Documentation](./rclone_integration.md)
- [API Reference](./api_reference.md#rclone-api)
- [Rclone Official Documentation](https://rclone.org/docs/)
