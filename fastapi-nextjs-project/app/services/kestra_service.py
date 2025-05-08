import os
import json
import logging
import yaml
import re
import httpx
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
from pathlib import Path

from app.core.kestra_config import kestra_config

logger = logging.getLogger(__name__)

class KestraService:
    """Service for interacting with Kestra workflow orchestration."""
    
    def __init__(self):
        """Initialize the Kestra service."""
        self.api_url = kestra_config.api_url
        self.auth_enabled = kestra_config.auth_enabled
        self.username = kestra_config.username
        self.password = kestra_config.password
        self.api_key = kestra_config.api_key
        self.default_namespace = kestra_config.default_namespace
        
        # Create directories if they don't exist
        os.makedirs(kestra_config.templates_dir, exist_ok=True)
        os.makedirs(kestra_config.flows_dir, exist_ok=True)
        
        # Initialize HTTP client
        self.client = httpx.AsyncClient(
            base_url=self.api_url,
            timeout=30.0
        )
        
        # Initialize authentication token
        self.auth_token = None
        self.token_expiry = None
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def _get_auth_token(self) -> str:
        """
        Get an authentication token for the Kestra API.
        
        Returns:
            Authentication token
        """
        if not self.auth_enabled:
            return None
        
        # Check if we already have a valid token
        if self.auth_token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.auth_token
        
        # If API key is provided, use it instead of username/password
        if self.api_key:
            self.auth_token = self.api_key
            # Set token expiry to a far future date
            self.token_expiry = datetime.now().replace(year=datetime.now().year + 1)
            return self.auth_token
        
        # Otherwise, authenticate with username and password
        if not self.username or not self.password:
            raise ValueError("Kestra authentication is enabled but no credentials are provided")
        
        try:
            response = await self.client.post(
                "/api/v1/auth/login",
                json={
                    "username": self.username,
                    "password": self.password
                }
            )
            response.raise_for_status()
            
            data = response.json()
            self.auth_token = data.get("token")
            
            # Set token expiry (assuming token is valid for 24 hours)
            self.token_expiry = datetime.now().replace(hour=datetime.now().hour + 24)
            
            return self.auth_token
        
        except Exception as e:
            logger.error(f"Error getting authentication token: {str(e)}")
            raise
    
    async def _make_request(self, method: str, path: str, **kwargs) -> Any:
        """
        Make a request to the Kestra API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API path
            **kwargs: Additional arguments for the request
            
        Returns:
            Response data
        """
        # Get authentication token if needed
        if self.auth_enabled:
            token = await self._get_auth_token()
            headers = kwargs.get("headers", {})
            headers["Authorization"] = f"Bearer {token}"
            kwargs["headers"] = headers
        
        # Make the request
        try:
            response = await getattr(self.client, method.lower())(path, **kwargs)
            response.raise_for_status()
            
            # Return JSON data if available, otherwise return the response
            if response.headers.get("content-type") == "application/json":
                return response.json()
            return response
        
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error making request: {str(e)}")
            raise
    
    async def get_namespaces(self) -> List[str]:
        """
        Get a list of available namespaces.
        
        Returns:
            List of namespace IDs
        """
        try:
            data = await self._make_request("GET", "/api/v1/namespaces")
            return [namespace.get("id") for namespace in data]
        except Exception as e:
            logger.error(f"Error getting namespaces: {str(e)}")
            return []
    
    async def get_flows(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get a list of flows in a namespace.
        
        Args:
            namespace: Namespace ID (default: default namespace)
            
        Returns:
            List of flows
        """
        namespace = namespace or self.default_namespace
        
        try:
            data = await self._make_request("GET", f"/api/v1/flows/search?namespace={namespace}")
            return data
        except Exception as e:
            logger.error(f"Error getting flows: {str(e)}")
            return []
    
    async def get_flow(self, namespace: str, flow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a flow by ID.
        
        Args:
            namespace: Namespace ID
            flow_id: Flow ID
            
        Returns:
            Flow data
        """
        try:
            data = await self._make_request("GET", f"/api/v1/flows/{namespace}/{flow_id}")
            return data
        except Exception as e:
            logger.error(f"Error getting flow: {str(e)}")
            return None
    
    async def create_flow(self, flow_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new flow.
        
        Args:
            flow_data: Flow data in YAML or JSON format
            
        Returns:
            Created flow data
        """
        try:
            # Ensure the flow has a namespace
            if "namespace" not in flow_data:
                flow_data["namespace"] = self.default_namespace
            
            # Create the flow
            data = await self._make_request("POST", "/api/v1/flows", json=flow_data)
            return data
        except Exception as e:
            logger.error(f"Error creating flow: {str(e)}")
            return None
    
    async def update_flow(self, namespace: str, flow_id: str, flow_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an existing flow.
        
        Args:
            namespace: Namespace ID
            flow_id: Flow ID
            flow_data: Flow data in YAML or JSON format
            
        Returns:
            Updated flow data
        """
        try:
            # Ensure the flow has the correct namespace and ID
            flow_data["namespace"] = namespace
            flow_data["id"] = flow_id
            
            # Update the flow
            data = await self._make_request("PUT", f"/api/v1/flows/{namespace}/{flow_id}", json=flow_data)
            return data
        except Exception as e:
            logger.error(f"Error updating flow: {str(e)}")
            return None
    
    async def delete_flow(self, namespace: str, flow_id: str) -> bool:
        """
        Delete a flow.
        
        Args:
            namespace: Namespace ID
            flow_id: Flow ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            await self._make_request("DELETE", f"/api/v1/flows/{namespace}/{flow_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting flow: {str(e)}")
            return False
    
    async def execute_flow(self, namespace: str, flow_id: str, inputs: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Execute a flow.
        
        Args:
            namespace: Namespace ID
            flow_id: Flow ID
            inputs: Input variables for the flow
            
        Returns:
            Execution data
        """
        try:
            data = await self._make_request(
                "POST", 
                f"/api/v1/executions/trigger/{namespace}/{flow_id}",
                json=inputs or {}
            )
            return data
        except Exception as e:
            logger.error(f"Error executing flow: {str(e)}")
            return None
    
    async def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get execution details.
        
        Args:
            execution_id: Execution ID
            
        Returns:
            Execution data
        """
        try:
            data = await self._make_request("GET", f"/api/v1/executions/{execution_id}")
            return data
        except Exception as e:
            logger.error(f"Error getting execution: {str(e)}")
            return None
    
    async def get_executions(self, namespace: Optional[str] = None, flow_id: Optional[str] = None, 
                            state: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get a list of executions.
        
        Args:
            namespace: Namespace ID (default: default namespace)
            flow_id: Flow ID (optional)
            state: Execution state (optional)
            limit: Maximum number of executions to return
            
        Returns:
            List of executions
        """
        namespace = namespace or self.default_namespace
        
        try:
            params = {
                "namespace": namespace,
                "size": limit
            }
            
            if flow_id:
                params["flowId"] = flow_id
            
            if state:
                params["state"] = state
            
            data = await self._make_request("GET", "/api/v1/executions/search", params=params)
            return data
        except Exception as e:
            logger.error(f"Error getting executions: {str(e)}")
            return []
    
    async def get_logs(self, execution_id: str) -> List[Dict[str, Any]]:
        """
        Get logs for an execution.
        
        Args:
            execution_id: Execution ID
            
        Returns:
            List of log entries
        """
        try:
            data = await self._make_request("GET", f"/api/v1/logs/{execution_id}")
            return data
        except Exception as e:
            logger.error(f"Error getting logs: {str(e)}")
            return []
    
    async def get_templates(self) -> List[Dict[str, Any]]:
        """
        Get a list of flow templates.
        
        Returns:
            List of templates
        """
        try:
            # Get templates from the API
            api_templates = await self._make_request("GET", "/api/v1/templates")
            
            # Get templates from the local directory
            local_templates = []
            for file_path in Path(kestra_config.templates_dir).glob("*.yaml"):
                try:
                    with open(file_path, "r") as f:
                        template_data = yaml.safe_load(f)
                        
                        # Add template metadata
                        template_data["source"] = "local"
                        template_data["file_path"] = str(file_path)
                        
                        local_templates.append(template_data)
                except Exception as e:
                    logger.error(f"Error loading template from {file_path}: {str(e)}")
            
            # Combine API and local templates
            return api_templates + local_templates
        except Exception as e:
            logger.error(f"Error getting templates: {str(e)}")
            
            # Fall back to local templates only
            local_templates = []
            for file_path in Path(kestra_config.templates_dir).glob("*.yaml"):
                try:
                    with open(file_path, "r") as f:
                        template_data = yaml.safe_load(f)
                        
                        # Add template metadata
                        template_data["source"] = "local"
                        template_data["file_path"] = str(file_path)
                        
                        local_templates.append(template_data)
                except Exception as e:
                    logger.error(f"Error loading template from {file_path}: {str(e)}")
            
            return local_templates
    
    async def create_template(self, template_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new template.
        
        Args:
            template_data: Template data in YAML or JSON format
            
        Returns:
            Created template data
        """
        try:
            # Try to create the template via the API
            try:
                data = await self._make_request("POST", "/api/v1/templates", json=template_data)
                return data
            except Exception as api_error:
                logger.warning(f"Error creating template via API: {str(api_error)}")
                
                # Fall back to creating a local template file
                template_id = template_data.get("id", f"template_{datetime.now().strftime('%Y%m%d%H%M%S')}")
                file_path = os.path.join(kestra_config.templates_dir, f"{template_id}.yaml")
                
                with open(file_path, "w") as f:
                    yaml.dump(template_data, f)
                
                # Add template metadata
                template_data["source"] = "local"
                template_data["file_path"] = file_path
                
                return template_data
        except Exception as e:
            logger.error(f"Error creating template: {str(e)}")
            return None
    
    async def delete_template(self, template_id: str) -> bool:
        """
        Delete a template.
        
        Args:
            template_id: Template ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Try to delete the template via the API
            try:
                await self._make_request("DELETE", f"/api/v1/templates/{template_id}")
                return True
            except Exception as api_error:
                logger.warning(f"Error deleting template via API: {str(api_error)}")
                
                # Fall back to deleting a local template file
                file_path = os.path.join(kestra_config.templates_dir, f"{template_id}.yaml")
                if os.path.exists(file_path):
                    os.remove(file_path)
                    return True
                
                return False
        except Exception as e:
            logger.error(f"Error deleting template: {str(e)}")
            return False
    
    async def create_flow_from_template(self, template_id: str, variables: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a flow from a template.
        
        Args:
            template_id: Template ID
            variables: Variables to substitute in the template
            
        Returns:
            Created flow data
        """
        try:
            # Get the template
            templates = await self.get_templates()
            template = next((t for t in templates if t.get("id") == template_id), None)
            
            if not template:
                raise ValueError(f"Template {template_id} not found")
            
            # If it's a local template, load it from the file
            if template.get("source") == "local":
                file_path = template.get("file_path")
                with open(file_path, "r") as f:
                    template_content = f.read()
            else:
                # Otherwise, get the template content from the API
                template_content = yaml.dump(template)
            
            # Substitute variables in the template
            for key, value in variables.items():
                template_content = template_content.replace(f"{{{{ {key} }}}}", str(value))
            
            # Parse the template content
            flow_data = yaml.safe_load(template_content)
            
            # Create the flow
            return await self.create_flow(flow_data)
        except Exception as e:
            logger.error(f"Error creating flow from template: {str(e)}")
            return None
    
    def parse_python_script(self, script_path: str) -> Dict[str, Any]:
        """
        Parse a Python script and extract information for creating a Kestra flow.
        
        Args:
            script_path: Path to the Python script
            
        Returns:
            Flow data
        """
        try:
            with open(script_path, "r") as f:
                script_content = f.read()
            
            # Extract flow information from script comments
            flow_id = None
            flow_name = None
            flow_description = None
            
            # Look for flow ID in comments
            id_match = re.search(r'#\s*Flow ID:\s*(.+)', script_content)
            if id_match:
                flow_id = id_match.group(1).strip()
            else:
                # Use the script filename as the flow ID
                flow_id = os.path.splitext(os.path.basename(script_path))[0]
                # Ensure the flow ID is valid
                flow_id = re.sub(r'[^a-zA-Z0-9_]', '_', flow_id)
            
            # Look for flow name in comments
            name_match = re.search(r'#\s*Flow Name:\s*(.+)', script_content)
            if name_match:
                flow_name = name_match.group(1).strip()
            else:
                # Use the script filename as the flow name
                flow_name = os.path.splitext(os.path.basename(script_path))[0]
            
            # Look for flow description in comments
            desc_match = re.search(r'#\s*Flow Description:\s*(.+)', script_content)
            if desc_match:
                flow_description = desc_match.group(1).strip()
            else:
                flow_description = f"Flow generated from {os.path.basename(script_path)}"
            
            # Extract input variables from script
            input_vars = []
            for match in re.finditer(r'#\s*Input:\s*(\w+)\s*\((\w+)\)\s*-\s*(.+)', script_content):
                var_name, var_type, var_desc = match.groups()
                input_vars.append({
                    "name": var_name.strip(),
                    "type": var_type.strip(),
                    "description": var_desc.strip()
                })
            
            # Create flow data
            flow_data = {
                "id": flow_id,
                "namespace": self.default_namespace,
                "revision": 1,
                "tasks": [
                    {
                        "id": "run_script",
                        "type": "io.kestra.plugin.scripts.python.Script",
                        "script": script_content
                    }
                ],
                "inputs": [
                    {
                        "name": var["name"],
                        "type": var["type"],
                        "description": var["description"]
                    } for var in input_vars
                ]
            }
            
            # Add name and description if available
            if flow_name:
                flow_data["name"] = flow_name
            
            if flow_description:
                flow_data["description"] = flow_description
            
            return flow_data
        except Exception as e:
            logger.error(f"Error parsing Python script: {str(e)}")
            raise
    
    def parse_shell_script(self, script_path: str) -> Dict[str, Any]:
        """
        Parse a shell script and extract information for creating a Kestra flow.
        
        Args:
            script_path: Path to the shell script
            
        Returns:
            Flow data
        """
        try:
            with open(script_path, "r") as f:
                script_content = f.read()
            
            # Extract flow information from script comments
            flow_id = None
            flow_name = None
            flow_description = None
            
            # Look for flow ID in comments
            id_match = re.search(r'#\s*Flow ID:\s*(.+)', script_content)
            if id_match:
                flow_id = id_match.group(1).strip()
            else:
                # Use the script filename as the flow ID
                flow_id = os.path.splitext(os.path.basename(script_path))[0]
                # Ensure the flow ID is valid
                flow_id = re.sub(r'[^a-zA-Z0-9_]', '_', flow_id)
            
            # Look for flow name in comments
            name_match = re.search(r'#\s*Flow Name:\s*(.+)', script_content)
            if name_match:
                flow_name = name_match.group(1).strip()
            else:
                # Use the script filename as the flow name
                flow_name = os.path.splitext(os.path.basename(script_path))[0]
            
            # Look for flow description in comments
            desc_match = re.search(r'#\s*Flow Description:\s*(.+)', script_content)
            if desc_match:
                flow_description = desc_match.group(1).strip()
            else:
                flow_description = f"Flow generated from {os.path.basename(script_path)}"
            
            # Extract input variables from script
            input_vars = []
            for match in re.finditer(r'#\s*Input:\s*(\w+)\s*\((\w+)\)\s*-\s*(.+)', script_content):
                var_name, var_type, var_desc = match.groups()
                input_vars.append({
                    "name": var_name.strip(),
                    "type": var_type.strip(),
                    "description": var_desc.strip()
                })
            
            # Determine the shell type
            shell_type = "BASH"
            if script_path.endswith(".sh"):
                shell_type = "BASH"
            elif script_path.endswith(".ps1"):
                shell_type = "POWERSHELL"
            
            # Create flow data
            flow_data = {
                "id": flow_id,
                "namespace": self.default_namespace,
                "revision": 1,
                "tasks": [
                    {
                        "id": "run_script",
                        "type": "io.kestra.plugin.scripts.shell.Script",
                        "shell": shell_type,
                        "commands": [script_content]
                    }
                ],
                "inputs": [
                    {
                        "name": var["name"],
                        "type": var["type"],
                        "description": var["description"]
                    } for var in input_vars
                ]
            }
            
            # Add name and description if available
            if flow_name:
                flow_data["name"] = flow_name
            
            if flow_description:
                flow_data["description"] = flow_description
            
            return flow_data
        except Exception as e:
            logger.error(f"Error parsing shell script: {str(e)}")
            raise
    
    async def create_flow_from_script(self, script_path: str) -> Optional[Dict[str, Any]]:
        """
        Create a flow from a script file.
        
        Args:
            script_path: Path to the script file
            
        Returns:
            Created flow data
        """
        try:
            # Parse the script based on its type
            if script_path.endswith(".py"):
                flow_data = self.parse_python_script(script_path)
            elif script_path.endswith((".sh", ".bash", ".ps1")):
                flow_data = self.parse_shell_script(script_path)
            else:
                raise ValueError(f"Unsupported script type: {script_path}")
            
            # Create the flow
            return await self.create_flow(flow_data)
        except Exception as e:
            logger.error(f"Error creating flow from script: {str(e)}")
            return None
    
    async def create_flow_from_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """
        Create flows from all scripts in a directory.
        
        Args:
            directory_path: Path to the directory containing scripts
            
        Returns:
            List of created flows
        """
        try:
            created_flows = []
            
            # Find all Python and shell scripts in the directory
            script_paths = []
            for ext in [".py", ".sh", ".bash", ".ps1"]:
                script_paths.extend(list(Path(directory_path).glob(f"*{ext}")))
            
            # Create a flow for each script
            for script_path in script_paths:
                flow = await self.create_flow_from_script(str(script_path))
                if flow:
                    created_flows.append(flow)
            
            return created_flows
        except Exception as e:
            logger.error(f"Error creating flows from directory: {str(e)}")
            return []
    
    async def setup_pocketbase_trigger(self, flow_id: str, collection: str, event_type: str = "create") -> bool:
        """
        Set up a PocketBase trigger for a flow.
        
        Args:
            flow_id: Flow ID
            collection: PocketBase collection name
            event_type: Event type (create, update, delete)
            
        Returns:
            True if successful, False otherwise
        """
        if not kestra_config.is_pocketbase_configured:
            logger.error("PocketBase integration is not configured")
            return False
        
        try:
            # Get the flow
            flow = await self.get_flow(self.default_namespace, flow_id)
            if not flow:
                raise ValueError(f"Flow {flow_id} not found")
            
            # Add a trigger to the flow
            if "triggers" not in flow:
                flow["triggers"] = []
            
            # Create a webhook trigger
            trigger = {
                "id": f"pocketbase_{collection}_{event_type}",
                "type": "io.kestra.plugin.webhook.Trigger",
                "key": f"{flow_id}_{collection}_{event_type}",
                "conditions": [
                    {
                        "type": "io.kestra.plugin.webhook.conditions.JsonPath",
                        "path": "$.collection",
                        "value": collection
                    },
                    {
                        "type": "io.kestra.plugin.webhook.conditions.JsonPath",
                        "path": "$.event",
                        "value": event_type
                    }
                ]
            }
            
            # Add the trigger to the flow
            flow["triggers"].append(trigger)
            
            # Update the flow
            updated_flow = await self.update_flow(self.default_namespace, flow_id, flow)
            if not updated_flow:
                raise ValueError(f"Failed to update flow {flow_id}")
            
            # Set up the webhook in PocketBase
            # TODO: Implement PocketBase webhook setup
            
            return True
        except Exception as e:
            logger.error(f"Error setting up PocketBase trigger: {str(e)}")
            return False
    
    async def generate_flow_visualization(self, flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a visualization of a flow.
        
        Args:
            flow_data: Flow data
            
        Returns:
            Visualization data
        """
        try:
            # Extract tasks and triggers from the flow
            tasks = flow_data.get("tasks", [])
            triggers = flow_data.get("triggers", [])
            
            # Create nodes for tasks and triggers
            nodes = []
            edges = []
            
            # Add trigger nodes
            for i, trigger in enumerate(triggers):
                nodes.append({
                    "id": trigger.get("id", f"trigger_{i}"),
                    "type": "trigger",
                    "label": trigger.get("id", f"Trigger {i+1}"),
                    "data": trigger
                })
            
            # Add task nodes
            for task in tasks:
                task_id = task.get("id")
                if not task_id:
                    continue
                
                nodes.append({
                    "id": task_id,
                    "type": "task",
                    "label": task.get("name", task_id),
                    "data": task
                })
                
                # Add edges for task dependencies
                dependencies = task.get("dependsOn", [])
                for dep in dependencies:
                    edges.append({
                        "source": dep,
                        "target": task_id
                    })
            
            # If there are no explicit dependencies, create a linear flow
            if not edges and len(nodes) > 1:
                for i in range(len(nodes) - 1):
                    edges.append({
                        "source": nodes[i]["id"],
                        "target": nodes[i + 1]["id"]
                    })
            
            return {
                "nodes": nodes,
                "edges": edges
            }
        except Exception as e:
            logger.error(f"Error generating flow visualization: {str(e)}")
            return {"nodes": [], "edges": []}

# Create a global instance of KestraService
kestra_service = KestraService()
