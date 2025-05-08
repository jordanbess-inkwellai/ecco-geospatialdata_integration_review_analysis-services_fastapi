#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---
name: generate_kestra_workflow
description: Generate Kestra workflow YAML from Python script metadata
author: Data Engineering Team
version: 1.0.0
date_created: 2023-04-29
tags:
  - kestra
  - workflow
  - automation
inputs:
  - name: script_path
    type: string
    description: Path to the Python script
    required: true
  - name: output_path
    type: string
    description: Path to save the generated workflow YAML
    required: true
  - name: template_path
    type: string
    description: Path to the template YAML (optional)
    required: false
outputs:
  - name: workflow_path
    type: string
    description: Path to the generated workflow YAML
dependencies:
  - pyyaml
  - jinja2
---
"""
import os
import sys
import re
import argparse
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_metadata(script_path: str) -> Dict[str, Any]:
    """
    Extract YAML metadata from a Python script.
    
    Args:
        script_path: Path to the Python script
        
    Returns:
        Dictionary containing the metadata
    """
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for metadata between triple quotes and --- markers
    metadata_pattern = r'"""[\s\n]*---\n(.*?)\n---[\s\n]*"""'
    match = re.search(metadata_pattern, content, re.DOTALL)
    
    if not match:
        raise ValueError(f"No metadata found in {script_path}")
    
    metadata_yaml = match.group(1)
    metadata = yaml.safe_load(metadata_yaml)
    
    return metadata

def generate_workflow(
    metadata: Dict[str, Any],
    script_path: str,
    template_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a Kestra workflow from script metadata.
    
    Args:
        metadata: Script metadata
        script_path: Path to the script
        template_path: Path to a template YAML file (optional)
        
    Returns:
        Dictionary containing the workflow definition
    """
    # Start with template if provided
    workflow = {}
    if template_path and os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            workflow = yaml.safe_load(f)
    
    # Set basic workflow properties
    workflow['id'] = metadata.get('name', os.path.basename(script_path).replace('.py', '')).replace('_', '-')
    workflow['namespace'] = metadata.get('namespace', 'default')
    workflow['description'] = metadata.get('description', '')
    
    # Add tags if present
    if 'tags' in metadata:
        workflow['tags'] = metadata['tags']
    
    # Add inputs based on metadata
    if 'inputs' in metadata:
        workflow['inputs'] = []
        for input_def in metadata['inputs']:
            kestra_input = {
                'name': input_def['name'],
                'type': input_def['type'].upper(),
                'description': input_def.get('description', '')
            }
            
            if 'required' in input_def:
                kestra_input['required'] = input_def['required']
            
            if 'default' in input_def:
                kestra_input['defaults'] = input_def['default']
            
            workflow['inputs'].append(kestra_input)
    
    # Add tasks if not already defined
    if 'tasks' not in workflow:
        workflow['tasks'] = []
    
    # Add main task to run the script if not already defined
    if not any(task.get('id') == 'run_script' for task in workflow['tasks']):
        # Get task configuration from metadata if available
        task_config = {}
        if 'kestra' in metadata:
            task_type = metadata['kestra'].get('task_type', 'io.kestra.plugin.scripts.python.Python')
            task_config = metadata['kestra'].get('task_config', {})
        else:
            task_type = 'io.kestra.plugin.scripts.python.Python'
        
        # Create input mapping for the task
        input_mapping = {}
        if 'inputs' in metadata:
            for input_def in metadata['inputs']:
                input_name = input_def['name']
                input_mapping[input_name] = f"{{{{ inputs.{input_name} }}}}"
        
        # Create the task
        task = {
            'id': 'run_script',
            'type': task_type,
            **task_config
        }
        
        # Add Python version if not specified
        if 'pythonVersion' not in task and task_type == 'io.kestra.plugin.scripts.python.Python':
            task['pythonVersion'] = '3.10'
        
        # Add input files if there are inputs
        if input_mapping:
            task['inputFiles'] = {
                'input.json': json.dumps(input_mapping, indent=2)
            }
        
        # Add the script content or path
        rel_script_path = os.path.relpath(script_path)
        task['script'] = f"""
import sys
import os
import json
import subprocess

# Path to the script
script_path = "{rel_script_path}"

# Check if input.json exists and load it
inputs = {{}}
if os.path.exists('input.json'):
    with open('input.json', 'r') as f:
        inputs = json.load(f)

# Build command
cmd = [sys.executable, script_path]
for key, value in inputs.items():
    cmd.append(f"--{{key}}")
    cmd.append(str(value))

# Run the script
result = subprocess.run(cmd, capture_output=True, text=True)

# Print output
print(result.stdout)

# Check for errors
if result.returncode != 0:
    print(f"Error: {{result.stderr}}")
    sys.exit(result.returncode)

# Check if output.json exists and load it
outputs = {{}}
if os.path.exists('output.json'):
    with open('output.json', 'r') as f:
        outputs = json.load(f)
    
    # Write outputs to file for Kestra
    with open('outputs.json', 'w') as out_file:
        json.dump(outputs, out_file)
"""
        
        # Add output files if there are outputs
        if 'outputs' in metadata:
            task['outputFiles'] = ['outputs.json']
        
        workflow['tasks'].append(task)
    
    # Add notification tasks if not already defined
    if not any(task.get('id') == 'notify_success' for task in workflow['tasks']):
        workflow['tasks'].append({
            'id': 'notify_success',
            'type': 'io.kestra.plugin.notifications.slack.SlackMessage',
            'url': '{{ inputs.slack_webhook }}',
            'message': f"""
:white_check_mark: {metadata.get('name', 'Script')} completed successfully

*Execution ID*: {{{{ execution.id }}}}
*Started*: {{{{ execution.startDate }}}}
*Duration*: {{{{ duration(execution.startDate, execution.endDate) }}}}

[View in Kestra]({{{{ kestra.url }}}}/executions/{{{{ execution.id }}}})
""",
            'dependsOn': ['run_script'],
            'when': {
                'condition': '{{ inputs.slack_webhook != null }}'
            }
        })
    
    # Add error handler if not already defined
    if 'errors' not in workflow:
        workflow['errors'] = [{
            'id': 'notify_failure',
            'type': 'io.kestra.plugin.notifications.slack.SlackMessage',
            'url': '{{ inputs.slack_webhook }}',
            'message': f"""
:x: {metadata.get('name', 'Script')} failed

*Execution ID*: {{{{ execution.id }}}}
*Started*: {{{{ execution.startDate }}}}
*Error*: {{{{ execution.state.exception.message }}}}

[View in Kestra]({{{{ kestra.url }}}}/executions/{{{{ execution.id }}}})
""",
            'when': {
                'condition': '{{ inputs.slack_webhook != null }}'
            }
        }]
    
    # Add slack_webhook input if not already defined
    if 'inputs' in workflow and not any(input_def.get('name') == 'slack_webhook' for input_def in workflow['inputs']):
        workflow['inputs'].append({
            'name': 'slack_webhook',
            'type': 'STRING',
            'description': 'Slack webhook URL for notifications',
            'required': False
        })
    
    return workflow

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Generate Kestra workflow YAML from Python script metadata')
    parser.add_argument('--script', required=True, help='Path to the Python script')
    parser.add_argument('--output', required=True, help='Path to save the generated workflow YAML')
    parser.add_argument('--template', help='Path to the template YAML (optional)')
    
    args = parser.parse_args()
    
    try:
        # Extract metadata from script
        logger.info(f"Extracting metadata from {args.script}")
        metadata = extract_metadata(args.script)
        
        # Generate workflow
        logger.info(f"Generating workflow")
        workflow = generate_workflow(metadata, args.script, args.template)
        
        # Save workflow
        logger.info(f"Saving workflow to {args.output}")
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            yaml.dump(workflow, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Workflow generated successfully: {args.output}")
        
        return {
            'workflow_path': args.output
        }
    
    except Exception as e:
        logger.error(f"Error generating workflow: {str(e)}")
        raise

if __name__ == '__main__':
    main()
