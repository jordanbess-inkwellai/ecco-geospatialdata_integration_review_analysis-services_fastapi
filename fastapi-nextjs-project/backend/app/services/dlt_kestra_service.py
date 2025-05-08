import os
import json
import logging
import tempfile
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import yaml

logger = logging.getLogger(__name__)

class DLTKestraService:
    """
    Service for integrating DLT (Data Load Tool) with Kestra orchestration
    """
    
    def __init__(self, kestra_service=None):
        """
        Initialize the DLT Kestra Service
        
        Args:
            kestra_service: Optional Kestra service instance
        """
        self.kestra_service = kestra_service
    
    async def generate_dlt_workflow(
        self,
        workflow_name: str,
        source_type: str,
        destination_type: str,
        source_config: Dict[str, Any],
        destination_config: Dict[str, Any],
        schedule: Optional[str] = None,
        namespace: str = "default",
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        python_version: str = "3.10"
    ) -> Dict[str, Any]:
        """
        Generate a Kestra workflow YAML for a DLT pipeline
        
        Args:
            workflow_name: Name of the workflow
            source_type: Type of source (e.g., 'postgres', 'mysql', 'api', 'github', etc.)
            destination_type: Type of destination (e.g., 'postgres', 'bigquery', 'duckdb', etc.)
            source_config: Configuration for the source
            destination_config: Configuration for the destination
            schedule: Optional cron schedule for the workflow
            namespace: Kestra namespace
            description: Optional workflow description
            tags: Optional tags for the workflow
            python_version: Python version to use
            
        Returns:
            Generated workflow definition
        """
        try:
            # Create workflow ID from name
            workflow_id = workflow_name.lower().replace(" ", "_")
            
            # Create base workflow structure
            workflow = {
                "id": workflow_id,
                "namespace": namespace,
                "tasks": [],
                "inputs": []
            }
            
            # Add metadata
            if description:
                workflow["description"] = description
            
            if tags:
                workflow["tags"] = tags
            
            # Add schedule if provided
            if schedule:
                workflow["triggers"] = [
                    {
                        "type": "schedule",
                        "cron": schedule
                    }
                ]
            
            # Add inputs for credentials and configurations
            # These will be passed at runtime or set as defaults
            
            # Source credentials input
            source_creds_input = {
                "name": "source_credentials",
                "type": "JSON",
                "description": f"Credentials for the {source_type} source",
                "required": True
            }
            
            # Destination credentials input
            dest_creds_input = {
                "name": "destination_credentials",
                "type": "JSON",
                "description": f"Credentials for the {destination_type} destination",
                "required": True
            }
            
            # Add inputs to workflow
            workflow["inputs"] = [source_creds_input, dest_creds_input]
            
            # Create Python script for DLT pipeline
            dlt_script = self._generate_dlt_script(
                source_type=source_type,
                destination_type=destination_type,
                source_config=source_config,
                destination_config=destination_config
            )
            
            # Create a Python task to run the DLT pipeline
            python_task = {
                "id": "run_dlt_pipeline",
                "type": "io.kestra.plugin.scripts.python.Python",
                "pythonVersion": python_version,
                "script": dlt_script,
                "inputFiles": {
                    "source_credentials.json": "{{ inputs.source_credentials }}",
                    "destination_credentials.json": "{{ inputs.destination_credentials }}"
                }
            }
            
            # Add task to workflow
            workflow["tasks"].append(python_task)
            
            # Add notification task on completion
            notification_task = {
                "id": "notify_completion",
                "type": "io.kestra.plugin.notifications.slack.SlackMessage",
                "url": "{{ inputs.slack_webhook_url }}",
                "message": f"DLT pipeline {workflow_name} completed with status: {{{{ task.run_dlt_pipeline.status }}}}",
                "dependsOn": ["run_dlt_pipeline"]
            }
            
            # Add optional Slack webhook URL input
            slack_input = {
                "name": "slack_webhook_url",
                "type": "STRING",
                "description": "Slack webhook URL for notifications",
                "required": False
            }
            workflow["inputs"].append(slack_input)
            
            # Add notification task conditionally
            workflow["tasks"].append(notification_task)
            
            return workflow
        except Exception as e:
            logger.error(f"Error generating DLT workflow: {str(e)}")
            raise
    
    def _generate_dlt_script(
        self,
        source_type: str,
        destination_type: str,
        source_config: Dict[str, Any],
        destination_config: Dict[str, Any]
    ) -> str:
        """
        Generate a Python script for a DLT pipeline
        
        Args:
            source_type: Type of source
            destination_type: Type of destination
            source_config: Configuration for the source
            destination_config: Configuration for the destination
            
        Returns:
            Python script as a string
        """
        # Create a template for the DLT script
        script = """
import os
import json
import dlt
from dlt.common.typing import TDataItem, TDataItems
from dlt.common.configuration import configure_source
from dlt.common.destination import Destination
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        # Load credentials from files
        with open("source_credentials.json", "r") as f:
            source_credentials = json.load(f)
        
        with open("destination_credentials.json", "r") as f:
            destination_credentials = json.load(f)
        
        logger.info("Starting DLT pipeline")
        
        # Configure source
"""
        
        # Add source configuration based on source type
        if source_type == "postgres":
            script += """
        # Configure PostgreSQL source
        source = dlt.sources.sql(
            connection_string=source_credentials.get("connection_string"),
            query=source_credentials.get("query")
        )
"""
        elif source_type == "mysql":
            script += """
        # Configure MySQL source
        source = dlt.sources.sql(
            connection_string=source_credentials.get("connection_string"),
            query=source_credentials.get("query")
        )
"""
        elif source_type == "api":
            script += """
        # Configure generic API source
        source = dlt.sources.http(
            url=source_credentials.get("url"),
            method=source_credentials.get("method", "GET"),
            headers=source_credentials.get("headers", {}),
            params=source_credentials.get("params", {})
        )
"""
        elif source_type in ["github", "stripe", "google_analytics", "salesforce"]:
            script += f"""
        # Configure {source_type} source
        source_config = configure_source(
            "{source_type}",
            credentials=source_credentials,
            config=source_credentials.get("config", {{}})
        )
        source = getattr(dlt.sources, "{source_type}")(**source_config)
"""
        else:
            # Generic source
            script += """
        # Configure custom source
        source_module = source_credentials.get("module")
        source_function = source_credentials.get("function")
        source_args = source_credentials.get("args", {})
        
        # Import the module dynamically
        module = __import__(source_module, fromlist=[source_function])
        source_func = getattr(module, source_function)
        
        # Create the source
        source = source_func(**source_args)
"""
        
        # Add destination configuration
        script += """
        # Configure destination
"""
        
        if destination_type == "postgres":
            script += """
        destination = {
            "type": "postgres",
            "connection_string": destination_credentials.get("connection_string"),
            "schema": destination_credentials.get("schema", "public")
        }
"""
        elif destination_type == "bigquery":
            script += """
        destination = {
            "type": "bigquery",
            "credentials": destination_credentials.get("credentials"),
            "dataset": destination_credentials.get("dataset")
        }
"""
        elif destination_type == "duckdb":
            script += """
        destination = {
            "type": "duckdb",
            "database": destination_credentials.get("database", "data.duckdb")
        }
"""
        elif destination_type == "redshift":
            script += """
        destination = {
            "type": "redshift",
            "connection_string": destination_credentials.get("connection_string"),
            "schema": destination_credentials.get("schema", "public")
        }
"""
        else:
            # Generic destination
            script += """
        destination = destination_credentials
"""
        
        # Add pipeline execution
        script += """
        # Create and run the pipeline
        pipeline_name = destination_credentials.get("pipeline_name", "dlt_kestra_pipeline")
        dataset_name = destination_credentials.get("dataset_name")
        table_name = destination_credentials.get("table_name")
        write_disposition = destination_credentials.get("write_disposition", "merge")
        primary_key = destination_credentials.get("primary_key")
        
        # Initialize the pipeline
        pipeline = dlt.pipeline(
            pipeline_name=pipeline_name,
            destination=destination,
            dataset_name=dataset_name,
            full_refresh=destination_credentials.get("full_refresh", False)
        )
        
        # Run the pipeline
        load_info = pipeline.run(
            source,
            table_name=table_name,
            write_disposition=write_disposition,
            primary_key=primary_key
        )
        
        # Log the results
        logger.info(f"Pipeline run completed with load_id: {load_info.load_id}")
        logger.info(f"Loaded to: {load_info.destination_name}.{load_info.dataset_name}.{load_info.table_name}")
        logger.info(f"Metrics: {load_info.metrics}")
        
        # Return success
        return {
            "status": "success",
            "load_id": load_info.load_id,
            "destination": f"{load_info.destination_name}.{load_info.dataset_name}.{load_info.table_name}",
            "metrics": {
                "inserted_rows": load_info.metrics.inserted_rows,
                "updated_rows": load_info.metrics.updated_rows,
                "deleted_rows": load_info.metrics.deleted_rows
            }
        }
    
    except Exception as e:
        logger.error(f"Error in DLT pipeline: {str(e)}")
        raise

if __name__ == "__main__":
    main()
"""
        
        return script
    
    async def create_dlt_workflow(
        self,
        workflow_name: str,
        source_type: str,
        destination_type: str,
        source_config: Dict[str, Any],
        destination_config: Dict[str, Any],
        schedule: Optional[str] = None,
        namespace: str = "default",
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        python_version: str = "3.10"
    ) -> Dict[str, Any]:
        """
        Create a DLT workflow in Kestra
        
        Args:
            workflow_name: Name of the workflow
            source_type: Type of source
            destination_type: Type of destination
            source_config: Configuration for the source
            destination_config: Configuration for the destination
            schedule: Optional cron schedule for the workflow
            namespace: Kestra namespace
            description: Optional workflow description
            tags: Optional tags for the workflow
            python_version: Python version to use
            
        Returns:
            Created workflow information
        """
        try:
            # Generate the workflow definition
            workflow = await self.generate_dlt_workflow(
                workflow_name=workflow_name,
                source_type=source_type,
                destination_type=destination_type,
                source_config=source_config,
                destination_config=destination_config,
                schedule=schedule,
                namespace=namespace,
                description=description,
                tags=tags,
                python_version=python_version
            )
            
            # Convert to YAML
            workflow_yaml = yaml.dump(workflow, sort_keys=False)
            
            # Create a temporary file with the workflow YAML
            with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as temp_file:
                temp_file.write(workflow_yaml.encode())
                temp_file_path = temp_file.name
            
            try:
                # Use Kestra CLI to create the workflow
                # This requires Kestra CLI to be installed
                import subprocess
                result = subprocess.run(
                    ["kestra", "flow", "create", "-f", temp_file_path],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                # Parse the result
                created_workflow = {
                    "id": workflow["id"],
                    "namespace": workflow["namespace"],
                    "status": "created",
                    "message": result.stdout
                }
                
                return created_workflow
            finally:
                # Clean up the temporary file
                os.unlink(temp_file_path)
        except Exception as e:
            logger.error(f"Error creating DLT workflow in Kestra: {str(e)}")
            raise
    
    async def run_dlt_workflow(
        self,
        workflow_id: str,
        namespace: str,
        source_credentials: Dict[str, Any],
        destination_credentials: Dict[str, Any],
        slack_webhook_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run a DLT workflow in Kestra
        
        Args:
            workflow_id: ID of the workflow
            namespace: Kestra namespace
            source_credentials: Credentials for the source
            destination_credentials: Credentials for the destination
            slack_webhook_url: Optional Slack webhook URL for notifications
            
        Returns:
            Execution information
        """
        try:
            # Prepare inputs
            inputs = {
                "source_credentials": json.dumps(source_credentials),
                "destination_credentials": json.dumps(destination_credentials)
            }
            
            if slack_webhook_url:
                inputs["slack_webhook_url"] = slack_webhook_url
            
            # Use Kestra service to trigger the workflow
            if self.kestra_service:
                execution = await self.kestra_service.trigger_workflow(
                    namespace=namespace,
                    flow_id=workflow_id,
                    inputs=inputs
                )
                return execution
            else:
                # Use Kestra CLI if service not available
                import subprocess
                
                # Create a temporary file with the inputs
                with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
                    temp_file.write(json.dumps(inputs).encode())
                    temp_file_path = temp_file.name
                
                try:
                    # Run the workflow
                    result = subprocess.run(
                        ["kestra", "execution", "trigger", "-f", temp_file_path, f"{namespace}.{workflow_id}"],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    
                    # Parse the execution ID from the output
                    import re
                    execution_id_match = re.search(r"Execution (\w+) triggered", result.stdout)
                    execution_id = execution_id_match.group(1) if execution_id_match else None
                    
                    return {
                        "id": execution_id,
                        "namespace": namespace,
                        "flowId": workflow_id,
                        "status": "RUNNING",
                        "message": result.stdout
                    }
                finally:
                    # Clean up the temporary file
                    os.unlink(temp_file_path)
        except Exception as e:
            logger.error(f"Error running DLT workflow in Kestra: {str(e)}")
            raise
