import os
import json
import logging
import requests
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)

class DocETLService:
    """Service for interacting with DocETL."""
    
    def __init__(self):
        """Initialize the DocETL service."""
        self.api_url = os.getenv("DOCETL_API_URL", "http://localhost:8001/api")
        self.is_configured = bool(self.api_url)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the status of the DocETL service.
        
        Returns:
            Status information
        """
        if not self.is_configured:
            return {
                "status": "not_configured",
                "message": "DocETL is not configured"
            }
        
        try:
            response = requests.get(f"{self.api_url}/status")
            response.raise_for_status()
            
            return {
                "status": "ok",
                "message": "DocETL is available",
                "data": response.json()
            }
        except Exception as e:
            logger.error(f"Error getting DocETL status: {str(e)}")
            return {
                "status": "error",
                "message": f"Error connecting to DocETL: {str(e)}"
            }
    
    def get_pipelines(self) -> List[Dict[str, Any]]:
        """
        Get a list of available pipelines.
        
        Returns:
            List of pipelines
        """
        if not self.is_configured:
            return []
        
        try:
            response = requests.get(f"{self.api_url}/pipelines")
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error getting pipelines: {str(e)}")
            return []
    
    def get_pipeline(self, pipeline_id: str) -> Dict[str, Any]:
        """
        Get details for a specific pipeline.
        
        Args:
            pipeline_id: Pipeline ID
            
        Returns:
            Pipeline details
        """
        if not self.is_configured:
            return {}
        
        try:
            response = requests.get(f"{self.api_url}/pipelines/{pipeline_id}")
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error getting pipeline {pipeline_id}: {str(e)}")
            return {}
    
    def run_pipeline(self, pipeline_id: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run a pipeline.
        
        Args:
            pipeline_id: Pipeline ID
            parameters: Pipeline parameters
            
        Returns:
            Pipeline run result
        """
        if not self.is_configured:
            return {
                "status": "error",
                "message": "DocETL is not configured"
            }
        
        try:
            response = requests.post(
                f"{self.api_url}/pipelines/{pipeline_id}/run",
                json=parameters or {}
            )
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error running pipeline {pipeline_id}: {str(e)}")
            return {
                "status": "error",
                "message": f"Error running pipeline: {str(e)}"
            }
    
    def get_pipeline_runs(self, pipeline_id: str) -> List[Dict[str, Any]]:
        """
        Get a list of runs for a specific pipeline.
        
        Args:
            pipeline_id: Pipeline ID
            
        Returns:
            List of pipeline runs
        """
        if not self.is_configured:
            return []
        
        try:
            response = requests.get(f"{self.api_url}/pipelines/{pipeline_id}/runs")
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error getting pipeline runs for {pipeline_id}: {str(e)}")
            return []
    
    def get_pipeline_run(self, pipeline_id: str, run_id: str) -> Dict[str, Any]:
        """
        Get details for a specific pipeline run.
        
        Args:
            pipeline_id: Pipeline ID
            run_id: Run ID
            
        Returns:
            Pipeline run details
        """
        if not self.is_configured:
            return {}
        
        try:
            response = requests.get(f"{self.api_url}/pipelines/{pipeline_id}/runs/{run_id}")
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error getting pipeline run {run_id} for {pipeline_id}: {str(e)}")
            return {}
    
    def get_pipeline_run_logs(self, pipeline_id: str, run_id: str) -> List[Dict[str, Any]]:
        """
        Get logs for a specific pipeline run.
        
        Args:
            pipeline_id: Pipeline ID
            run_id: Run ID
            
        Returns:
            Pipeline run logs
        """
        if not self.is_configured:
            return []
        
        try:
            response = requests.get(f"{self.api_url}/pipelines/{pipeline_id}/runs/{run_id}/logs")
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error getting pipeline run logs for {run_id}: {str(e)}")
            return []
    
    def create_pipeline(self, pipeline_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new pipeline.
        
        Args:
            pipeline_config: Pipeline configuration
            
        Returns:
            Created pipeline
        """
        if not self.is_configured:
            return {
                "status": "error",
                "message": "DocETL is not configured"
            }
        
        try:
            response = requests.post(
                f"{self.api_url}/pipelines",
                json=pipeline_config
            )
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error creating pipeline: {str(e)}")
            return {
                "status": "error",
                "message": f"Error creating pipeline: {str(e)}"
            }
    
    def update_pipeline(self, pipeline_id: str, pipeline_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing pipeline.
        
        Args:
            pipeline_id: Pipeline ID
            pipeline_config: Pipeline configuration
            
        Returns:
            Updated pipeline
        """
        if not self.is_configured:
            return {
                "status": "error",
                "message": "DocETL is not configured"
            }
        
        try:
            response = requests.put(
                f"{self.api_url}/pipelines/{pipeline_id}",
                json=pipeline_config
            )
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error updating pipeline {pipeline_id}: {str(e)}")
            return {
                "status": "error",
                "message": f"Error updating pipeline: {str(e)}"
            }
    
    def delete_pipeline(self, pipeline_id: str) -> Dict[str, Any]:
        """
        Delete a pipeline.
        
        Args:
            pipeline_id: Pipeline ID
            
        Returns:
            Deletion result
        """
        if not self.is_configured:
            return {
                "status": "error",
                "message": "DocETL is not configured"
            }
        
        try:
            response = requests.delete(f"{self.api_url}/pipelines/{pipeline_id}")
            response.raise_for_status()
            
            return {
                "status": "success",
                "message": f"Pipeline {pipeline_id} deleted successfully"
            }
        except Exception as e:
            logger.error(f"Error deleting pipeline {pipeline_id}: {str(e)}")
            return {
                "status": "error",
                "message": f"Error deleting pipeline: {str(e)}"
            }
    
    def get_extractors(self) -> List[Dict[str, Any]]:
        """
        Get a list of available extractors.
        
        Returns:
            List of extractors
        """
        if not self.is_configured:
            return []
        
        try:
            response = requests.get(f"{self.api_url}/extractors")
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error getting extractors: {str(e)}")
            return []
    
    def get_transformers(self) -> List[Dict[str, Any]]:
        """
        Get a list of available transformers.
        
        Returns:
            List of transformers
        """
        if not self.is_configured:
            return []
        
        try:
            response = requests.get(f"{self.api_url}/transformers")
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error getting transformers: {str(e)}")
            return []
    
    def get_loaders(self) -> List[Dict[str, Any]]:
        """
        Get a list of available loaders.
        
        Returns:
            List of loaders
        """
        if not self.is_configured:
            return []
        
        try:
            response = requests.get(f"{self.api_url}/loaders")
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error getting loaders: {str(e)}")
            return []

# Create a global instance of DocETLService
docetl_service = DocETLService()
