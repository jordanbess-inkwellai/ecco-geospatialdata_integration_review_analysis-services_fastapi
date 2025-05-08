from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, Path, Body, File, UploadFile, Form
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import os
import json
import yaml
from datetime import datetime

from app.core.database import get_db
from app.core.kestra_config import kestra_config
from app.services.kestra_service import kestra_service
from app.schemas.kestra_schemas import (
    KestraFlow,
    KestraExecution,
    KestraLogEntry,
    KestraTemplate,
    KestraFlowVisualization,
    CreateFlowFromScriptRequest,
    CreateFlowFromDirectoryRequest,
    SetupPocketBaseTriggerRequest,
    ExecuteFlowRequest
)

router = APIRouter()

@router.get("/status", response_model=Dict[str, Any])
async def get_kestra_status():
    """
    Get the status of the Kestra integration.
    
    Returns:
        Status information
    """
    return {
        "configured": kestra_config.is_configured,
        "auth_configured": kestra_config.is_auth_configured,
        "pocketbase_configured": kestra_config.is_pocketbase_configured,
        "api_url": kestra_config.api_url,
        "default_namespace": kestra_config.default_namespace
    }

@router.get("/namespaces", response_model=List[str])
async def get_namespaces():
    """
    Get a list of available namespaces.
    
    Returns:
        List of namespace IDs
    """
    if not kestra_config.is_configured:
        raise HTTPException(status_code=400, detail="Kestra is not configured")
    
    try:
        namespaces = await kestra_service.get_namespaces()
        return namespaces
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting namespaces: {str(e)}")

@router.get("/flows", response_model=List[Dict[str, Any]])
async def get_flows(namespace: Optional[str] = Query(None)):
    """
    Get a list of flows in a namespace.
    
    Args:
        namespace: Namespace ID (default: default namespace)
        
    Returns:
        List of flows
    """
    if not kestra_config.is_configured:
        raise HTTPException(status_code=400, detail="Kestra is not configured")
    
    try:
        flows = await kestra_service.get_flows(namespace)
        return flows
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting flows: {str(e)}")

@router.get("/flows/{namespace}/{flow_id}", response_model=Dict[str, Any])
async def get_flow(namespace: str, flow_id: str):
    """
    Get a flow by ID.
    
    Args:
        namespace: Namespace ID
        flow_id: Flow ID
        
    Returns:
        Flow data
    """
    if not kestra_config.is_configured:
        raise HTTPException(status_code=400, detail="Kestra is not configured")
    
    try:
        flow = await kestra_service.get_flow(namespace, flow_id)
        if not flow:
            raise HTTPException(status_code=404, detail=f"Flow {flow_id} not found")
        return flow
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting flow: {str(e)}")

@router.post("/flows", response_model=Dict[str, Any])
async def create_flow(flow_data: Dict[str, Any] = Body(...)):
    """
    Create a new flow.
    
    Args:
        flow_data: Flow data in YAML or JSON format
        
    Returns:
        Created flow data
    """
    if not kestra_config.is_configured:
        raise HTTPException(status_code=400, detail="Kestra is not configured")
    
    try:
        flow = await kestra_service.create_flow(flow_data)
        if not flow:
            raise HTTPException(status_code=500, detail="Failed to create flow")
        return flow
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating flow: {str(e)}")

@router.put("/flows/{namespace}/{flow_id}", response_model=Dict[str, Any])
async def update_flow(namespace: str, flow_id: str, flow_data: Dict[str, Any] = Body(...)):
    """
    Update an existing flow.
    
    Args:
        namespace: Namespace ID
        flow_id: Flow ID
        flow_data: Flow data in YAML or JSON format
        
    Returns:
        Updated flow data
    """
    if not kestra_config.is_configured:
        raise HTTPException(status_code=400, detail="Kestra is not configured")
    
    try:
        flow = await kestra_service.update_flow(namespace, flow_id, flow_data)
        if not flow:
            raise HTTPException(status_code=500, detail=f"Failed to update flow {flow_id}")
        return flow
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating flow: {str(e)}")

@router.delete("/flows/{namespace}/{flow_id}", response_model=Dict[str, str])
async def delete_flow(namespace: str, flow_id: str):
    """
    Delete a flow.
    
    Args:
        namespace: Namespace ID
        flow_id: Flow ID
        
    Returns:
        Success message
    """
    if not kestra_config.is_configured:
        raise HTTPException(status_code=400, detail="Kestra is not configured")
    
    try:
        success = await kestra_service.delete_flow(namespace, flow_id)
        if not success:
            raise HTTPException(status_code=500, detail=f"Failed to delete flow {flow_id}")
        return {"message": f"Flow {flow_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting flow: {str(e)}")

@router.post("/flows/execute", response_model=Dict[str, Any])
async def execute_flow(request: ExecuteFlowRequest):
    """
    Execute a flow.
    
    Args:
        request: Execution request
        
    Returns:
        Execution data
    """
    if not kestra_config.is_configured:
        raise HTTPException(status_code=400, detail="Kestra is not configured")
    
    try:
        execution = await kestra_service.execute_flow(
            request.namespace, 
            request.flow_id, 
            request.inputs
        )
        if not execution:
            raise HTTPException(status_code=500, detail=f"Failed to execute flow {request.flow_id}")
        return execution
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing flow: {str(e)}")

@router.get("/executions/{execution_id}", response_model=Dict[str, Any])
async def get_execution(execution_id: str):
    """
    Get execution details.
    
    Args:
        execution_id: Execution ID
        
    Returns:
        Execution data
    """
    if not kestra_config.is_configured:
        raise HTTPException(status_code=400, detail="Kestra is not configured")
    
    try:
        execution = await kestra_service.get_execution(execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail=f"Execution {execution_id} not found")
        return execution
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting execution: {str(e)}")

@router.get("/executions", response_model=List[Dict[str, Any]])
async def get_executions(
    namespace: Optional[str] = Query(None),
    flow_id: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    limit: int = Query(10)
):
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
    if not kestra_config.is_configured:
        raise HTTPException(status_code=400, detail="Kestra is not configured")
    
    try:
        executions = await kestra_service.get_executions(namespace, flow_id, state, limit)
        return executions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting executions: {str(e)}")

@router.get("/logs/{execution_id}", response_model=List[Dict[str, Any]])
async def get_logs(execution_id: str):
    """
    Get logs for an execution.
    
    Args:
        execution_id: Execution ID
        
    Returns:
        List of log entries
    """
    if not kestra_config.is_configured:
        raise HTTPException(status_code=400, detail="Kestra is not configured")
    
    try:
        logs = await kestra_service.get_logs(execution_id)
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting logs: {str(e)}")

@router.get("/templates", response_model=List[Dict[str, Any]])
async def get_templates():
    """
    Get a list of flow templates.
    
    Returns:
        List of templates
    """
    if not kestra_config.is_configured:
        raise HTTPException(status_code=400, detail="Kestra is not configured")
    
    try:
        templates = await kestra_service.get_templates()
        return templates
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting templates: {str(e)}")

@router.post("/templates", response_model=Dict[str, Any])
async def create_template(template_data: Dict[str, Any] = Body(...)):
    """
    Create a new template.
    
    Args:
        template_data: Template data in YAML or JSON format
        
    Returns:
        Created template data
    """
    if not kestra_config.is_configured:
        raise HTTPException(status_code=400, detail="Kestra is not configured")
    
    try:
        template = await kestra_service.create_template(template_data)
        if not template:
            raise HTTPException(status_code=500, detail="Failed to create template")
        return template
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating template: {str(e)}")

@router.delete("/templates/{template_id}", response_model=Dict[str, str])
async def delete_template(template_id: str):
    """
    Delete a template.
    
    Args:
        template_id: Template ID
        
    Returns:
        Success message
    """
    if not kestra_config.is_configured:
        raise HTTPException(status_code=400, detail="Kestra is not configured")
    
    try:
        success = await kestra_service.delete_template(template_id)
        if not success:
            raise HTTPException(status_code=500, detail=f"Failed to delete template {template_id}")
        return {"message": f"Template {template_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting template: {str(e)}")

@router.post("/flows/from-template", response_model=Dict[str, Any])
async def create_flow_from_template(
    template_id: str = Form(...),
    variables: str = Form("{}")
):
    """
    Create a flow from a template.
    
    Args:
        template_id: Template ID
        variables: Variables to substitute in the template (JSON string)
        
    Returns:
        Created flow data
    """
    if not kestra_config.is_configured:
        raise HTTPException(status_code=400, detail="Kestra is not configured")
    
    try:
        # Parse variables
        variables_dict = json.loads(variables)
        
        flow = await kestra_service.create_flow_from_template(template_id, variables_dict)
        if not flow:
            raise HTTPException(status_code=500, detail=f"Failed to create flow from template {template_id}")
        return flow
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in variables")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating flow from template: {str(e)}")

@router.post("/flows/from-script", response_model=Dict[str, Any])
async def create_flow_from_script(request: CreateFlowFromScriptRequest):
    """
    Create a flow from a script file.
    
    Args:
        request: Script path
        
    Returns:
        Created flow data
    """
    if not kestra_config.is_configured:
        raise HTTPException(status_code=400, detail="Kestra is not configured")
    
    try:
        # Check if the script file exists
        if not os.path.exists(request.script_path):
            raise HTTPException(status_code=404, detail=f"Script file {request.script_path} not found")
        
        flow = await kestra_service.create_flow_from_script(request.script_path)
        if not flow:
            raise HTTPException(status_code=500, detail=f"Failed to create flow from script {request.script_path}")
        return flow
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating flow from script: {str(e)}")

@router.post("/flows/from-directory", response_model=List[Dict[str, Any]])
async def create_flows_from_directory(request: CreateFlowFromDirectoryRequest):
    """
    Create flows from all scripts in a directory.
    
    Args:
        request: Directory path
        
    Returns:
        List of created flows
    """
    if not kestra_config.is_configured:
        raise HTTPException(status_code=400, detail="Kestra is not configured")
    
    try:
        # Check if the directory exists
        if not os.path.exists(request.directory_path) or not os.path.isdir(request.directory_path):
            raise HTTPException(status_code=404, detail=f"Directory {request.directory_path} not found")
        
        flows = await kestra_service.create_flow_from_directory(request.directory_path)
        return flows
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating flows from directory: {str(e)}")

@router.post("/flows/upload-script", response_model=Dict[str, Any])
async def upload_script_and_create_flow(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Upload a script file and create a flow from it.
    
    Args:
        file: Script file
        
    Returns:
        Created flow data
    """
    if not kestra_config.is_configured:
        raise HTTPException(status_code=400, detail="Kestra is not configured")
    
    try:
        # Save the uploaded file
        file_path = os.path.join(kestra_config.flows_dir, file.filename)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Create a flow from the script
        flow = await kestra_service.create_flow_from_script(file_path)
        if not flow:
            raise HTTPException(status_code=500, detail=f"Failed to create flow from script {file.filename}")
        
        return flow
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading script and creating flow: {str(e)}")

@router.post("/pocketbase/trigger", response_model=Dict[str, str])
async def setup_pocketbase_trigger(request: SetupPocketBaseTriggerRequest):
    """
    Set up a PocketBase trigger for a flow.
    
    Args:
        request: Trigger configuration
        
    Returns:
        Success message
    """
    if not kestra_config.is_configured:
        raise HTTPException(status_code=400, detail="Kestra is not configured")
    
    if not kestra_config.is_pocketbase_configured:
        raise HTTPException(status_code=400, detail="PocketBase integration is not configured")
    
    try:
        success = await kestra_service.setup_pocketbase_trigger(
            request.flow_id,
            request.collection,
            request.event_type
        )
        
        if not success:
            raise HTTPException(status_code=500, detail=f"Failed to set up PocketBase trigger for flow {request.flow_id}")
        
        return {"message": f"PocketBase trigger set up successfully for flow {request.flow_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting up PocketBase trigger: {str(e)}")

@router.post("/flows/visualize", response_model=Dict[str, Any])
async def visualize_flow(flow_data: Dict[str, Any] = Body(...)):
    """
    Generate a visualization of a flow.
    
    Args:
        flow_data: Flow data
        
    Returns:
        Visualization data
    """
    if not kestra_config.is_configured:
        raise HTTPException(status_code=400, detail="Kestra is not configured")
    
    try:
        visualization = await kestra_service.generate_flow_visualization(flow_data)
        return visualization
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating flow visualization: {str(e)}")

@router.get("/flows/{namespace}/{flow_id}/visualize", response_model=Dict[str, Any])
async def visualize_existing_flow(namespace: str, flow_id: str):
    """
    Generate a visualization of an existing flow.
    
    Args:
        namespace: Namespace ID
        flow_id: Flow ID
        
    Returns:
        Visualization data
    """
    if not kestra_config.is_configured:
        raise HTTPException(status_code=400, detail="Kestra is not configured")
    
    try:
        # Get the flow
        flow = await kestra_service.get_flow(namespace, flow_id)
        if not flow:
            raise HTTPException(status_code=404, detail=f"Flow {flow_id} not found")
        
        # Generate the visualization
        visualization = await kestra_service.generate_flow_visualization(flow)
        return visualization
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error visualizing flow: {str(e)}")
