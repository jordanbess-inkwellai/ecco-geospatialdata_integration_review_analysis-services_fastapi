# PostGIS Microservices Analysis

This project integrates various geospatial microservices into a unified platform for geospatial data management and analysis, with a FastAPI backend and a Next.js PWA frontend.

## Features

- **Geospatial Analysis**: Buffer, intersection, distance, area, convex hull, simplification, Voronoi diagrams
- **Spatial Search**: Bounding box search, spatial relationship search, nearest neighbor search, attribute and spatial filtering
- **Raster Analysis**: Value at point, statistics, contour generation
- **Network Analysis**: Shortest path, service area (requires pgRouting)
- **Data Processing**: Process and transform geospatial data with powerful tools
- **AI-Powered Data Validation**: Optional AI models for data validation, schema matching, and transformation suggestions
- **Data Import/Export**: Import and export geospatial data in various formats
- **Box.com Integration**: Browse, import, and manage files from Box.com with metadata extraction
- **Workflow Orchestration**: Integrate with Kestra for workflow orchestration
- **DuckDB Integration**: Use DuckDB for fast data inspection and querying

as a starting point this project leverages the existing great work by this Open Source Developer
 https://github.com/mkeller3

-FastImporter - Import GIS Data to PostGIS

-FastGeospatial  - Geospatial Analysis - this is where we will extend to the queries we need

-FastGeofeature -geospatial api to serve data via the OGC Features API standard. (not for production just another interface to query data and integrate it into local map)

-FastGeostats  -geospatial api to perform math and statistics on tables from a multitude of PostgreSQL databases with geographical data

-FastGeoTable -PostGIS geospatial api to enable creating/editing geographical tables within a spatial database.

-FastGeosuitability - suitability analysis with geographical tables within a spatial database.

Extends this to support the additional spatial analysis queries for the spatial intelligence team It uses DUCKDB and OGR FDW + PG_Analytics FDW for Postgres to support reviewing data before input getting metadata information It can connect to any cloud storage or file system supported by httpfs extension other file systems python and box.com official package

Data Visualization/Mapping Component It uses python LEAFMP https://leafmap.org/ jupyter Noteobook (using it with maplibre and deckgl maps but there are others) with Papermill https://papermill.readthedocs.io/en/latest/ and https://github.com/marimo-team/marimo and https://github.com/teableio/teable is used to able to preview attribute data It uses MARTIN and PG_FeatureServer for NON PRODUTION (DEV/TEST/STAGING) Serving of Geospatial Data for QA and Review to a Internal Web Map and configures the web map to use the dynamic and cached map tiles and GPKG

To create cached map tiles of vector GIS Data as PMTILES or MBTILES this package is used https://github.com/felt/tippecanoe Then jordan wrote a python script to convert MBTILES or folder of tiles to GPKG vector tiles as another storage container

There is a NEXTJS PWA Web App for internal Developer/Data Engineer use to manage this import process and preview data and metadata before executing a workflow

Other Capabilities: Support for any OGR or DUCKDB format Support for converting ESRI Mobile Geodatabase SQLite to GPKG or other GIS Format Ability to import 3D Geometry into postgis

NextJS PWA web app can create basic styling symbology and labeling for GL JSON Vector Tiles and create SLD symbology encoding and as needed introduce geostyler https://geostyler.org/ for import into geoserver/geonode It also can create GeoJSON Simple Style Spec

It uses pocketbase server and it's real-time API and hooks to allow the front-end to subscribe and see events it also has pyDANTIC and Google Cloud python https://github.com/GoogleCloudPlatform/cloud-sql-python-connector Pocketbase is using GOOGLE SSO signin

with some roles: Viewer - Can only view data, no modifications Analyst - Can run select queries but not modify data Project Manager - Can make assignments and manage workflows but not modify data Data Engineer - Can upload and modify data Admin - Full access to all features

HERE IS a high level architecture: Frontend Layer NextJS PWA Application QGIS Plugin

API Layer FastAPI Microservices API Endpoints

Processing Layer DuckDB Tippecanoe Kestra Workflows DLT Pipelines

Data Layer PostgreSQL/PostGIS Vector Tiles (PMTiles/MBTiles) File Storage

Integration Layer PocketBase Martin MapLibre Box.com Integration

the project includes integration with GeoDiff and DBFriend for data conflation and change detection:

GeoDiff: Detect and apply changes between geospatial datasets

Create changesets between GeoPackage files
Apply changesets to update files
List changes in a changeset
Rebase changes to resolve conflicts
DBFriend: Compare and synchronize databases

Compare database schemas and data
Generate SQL scripts for synchronization
Apply changes between databases
There are optional build Flags to introduce AI Models specifically trained for working on Data Schema Review and Data QA/QC and Other Data Engineering Tasks

## Project Structure

```
fastapi-nextjs-project
├── backend
│   ├── app
│   │   ├── main.py
│   │   ├── api
│   │   │   ├── v1
│   │   │   │   ├── fast_geospatial.py
│   │   │   │   ├── fast_importer.py
│   │   │   │   ├── fate_geo_feature.py
│   │   │   │   ├── fast_geo_table.py
│   │   │   │   └── fast_geo_suitability.py
│   │   ├── core
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   ├── models
│   │   │   └── __init__.py
│   │   ├── schemas
│   │   │   └── __init__.py
│   │   └── utils
│   │       └── __init__.py
│   ├── requirements.txt
│   └── README.md
├── frontend
│   ├── public
│   │   └── manifest.json
│   ├── src
│   │   ├── pages
│   │   │   ├── _app.tsx
│   │   │   ├── index.tsx
│   │   │   └── api
│   │   │       └── hello.ts
│   │   ├── components
│   │   │   └── Layout.tsx
│   │   ├── styles
│   │   │   └── globals.css
│   │   └── utils
│   │       └── api.ts
│   ├── package.json
│   ├── tsconfig.json
│   └── README.md
└── README.md
```

## Backend

The backend is built using FastAPI and includes several microservices for handling geospatial data:

- **FastGeospatial**: Endpoints for geospatial data management.
- **FastImporter**: Endpoints for importing data.
- **FateGeoFeature**: Endpoints for managing geo-features.
- **FastGeoTable**: Endpoints for table-related operations.
- **FastGeoSuitability**: Endpoints for assessing suitability based on geospatial queries.

### Setup

1. Navigate to the `backend` directory.
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the FastAPI application:
   ```
   uvicorn app.main:app --reload
   ```

## Frontend

The frontend is developed using Next.js and serves as a PWA, allowing users to interact with the backend services.

### Setup

1. Navigate to the `frontend` directory.
2. Install the required dependencies:
   ```
   npm install
   ```
3. Run the Next.js application:
   ```
   npm run dev
   ```

## Configuration

Database connection settings and other configurations can be adjusted in the `app/core/config.py` file.

## AI Features

This project includes optional AI capabilities for data validation, schema matching, and transformation suggestions. These features are controlled by a build flag and can be enabled or disabled as needed.

### Available AI Models

The following AI models are supported:

1. **Jellyfish-13B** (default): A powerful large language model optimized for data understanding and schema matching.
2. **XLNet**: Excels at understanding the context and relationships in sequential data.
3. **T5**: Text-to-Text Transfer Transformer designed for various text transformation tasks.
4. **BERT**: Provides deep bidirectional representations and is excellent for understanding context.

See [README-AI.md](README-AI.md) for detailed instructions on enabling and using the AI features.

## Box.com Integration

The project includes integration with Box.com for file management and geospatial data import:

- Browse files and folders in Box.com
- Import geospatial data files with automatic metadata extraction
- Search for files in Box.com
- Create shared links for Box.com files
- Download files from Box.com

See [BOX_INTEGRATION.md](docs/BOX_INTEGRATION.md) for detailed instructions on setting up and using the Box.com integration.

## Workflow Orchestration

The project includes integration with Kestra for workflow orchestration:

- Create, edit, and manage data processing workflows visually
- Convert Python and shell scripts into workflows automatically
- Execute workflows and monitor their execution
- Create workflow templates for reuse
- Set up triggers for workflows (schedule, webhook, etc.)
- Integrate with PocketBase for real-time triggers

See [KESTRA_INTEGRATION.md](docs/KESTRA_INTEGRATION.md) for detailed instructions on setting up and using the Kestra workflow integration.

## DuckDB Analytics

The project includes integration with DuckDB for fast data inspection and analysis:

- Create and manage DuckDB databases
- Import data from various file formats (CSV, Parquet, JSON, Excel, Shapefile, GeoPackage, GeoJSON)
- Execute SQL queries on the data
- Visualize query results in tables, charts, and maps
- Export data to various formats
- Connect to external databases (PostgreSQL, MySQL, SQLite)
- Perform spatial analysis on geospatial data

See [DUCKDB_INTEGRATION.md](docs/DUCKDB_INTEGRATION.md) for detailed instructions on setting up and using the DuckDB integration.

## Martin MapLibre Integration

The project includes integration with Martin MapLibre for mapping and visualization:

- Visualize geospatial data from PostGIS databases using vector tiles
- Upload and manage PMTiles, MBTiles, raster tiles, and terrain tiles
- Create and customize MapLibre GL styles
- Combine data from multiple sources in a single map
- Export data to various formats

See [MARTIN_INTEGRATION.md](docs/MARTIN_INTEGRATION.md) for detailed instructions on setting up and using the Martin MapLibre integration.

## DocETL Integration

The project includes optional integration with DocETL for document processing:

- Extract text and metadata from various document formats
- Transform extracted data with customizable transformers
- Load processed data into different storage systems
- Create and manage document processing pipelines
- Monitor pipeline execution and view logs

See [DOCETL_INTEGRATION.md](docs/DOCETL_INTEGRATION.md) for detailed instructions on setting up and using the DocETL integration.

## Querybook Integration

The project includes optional integration with Querybook for data analysis:

- Write and run SQL queries against various data sources
- Create and share notebooks with SQL queries and Python scripts
- Visualize query results with charts and tables
- Collaborate with team members on data analysis
- Schedule queries to run periodically

See [QUERYBOOK_INTEGRATION.md](docs/QUERYBOOK_INTEGRATION.md) for detailed instructions on setting up and using the Querybook integration.

## Performance Optimization

The project includes performance optimization guidelines for handling large datasets and high user loads:

- Database optimization for PostgreSQL/PostGIS and DuckDB
- Vector tile optimization for Martin MapLibre
- Frontend optimization for NextJS and MapLibre
- Workflow optimization for Kestra
- Server optimization for FastAPI
- Monitoring and profiling techniques

See [PERFORMANCE_OPTIMIZATION.md](docs/PERFORMANCE_OPTIMIZATION.md) for detailed performance optimization guidelines.

## Deployment

The project includes deployment instructions for various environments:

- Local development deployment
- Docker deployment using Docker Compose and Docker Swarm
- Kubernetes deployment
- Cloud deployment on AWS, Azure, and Google Cloud
- Continuous integration and deployment
- Monitoring, logging, backup, and security considerations

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment instructions.

## Usage

Once both the backend and frontend are running, you can access the application through your web browser. The frontend will provide a user-friendly interface to interact with the backend services.

## Deployment Options

### Local Docker Deployment

The project includes Docker and Docker Compose configurations for easy local deployment:

```bash
# Start all services
docker-compose up

# Start only specific services
docker-compose up api frontend db

# Start with AI features enabled (Jellyfish-13B model)
docker-compose up api-jellyfish frontend db
```

### Google Cloud Deployment

For production deployments, we provide infrastructure as code and deployment scripts for Google Cloud Platform:

1. Set up the infrastructure with Terraform:
   ```bash
   ./scripts/gcp/setup-project.sh --project-id=YOUR_PROJECT_ID
   cd terraform && terraform apply
   ```

2. Deploy the application to GKE:
   ```bash
   ./scripts/gcp/deploy.sh --project-id=YOUR_PROJECT_ID
   ```

3. Set up monitoring and alerting:
   ```bash
   ./scripts/gcp/setup-monitoring.sh --project-id=YOUR_PROJECT_ID
   ```

For detailed instructions, see [Google Cloud Deployment Guide](docs/GOOGLE_CLOUD_DEPLOYMENT.md).

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.