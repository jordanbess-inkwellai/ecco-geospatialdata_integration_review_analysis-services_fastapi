# DocETL Integration

This document provides information about the DocETL integration in the MCP Server application.

## Overview

[DocETL](https://github.com/ucbepic/docetl) is a Python package for extracting, transforming, and loading document data. It provides a framework for building document processing pipelines that can extract text and metadata from various document formats, transform the extracted data, and load it into different storage systems.

The MCP Server integrates DocETL to provide a user-friendly interface for creating, managing, and running document processing pipelines.

## Features

- Create and manage document processing pipelines
- Run pipelines with custom parameters
- Monitor pipeline execution and view logs
- Browse available extractors, transformers, and loaders
- Visualize pipeline results

## Setup and Configuration

### Prerequisites

To use the DocETL integration, you need:

1. DocETL server running and accessible
2. Python 3.7 or higher
3. Required document processing libraries (depending on the document formats you want to process)

### Configuration

The DocETL integration is configured using environment variables:

```
# DocETL server settings
DOCETL_API_URL=http://localhost:8001/api

# Frontend settings
NEXT_PUBLIC_DOCETL_ENABLED=true
NEXT_PUBLIC_DOCETL_API_URL=http://localhost:8001/api
```

## Usage

### Creating a Pipeline

1. Navigate to the DocETL page
2. Click the "Create Pipeline" button
3. Define the pipeline configuration in JSON format:

```json
{
  "name": "My Pipeline",
  "description": "Extract text from PDF documents",
  "extractor": {
    "type": "pdf",
    "config": {
      "extract_images": true,
      "extract_tables": true
    }
  },
  "transformers": [
    {
      "type": "text_cleanup",
      "config": {
        "remove_whitespace": true,
        "lowercase": false
      }
    },
    {
      "type": "language_detection",
      "config": {}
    }
  ],
  "loader": {
    "type": "database",
    "config": {
      "table_name": "documents",
      "connection_string": "postgresql://user:password@localhost:5432/db"
    }
  }
}
```

4. Click "Create"

### Running a Pipeline

1. Navigate to the DocETL page
2. Select a pipeline from the list
3. Click the "Run" button
4. Define the run parameters in JSON format:

```json
{
  "input_path": "/path/to/documents",
  "output_path": "/path/to/output",
  "file_pattern": "*.pdf"
}
```

5. Click "Run"

### Monitoring Pipeline Execution

1. Navigate to the DocETL page
2. Select the "Runs" tab
3. Select a pipeline from the list
4. View the list of runs for the selected pipeline
5. Click on a run to view its logs

## API Endpoints

The following API endpoints are available for the DocETL integration:

### Status and Information

- `GET /api/v1/docetl/status` - Get the status of the DocETL service

### Pipelines

- `GET /api/v1/docetl/pipelines` - Get a list of available pipelines
- `GET /api/v1/docetl/pipelines/{pipeline_id}` - Get details for a specific pipeline
- `POST /api/v1/docetl/pipelines` - Create a new pipeline
- `PUT /api/v1/docetl/pipelines/{pipeline_id}` - Update an existing pipeline
- `DELETE /api/v1/docetl/pipelines/{pipeline_id}` - Delete a pipeline

### Pipeline Runs

- `POST /api/v1/docetl/pipelines/{pipeline_id}/run` - Run a pipeline
- `GET /api/v1/docetl/pipelines/{pipeline_id}/runs` - Get a list of runs for a specific pipeline
- `GET /api/v1/docetl/pipelines/{pipeline_id}/runs/{run_id}` - Get details for a specific pipeline run
- `GET /api/v1/docetl/pipelines/{pipeline_id}/runs/{run_id}/logs` - Get logs for a specific pipeline run

### Components

- `GET /api/v1/docetl/extractors` - Get a list of available extractors
- `GET /api/v1/docetl/transformers` - Get a list of available transformers
- `GET /api/v1/docetl/loaders` - Get a list of available loaders

## Pipeline Configuration

### Extractors

Extractors are responsible for extracting text and metadata from documents. The following extractors are available:

- `pdf` - Extract text and metadata from PDF documents
- `docx` - Extract text and metadata from DOCX documents
- `txt` - Extract text from plain text files
- `image` - Extract text from images using OCR
- `html` - Extract text and metadata from HTML documents
- `email` - Extract text and metadata from email messages

### Transformers

Transformers are responsible for transforming the extracted data. The following transformers are available:

- `text_cleanup` - Clean up text by removing whitespace, lowercasing, etc.
- `language_detection` - Detect the language of the text
- `named_entity_recognition` - Extract named entities from the text
- `sentiment_analysis` - Analyze the sentiment of the text
- `topic_modeling` - Extract topics from the text
- `summarization` - Generate a summary of the text

### Loaders

Loaders are responsible for loading the transformed data into storage systems. The following loaders are available:

- `database` - Load data into a database
- `file` - Load data into a file
- `elasticsearch` - Load data into Elasticsearch
- `api` - Load data via an API

## Integration with Other Components

### Integration with Kestra Workflows

DocETL pipelines can be integrated with Kestra workflows to create more complex document processing workflows. For example, you can create a Kestra workflow that:

1. Downloads documents from Box.com
2. Processes the documents using DocETL
3. Loads the processed data into PostGIS
4. Visualizes the data using Martin MapLibre

### Integration with DuckDB

DocETL can be used with DuckDB to analyze document data. For example, you can:

1. Extract text and metadata from documents using DocETL
2. Load the extracted data into DuckDB
3. Analyze the data using SQL queries
4. Visualize the results using charts and maps

## Troubleshooting

### Connection Issues

If you're having trouble connecting to the DocETL server:

1. Check that the DocETL server is running
2. Verify the `DOCETL_API_URL` environment variable
3. Check the server logs for error messages

### Pipeline Execution Issues

If a pipeline fails to execute:

1. Check the pipeline configuration for errors
2. Verify that the input files exist and are accessible
3. Check the pipeline run logs for error messages

### Component Issues

If a component (extractor, transformer, or loader) fails:

1. Check the component configuration for errors
2. Verify that the required libraries are installed
3. Check the pipeline run logs for error messages

## Limitations

The current implementation has the following limitations:

1. Limited support for large documents
2. No support for real-time document processing
3. Limited support for complex document formats
4. No support for distributed processing
