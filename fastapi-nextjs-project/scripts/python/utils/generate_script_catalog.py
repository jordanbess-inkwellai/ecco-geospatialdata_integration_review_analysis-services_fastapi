#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---
name: generate_script_catalog
description: Generate a catalog of all scripts in the repository
author: Data Engineering Team
version: 1.0.0
date_created: 2023-04-29
tags:
  - catalog
  - documentation
inputs:
  - name: scripts_dir
    type: string
    description: Path to the scripts directory
    default: "scripts"
  - name: output_path
    type: string
    description: Path to save the catalog JSON
    default: "frontend/public/data/script_catalog.json"
outputs:
  - name: catalog_path
    type: string
    description: Path to the generated catalog JSON
dependencies:
  - pyyaml
---
"""
import os
import sys
import re
import argparse
import yaml
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_metadata(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Extract YAML metadata from a script file.
    
    Args:
        file_path: Path to the script file
        
    Returns:
        Dictionary containing the metadata or None if no metadata found
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # For Python files
        if file_path.endswith('.py'):
            metadata_pattern = r'"""[\s\n]*---\n(.*?)\n---[\s\n]*"""'
            match = re.search(metadata_pattern, content, re.DOTALL)
            
            if match:
                metadata_yaml = match.group(1)
                metadata = yaml.safe_load(metadata_yaml)
                return metadata
        
        # For SQL files
        elif file_path.endswith('.sql'):
            metadata_pattern = r'--\s*---\n(.*?)\n--\s*---'
            match = re.search(metadata_pattern, content, re.DOTALL)
            
            if match:
                metadata_yaml = match.group(1)
                metadata = yaml.safe_load(metadata_yaml)
                return metadata
        
        # For Bash files
        elif file_path.endswith('.sh'):
            metadata_pattern = r'#\s*---\n(.*?)\n#\s*---'
            match = re.search(metadata_pattern, content, re.DOTALL)
            
            if match:
                metadata_yaml = match.group(1)
                metadata = yaml.safe_load(metadata_yaml)
                return metadata
        
        # For YAML files (Kestra workflows)
        elif file_path.endswith('.yaml') or file_path.endswith('.yml'):
            try:
                metadata = yaml.safe_load(content)
                # Extract basic workflow metadata
                if 'id' in metadata and 'tasks' in metadata:
                    return {
                        'name': metadata.get('id'),
                        'description': metadata.get('description', ''),
                        'namespace': metadata.get('namespace', 'default'),
                        'tags': metadata.get('tags', []),
                        'inputs': metadata.get('inputs', []),
                        'outputs': [],  # Kestra doesn't have explicit outputs
                        'type': 'kestra_workflow'
                    }
            except Exception as e:
                logger.warning(f"Error parsing YAML file {file_path}: {str(e)}")
        
        return None
    
    except Exception as e:
        logger.warning(f"Error extracting metadata from {file_path}: {str(e)}")
        return None

def scan_scripts_directory(scripts_dir: str) -> List[Dict[str, Any]]:
    """
    Scan the scripts directory and extract metadata from all scripts.
    
    Args:
        scripts_dir: Path to the scripts directory
        
    Returns:
        List of dictionaries containing script metadata
    """
    scripts = []
    
    for root, _, files in os.walk(scripts_dir):
        for file in files:
            if file.endswith(('.py', '.sql', '.sh', '.yaml', '.yml')):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, start=os.path.dirname(scripts_dir))
                
                metadata = extract_metadata(file_path)
                if metadata:
                    # Add file information
                    metadata['file_path'] = rel_path
                    metadata['file_type'] = os.path.splitext(file)[1][1:]  # Get extension without dot
                    
                    # Determine script type if not specified
                    if 'type' not in metadata:
                        if file_path.endswith('.py'):
                            if 'dlt' in file_path:
                                metadata['type'] = 'dlt_pipeline'
                            else:
                                metadata['type'] = 'python_script'
                        elif file_path.endswith('.sql'):
                            metadata['type'] = 'sql_script'
                        elif file_path.endswith('.sh'):
                            metadata['type'] = 'bash_script'
                        elif file_path.endswith(('.yaml', '.yml')):
                            if 'kestra' in file_path:
                                metadata['type'] = 'kestra_workflow'
                            else:
                                metadata['type'] = 'yaml_config'
                    
                    # Add category based on directory structure
                    parts = rel_path.split(os.sep)
                    if len(parts) > 1:
                        metadata['category'] = parts[0]
                        if len(parts) > 2:
                            metadata['subcategory'] = parts[1]
                    
                    scripts.append(metadata)
    
    return scripts

def generate_catalog(scripts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate a catalog from script metadata.
    
    Args:
        scripts: List of script metadata
        
    Returns:
        Dictionary containing the catalog
    """
    # Group scripts by type
    script_types = {}
    for script in scripts:
        script_type = script.get('type', 'unknown')
        if script_type not in script_types:
            script_types[script_type] = []
        script_types[script_type].append(script)
    
    # Group scripts by category
    categories = {}
    for script in scripts:
        category = script.get('category', 'other')
        if category not in categories:
            categories[category] = []
        categories[category].append(script)
    
    # Group scripts by tag
    tags = {}
    for script in scripts:
        for tag in script.get('tags', []):
            if tag not in tags:
                tags[tag] = []
            tags[tag].append(script)
    
    return {
        'scripts': scripts,
        'by_type': script_types,
        'by_category': categories,
        'by_tag': tags,
        'count': len(scripts),
        'generated_at': str(datetime.datetime.now())
    }

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Generate a catalog of all scripts in the repository')
    parser.add_argument('--scripts_dir', default='scripts', help='Path to the scripts directory')
    parser.add_argument('--output', default='frontend/public/data/script_catalog.json', help='Path to save the catalog JSON')
    
    args = parser.parse_args()
    
    try:
        # Scan scripts directory
        logger.info(f"Scanning scripts directory: {args.scripts_dir}")
        scripts = scan_scripts_directory(args.scripts_dir)
        
        # Generate catalog
        logger.info(f"Generating catalog with {len(scripts)} scripts")
        catalog = generate_catalog(scripts)
        
        # Save catalog
        logger.info(f"Saving catalog to {args.output}")
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(catalog, f, indent=2)
        
        logger.info(f"Catalog generated successfully: {args.output}")
        
        return {
            'catalog_path': args.output,
            'script_count': len(scripts)
        }
    
    except Exception as e:
        logger.error(f"Error generating catalog: {str(e)}")
        raise

if __name__ == '__main__':
    import datetime
    main()
