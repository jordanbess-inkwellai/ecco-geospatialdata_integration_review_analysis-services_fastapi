#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---
name: postgres_to_duckdb
description: Extract data from PostgreSQL and load into DuckDB for analysis
author: Data Engineering Team
version: 1.0.0
date_created: 2023-04-29
date_modified: 2023-04-29
tags:
  - postgres
  - duckdb
  - etl
  - geospatial
inputs:
  - name: postgres_connection
    type: string
    description: PostgreSQL connection string
    required: true
  - name: query
    type: string
    description: SQL query to extract data
    required: true
  - name: duckdb_path
    type: string
    description: Path to DuckDB database file
    default: "data/analytics.duckdb"
  - name: output_table
    type: string
    description: Name of the output table in DuckDB
    required: true
  - name: primary_key
    type: string
    description: Primary key column(s), comma-separated
    required: false
  - name: write_disposition
    type: string
    description: How to write data (append, replace, merge)
    default: "merge"
outputs:
  - name: row_count
    type: integer
    description: Number of rows processed
  - name: output_path
    type: string
    description: Path to the DuckDB database
dependencies:
  - dlt
  - psycopg2-binary
  - duckdb
kestra:
  task_type: io.kestra.plugin.scripts.python.Python
  task_config:
    pythonVersion: "3.10"
---
"""
import os
import argparse
import logging
import dlt
from dlt.common.typing import TDataItem, TDataItems
import json

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function to run the pipeline."""
    parser = argparse.ArgumentParser(description='Extract data from PostgreSQL and load into DuckDB')
    parser.add_argument('--postgres_connection', required=True, help='PostgreSQL connection string')
    parser.add_argument('--query', required=True, help='SQL query to extract data')
    parser.add_argument('--duckdb_path', default='data/analytics.duckdb', help='Path to DuckDB database file')
    parser.add_argument('--output_table', required=True, help='Name of the output table in DuckDB')
    parser.add_argument('--primary_key', help='Primary key column(s), comma-separated')
    parser.add_argument('--write_disposition', default='merge', help='How to write data (append, replace, merge)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Check if running in Kestra
    in_kestra = os.environ.get('KESTRA_EXECUTION_ID') is not None
    
    # If running in Kestra, check for input file
    if in_kestra and os.path.exists('input.json'):
        with open('input.json', 'r') as f:
            kestra_inputs = json.load(f)
            
        # Override arguments with Kestra inputs if provided
        if 'postgres_connection' in kestra_inputs:
            args.postgres_connection = kestra_inputs['postgres_connection']
        if 'query' in kestra_inputs:
            args.query = kestra_inputs['query']
        if 'duckdb_path' in kestra_inputs:
            args.duckdb_path = kestra_inputs['duckdb_path']
        if 'output_table' in kestra_inputs:
            args.output_table = kestra_inputs['output_table']
        if 'primary_key' in kestra_inputs:
            args.primary_key = kestra_inputs['primary_key']
        if 'write_disposition' in kestra_inputs:
            args.write_disposition = kestra_inputs['write_disposition']
    
    logger.info(f"Starting postgres_to_duckdb pipeline")
    logger.info(f"Output table: {args.output_table}")
    logger.info(f"DuckDB path: {args.duckdb_path}")
    
    try:
        # Ensure directory exists for DuckDB file
        os.makedirs(os.path.dirname(os.path.abspath(args.duckdb_path)), exist_ok=True)
        
        # Configure source
        source = dlt.sources.sql(
            connection_string=args.postgres_connection,
            query=args.query
        )
        
        # Configure destination
        destination = {
            "type": "duckdb",
            "database": args.duckdb_path
        }
        
        # Create pipeline
        pipeline = dlt.pipeline(
            pipeline_name=f"postgres_to_duckdb_{args.output_table}",
            destination=destination,
            dataset_name="analytics"
        )
        
        # Parse primary key if provided
        primary_key = None
        if args.primary_key:
            primary_key = [key.strip() for key in args.primary_key.split(',')]
        
        # Run pipeline
        load_info = pipeline.run(
            source,
            table_name=args.output_table,
            write_disposition=args.write_disposition,
            primary_key=primary_key
        )
        
        # Log results
        logger.info(f"Pipeline run completed with load_id: {load_info.load_id}")
        logger.info(f"Loaded to: {load_info.destination_name}.{load_info.dataset_name}.{load_info.table_name}")
        logger.info(f"Inserted rows: {load_info.metrics.inserted_rows}")
        logger.info(f"Updated rows: {load_info.metrics.updated_rows}")
        logger.info(f"Deleted rows: {load_info.metrics.deleted_rows}")
        
        # Write output for Kestra if needed
        if in_kestra:
            with open('output.json', 'w') as f:
                json.dump({
                    'row_count': load_info.metrics.inserted_rows + load_info.metrics.updated_rows,
                    'output_path': args.duckdb_path
                }, f)
        
        return {
            'row_count': load_info.metrics.inserted_rows + load_info.metrics.updated_rows,
            'output_path': args.duckdb_path
        }
    
    except Exception as e:
        logger.error(f"Error in pipeline: {str(e)}")
        if in_kestra:
            with open('error.json', 'w') as f:
                json.dump({
                    'error': str(e)
                }, f)
        raise

if __name__ == '__main__':
    main()
