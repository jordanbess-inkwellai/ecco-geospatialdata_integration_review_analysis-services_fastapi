from sqlalchemy import Column, String, Integer, Boolean, JSON, Text, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel, Base
from datetime import datetime


class WorkflowType(str, enum.Enum):
    """Enum for workflow types"""
    DATA_IMPORT = "data_import"
    DATA_EXPORT = "data_export"
    DATA_TRANSFORMATION = "data_transformation"
    NOTEBOOK_EXECUTION = "notebook_execution"
    MARIMO_EXECUTION = "marimo_execution"
    CUSTOM = "custom"


class WorkflowStatus(str, enum.Enum):
    """Enum for workflow status"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OrchestratorType(str, enum.Enum):
    """Enum for orchestrator types"""
    KESTRA = "kestra"
    AIRFLOW = "airflow"
    PREFECT = "prefect"
    DAGSTER = "dagster"
    INTERNAL = "internal"  # Our own simple scheduler
    CUSTOM = "custom"


class Workflow(Base, BaseModel):
    """Model for workflows that can be orchestrated"""
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Workflow details
    workflow_type = Column(String(50), nullable=False)
    orchestrator_type = Column(String(50), default=OrchestratorType.INTERNAL, nullable=False)
    
    # For external orchestrators
    external_id = Column(String(255), nullable=True)  # ID in the external system
    external_url = Column(String(1024), nullable=True)  # URL to the workflow in the external system
    
    # Configuration
    config = Column(JSON, nullable=True)  # Configuration for the workflow
    
    # Schedule
    is_scheduled = Column(Boolean, default=False, nullable=False)
    schedule = Column(String(255), nullable=True)  # Cron expression
    
    # Status
    status = Column(String(50), default=WorkflowStatus.DRAFT, nullable=False)
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    
    # Webhook
    webhook_enabled = Column(Boolean, default=False, nullable=False)
    webhook_url = Column(String(1024), nullable=True)
    webhook_secret = Column(String(255), nullable=True)
    
    # Relationships
    executions = relationship("WorkflowExecution", back_populates="workflow", cascade="all, delete-orphan")
    tasks = relationship("WorkflowTask", back_populates="workflow", cascade="all, delete-orphan")


class WorkflowTask(Base, BaseModel):
    """Model for tasks within a workflow"""
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Task details
    task_type = Column(String(50), nullable=False)
    config = Column(JSON, nullable=True)  # Configuration for the task
    
    # Execution order
    order = Column(Integer, default=0, nullable=False)
    depends_on = Column(JSON, nullable=True)  # List of task IDs this task depends on
    
    # Retry configuration
    max_retries = Column(Integer, default=0, nullable=False)
    retry_delay = Column(Integer, default=60, nullable=False)  # in seconds
    
    # Relationships
    workflow_id = Column(Integer, ForeignKey('workflow.id'), nullable=False)
    workflow = relationship("Workflow", back_populates="tasks")


class WorkflowExecution(Base, BaseModel):
    """Model for workflow execution history"""
    
    # Execution details
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(50), nullable=False)
    
    # For external orchestrators
    external_execution_id = Column(String(255), nullable=True)
    external_url = Column(String(1024), nullable=True)
    
    # Results
    result = Column(JSON, nullable=True)
    logs = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Relationships
    workflow_id = Column(Integer, ForeignKey('workflow.id'), nullable=False)
    workflow = relationship("Workflow", back_populates="executions")
    task_executions = relationship("TaskExecution", back_populates="workflow_execution", cascade="all, delete-orphan")


class TaskExecution(Base, BaseModel):
    """Model for task execution history"""
    
    # Task reference
    task_name = Column(String(255), nullable=False)
    task_type = Column(String(50), nullable=False)
    
    # Execution details
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(50), nullable=False)
    
    # Results
    result = Column(JSON, nullable=True)
    logs = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Retry information
    attempt = Column(Integer, default=1, nullable=False)
    
    # Relationships
    workflow_execution_id = Column(Integer, ForeignKey('workflowexecution.id'), nullable=False)
    workflow_execution = relationship("WorkflowExecution", back_populates="task_executions")
    workflow_task_id = Column(Integer, ForeignKey('workflowtask.id'), nullable=True)


class KestrahookConfig(Base, BaseModel):
    """Configuration for Kestra webhooks"""
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Webhook details
    webhook_url = Column(String(1024), nullable=False)
    webhook_method = Column(String(10), default="POST", nullable=False)
    webhook_headers = Column(JSON, nullable=True)
    
    # Authentication
    auth_type = Column(String(50), default="none", nullable=False)  # none, basic, token, oauth2
    auth_config = Column(JSON, nullable=True)
    
    # Payload template
    payload_template = Column(Text, nullable=True)  # Jinja2 template for the payload
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    last_triggered_at = Column(DateTime, nullable=True)
    
    # Associated workflow if any
    workflow_id = Column(Integer, ForeignKey('workflow.id'), nullable=True)
