import os
import subprocess
import json
import tempfile
import logging
import asyncio
import time
import re
from typing import Dict, List, Any, Optional, Union, BinaryIO, Tuple
from pathlib import Path
import shutil

from app.utils.error_handling import (
    RcloneError, RcloneConnectionError, RcloneAuthenticationError,
    RclonePermissionError, RcloneFileNotFoundError, RcloneConfigError,
    RcloneExecutionError, handle_rclone_error, with_retry
)

logger = logging.getLogger(__name__)

class RcloneService:
    """Service for interacting with remote storage using Rclone"""

    def __init__(self):
        """Initialize Rclone service"""
        self.rclone_path = self._find_rclone_executable()
        self.config_path = os.path.join(os.getcwd(), "data", "rclone", "rclone.conf")
        self.temp_dir = os.path.join(os.getcwd(), "data", "temp")

        # Create directories if they don't exist
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)

        # Create empty config file if it doesn't exist
        if not os.path.exists(self.config_path):
            with open(self.config_path, "w") as f:
                f.write("# Rclone configuration file\n")

        # Check if Rclone is available
        if self.rclone_path == "rclone" and not self._is_rclone_in_path():
            logger.warning("Rclone executable not found. Please install Rclone: https://rclone.org/downloads/")
        else:
            logger.info(f"Rclone service initialized with config: {self.config_path}")

    def _find_rclone_executable(self) -> str:
        """Find the Rclone executable path"""
        # Check if rclone is in PATH
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run(["where", "rclone"], capture_output=True, text=True, check=False)
                if result.returncode == 0:
                    return result.stdout.strip().split('\n')[0]
            else:  # Linux/Mac
                result = subprocess.run(["which", "rclone"], capture_output=True, text=True, check=False)
                if result.returncode == 0:
                    return result.stdout.strip()
        except Exception as e:
            logger.warning(f"Error finding rclone in PATH: {str(e)}")

        # Check common installation locations
        common_paths = []

        if os.name == 'nt':  # Windows
            common_paths = [
                r"C:\Program Files\rclone\rclone.exe",
                r"C:\Program Files (x86)\rclone\rclone.exe",
                os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'rclone', 'rclone.exe')
            ]
        else:  # Linux/Mac
            common_paths = [
                "/usr/bin/rclone",
                "/usr/local/bin/rclone",
                "/opt/rclone/rclone",
                os.path.join(os.path.expanduser("~"), "bin", "rclone")
            ]

        for path in common_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path

        # If not found, return just the command name and hope it's in PATH when used
        logger.warning("Rclone executable not found in common locations. Using 'rclone' command.")
        return "rclone"

    def _is_rclone_in_path(self) -> bool:
        """Check if rclone is available in PATH"""
        try:
            result = subprocess.run(["rclone", "--version"], capture_output=True, text=True, check=False)
            return result.returncode == 0
        except Exception:
            return False

    async def _run_rclone_command(self, args: List[str], input_data: Optional[str] = None,
                             max_retries: int = 3, retry_delay: float = 1.0) -> Dict[str, Any]:
        """
        Run an Rclone command and return the result

        Args:
            args: Command arguments
            input_data: Input data for the command
            max_retries: Maximum number of retries for transient errors
            retry_delay: Delay between retries in seconds

        Returns:
            Result of the command
        """
        cmd = [self.rclone_path, "--config", self.config_path] + args

        # Add --json flag for commands that support it
        if args[0] in ["lsf", "ls", "lsl", "lsjson", "about", "size"]:
            if "--json" not in args:
                cmd.append("--json")

        logger.debug(f"Running rclone command: {' '.join(cmd)}")

        retries = 0
        while retries <= max_retries:
            try:
                # Run the command
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdin=asyncio.subprocess.PIPE if input_data else None,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )

                # Send input if provided
                if input_data:
                    stdout, stderr = await process.communicate(input_data.encode())
                else:
                    stdout, stderr = await process.communicate()

                # Process output
                stdout_str = stdout.decode().strip() if stdout else ""
                stderr_str = stderr.decode().strip() if stderr else ""

                if process.returncode != 0:
                    # Check if this is a retryable error
                    if retries < max_retries and self._is_retryable_error(stderr_str):
                        retries += 1
                        wait_time = retry_delay * (2 ** (retries - 1))  # Exponential backoff
                        logger.warning(f"Retrying command after {wait_time}s due to: {stderr_str}")
                        await asyncio.sleep(wait_time)
                        continue

                    # Not retryable or max retries reached
                    logger.error(f"Rclone command failed: {stderr_str}")
                    return handle_rclone_error(stderr_str)

                # Try to parse JSON output
                result = {
                    "success": True,
                    "output": stdout_str,
                    "command": " ".join(cmd)
                }

                if stdout_str and (args[0] in ["lsf", "ls", "lsl", "lsjson", "about", "size"] or "--json" in args):
                    try:
                        result["data"] = json.loads(stdout_str)
                    except json.JSONDecodeError:
                        # Not JSON output, keep as string
                        pass

                return result

            except Exception as e:
                # Check if this is a retryable error
                if retries < max_retries and isinstance(e, (ConnectionError, TimeoutError)):
                    retries += 1
                    wait_time = retry_delay * (2 ** (retries - 1))  # Exponential backoff
                    logger.warning(f"Retrying command after {wait_time}s due to: {str(e)}")
                    await asyncio.sleep(wait_time)
                    continue

                # Not retryable or max retries reached
                logger.error(f"Error running rclone command: {str(e)}")
                return handle_rclone_error(str(e))

        # This should never be reached, but just in case
        return handle_rclone_error("Maximum retries exceeded")

    def _is_retryable_error(self, error_message: str) -> bool:
        """
        Check if an error is retryable

        Args:
            error_message: Error message from Rclone

        Returns:
            True if the error is retryable, False otherwise
        """
        retryable_patterns = [
            r"connection.*failed|network error|timeout|connection reset|EOF|broken pipe",
            r"too many requests|rate limit|throttle|429",
            r"internal server error|500|503|service unavailable",
            r"token.*expired|refresh.*token"
        ]

        for pattern in retryable_patterns:
            if re.search(pattern, error_message, re.IGNORECASE):
                return True

        return False

    async def list_remotes(self) -> Dict[str, Any]:
        """List configured remotes"""
        result = await self._run_rclone_command(["listremotes"])

        if not result["success"]:
            return result

        remotes = []
        for line in result["output"].split("\n"):
            if line.strip():
                # Remove trailing colon
                remote = line.strip()
                if remote.endswith(":"):
                    remote = remote[:-1]
                remotes.append(remote)

        return {
            "success": True,
            "remotes": remotes
        }

    async def add_remote(self, name: str, remote_type: str, params: Dict[str, str]) -> Dict[str, Any]:
        """
        Add a new remote configuration

        Args:
            name: Name for the remote
            remote_type: Type of remote (e.g., 's3', 'drive', 'box')
            params: Parameters for the remote configuration

        Returns:
            Result of the operation
        """
        # Create config string
        config_lines = [f"[{name}]", f"type = {remote_type}"]

        for key, value in params.items():
            config_lines.append(f"{key} = {value}")

        config_str = "\n".join(config_lines) + "\n"

        # Append to config file
        try:
            with open(self.config_path, "a") as f:
                f.write("\n" + config_str)

            logger.info(f"Added remote '{name}' of type '{remote_type}'")

            return {
                "success": True,
                "message": f"Remote '{name}' added successfully",
                "name": name,
                "type": remote_type
            }
        except Exception as e:
            logger.error(f"Error adding remote: {str(e)}")
            return {
                "success": False,
                "error": f"Error adding remote: {str(e)}"
            }

    async def remove_remote(self, name: str) -> Dict[str, Any]:
        """Remove a remote configuration"""
        try:
            # Read current config
            with open(self.config_path, "r") as f:
                config_lines = f.readlines()

            # Find and remove the remote section
            new_config_lines = []
            in_remote_section = False
            remote_found = False

            for line in config_lines:
                if line.strip() == f"[{name}]":
                    in_remote_section = True
                    remote_found = True
                    continue

                if in_remote_section and line.strip().startswith("["):
                    in_remote_section = False

                if not in_remote_section:
                    new_config_lines.append(line)

            if not remote_found:
                return {
                    "success": False,
                    "error": f"Remote '{name}' not found"
                }

            # Write updated config
            with open(self.config_path, "w") as f:
                f.writelines(new_config_lines)

            logger.info(f"Removed remote '{name}'")

            return {
                "success": True,
                "message": f"Remote '{name}' removed successfully"
            }
        except Exception as e:
            logger.error(f"Error removing remote: {str(e)}")
            return {
                "success": False,
                "error": f"Error removing remote: {str(e)}"
            }

    async def list_files(self, remote_path: str, recursive: bool = False) -> Dict[str, Any]:
        """
        List files in a remote path

        Args:
            remote_path: Remote path in the format 'remote:path'
            recursive: Whether to list files recursively

        Returns:
            List of files
        """
        args = ["lsjson"]

        if recursive:
            args.append("-R")

        args.append(remote_path)

        result = await self._run_rclone_command(args)

        if not result["success"]:
            return result

        return {
            "success": True,
            "path": remote_path,
            "files": result.get("data", [])
        }

    @with_retry(max_retries=3, retry_exceptions=[RcloneConnectionError, RcloneAuthenticationError])
    async def download_file(self, remote_path: str, local_path: Optional[str] = None,
                           progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """
        Download a file from a remote path

        Args:
            remote_path: Remote path in the format 'remote:path/to/file'
            local_path: Local path to save the file (optional)
            progress_callback: Callback function for progress updates (optional)

        Returns:
            Result of the operation
        """
        try:
            # Generate a temporary local path if not provided
            if not local_path:
                # Extract filename from remote path
                filename = os.path.basename(remote_path.split(":", 1)[1] if ":" in remote_path else remote_path)
                local_path = os.path.join(self.temp_dir, filename)

            # Ensure directory exists
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            # Get file size for progress reporting
            file_info = None
            if progress_callback:
                file_list_result = await self.list_files(os.path.dirname(remote_path) if ":" in remote_path else "", False)
                if file_list_result["success"]:
                    for file in file_list_result.get("files", []):
                        if file["Path"] == os.path.basename(remote_path):
                            file_info = file
                            break

            # Add progress flag if callback provided
            args = ["copy", remote_path, os.path.dirname(local_path)]
            if progress_callback:
                args.append("--progress")

            # Run copy command
            result = await self._run_rclone_command(args)

            if not result["success"]:
                return result

            # Check if file was downloaded
            expected_file = os.path.join(os.path.dirname(local_path), filename)
            if not os.path.exists(expected_file):
                raise RcloneFileNotFoundError(f"File not found after download: {expected_file}")

            # Get file size for verification
            file_size = os.path.getsize(expected_file)

            # Verify file size if we have the info
            if file_info and file_info["Size"] != file_size:
                logger.warning(f"Downloaded file size ({file_size}) doesn't match remote file size ({file_info['Size']})")

            return {
                "success": True,
                "remote_path": remote_path,
                "local_path": expected_file,
                "size": file_size,
                "message": f"File downloaded successfully to {expected_file}"
            }
        except RcloneError as e:
            return handle_rclone_error(e)
        except Exception as e:
            logger.error(f"Error downloading file: {str(e)}")
            return handle_rclone_error(str(e))

    @with_retry(max_retries=3, retry_exceptions=[RcloneConnectionError, RcloneAuthenticationError])
    async def upload_file(self, local_path: str, remote_path: str,
                         chunk_size: int = 0, progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """
        Upload a file to a remote path

        Args:
            local_path: Local path of the file to upload
            remote_path: Remote path in the format 'remote:path/to/file'
            chunk_size: Size of chunks for large file uploads (in MB, 0 for no chunking)
            progress_callback: Callback function for progress updates (optional)

        Returns:
            Result of the operation
        """
        try:
            if not os.path.exists(local_path):
                raise RcloneFileNotFoundError(f"Local file not found: {local_path}")

            file_size = os.path.getsize(local_path)

            # Use chunked upload for large files if requested
            if chunk_size > 0 and file_size > chunk_size * 1024 * 1024:
                return await self._chunked_upload(local_path, remote_path, chunk_size, progress_callback)

            # Add progress flag if callback provided
            args = ["copy", local_path, remote_path]
            if progress_callback:
                args.append("--progress")

            # Add transfer options for large files
            if file_size > 100 * 1024 * 1024:  # 100 MB
                args.extend(["--transfers", "4"])  # Use multiple transfers
                args.extend(["--checkers", "8"])   # Use more checkers

            # Run copy command
            result = await self._run_rclone_command(args)

            if not result["success"]:
                return result

            return {
                "success": True,
                "local_path": local_path,
                "remote_path": remote_path,
                "size": file_size,
                "message": f"File uploaded successfully to {remote_path}"
            }
        except RcloneError as e:
            return handle_rclone_error(e)
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            return handle_rclone_error(str(e))

    async def _chunked_upload(self, local_path: str, remote_path: str,
                             chunk_size_mb: int, progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """
        Upload a large file in chunks

        Args:
            local_path: Local path of the file to upload
            remote_path: Remote path in the format 'remote:path/to/file'
            chunk_size_mb: Size of chunks in MB
            progress_callback: Callback function for progress updates (optional)

        Returns:
            Result of the operation
        """
        try:
            file_size = os.path.getsize(local_path)
            chunk_size = chunk_size_mb * 1024 * 1024  # Convert to bytes

            # Create a temporary directory for chunks
            temp_dir = tempfile.mkdtemp(prefix="rclone_chunks_")

            try:
                # Split the file into chunks
                chunks = []
                with open(local_path, "rb") as f:
                    chunk_num = 0
                    while True:
                        chunk_data = f.read(chunk_size)
                        if not chunk_data:
                            break

                        chunk_path = os.path.join(temp_dir, f"chunk_{chunk_num:05d}")
                        with open(chunk_path, "wb") as chunk_file:
                            chunk_file.write(chunk_data)

                        chunks.append(chunk_path)
                        chunk_num += 1

                        if progress_callback:
                            progress = min(1.0, (chunk_num * chunk_size) / file_size)
                            progress_callback("splitting", progress)

                # Upload each chunk
                remote_dir = os.path.dirname(remote_path)
                remote_filename = os.path.basename(remote_path)
                temp_remote_dir = f"{remote_dir}/.tmp_{remote_filename}"

                # Create temporary directory on remote
                mkdir_result = await self._run_rclone_command(["mkdir", temp_remote_dir])
                if not mkdir_result["success"]:
                    return mkdir_result

                # Upload chunks
                for i, chunk_path in enumerate(chunks):
                    chunk_remote_path = f"{temp_remote_dir}/chunk_{i:05d}"

                    upload_result = await self._run_rclone_command(["copy", chunk_path, chunk_remote_path])
                    if not upload_result["success"]:
                        return upload_result

                    if progress_callback:
                        progress = min(1.0, (i + 1) / len(chunks))
                        progress_callback("uploading", progress)

                # Concatenate chunks on the remote
                concat_script = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
                try:
                    with open(concat_script.name, "w") as f:
                        for i in range(len(chunks)):
                            f.write(f"copy {temp_remote_dir}/chunk_{i:05d} {remote_path}\n")

                    # Run the concatenation script
                    concat_result = await self._run_rclone_command(["rcat", remote_path],
                                                                  input_data=open(concat_script.name, "r").read())
                    if not concat_result["success"]:
                        return concat_result

                    # Clean up temporary remote directory
                    cleanup_result = await self._run_rclone_command(["purge", temp_remote_dir])
                    if not cleanup_result["success"]:
                        logger.warning(f"Failed to clean up temporary remote directory: {cleanup_result.get('error')}")

                    return {
                        "success": True,
                        "local_path": local_path,
                        "remote_path": remote_path,
                        "size": file_size,
                        "chunks": len(chunks),
                        "message": f"File uploaded successfully to {remote_path} in {len(chunks)} chunks"
                    }
                finally:
                    os.unlink(concat_script.name)
            finally:
                # Clean up temporary directory
                shutil.rmtree(temp_dir, ignore_errors=True)
        except RcloneError as e:
            return handle_rclone_error(e)
        except Exception as e:
            logger.error(f"Error in chunked upload: {str(e)}")
            return handle_rclone_error(str(e))

    async def sync_directory(
        self,
        source_path: str,
        dest_path: str,
        delete: bool = False
    ) -> Dict[str, Any]:
        """
        Sync directories

        Args:
            source_path: Source path (local or remote)
            dest_path: Destination path (local or remote)
            delete: Whether to delete files in destination that don't exist in source

        Returns:
            Result of the operation
        """
        args = ["sync", source_path, dest_path]

        if delete:
            args.append("--delete-dest")

        result = await self._run_rclone_command(args)

        if not result["success"]:
            return result

        return {
            "success": True,
            "source_path": source_path,
            "dest_path": dest_path,
            "message": f"Directory synced successfully from {source_path} to {dest_path}"
        }

    async def get_remote_info(self, remote_path: str) -> Dict[str, Any]:
        """
        Get information about a remote

        Args:
            remote_path: Remote path in the format 'remote:'

        Returns:
            Information about the remote
        """
        result = await self._run_rclone_command(["about", remote_path])

        if not result["success"]:
            return result

        return {
            "success": True,
            "remote": remote_path,
            "info": result.get("data", {})
        }

    async def create_public_link(self, remote_path: str, expire: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a public link for a file

        Args:
            remote_path: Remote path in the format 'remote:path/to/file'
            expire: Expiration time (e.g., '1d', '2h30m')

        Returns:
            Public link
        """
        args = ["link", remote_path]

        if expire:
            args.extend(["--expire", expire])

        result = await self._run_rclone_command(args)

        if not result["success"]:
            return result

        return {
            "success": True,
            "remote_path": remote_path,
            "link": result["output"].strip()
        }

    async def box_auth(self, client_id: str, client_secret: str) -> Dict[str, Any]:
        """
        Authenticate with Box.com

        Args:
            client_id: Box API client ID
            client_secret: Box API client secret

        Returns:
            Result of the authentication process
        """
        # Create a temporary config file for this operation
        temp_config = tempfile.NamedTemporaryFile(delete=False, suffix=".conf")
        temp_config.close()

        try:
            # Start the authentication process
            cmd = [
                self.rclone_path,
                "--config", temp_config.name,
                "config",
                "create",
                "box",
                "box",
                "client_id", client_id,
                "client_secret", client_secret
            ]

            logger.debug(f"Running Box auth command: {' '.join(cmd)}")

            # This is interactive, so we need to handle it differently
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait for the process to complete
            stdout, stderr = process.communicate(input="n\n")  # Answer 'n' to advanced config

            if process.returncode != 0:
                logger.error(f"Box auth failed: {stderr}")
                return {
                    "success": False,
                    "error": stderr,
                    "command": " ".join(cmd)
                }

            # Read the generated config
            with open(temp_config.name, "r") as f:
                box_config = f.read()

            # Extract the relevant parts and add to our config
            config_lines = box_config.split("\n")
            box_section = []
            in_box_section = False

            for line in config_lines:
                if line.strip() == "[box]":
                    in_box_section = True
                    box_section.append("[box]")
                elif in_box_section and line.strip().startswith("["):
                    in_box_section = False
                elif in_box_section:
                    box_section.append(line)

            # Add to our config
            with open(self.config_path, "a") as f:
                f.write("\n" + "\n".join(box_section) + "\n")

            return {
                "success": True,
                "message": "Box authentication successful",
                "remote": "box:"
            }
        except Exception as e:
            logger.error(f"Error during Box authentication: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            # Clean up
            try:
                os.unlink(temp_config.name)
            except:
                pass


# Initialize the service
rclone_service = RcloneService()
