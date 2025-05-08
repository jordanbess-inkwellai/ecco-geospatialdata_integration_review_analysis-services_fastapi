import os
import json
import logging
import tempfile
from typing import Dict, List, Any, Optional, BinaryIO, Union
from datetime import datetime
from pathlib import Path

from boxsdk import Client, OAuth2, JWTAuth
from boxsdk.object.folder import Folder
from boxsdk.object.file import File
from boxsdk.object.metadata_template import MetadataTemplate
from boxsdk.object.metadata_cascade_policy import MetadataCascadePolicy
from boxsdk.exception.box_exception import BoxException, BoxAPIException

from app.core.box_config import box_config
from app.core.config import settings

logger = logging.getLogger(__name__)

class BoxService:
    """Service for interacting with Box.com API."""
    
    def __init__(self):
        """Initialize the Box.com service."""
        self.client = None
        self.auth = None
        self.metadata_template = None
        
        # Create cache directory if it doesn't exist
        os.makedirs(box_config.cache_dir, exist_ok=True)
        
        # Initialize Box client if configured
        if box_config.is_configured:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Box.com client."""
        try:
            # Try JWT authentication first if configured
            if box_config.is_jwt_configured:
                logger.info("Initializing Box.com client with JWT authentication")
                self.auth = JWTAuth(
                    client_id=box_config.client_id,
                    client_secret=box_config.client_secret,
                    enterprise_id=box_config.enterprise_id,
                    jwt_key_id=None,  # Will be read from the private key file
                    rsa_private_key_file_sys_path=box_config.private_key_path,
                    rsa_private_key_passphrase=box_config.private_key_password,
                )
                self.client = Client(self.auth)
            
            # Fall back to OAuth2 if JWT is not configured
            elif box_config.is_oauth_configured:
                logger.info("Initializing Box.com client with OAuth2 authentication")
                self.auth = OAuth2(
                    client_id=box_config.client_id,
                    client_secret=box_config.client_secret,
                    store_tokens=self._store_tokens,
                )
                
                # Try to load tokens from cache
                access_token, refresh_token = self._load_tokens()
                if access_token and refresh_token:
                    self.auth.refresh(access_token=access_token)
                
                self.client = Client(self.auth)
            
            else:
                logger.warning("Box.com API is not properly configured")
                return
            
            # Initialize metadata template
            self._initialize_metadata_template()
            
            logger.info("Box.com client initialized successfully")
        
        except Exception as e:
            logger.error(f"Error initializing Box.com client: {str(e)}")
            self.client = None
            self.auth = None
    
    def _store_tokens(self, access_token, refresh_token):
        """Store OAuth2 tokens in cache."""
        token_cache_path = os.path.join(box_config.cache_dir, "tokens.json")
        with open(token_cache_path, "w") as f:
            json.dump({
                "access_token": access_token,
                "refresh_token": refresh_token,
                "updated_at": datetime.now().isoformat()
            }, f)
    
    def _load_tokens(self):
        """Load OAuth2 tokens from cache."""
        token_cache_path = os.path.join(box_config.cache_dir, "tokens.json")
        if os.path.exists(token_cache_path):
            try:
                with open(token_cache_path, "r") as f:
                    tokens = json.load(f)
                return tokens.get("access_token"), tokens.get("refresh_token")
            except Exception as e:
                logger.error(f"Error loading tokens from cache: {str(e)}")
        
        return None, None
    
    def _initialize_metadata_template(self):
        """Initialize or create the geospatial metadata template."""
        if not self.client:
            return
        
        try:
            # Try to get the existing template
            templates = self.client.metadata_template_manager.get_metadata_templates(
                scope=box_config.metadata_template_scope,
                template_key=box_config.metadata_template_name
            )
            
            if templates:
                self.metadata_template = templates[0]
                logger.info(f"Found existing metadata template: {self.metadata_template.displayName}")
                return
            
            # Create the template if it doesn't exist
            logger.info(f"Creating metadata template: {box_config.metadata_template_name}")
            self.metadata_template = self.client.metadata_template_manager.create_metadata_template(
                display_name="Geospatial Metadata",
                fields=[
                    {
                        "type": "string",
                        "displayName": "Coordinate Reference System",
                        "key": "crs",
                        "description": "Coordinate Reference System (e.g., EPSG:4326)"
                    },
                    {
                        "type": "string",
                        "displayName": "Geometry Type",
                        "key": "geometryType",
                        "description": "Type of geometry (e.g., Point, LineString, Polygon)"
                    },
                    {
                        "type": "string",
                        "displayName": "Feature Count",
                        "key": "featureCount",
                        "description": "Number of features in the dataset"
                    },
                    {
                        "type": "string",
                        "displayName": "Bounding Box",
                        "key": "boundingBox",
                        "description": "Bounding box coordinates (minX,minY,maxX,maxY)"
                    },
                    {
                        "type": "string",
                        "displayName": "Attributes",
                        "key": "attributes",
                        "description": "List of attribute fields"
                    },
                    {
                        "type": "date",
                        "displayName": "Last Updated",
                        "key": "lastUpdated",
                        "description": "Date when the metadata was last updated"
                    },
                    {
                        "type": "string",
                        "displayName": "Data Format",
                        "key": "dataFormat",
                        "description": "Format of the geospatial data (e.g., Shapefile, GeoJSON)"
                    }
                ],
                template_key=box_config.metadata_template_name,
                hidden=False,
                scope=box_config.metadata_template_scope
            )
            
            logger.info(f"Created metadata template: {self.metadata_template.displayName}")
        
        except Exception as e:
            logger.error(f"Error initializing metadata template: {str(e)}")
            self.metadata_template = None
    
    def get_oauth_authorize_url(self) -> str:
        """Get the OAuth2 authorization URL."""
        if not box_config.is_oauth_configured:
            raise ValueError("Box.com OAuth2 is not configured")
        
        return self.auth.get_authorization_url(box_config.redirect_uri)[0]
    
    def complete_oauth_flow(self, auth_code: str) -> bool:
        """Complete the OAuth2 flow with the authorization code."""
        if not box_config.is_oauth_configured:
            raise ValueError("Box.com OAuth2 is not configured")
        
        try:
            access_token, refresh_token = self.auth.authenticate(auth_code)
            self._store_tokens(access_token, refresh_token)
            self.client = Client(self.auth)
            self._initialize_metadata_template()
            return True
        except Exception as e:
            logger.error(f"Error completing OAuth2 flow: {str(e)}")
            return False
    
    def list_folder_contents(self, folder_id: str = "0") -> List[Dict[str, Any]]:
        """
        List the contents of a Box folder.
        
        Args:
            folder_id: ID of the folder to list (default: "0" for root folder)
            
        Returns:
            List of items in the folder
        """
        if not self.client:
            raise ValueError("Box.com client is not initialized")
        
        try:
            folder = self.client.folder(folder_id=folder_id).get()
            items = []
            
            # Get folder items with limit of 100 per page
            item_limit = 100
            offset = 0
            
            while True:
                item_collection = folder.get_items(limit=item_limit, offset=offset)
                
                if not item_collection:
                    break
                
                for item in item_collection:
                    item_info = {
                        "id": item.id,
                        "name": item.name,
                        "type": item.type,
                        "size": getattr(item, "size", None),
                        "created_at": getattr(item, "created_at", None),
                        "modified_at": getattr(item, "modified_at", None),
                        "has_metadata": False
                    }
                    
                    # Check if item has geospatial metadata
                    if item.type == "file" and self.metadata_template:
                        try:
                            metadata = item.metadata(
                                scope=box_config.metadata_template_scope,
                                template=box_config.metadata_template_name
                            ).get()
                            if metadata:
                                item_info["has_metadata"] = True
                                item_info["metadata"] = metadata
                        except BoxAPIException as e:
                            # Ignore 404 errors (no metadata)
                            if e.status != 404:
                                logger.error(f"Error getting metadata for file {item.id}: {str(e)}")
                    
                    items.append(item_info)
                
                # Check if we've reached the end of the items
                if len(item_collection) < item_limit:
                    break
                
                offset += item_limit
            
            return items
        
        except Exception as e:
            logger.error(f"Error listing folder contents: {str(e)}")
            raise
    
    def download_file(self, file_id: str, destination_path: Optional[str] = None) -> str:
        """
        Download a file from Box.
        
        Args:
            file_id: ID of the file to download
            destination_path: Path where the file should be saved (optional)
            
        Returns:
            Path to the downloaded file
        """
        if not self.client:
            raise ValueError("Box.com client is not initialized")
        
        try:
            file_obj = self.client.file(file_id=file_id).get()
            
            # If no destination path is provided, create a temporary file
            if not destination_path:
                # Create a temporary file with the same extension
                file_name = file_obj.name
                file_ext = os.path.splitext(file_name)[1]
                
                with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False, dir=box_config.cache_dir) as temp_file:
                    destination_path = temp_file.name
            
            # Download the file
            with open(destination_path, "wb") as output_file:
                file_obj.download_to(output_file)
            
            return destination_path
        
        except Exception as e:
            logger.error(f"Error downloading file: {str(e)}")
            raise
    
    def upload_file(self, folder_id: str, file_path: str, file_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload a file to Box.
        
        Args:
            folder_id: ID of the folder to upload to
            file_path: Path to the file to upload
            file_name: Name to give the file in Box (optional)
            
        Returns:
            Information about the uploaded file
        """
        if not self.client:
            raise ValueError("Box.com client is not initialized")
        
        try:
            folder = self.client.folder(folder_id=folder_id)
            
            # Use the original file name if none is provided
            if not file_name:
                file_name = os.path.basename(file_path)
            
            # Upload the file
            with open(file_path, "rb") as file_content:
                uploaded_file = folder.upload_stream(file_content, file_name)
            
            return {
                "id": uploaded_file.id,
                "name": uploaded_file.name,
                "type": uploaded_file.type,
                "size": uploaded_file.size,
                "created_at": uploaded_file.created_at,
                "modified_at": uploaded_file.modified_at
            }
        
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            raise
    
    def update_metadata(self, file_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the geospatial metadata for a file.
        
        Args:
            file_id: ID of the file to update
            metadata: Metadata to apply to the file
            
        Returns:
            Updated metadata
        """
        if not self.client or not self.metadata_template:
            raise ValueError("Box.com client or metadata template is not initialized")
        
        try:
            file_obj = self.client.file(file_id=file_id)
            
            try:
                # Try to get existing metadata
                existing_metadata = file_obj.metadata(
                    scope=box_config.metadata_template_scope,
                    template=box_config.metadata_template_name
                ).get()
                
                # Update existing metadata
                updated_metadata = file_obj.metadata(
                    scope=box_config.metadata_template_scope,
                    template=box_config.metadata_template_name
                ).update(metadata)
                
                return updated_metadata
            
            except BoxAPIException as e:
                # If metadata doesn't exist (404), create it
                if e.status == 404:
                    created_metadata = file_obj.metadata(
                        scope=box_config.metadata_template_scope,
                        template=box_config.metadata_template_name
                    ).create(metadata)
                    
                    return created_metadata
                else:
                    raise
        
        except Exception as e:
            logger.error(f"Error updating metadata: {str(e)}")
            raise
    
    def search_files(self, query: str, file_extensions: Optional[List[str]] = None, 
                     metadata_query: Optional[Dict[str, Any]] = None, 
                     limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search for files in Box.
        
        Args:
            query: Search query
            file_extensions: List of file extensions to filter by (optional)
            metadata_query: Metadata query to filter by (optional)
            limit: Maximum number of results to return
            
        Returns:
            List of matching files
        """
        if not self.client:
            raise ValueError("Box.com client is not initialized")
        
        try:
            # Build the query
            search_query = query
            
            # Add file extension filter
            if file_extensions:
                ext_filter = " OR ".join([f"extension:{ext}" for ext in file_extensions])
                search_query = f"{search_query} ({ext_filter})"
            
            # Perform the search
            search_results = self.client.search().query(
                query=search_query,
                limit=limit,
                file_extensions=file_extensions,
                content_types=["name", "description", "file_content"],
                type="file"
            )
            
            # Process the results
            results = []
            for item in search_results:
                item_info = {
                    "id": item.id,
                    "name": item.name,
                    "type": item.type,
                    "size": getattr(item, "size", None),
                    "created_at": getattr(item, "created_at", None),
                    "modified_at": getattr(item, "modified_at", None),
                    "has_metadata": False
                }
                
                # Check if item has geospatial metadata
                if item.type == "file" and self.metadata_template:
                    try:
                        metadata = item.metadata(
                            scope=box_config.metadata_template_scope,
                            template=box_config.metadata_template_name
                        ).get()
                        if metadata:
                            item_info["has_metadata"] = True
                            item_info["metadata"] = metadata
                            
                            # Filter by metadata if specified
                            if metadata_query:
                                match = True
                                for key, value in metadata_query.items():
                                    if key not in metadata or metadata[key] != value:
                                        match = False
                                        break
                                
                                if not match:
                                    continue
                    except BoxAPIException as e:
                        # Ignore 404 errors (no metadata)
                        if e.status != 404:
                            logger.error(f"Error getting metadata for file {item.id}: {str(e)}")
                
                results.append(item_info)
            
            return results
        
        except Exception as e:
            logger.error(f"Error searching files: {str(e)}")
            raise
    
    def create_shared_link(self, file_id: str, access: str = "open", 
                          password: Optional[str] = None, 
                          expires_at: Optional[datetime] = None) -> str:
        """
        Create a shared link for a file.
        
        Args:
            file_id: ID of the file to share
            access: Access level ("open", "company", or "collaborators")
            password: Optional password to protect the link
            expires_at: Optional expiration date for the link
            
        Returns:
            Shared link URL
        """
        if not self.client:
            raise ValueError("Box.com client is not initialized")
        
        try:
            file_obj = self.client.file(file_id=file_id)
            
            shared_link = file_obj.get_shared_link(
                access=access,
                password=password,
                expires_at=expires_at,
                allow_download=True,
                allow_preview=True
            )
            
            return shared_link
        
        except Exception as e:
            logger.error(f"Error creating shared link: {str(e)}")
            raise
    
    def extract_metadata_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Extract geospatial metadata from a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Extracted metadata
        """
        try:
            # Import here to avoid circular imports
            from app.services.geospatial_service import GeospatialService
            
            geo_service = GeospatialService()
            file_info = geo_service.get_file_info(file_path)
            
            # Convert file info to Box metadata format
            metadata = {
                "crs": file_info.get("crs", "Unknown"),
                "geometryType": file_info.get("geometry_type", "Unknown"),
                "featureCount": str(file_info.get("feature_count", 0)),
                "boundingBox": ",".join(map(str, file_info.get("bounds", [0, 0, 0, 0]))),
                "attributes": ",".join(file_info.get("fields", [])),
                "lastUpdated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z"),
                "dataFormat": file_info.get("driver", "Unknown")
            }
            
            return metadata
        
        except Exception as e:
            logger.error(f"Error extracting metadata from file: {str(e)}")
            return {
                "crs": "Unknown",
                "geometryType": "Unknown",
                "featureCount": "0",
                "boundingBox": "0,0,0,0",
                "attributes": "",
                "lastUpdated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z"),
                "dataFormat": "Unknown"
            }
    
    def import_file_with_metadata(self, file_id: str, destination_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Import a file from Box, download it, and extract its metadata.
        
        Args:
            file_id: ID of the file to import
            destination_path: Path where the file should be saved (optional)
            
        Returns:
            Information about the imported file including metadata
        """
        if not self.client:
            raise ValueError("Box.com client is not initialized")
        
        try:
            # Get file info
            file_obj = self.client.file(file_id=file_id).get()
            file_info = {
                "id": file_obj.id,
                "name": file_obj.name,
                "type": file_obj.type,
                "size": file_obj.size,
                "created_at": file_obj.created_at,
                "modified_at": file_obj.modified_at
            }
            
            # Download the file
            local_path = self.download_file(file_id, destination_path)
            file_info["local_path"] = local_path
            
            # Check if file already has metadata
            try:
                existing_metadata = file_obj.metadata(
                    scope=box_config.metadata_template_scope,
                    template=box_config.metadata_template_name
                ).get()
                
                if existing_metadata:
                    file_info["metadata"] = existing_metadata
                    return file_info
            except BoxAPIException as e:
                # Ignore 404 errors (no metadata)
                if e.status != 404:
                    logger.error(f"Error getting metadata for file {file_id}: {str(e)}")
            
            # Extract metadata from the file
            metadata = self.extract_metadata_from_file(local_path)
            
            # Update the file's metadata in Box
            updated_metadata = self.update_metadata(file_id, metadata)
            file_info["metadata"] = updated_metadata
            
            return file_info
        
        except Exception as e:
            logger.error(f"Error importing file with metadata: {str(e)}")
            raise

# Create a global instance of BoxService
box_service = BoxService()
