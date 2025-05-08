from fastapi import APIRouter, Depends, HTTPException, Body, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
import logging
import json
from datetime import datetime
import pocketbase
from pocketbase.client import ClientResponseError

from app.core.database import get_db
from app.services.kestra_service import KestraService
from app.core.security import get_current_user
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize Kestra Service
kestra_service = KestraService()

# Initialize PocketBase client
pb_client = pocketbase.Client(settings.POCKETBASE_URL)


@router.get("/workflows")
async def get_workflows(
    namespace: Optional[str] = None,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get workflows from Kestra
    """
    try:
        workflows = await kestra_service.get_workflows(namespace)
        return workflows
    except Exception as e:
        logger.error(f"Error getting workflows: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting workflows: {str(e)}")


@router.get("/workflows/{namespace}/{flow_id}")
async def get_workflow(
    namespace: str,
    flow_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get a specific workflow from Kestra
    """
    try:
        workflow = await kestra_service.get_workflow(namespace, flow_id)
        return workflow
    except Exception as e:
        logger.error(f"Error getting workflow {namespace}/{flow_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting workflow: {str(e)}")


@router.post("/workflows/trigger/{namespace}/{flow_id}")
async def trigger_workflow(
    namespace: str,
    flow_id: str,
    inputs: Optional[Dict[str, Any]] = Body(None),
    current_user: Dict = Depends(get_current_user)
):
    """
    Trigger a workflow execution
    """
    try:
        execution = await kestra_service.trigger_workflow(namespace, flow_id, inputs)
        return execution
    except Exception as e:
        logger.error(f"Error triggering workflow {namespace}/{flow_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error triggering workflow: {str(e)}")


@router.get("/executions")
async def get_executions(
    namespace: Optional[str] = None,
    flow_id: Optional[str] = None,
    state: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get workflow executions
    """
    try:
        executions = await kestra_service.get_executions(namespace, flow_id, state, limit)
        return executions
    except Exception as e:
        logger.error(f"Error getting executions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting executions: {str(e)}")


@router.get("/executions/{execution_id}")
async def get_execution(
    execution_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get a specific execution
    """
    try:
        execution = await kestra_service.get_execution(execution_id)
        return execution
    except Exception as e:
        logger.error(f"Error getting execution {execution_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting execution: {str(e)}")


@router.post("/executions/{execution_id}/restart")
async def restart_execution(
    execution_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Restart a failed execution
    """
    try:
        execution = await kestra_service.restart_execution(execution_id)
        return execution
    except Exception as e:
        logger.error(f"Error restarting execution {execution_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error restarting execution: {str(e)}")


@router.post("/executions/{execution_id}/stop")
async def stop_execution(
    execution_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Stop a running execution
    """
    try:
        execution = await kestra_service.stop_execution(execution_id)
        return execution
    except Exception as e:
        logger.error(f"Error stopping execution {execution_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error stopping execution: {str(e)}")


@router.get("/logs/{execution_id}")
async def get_logs(
    execution_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get logs for an execution
    """
    try:
        logs = await kestra_service.get_logs(execution_id)
        return logs
    except Exception as e:
        logger.error(f"Error getting logs for execution {execution_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting logs: {str(e)}")


@router.post("/webhooks")
async def create_webhook(
    namespace: str = Body(...),
    flow_id: str = Body(...),
    key: Optional[str] = Body(None),
    current_user: Dict = Depends(get_current_user)
):
    """
    Create a webhook trigger for a workflow
    """
    try:
        webhook = await kestra_service.create_webhook_trigger(namespace, flow_id, key)
        return webhook
    except Exception as e:
        logger.error(f"Error creating webhook for {namespace}/{flow_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating webhook: {str(e)}")


@router.delete("/webhooks/{webhook_id}")
async def delete_webhook(
    webhook_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Delete a webhook trigger
    """
    try:
        success = await kestra_service.delete_webhook_trigger(webhook_id)
        return {"success": success}
    except Exception as e:
        logger.error(f"Error deleting webhook {webhook_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting webhook: {str(e)}")


@router.post("/sync/workflows")
async def sync_workflows(
    background_tasks: BackgroundTasks,
    namespace: Optional[str] = Body(None),
    current_user: Dict = Depends(get_current_user)
):
    """
    Sync workflows from Kestra to PocketBase
    """
    try:
        # Authenticate with PocketBase
        pb_client.auth_with_token(current_user.get("token"))
        
        # Get workflows from Kestra
        workflows = await kestra_service.get_workflows(namespace)
        
        # Sync workflows to PocketBase in the background
        background_tasks.add_task(sync_workflows_to_pocketbase, workflows, current_user.get("id"))
        
        return {
            "message": f"Syncing {len(workflows)} workflows in the background",
            "workflow_count": len(workflows)
        }
    except Exception as e:
        logger.error(f"Error syncing workflows: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error syncing workflows: {str(e)}")


@router.post("/sync/executions")
async def sync_executions(
    background_tasks: BackgroundTasks,
    namespace: Optional[str] = Body(None),
    flow_id: Optional[str] = Body(None),
    limit: int = Body(100),
    current_user: Dict = Depends(get_current_user)
):
    """
    Sync executions from Kestra to PocketBase
    """
    try:
        # Authenticate with PocketBase
        pb_client.auth_with_token(current_user.get("token"))
        
        # Get executions from Kestra
        executions = await kestra_service.get_executions(namespace, flow_id, None, limit)
        
        # Sync executions to PocketBase in the background
        background_tasks.add_task(sync_executions_to_pocketbase, executions)
        
        return {
            "message": f"Syncing {len(executions)} executions in the background",
            "execution_count": len(executions)
        }
    except Exception as e:
        logger.error(f"Error syncing executions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error syncing executions: {str(e)}")


@router.post("/triggers")
async def create_pocketbase_trigger(
    name: str = Body(...),
    workflow_id: str = Body(...),
    collection: str = Body(...),
    event_type: str = Body(...),
    filter: Optional[str] = Body(None),
    inputs: Optional[Dict[str, Any]] = Body(None),
    current_user: Dict = Depends(get_current_user)
):
    """
    Create a PocketBase event trigger for a Kestra workflow
    """
    try:
        # Authenticate with PocketBase
        pb_client.auth_with_token(current_user.get("token"))
        
        # Get the workflow from PocketBase
        workflow = await pb_client.collection('kestra_workflows').get_one(workflow_id)
        
        # Create the trigger
        trigger_data = {
            'name': name,
            'workflow': workflow_id,
            'trigger_type': 'pocketbase_event',
            'collection': collection,
            'event_type': event_type,
            'filter': filter,
            'inputs': json.dumps(inputs or {}),
            'enabled': True,
            'owner': current_user.get("id")
        }
        
        trigger = await pb_client.collection('kestra_triggers').create(trigger_data)
        
        return trigger
    except ClientResponseError as e:
        logger.error(f"PocketBase error creating trigger: {str(e)}")
        raise HTTPException(status_code=e.status, detail=e.data.get('message', str(e)))
    except Exception as e:
        logger.error(f"Error creating PocketBase trigger: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating trigger: {str(e)}")


@router.post("/triggers/database-alert")
async def create_database_alert_trigger(
    name: str = Body(...),
    workflow_id: str = Body(...),
    inputs: Optional[Dict[str, Any]] = Body(None),
    current_user: Dict = Depends(get_current_user)
):
    """
    Create a database alert trigger for a Kestra workflow
    """
    try:
        # Authenticate with PocketBase
        pb_client.auth_with_token(current_user.get("token"))
        
        # Get the workflow from PocketBase
        workflow = await pb_client.collection('kestra_workflows').get_one(workflow_id)
        
        # Create the trigger
        trigger_data = {
            'name': name,
            'workflow': workflow_id,
            'trigger_type': 'database_alert',
            'inputs': json.dumps(inputs or {}),
            'enabled': True,
            'owner': current_user.get("id")
        }
        
        trigger = await pb_client.collection('kestra_triggers').create(trigger_data)
        
        return trigger
    except ClientResponseError as e:
        logger.error(f"PocketBase error creating trigger: {str(e)}")
        raise HTTPException(status_code=e.status, detail=e.data.get('message', str(e)))
    except Exception as e:
        logger.error(f"Error creating database alert trigger: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating trigger: {str(e)}")


# Background task to sync workflows to PocketBase
async def sync_workflows_to_pocketbase(workflows: List[Dict[str, Any]], owner_id: str):
    try:
        for workflow in workflows:
            try:
                await kestra_service.sync_workflow_to_pocketbase(pb_client, workflow, owner_id)
            except Exception as e:
                logger.error(f"Error syncing workflow {workflow.get('namespace')}/{workflow.get('id')}: {str(e)}")
    except Exception as e:
        logger.error(f"Error in sync_workflows_to_pocketbase: {str(e)}")


# Background task to sync executions to PocketBase
async def sync_executions_to_pocketbase(executions: List[Dict[str, Any]]):
    try:
        for execution in executions:
            try:
                await kestra_service.sync_execution_to_pocketbase(pb_client, execution)
            except Exception as e:
                logger.error(f"Error syncing execution {execution.get('id')}: {str(e)}")
    except Exception as e:
        logger.error(f"Error in sync_executions_to_pocketbase: {str(e)}")


# Webhook endpoint for Kestra to call back
@router.post("/webhook/{webhook_id}")
async def webhook_callback(
    webhook_id: str,
    payload: Dict[str, Any] = Body(...)
):
    """
    Webhook callback endpoint for Kestra
    """
    try:
        # Process the webhook payload
        # This could update execution status in PocketBase, trigger other actions, etc.
        logger.info(f"Received webhook callback for {webhook_id}: {json.dumps(payload)}")
        
        # For now, just return the payload
        return payload
    except Exception as e:
        logger.error(f"Error processing webhook callback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {str(e)}")
