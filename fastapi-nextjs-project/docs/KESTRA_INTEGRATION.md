# Kestra Workflow Integration

This document provides information about the Kestra workflow orchestration integration in the MCP Server application.

## Overview

The Kestra workflow integration allows users to:

1. Create, edit, and manage data processing workflows visually
2. Convert Python and shell scripts into workflows automatically
3. Execute workflows and monitor their execution
4. Create workflow templates for reuse
5. Set up triggers for workflows (schedule, webhook, etc.)
6. Integrate with PocketBase for real-time triggers

## Setup and Configuration

### Prerequisites

To use the Kestra workflow integration, you need:

1. A running Kestra server
2. (Optional) PocketBase server for real-time triggers

### Configuration

The Kestra integration is configured using environment variables:

```
# Kestra API settings
KESTRA_API_URL=http://localhost:8080
KESTRA_AUTH_ENABLED=false
KESTRA_USERNAME=admin
KESTRA_PASSWORD=password
KESTRA_API_KEY=your_api_key

# Namespace settings
KESTRA_DEFAULT_NAMESPACE=default

# Webhook settings
KESTRA_WEBHOOK_URL=https://your-app-url/api/v1/workflows/webhook
KESTRA_WEBHOOK_SECRET=your_webhook_secret

# PocketBase integration settings
POCKETBASE_URL=http://localhost:8090
POCKETBASE_EMAIL=admin@example.com
POCKETBASE_PASSWORD=password

# Local settings
KESTRA_TEMPLATES_DIR=/path/to/templates
KESTRA_FLOWS_DIR=/path/to/flows
```

## Workflow Builder

The workflow builder is a visual tool for creating and editing workflows. It allows you to:

1. Add tasks and triggers to your workflow
2. Connect tasks to define the workflow execution order
3. Configure task and trigger properties
4. Save and execute workflows

### Task Types

The following task types are supported:

- **Python Script**: Execute Python code
- **Shell Script**: Execute shell commands
- **HTTP Request**: Make HTTP requests
- **File Read/Write**: Read and write files
- **SQL Query**: Execute SQL queries
- **Flow Trigger**: Trigger another workflow

### Trigger Types

The following trigger types are supported:

- **Webhook**: Trigger a workflow via HTTP webhook
- **Schedule**: Trigger a workflow on a schedule
- **Flow**: Trigger a workflow when another workflow completes

## Script to Workflow Conversion

The script to workflow conversion feature allows you to convert existing Python and shell scripts into Kestra workflows. It supports:

1. Uploading scripts directly through the UI
2. Converting scripts from a directory on the server
3. Extracting input parameters from script comments
4. Automatically generating workflow configurations

### Script Format

To get the best results from the script conversion, add special comments to your scripts:

```python
# Flow ID: my_workflow
# Flow Name: My Workflow
# Flow Description: This workflow does something awesome
# Input: input_file (STRING) - Path to the input file
# Input: output_dir (STRING) - Path to the output directory

import os
import sys

input_file = sys.argv[1]
output_dir = sys.argv[2]

# Your script code here
```

## Workflow Execution

The workflow execution feature allows you to:

1. Execute workflows manually
2. Monitor workflow execution status
3. View execution logs
4. View execution inputs and outputs

## API Endpoints

The following API endpoints are available for the Kestra workflow integration:

### Status and Information

- `GET /api/v1/workflows/status` - Get the status of the Kestra integration
- `GET /api/v1/workflows/namespaces` - Get a list of available namespaces

### Workflow Management

- `GET /api/v1/workflows/flows` - Get a list of flows
- `GET /api/v1/workflows/flows/{namespace}/{flow_id}` - Get a flow by ID
- `POST /api/v1/workflows/flows` - Create a new flow
- `PUT /api/v1/workflows/flows/{namespace}/{flow_id}` - Update an existing flow
- `DELETE /api/v1/workflows/flows/{namespace}/{flow_id}` - Delete a flow

### Workflow Execution

- `POST /api/v1/workflows/flows/execute` - Execute a flow
- `GET /api/v1/workflows/executions/{execution_id}` - Get execution details
- `GET /api/v1/workflows/executions` - Get a list of executions
- `GET /api/v1/workflows/logs/{execution_id}` - Get logs for an execution

### Templates

- `GET /api/v1/workflows/templates` - Get a list of flow templates
- `POST /api/v1/workflows/templates` - Create a new template
- `DELETE /api/v1/workflows/templates/{template_id}` - Delete a template
- `POST /api/v1/workflows/flows/from-template` - Create a flow from a template

### Script Conversion

- `POST /api/v1/workflows/flows/from-script` - Create a flow from a script file
- `POST /api/v1/workflows/flows/from-directory` - Create flows from all scripts in a directory
- `POST /api/v1/workflows/flows/upload-script` - Upload a script file and create a flow from it

### PocketBase Integration

- `POST /api/v1/workflows/pocketbase/trigger` - Set up a PocketBase trigger for a flow

### Visualization

- `POST /api/v1/workflows/flows/visualize` - Generate a visualization of a flow
- `GET /api/v1/workflows/flows/{namespace}/{flow_id}/visualize` - Generate a visualization of an existing flow

## Frontend Components

The frontend includes the following components for Kestra workflow integration:

- `WorkflowBuilder` - A component for building and editing workflows
- `WorkflowList` - A component for listing and managing workflows
- `WorkflowExecutions` - A component for viewing workflow executions
- `ScriptToWorkflow` - A component for converting scripts to workflows

## Usage

### Creating a Workflow

1. Navigate to the Workflows page
2. Click the "Create Workflow" button
3. Use the visual builder to create your workflow:
   - Add tasks and triggers
   - Connect tasks to define the execution order
   - Configure task and trigger properties
4. Click "Save" to save your workflow

### Converting Scripts to Workflows

1. Navigate to the Workflows page
2. Click the "Create Workflow" button
3. Select the "From Scripts" tab
4. Upload your scripts or enter a directory path
5. Click "Convert to Workflows"

### Executing a Workflow

1. Navigate to the Workflows page
2. Find the workflow you want to execute
3. Click the "Execute" button in the actions menu
4. View the execution status and logs in the Executions tab

### Setting Up a PocketBase Trigger

1. Create a workflow that you want to trigger from PocketBase
2. Use the API to set up a PocketBase trigger:
   ```
   POST /api/v1/workflows/pocketbase/trigger
   {
     "flow_id": "your_workflow_id",
     "collection": "your_collection",
     "event_type": "create"
   }
   ```
3. The workflow will be triggered when a new record is created in the specified collection

## Troubleshooting

### Connection Issues

If you're having trouble connecting to the Kestra server:

1. Check that the Kestra server is running
2. Verify the `KESTRA_API_URL` environment variable
3. Check the authentication settings if authentication is enabled

### Workflow Execution Issues

If a workflow fails to execute:

1. Check the execution logs for error messages
2. Verify that all task dependencies are correctly configured
3. Check that all required inputs are provided

### Script Conversion Issues

If script conversion fails:

1. Check that the script is in a supported format (Python, shell)
2. Verify that the script has the correct permissions
3. Add special comments to the script to provide more information

## Limitations

The current implementation has the following limitations:

1. Limited support for complex workflow patterns
2. No support for distributed workflows
3. Limited error handling and recovery options
4. No support for workflow versioning
