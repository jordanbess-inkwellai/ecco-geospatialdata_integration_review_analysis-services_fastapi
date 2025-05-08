import pytest
import os
import tempfile
import json
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio

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
async def test_list_remotes_empty(rclone_service):
    """Test listing remotes when none are configured"""
    with patch('app.services.rclone_service.asyncio.create_subprocess_exec') as mock_exec:
        # Mock process
        process_mock = AsyncMock()
        process_mock.communicate.return_value = (b"", b"")
        process_mock.returncode = 0
        mock_exec.return_value = process_mock
        
        result = await rclone_service.list_remotes()
        
        assert result["success"] is True
        assert "remotes" in result
        assert len(result["remotes"]) == 0

@pytest.mark.asyncio
async def test_list_remotes(rclone_service):
    """Test listing remotes when some are configured"""
    with patch('app.services.rclone_service.asyncio.create_subprocess_exec') as mock_exec:
        # Mock process
        process_mock = AsyncMock()
        process_mock.communicate.return_value = (b"remote1:\nremote2:", b"")
        process_mock.returncode = 0
        mock_exec.return_value = process_mock
        
        result = await rclone_service.list_remotes()
        
        assert result["success"] is True
        assert "remotes" in result
        assert len(result["remotes"]) == 2
        assert "remote1" in result["remotes"]
        assert "remote2" in result["remotes"]

@pytest.mark.asyncio
async def test_add_remote(rclone_service):
    """Test adding a remote configuration"""
    # Test data
    name = "test_remote"
    remote_type = "s3"
    params = {
        "access_key_id": "test_key",
        "secret_access_key": "test_secret"
    }
    
    # Call the method
    result = await rclone_service.add_remote(name, remote_type, params)
    
    # Verify result
    assert result["success"] is True
    assert result["name"] == name
    assert result["type"] == remote_type
    
    # Verify config file was updated
    with open(rclone_service.config_path, "r") as f:
        config_content = f.read()
    
    assert f"[{name}]" in config_content
    assert f"type = {remote_type}" in config_content
    assert "access_key_id = test_key" in config_content
    assert "secret_access_key = test_secret" in config_content

@pytest.mark.asyncio
async def test_remove_remote(rclone_service):
    """Test removing a remote configuration"""
    # First add a remote
    name = "test_remote"
    remote_type = "s3"
    params = {"access_key_id": "test_key"}
    await rclone_service.add_remote(name, remote_type, params)
    
    # Now remove it
    result = await rclone_service.remove_remote(name)
    
    # Verify result
    assert result["success"] is True
    
    # Verify config file was updated
    with open(rclone_service.config_path, "r") as f:
        config_content = f.read()
    
    assert f"[{name}]" not in config_content
    assert "access_key_id = test_key" not in config_content

@pytest.mark.asyncio
async def test_list_files(rclone_service):
    """Test listing files in a remote path"""
    with patch('app.services.rclone_service.asyncio.create_subprocess_exec') as mock_exec:
        # Mock process
        process_mock = AsyncMock()
        mock_files = [
            {"Path": "file1.txt", "Name": "file1.txt", "Size": 100, "MimeType": "text/plain", "ModTime": "2023-01-01T12:00:00Z", "IsDir": False},
            {"Path": "folder1", "Name": "folder1", "Size": 0, "MimeType": "inode/directory", "ModTime": "2023-01-01T12:00:00Z", "IsDir": True}
        ]
        process_mock.communicate.return_value = (json.dumps(mock_files).encode(), b"")
        process_mock.returncode = 0
        mock_exec.return_value = process_mock
        
        result = await rclone_service.list_files("remote:path")
        
        assert result["success"] is True
        assert result["path"] == "remote:path"
        assert "files" in result
        assert len(result["files"]) == 2
        assert result["files"][0]["Name"] == "file1.txt"
        assert result["files"][1]["Name"] == "folder1"
        assert result["files"][1]["IsDir"] is True

@pytest.mark.asyncio
async def test_download_file(rclone_service):
    """Test downloading a file from a remote path"""
    with patch('app.services.rclone_service.asyncio.create_subprocess_exec') as mock_exec, \
         patch('os.path.exists') as mock_exists, \
         patch('os.path.basename') as mock_basename:
        
        # Mock process
        process_mock = AsyncMock()
        process_mock.communicate.return_value = (b"", b"")
        process_mock.returncode = 0
        mock_exec.return_value = process_mock
        
        # Mock file existence check
        mock_exists.return_value = True
        
        # Mock basename
        mock_basename.return_value = "file1.txt"
        
        result = await rclone_service.download_file("remote:path/file1.txt")
        
        assert result["success"] is True
        assert result["remote_path"] == "remote:path/file1.txt"
        assert "local_path" in result
        assert "file1.txt" in result["local_path"]

@pytest.mark.asyncio
async def test_upload_file(rclone_service):
    """Test uploading a file to a remote path"""
    with patch('app.services.rclone_service.asyncio.create_subprocess_exec') as mock_exec, \
         patch('os.path.exists') as mock_exists:
        
        # Mock process
        process_mock = AsyncMock()
        process_mock.communicate.return_value = (b"", b"")
        process_mock.returncode = 0
        mock_exec.return_value = process_mock
        
        # Mock file existence check
        mock_exists.return_value = True
        
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(b"test content")
        temp_file.close()
        
        try:
            result = await rclone_service.upload_file(temp_file.name, "remote:path/file1.txt")
            
            assert result["success"] is True
            assert result["local_path"] == temp_file.name
            assert result["remote_path"] == "remote:path/file1.txt"
        finally:
            # Clean up
            os.unlink(temp_file.name)

@pytest.mark.asyncio
async def test_sync_directory(rclone_service):
    """Test syncing directories"""
    with patch('app.services.rclone_service.asyncio.create_subprocess_exec') as mock_exec:
        # Mock process
        process_mock = AsyncMock()
        process_mock.communicate.return_value = (b"", b"")
        process_mock.returncode = 0
        mock_exec.return_value = process_mock
        
        result = await rclone_service.sync_directory("local/path", "remote:path", delete=True)
        
        assert result["success"] is True
        assert result["source_path"] == "local/path"
        assert result["dest_path"] == "remote:path"
        
        # Verify the correct command was called
        args, kwargs = mock_exec.call_args
        cmd = args[0]
        assert cmd == rclone_service.rclone_path
        assert "sync" in args
        assert "local/path" in args
        assert "remote:path" in args
        assert "--delete-dest" in args

@pytest.mark.asyncio
async def test_get_remote_info(rclone_service):
    """Test getting information about a remote"""
    with patch('app.services.rclone_service.asyncio.create_subprocess_exec') as mock_exec:
        # Mock process
        process_mock = AsyncMock()
        mock_info = {"Total": "1000000", "Used": "500000", "Free": "500000"}
        process_mock.communicate.return_value = (json.dumps(mock_info).encode(), b"")
        process_mock.returncode = 0
        mock_exec.return_value = process_mock
        
        result = await rclone_service.get_remote_info("remote:")
        
        assert result["success"] is True
        assert result["remote"] == "remote:"
        assert "info" in result
        assert result["info"]["Total"] == "1000000"
        assert result["info"]["Used"] == "500000"
        assert result["info"]["Free"] == "500000"

@pytest.mark.asyncio
async def test_create_public_link(rclone_service):
    """Test creating a public link for a file"""
    with patch('app.services.rclone_service.asyncio.create_subprocess_exec') as mock_exec:
        # Mock process
        process_mock = AsyncMock()
        process_mock.communicate.return_value = (b"https://example.com/shared/file1.txt", b"")
        process_mock.returncode = 0
        mock_exec.return_value = process_mock
        
        result = await rclone_service.create_public_link("remote:path/file1.txt", expire="1d")
        
        assert result["success"] is True
        assert result["remote_path"] == "remote:path/file1.txt"
        assert result["link"] == "https://example.com/shared/file1.txt"
        
        # Verify the correct command was called
        args, kwargs = mock_exec.call_args
        cmd = args[0]
        assert cmd == rclone_service.rclone_path
        assert "link" in args
        assert "remote:path/file1.txt" in args
        assert "--expire" in args
        assert "1d" in args
