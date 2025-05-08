import os
import json
import logging
import requests
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class OgcApiRecordsService:
    """
    Service for interacting with OGC API Records endpoints
    
    This service provides functionality to:
    - Search for records in an OGC API Records catalog
    - Publish new records to an OGC API Records catalog
    - Update existing records
    - Delete records
    - Validate record metadata
    """
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize the OGC API Records service
        
        Args:
            base_url: Base URL of the OGC API Records endpoint
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {}
        
        if api_key:
            self.headers['Authorization'] = f'Bearer {api_key}'
    
    async def get_conformance(self) -> Dict[str, Any]:
        """
        Get conformance information from the OGC API Records endpoint
        
        Returns:
            Dictionary with conformance information
        """
        try:
            url = f"{self.base_url}/conformance"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting conformance information: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error getting conformance information: {str(e)}")
    
    async def get_collections(self) -> Dict[str, Any]:
        """
        Get collections from the OGC API Records endpoint
        
        Returns:
            Dictionary with collections information
        """
        try:
            url = f"{self.base_url}/collections"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting collections: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error getting collections: {str(e)}")
    
    async def get_collection(self, collection_id: str) -> Dict[str, Any]:
        """
        Get information about a specific collection
        
        Args:
            collection_id: ID of the collection
            
        Returns:
            Dictionary with collection information
        """
        try:
            url = f"{self.base_url}/collections/{collection_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting collection {collection_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error getting collection {collection_id}: {str(e)}")
    
    async def search_records(
        self, 
        collection_id: Optional[str] = None,
        q: Optional[str] = None,
        bbox: Optional[List[float]] = None,
        datetime_range: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
        filter_lang: Optional[str] = None,
        filter_query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for records in the OGC API Records catalog
        
        Args:
            collection_id: Optional collection ID to search within
            q: Optional full-text search query
            bbox: Optional bounding box [minx, miny, maxx, maxy]
            datetime_range: Optional datetime range (e.g., "2023-01-01/2023-12-31")
            limit: Maximum number of records to return
            offset: Offset for pagination
            filter_lang: Optional filter language (e.g., "cql-text")
            filter_query: Optional filter query
            
        Returns:
            Dictionary with search results
        """
        try:
            # Determine URL based on whether a collection ID is provided
            if collection_id:
                url = f"{self.base_url}/collections/{collection_id}/items"
            else:
                url = f"{self.base_url}/records"
            
            # Build query parameters
            params = {
                "limit": limit,
                "offset": offset
            }
            
            if q:
                params["q"] = q
            
            if bbox:
                params["bbox"] = ",".join(map(str, bbox))
            
            if datetime_range:
                params["datetime"] = datetime_range
            
            if filter_lang and filter_query:
                params["filter-lang"] = filter_lang
                params["filter"] = filter_query
            
            # Make request
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching records: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error searching records: {str(e)}")
    
    async def get_record(self, collection_id: str, record_id: str) -> Dict[str, Any]:
        """
        Get a specific record from the OGC API Records catalog
        
        Args:
            collection_id: Collection ID
            record_id: Record ID
            
        Returns:
            Dictionary with record information
        """
        try:
            url = f"{self.base_url}/collections/{collection_id}/items/{record_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting record {record_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error getting record {record_id}: {str(e)}")
    
    async def create_record(self, collection_id: str, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new record in the OGC API Records catalog
        
        Args:
            collection_id: Collection ID
            record: Record data in GeoJSON format
            
        Returns:
            Dictionary with created record information
        """
        try:
            url = f"{self.base_url}/collections/{collection_id}/items"
            
            # Ensure record has required properties
            if "type" not in record:
                record["type"] = "Feature"
            
            if "properties" not in record:
                record["properties"] = {}
            
            # Add timestamp if not present
            if "created" not in record["properties"]:
                record["properties"]["created"] = datetime.now().isoformat()
            
            # Make request
            response = requests.post(
                url, 
                json=record, 
                headers={**self.headers, "Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            # Some implementations return the created record, others just return a status
            if response.content:
                return response.json()
            else:
                return {"status": "success", "message": "Record created successfully"}
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating record: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error creating record: {str(e)}")
    
    async def update_record(self, collection_id: str, record_id: str, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing record in the OGC API Records catalog
        
        Args:
            collection_id: Collection ID
            record_id: Record ID
            record: Updated record data in GeoJSON format
            
        Returns:
            Dictionary with updated record information
        """
        try:
            url = f"{self.base_url}/collections/{collection_id}/items/{record_id}"
            
            # Ensure record has required properties
            if "type" not in record:
                record["type"] = "Feature"
            
            if "id" not in record:
                record["id"] = record_id
            
            if "properties" not in record:
                record["properties"] = {}
            
            # Add timestamp if not present
            if "updated" not in record["properties"]:
                record["properties"]["updated"] = datetime.now().isoformat()
            
            # Make request
            response = requests.put(
                url, 
                json=record, 
                headers={**self.headers, "Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            # Some implementations return the updated record, others just return a status
            if response.content:
                return response.json()
            else:
                return {"status": "success", "message": "Record updated successfully"}
        except requests.exceptions.RequestException as e:
            logger.error(f"Error updating record {record_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error updating record {record_id}: {str(e)}")
    
    async def delete_record(self, collection_id: str, record_id: str) -> Dict[str, Any]:
        """
        Delete a record from the OGC API Records catalog
        
        Args:
            collection_id: Collection ID
            record_id: Record ID
            
        Returns:
            Dictionary with deletion status
        """
        try:
            url = f"{self.base_url}/collections/{collection_id}/items/{record_id}"
            response = requests.delete(url, headers=self.headers)
            response.raise_for_status()
            
            return {"status": "success", "message": f"Record {record_id} deleted successfully"}
        except requests.exceptions.RequestException as e:
            logger.error(f"Error deleting record {record_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error deleting record {record_id}: {str(e)}")
    
    async def validate_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a record against the OGC API Records schema
        
        Args:
            record: Record data in GeoJSON format
            
        Returns:
            Dictionary with validation results
        """
        # Basic validation
        validation_errors = []
        
        # Check required fields
        if "type" not in record or record["type"] != "Feature":
            validation_errors.append("Record must be a GeoJSON Feature")
        
        if "properties" not in record:
            validation_errors.append("Record must have properties")
        else:
            # Check required properties
            properties = record["properties"]
            
            if "title" not in properties:
                validation_errors.append("Record must have a title")
            
            if "description" not in properties:
                validation_errors.append("Record must have a description")
            
            if "type" not in properties:
                validation_errors.append("Record must have a type")
        
        # Return validation results
        if validation_errors:
            return {
                "valid": False,
                "errors": validation_errors
            }
        else:
            return {
                "valid": True
            }
    
    async def create_metadata_record(
        self,
        collection_id: str,
        title: str,
        description: str,
        keywords: List[str],
        resource_type: str,
        resource_url: str,
        bbox: Optional[List[float]] = None,
        temporal_extent: Optional[List[str]] = None,
        contact: Optional[Dict[str, str]] = None,
        additional_properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a metadata record in the OGC API Records catalog
        
        Args:
            collection_id: Collection ID
            title: Record title
            description: Record description
            keywords: List of keywords
            resource_type: Type of resource (e.g., "dataset", "service")
            resource_url: URL of the resource
            bbox: Optional bounding box [minx, miny, maxx, maxy]
            temporal_extent: Optional temporal extent [start, end]
            contact: Optional contact information
            additional_properties: Optional additional properties
            
        Returns:
            Dictionary with created record information
        """
        # Create record properties
        properties = {
            "title": title,
            "description": description,
            "keywords": keywords,
            "type": resource_type,
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
            "links": [
                {
                    "href": resource_url,
                    "rel": "item",
                    "type": "application/json",
                    "title": title
                }
            ]
        }
        
        # Add temporal extent if provided
        if temporal_extent:
            properties["temporal"] = {
                "interval": [temporal_extent]
            }
        
        # Add contact information if provided
        if contact:
            properties["contacts"] = [contact]
        
        # Add additional properties if provided
        if additional_properties:
            properties.update(additional_properties)
        
        # Create record
        record = {
            "type": "Feature",
            "properties": properties
        }
        
        # Add geometry if bbox is provided
        if bbox:
            record["geometry"] = {
                "type": "Polygon",
                "coordinates": [[
                    [bbox[0], bbox[1]],
                    [bbox[0], bbox[3]],
                    [bbox[2], bbox[3]],
                    [bbox[2], bbox[1]],
                    [bbox[0], bbox[1]]
                ]]
            }
        
        # Create record in catalog
        return await self.create_record(collection_id, record)
