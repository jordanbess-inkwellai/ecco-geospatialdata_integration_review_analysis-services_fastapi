from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum

class ExecutionState(str, Enum):
    """Enum for execution states."""
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    RESTARTED = "RESTARTED"
    KILLING = "KILLING"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    FAILED = "FAILED"
    KILLED = "KILLED"

class TaskType(str, Enum):
    """Enum for common task types."""
    PYTHON_SCRIPT = "io.kestra.plugin.scripts.python.Script"
    SHELL_SCRIPT = "io.kestra.plugin.scripts.shell.Script"
    HTTP_REQUEST = "io.kestra.plugin.http.Request"
    FILE_READ = "io.kestra.plugin.fs.http.Read"
    FILE_WRITE = "io.kestra.plugin.fs.http.Write"
    SQL_QUERY = "io.kestra.plugin.jdbc.Query"
    FLOW_TRIGGER = "io.kestra.plugin.core.flow.Trigger"

class TriggerType(str, Enum):
    """Enum for common trigger types."""
    WEBHOOK = "io.kestra.plugin.webhook.Trigger"
    SCHEDULE = "io.kestra.plugin.schedules.Schedule"
    FLOW = "io.kestra.plugin.core.trigger.Flow"

class KestraTask(BaseModel):
    """Schema for a Kestra task."""
    
    id: str = Field(..., description="Task ID")
    type: str = Field(..., description="Task type")
    description: Optional[str] = Field(None, description="Task description")
    
    class Config:
        extra = "allow"  # Allow additional fields

class KestraTrigger(BaseModel):
    """Schema for a Kestra trigger."""
    
    id: str = Field(..., description="Trigger ID")
    type: str = Field(..., description="Trigger type")
    description: Optional[str] = Field(None, description="Trigger description")
    
    class Config:
        extra = "allow"  # Allow additional fields

class KestraInput(BaseModel):
    """Schema for a Kestra flow input."""
    
    name: str = Field(..., description="Input name")
    type: str = Field(..., description="Input type")
    description: Optional[str] = Field(None, description="Input description")
    required: Optional[bool] = Field(None, description="Whether the input is required")
    defaults: Optional[Any] = Field(None, description="Default value")
    
    class Config:
        extra = "allow"  # Allow additional fields

class KestraOutput(BaseModel):
    """Schema for a Kestra flow output."""
    
    name: str = Field(..., description="Output name")
    type: str = Field(..., description="Output type")
    description: Optional[str] = Field(None, description="Output description")
    
    class Config:
        extra = "allow"  # Allow additional fields

class KestraFlow(BaseModel):
    """Schema for a Kestra flow."""
    
    id: str = Field(..., description="Flow ID")
    namespace: str = Field(..., description="Namespace")
    revision: Optional[int] = Field(None, description="Revision number")
    description: Optional[str] = Field(None, description="Flow description")
    tasks: List[Dict[str, Any]] = Field(..., description="Flow tasks")
    triggers: Optional[List[Dict[str, Any]]] = Field(None, description="Flow triggers")
    inputs: Optional[List[Dict[str, Any]]] = Field(None, description="Flow inputs")
    outputs: Optional[List[Dict[str, Any]]] = Field(None, description="Flow outputs")
    
    class Config:
        extra = "allow"  # Allow additional fields

class KestraExecution(BaseModel):
    """Schema for a Kestra execution."""
    
    id: str = Field(..., description="Execution ID")
    namespace: str = Field(..., description="Namespace")
    flowId: str = Field(..., description="Flow ID")
    state: ExecutionState = Field(..., description="Execution state")
    startDate: Optional[datetime] = Field(None, description="Start date")
    endDate: Optional[datetime] = Field(None, description="End date")
    inputs: Optional[Dict[str, Any]] = Field(None, description="Execution inputs")
    
    class Config:
        extra = "allow"  # Allow additional fields

class KestraLogEntry(BaseModel):
    """Schema for a Kestra log entry."""
    
    executionId: str = Field(..., description="Execution ID")
    taskId: Optional[str] = Field(None, description="Task ID")
    level: str = Field(..., description="Log level")
    message: str = Field(..., description="Log message")
    timestamp: datetime = Field(..., description="Log timestamp")
    
    class Config:
        extra = "allow"  # Allow additional fields

class KestraTemplate(BaseModel):
    """Schema for a Kestra template."""
    
    id: str = Field(..., description="Template ID")
    namespace: Optional[str] = Field(None, description="Namespace")
    description: Optional[str] = Field(None, description="Template description")
    tasks: List[Dict[str, Any]] = Field(..., description="Template tasks")
    inputs: Optional[List[Dict[str, Any]]] = Field(None, description="Template inputs")
    
    class Config:
        extra = "allow"  # Allow additional fields

class KestraFlowVisualization(BaseModel):
    """Schema for a Kestra flow visualization."""
    
    nodes: List[Dict[str, Any]] = Field(..., description="Visualization nodes")
    edges: List[Dict[str, Any]] = Field(..., description="Visualization edges")

class CreateFlowFromScriptRequest(BaseModel):
    """Schema for creating a flow from a script."""
    
    script_path: str = Field(..., description="Path to the script file")

class CreateFlowFromDirectoryRequest(BaseModel):
    """Schema for creating flows from a directory."""
    
    directory_path: str = Field(..., description="Path to the directory containing scripts")

class SetupPocketBaseTriggerRequest(BaseModel):
    """Schema for setting up a PocketBase trigger."""
    
    flow_id: str = Field(..., description="Flow ID")
    collection: str = Field(..., description="PocketBase collection name")
    event_type: str = Field("create", description="Event type (create, update, delete)")

class ExecuteFlowRequest(BaseModel):
    """Schema for executing a flow."""
    
    namespace: str = Field(..., description="Namespace")
    flow_id: str = Field(..., description="Flow ID")
    inputs: Optional[Dict[str, Any]] = Field(None, description="Input variables for the flow")
