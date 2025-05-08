# Querybook Integration

This document provides information about the Querybook integration in the MCP Server application.

## Overview

[Querybook](https://github.com/pinterest/querybook) is a Big Data IDE that allows users to write, run, and share SQL queries and Python scripts. It provides a collaborative environment for data exploration, analysis, and visualization.

The MCP Server integrates Querybook to provide a seamless experience for data analysis and exploration, with consistent branding and navigation.

## Features

- Write and run SQL queries against various data sources
- Create and share notebooks with SQL queries and Python scripts
- Visualize query results with charts and tables
- Collaborate with team members on data analysis
- Schedule queries to run periodically
- Export query results to various formats

## Setup and Configuration

### Prerequisites

To use the Querybook integration, you need:

1. Querybook server running and accessible
2. Data sources configured in Querybook (e.g., PostgreSQL, MySQL, Presto, Hive, etc.)

### Configuration

The Querybook integration is configured using environment variables:

```
# Querybook server settings
NEXT_PUBLIC_QUERYBOOK_ENABLED=true
NEXT_PUBLIC_QUERYBOOK_URL=http://localhost:10001
NEXT_PUBLIC_QUERYBOOK_API_URL=http://localhost:10001/api/v1
```

## Installation

### Docker Installation

The easiest way to install Querybook is using Docker:

```bash
# Clone the Querybook repository
git clone https://github.com/pinterest/querybook.git
cd querybook

# Build the Docker image
docker-compose build

# Start Querybook
docker-compose up -d
```

### Manual Installation

For manual installation, follow these steps:

1. Clone the Querybook repository:
   ```bash
   git clone https://github.com/pinterest/querybook.git
   cd querybook
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Node.js dependencies:
   ```bash
   cd querybook/webapp
   npm install
   ```

4. Build the frontend:
   ```bash
   npm run build
   ```

5. Configure Querybook:
   ```bash
   cp querybook/config/querybook_config.yaml.example querybook/config/querybook_config.yaml
   # Edit querybook_config.yaml to configure your environment
   ```

6. Start Querybook:
   ```bash
   python querybook/scripts/run_webserver.py
   ```

## Integration with MCP Server

### Frontend Integration

The MCP Server integrates Querybook in the frontend using an iframe that loads the Querybook web interface. The integration includes:

1. A menu item in the sidebar for accessing Querybook
2. A dedicated page for the Querybook interface
3. Consistent branding and styling

### Authentication Integration

If you're using authentication in both MCP Server and Querybook, you can configure single sign-on (SSO) to provide a seamless experience:

1. Configure Querybook to use the same authentication provider as MCP Server (e.g., Google SSO)
2. Set up token-based authentication between MCP Server and Querybook

## Usage

### Accessing Querybook

1. Navigate to the MCP Server web interface
2. Click on the "Querybook" item in the sidebar
3. The Querybook interface will load in the main content area

### Creating a Query

1. Click on the "+" button to create a new query
2. Select a data source from the dropdown
3. Write your SQL query in the editor
4. Click "Run" to execute the query
5. View the results in the results panel

### Creating a Notebook

1. Click on the "+" button to create a new notebook
2. Add a title and description for the notebook
3. Click "Create"
4. Add query cells to the notebook
5. Write and run queries in the cells
6. Add text cells for documentation

### Sharing a Notebook

1. Open the notebook you want to share
2. Click on the "Share" button
3. Set the sharing permissions (public, team, or specific users)
4. Copy the sharing link and send it to your collaborators

## Integration with Other Components

### Integration with DuckDB

Querybook can be configured to use DuckDB as a data source, allowing you to:

1. Query data from DuckDB
2. Visualize DuckDB query results
3. Share DuckDB queries with your team

To configure DuckDB as a data source in Querybook:

1. Add a DuckDB engine configuration to Querybook's configuration file
2. Specify the path to the DuckDB database file
3. Restart Querybook

### Integration with PostGIS

Querybook can be configured to use PostGIS as a data source, allowing you to:

1. Query geospatial data from PostGIS
2. Visualize geospatial query results
3. Share PostGIS queries with your team

To configure PostGIS as a data source in Querybook:

1. Add a PostgreSQL engine configuration to Querybook's configuration file
2. Specify the connection details for your PostGIS database
3. Restart Querybook

### Integration with Martin MapLibre

Query results from Querybook can be visualized on a map using Martin MapLibre:

1. Run a query in Querybook that returns geospatial data
2. Export the query results to a format supported by Martin MapLibre (e.g., GeoJSON)
3. Load the exported data in Martin MapLibre for visualization

## Customization

### Branding Customization

To customize the branding of Querybook to match the MCP Server:

1. Create a custom CSS file with your branding styles
2. Add the CSS file to the Querybook configuration
3. Restart Querybook

Example custom CSS:

```css
:root {
  --color-primary: #3f51b5;
  --color-secondary: #f50057;
  --color-background: #f5f5f5;
  --color-text: #333333;
}

.navbar {
  background-color: var(--color-primary);
}

.btn-primary {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
}

.btn-secondary {
  background-color: var(--color-secondary);
  border-color: var(--color-secondary);
}
```

### Feature Customization

To customize the features available in Querybook:

1. Edit the Querybook configuration file
2. Enable or disable features as needed
3. Restart Querybook

Example configuration:

```yaml
features:
  enable_query_execution: true
  enable_query_scheduling: true
  enable_query_sharing: true
  enable_notebook_sharing: true
  enable_data_upload: false
  enable_data_download: true
  enable_chart_visualization: true
  enable_table_visualization: true
  enable_map_visualization: true
```

## Troubleshooting

### Connection Issues

If you're having trouble connecting to the Querybook server:

1. Check that the Querybook server is running
2. Verify the `NEXT_PUBLIC_QUERYBOOK_URL` environment variable
3. Check the Querybook server logs for error messages

### Authentication Issues

If you're having trouble with authentication:

1. Check that the authentication provider is configured correctly in both MCP Server and Querybook
2. Verify that the user has the necessary permissions in Querybook
3. Check the Querybook server logs for authentication-related error messages

### Query Execution Issues

If queries are failing to execute:

1. Check that the data source is configured correctly in Querybook
2. Verify that the user has the necessary permissions to access the data source
3. Check the query syntax for errors
4. Check the Querybook server logs for query execution error messages

## Limitations

The current implementation has the following limitations:

1. Limited integration with MCP Server's authentication system
2. No direct integration with MCP Server's data sources
3. Limited customization of the Querybook interface
4. No support for offline mode

## Future Enhancements

Planned enhancements for the Querybook integration include:

1. Deeper integration with MCP Server's authentication system
2. Direct integration with MCP Server's data sources
3. More customization options for the Querybook interface
4. Support for offline mode
5. Integration with MCP Server's notification system
