import pytest
import os
import tempfile
import json
from unittest.mock import patch, MagicMock, AsyncMock
import subprocess

from app.services.rclone_service import RcloneService

@pytest.fixture
def rclone_service():
    """Create a RcloneService instance with a temporary config file for testing"""
    service = RcloneService()
    # Override config path for testing
    temp_dir = tempfile.mkdtemp()
    service.config_path = os.path.join(temp_dir, "rclone_test.conf")
    service.temp_dir = temp_dir
    
    # Create empty config file
    with open(service.config_path, "w") as f:
        f.write("# Rclone test configuration file\n")
    
    return service

@pytest.mark.asyncio
async def test_box_auth(rclone_service):
    """Test Box.com authentication"""
    with patch('subprocess.Popen') as mock_popen:
        # Mock process
        process_mock = MagicMock()
        process_mock.communicate.return_value = ("Box auth successful", "")
        process_mock.returncode = 0
        mock_popen.return_value = process_mock
        
        # Mock file operations
        with patch('builtins.open', MagicMock()), \
             patch('os.unlink', MagicMock()):
            
            # Mock reading the generated config
            with patch('app.services.rclone_service.open', MagicMock()) as mock_open:
                mock_file = MagicMock()
                mock_file.read.return_value = """
                [box]
                type = box
                client_id = test_client_id
                client_secret = test_client_secret
                token = {"access_token":"test_token"}
                """
                mock_open.return_value.__enter__.return_value = mock_file
                
                result = await rclone_service.box_auth("test_client_id", "test_client_secret")
                
                assert result["success"] is True
                assert result["message"] == "Box authentication successful"
                assert result["remote"] == "box:"

@pytest.mark.asyncio
async def test_extract_box_metadata(rclone_service):
    """Test extracting metadata from Box.com files"""
    # First mock the lsjson command to get file info
    with patch('app.services.rclone_service.asyncio.create_subprocess_exec') as mock_exec:
        # Mock process for lsjson
        process_mock = AsyncMock()
        mock_files = [
            {"Path": "file1.txt", "Name": "file1.txt", "Size": 100, "MimeType": "text/plain", "ModTime": "2023-01-01T12:00:00Z", "IsDir": False, "ID": "123456"}
        ]
        process_mock.communicate.return_value = (json.dumps(mock_files).encode(), b"")
        process_mock.returncode = 0
        mock_exec.return_value = process_mock
        
        # Now mock the Box SDK
        with patch('app.services.rclone_service.boxsdk') as mock_boxsdk, \
             patch('app.services.rclone_service.open', MagicMock()) as mock_open:
            
            # Mock reading the config file
            mock_file = MagicMock()
            mock_file.read.return_value = """
            client_id = test_client_id
            client_secret = test_client_secret
            """
            mock_open.return_value.__enter__.return_value = mock_file
            
            # Mock Box client and file
            mock_client = MagicMock()
            mock_file = MagicMock()
            mock_file.id = "123456"
            mock_file.name = "file1.txt"
            mock_file.size = 100
            mock_file.created_at = "2023-01-01T12:00:00Z"
            mock_file.modified_at = "2023-01-01T12:00:00Z"
            mock_file.description = "Test file"
            
            # Mock metadata
            mock_metadata = MagicMock()
            mock_metadata.get.return_value = [{"template": "properties", "field1": "value1"}]
            mock_file.metadata.return_value = mock_metadata
            
            # Set up the mock chain
            mock_client.file.return_value.get.return_value = mock_file
            mock_boxsdk.Client.return_value = mock_client
            mock_boxsdk.OAuth2.return_value = MagicMock()
            
            result = await rclone_service.extract_box_metadata("box:file1.txt")
            
            assert result["success"] is True
            assert result["file_path"] == "box:file1.txt"
            assert "metadata" in result
            assert result["metadata"]["id"] == "123456"
            assert result["metadata"]["name"] == "file1.txt"
            assert result["metadata"]["size"] == 100

@pytest.mark.asyncio
async def test_scan_files_for_metadata(rclone_service):
    """Test scanning files for metadata"""
    # Mock list_files method
    with patch.object(rclone_service, 'list_files') as mock_list_files:
        mock_list_files.return_value = {
            "success": True,
            "files": [
                {"Path": "file1.txt", "Name": "file1.txt", "Size": 100, "ModTime": "2023-01-01T12:00:00Z", "IsDir": False},
                {"Path": "folder1", "Name": "folder1", "Size": 0, "ModTime": "2023-01-01T12:00:00Z", "IsDir": True}
            ]
        }
        
        # Mock extract_box_metadata method for Box remotes
        with patch.object(rclone_service, 'extract_box_metadata') as mock_extract_metadata:
            mock_extract_metadata.return_value = {
                "success": True,
                "metadata": {
                    "id": "123456",
                    "name": "file1.txt",
                    "size": 100,
                    "created_at": "2023-01-01T12:00:00Z",
                    "modified_at": "2023-01-01T12:00:00Z",
                    "description": "Test file",
                    "metadata": {"properties": {"field1": "value1"}}
                }
            }
            
            # Test with Box remote
            result = await rclone_service.scan_files_for_metadata("box:path")
            
            assert result["success"] is True
            assert result["remote_path"] == "box:path"
            assert result["file_count"] == 1  # Only non-directory files
            assert len(result["files"]) == 1
            assert result["files"][0]["name"] == "file1.txt"
            assert "metadata" in result["files"][0]
            
            # Test with non-Box remote
            result = await rclone_service.scan_files_for_metadata("s3:path")
            
            assert result["success"] is True
            assert result["remote_path"] == "s3:path"
            assert result["file_count"] == 1  # Only non-directory files
            assert len(result["files"]) == 1
            assert result["files"][0]["name"] == "file1.txt"
            assert "path" in result["files"][0]
            assert "size" in result["files"][0]
