import os
import json
import logging
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class KestraService:
    """
    Service for interacting with Kestra API
    """
    
    def __init__(self, api_url: Optional[str] = None):
        """Initialize the Kestra Service"""
        self.api_url = api_url or os.environ.get("KESTRA_API_URL", "http://localhost:8080/api/v1")
    
    async def get_workflows(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get workflows from Kestra
        
        Args:
            namespace: Optional namespace to filter workflows
            
        Returns:
            List of workflows
        """
        url = f"{self.api_url}/flows"
        if namespace:
            url += f"?namespace={namespace}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Error getting workflows: {error_text}")
                    raise Exception(f"Error getting workflows: {response.status} - {error_text}")
                
                return await response.json()
    
    async def get_workflow(self, namespace: str, flow_id: str) -> Dict[str, Any]:
        """
        Get a specific workflow from Kestra
        
        Args:
            namespace: Workflow namespace
            flow_id: Workflow ID
            
        Returns:
            Workflow details
        """
        url = f"{self.api_url}/flows/{namespace}/{flow_id}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Error getting workflow {namespace}/{flow_id}: {error_text}")
                    raise Exception(f"Error getting workflow: {response.status} - {error_text}")
                
                return await response.json()
    
    async def trigger_workflow(self, namespace: str, flow_id: str, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Trigger a workflow execution
        
        Args:
            namespace: Workflow namespace
            flow_id: Workflow ID
            inputs: Optional inputs for the workflow
            
        Returns:
            Execution details
        """
        url = f"{self.api_url}/executions/trigger/{namespace}/{flow_id}"
        payload = {"inputs": inputs or {}}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Error triggering workflow {namespace}/{flow_id}: {error_text}")
                    raise Exception(f"Error triggering workflow: {response.status} - {error_text}")
                
                return await response.json()
    
    async def get_executions(self, namespace: Optional[str] = None, flow_id: Optional[str] = None, 
                            state: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get workflow executions
        
        Args:
            namespace: Optional namespace to filter executions
            flow_id: Optional workflow ID to filter executions
            state: Optional state to filter executions
            limit: Maximum number of executions to return
            
        Returns:
            List of executions
        """
        url = f"{self.api_url}/executions/search"
        params = {"size": limit}
        
        if namespace:
            params["namespace"] = namespace
        if flow_id:
            params["flowId"] = flow_id
        if state:
            params["state"] = state
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Error getting executions: {error_text}")
                    raise Exception(f"Error getting executions: {response.status} - {error_text}")
                
                return await response.json()
    
    async def get_execution(self, execution_id: str) -> Dict[str, Any]:
        """
        Get a specific execution
        
        Args:
            execution_id: Execution ID
            
        Returns:
            Execution details
        """
        url = f"{self.api_url}/executions/{execution_id}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Error getting execution {execution_id}: {error_text}")
                    raise Exception(f"Error getting execution: {response.status} - {error_text}")
                
                return await response.json()
    
    async def restart_execution(self, execution_id: str) -> Dict[str, Any]:
        """
        Restart a failed execution
        
        Args:
            execution_id: Execution ID
            
        Returns:
            New execution details
        """
        url = f"{self.api_url}/executions/{execution_id}/restart"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Error restarting execution {execution_id}: {error_text}")
                    raise Exception(f"Error restarting execution: {response.status} - {error_text}")
                
                return await response.json()
    
    async def stop_execution(self, execution_id: str) -> Dict[str, Any]:
        """
        Stop a running execution
        
        Args:
            execution_id: Execution ID
            
        Returns:
            Execution details
        """
        url = f"{self.api_url}/executions/{execution_id}/kill"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Error stopping execution {execution_id}: {error_text}")
                    raise Exception(f"Error stopping execution: {response.status} - {error_text}")
                
                return await response.json()
    
    async def get_logs(self, execution_id: str) -> List[Dict[str, Any]]:
        """
        Get logs for an execution
        
        Args:
            execution_id: Execution ID
            
        Returns:
            List of log entries
        """
        url = f"{self.api_url}/logs/{execution_id}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Error getting logs for execution {execution_id}: {error_text}")
                    raise Exception(f"Error getting logs: {response.status} - {error_text}")
                
                return await response.json()
    
    async def create_webhook_trigger(self, namespace: str, flow_id: str, 
                                   key: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a webhook trigger for a workflow
        
        Args:
            namespace: Workflow namespace
            flow_id: Workflow ID
            key: Optional key for the webhook
            
        Returns:
            Webhook details
        """
        url = f"{self.api_url}/webhooks"
        payload = {
            "namespace": namespace,
            "flowId": flow_id
        }
        
        if key:
            payload["key"] = key
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Error creating webhook for {namespace}/{flow_id}: {error_text}")
                    raise Exception(f"Error creating webhook: {response.status} - {error_text}")
                
                return await response.json()
    
    async def delete_webhook_trigger(self, webhook_id: str) -> bool:
        """
        Delete a webhook trigger
        
        Args:
            webhook_id: Webhook ID
            
        Returns:
            True if successful
        """
        url = f"{self.api_url}/webhooks/{webhook_id}"
        
        async with aiohttp.ClientSession() as session:
            async with session.delete(url) as response:
                if response.status != 204:
                    error_text = await response.text()
                    logger.error(f"Error deleting webhook {webhook_id}: {error_text}")
                    raise Exception(f"Error deleting webhook: {response.status} - {error_text}")
                
                return True
    
    async def sync_workflow_to_pocketbase(self, pb_client, workflow: Dict[str, Any], owner_id: str) -> Dict[str, Any]:
        """
        Sync a Kestra workflow to PocketBase
        
        Args:
            pb_client: PocketBase client
            workflow: Workflow details from Kestra
            owner_id: Owner user ID
            
        Returns:
            PocketBase record
        """
        try:
            # Check if workflow already exists
            existing_records = await pb_client.collection('kestra_workflows').get_list(
                1, 1, 
                {
                    'filter': f'namespace="{workflow["namespace"]}" && workflow_id="{workflow["id"]}"'
                }
            )
            
            workflow_data = {
                'name': workflow.get('name', 'Unnamed Workflow'),
                'namespace': workflow['namespace'],
                'workflow_id': workflow['id'],
                'description': workflow.get('description', ''),
                'tags': json.dumps(workflow.get('tags', [])),
                'triggers': json.dumps(workflow.get('triggers', [])),
                'tasks': json.dumps(workflow.get('tasks', [])),
                'enabled': True,
                'owner': owner_id
            }
            
            if existing_records.total_items > 0:
                # Update existing record
                existing_id = existing_records.items[0].id
                return await pb_client.collection('kestra_workflows').update(existing_id, workflow_data)
            else:
                # Create new record
                return await pb_client.collection('kestra_workflows').create(workflow_data)
        
        except Exception as e:
            logger.error(f"Error syncing workflow to PocketBase: {str(e)}")
            raise
    
    async def sync_execution_to_pocketbase(self, pb_client, execution: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sync a Kestra execution to PocketBase
        
        Args:
            pb_client: PocketBase client
            execution: Execution details from Kestra
            
        Returns:
            PocketBase record
        """
        try:
            # Find the workflow record
            workflow_records = await pb_client.collection('kestra_workflows').get_list(
                1, 1, 
                {
                    'filter': f'namespace="{execution["namespace"]}" && workflow_id="{execution["flowId"]}"'
                }
            )
            
            if workflow_records.total_items == 0:
                raise Exception(f"Workflow {execution['namespace']}/{execution['flowId']} not found in PocketBase")
            
            workflow_id = workflow_records.items[0].id
            
            # Check if execution already exists
            existing_records = await pb_client.collection('kestra_executions').get_list(
                1, 1, 
                {
                    'filter': f'execution_id="{execution["id"]}"'
                }
            )
            
            execution_data = {
                'workflow': workflow_id,
                'execution_id': execution['id'],
                'namespace': execution['namespace'],
                'workflow_id': execution['flowId'],
                'status': execution['state'],
                'inputs': json.dumps(execution.get('inputs', {})),
                'outputs': json.dumps(execution.get('outputs', {})),
                'task_runs': json.dumps(execution.get('taskRunList', []))
            }
            
            # Add dates if available
            if 'startDate' in execution:
                execution_data['start_date'] = datetime.fromisoformat(execution['startDate'].replace('Z', '+00:00')).isoformat()
            
            if 'endDate' in execution:
                execution_data['end_date'] = datetime.fromisoformat(execution['endDate'].replace('Z', '+00:00')).isoformat()
            
            # Calculate duration if both dates are available
            if 'startDate' in execution and 'endDate' in execution:
                start = datetime.fromisoformat(execution['startDate'].replace('Z', '+00:00'))
                end = datetime.fromisoformat(execution['endDate'].replace('Z', '+00:00'))
                execution_data['duration'] = (end - start).total_seconds() * 1000  # Duration in milliseconds
            
            if existing_records.total_items > 0:
                # Update existing record
                existing_id = existing_records.items[0].id
                return await pb_client.collection('kestra_executions').update(existing_id, execution_data)
            else:
                # Create new record
                return await pb_client.collection('kestra_executions').create(execution_data)
        
        except Exception as e:
            logger.error(f"Error syncing execution to PocketBase: {str(e)}")
            raise
