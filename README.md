# Integrated Geospatial API

A comprehensive platform for geospatial data management and analysis, integrating multiple FastAPI microservices with a Next.js PWA frontend.
ython fast API microservices and kestra orchestration for reviewing geospatial data sources and importing into POSTGIS, GeoServer and executing spatial functions and queries


PYTHON FAST API microservices wrapped in OGC API PROCESSES - for analysis functions.

as a starting point this project leverages the existing great https://github.com/mkeller3

- -FastImporter - Import GIS Data to PostGIS
- 
- -FastGeospatial
- 
- -FastGeofeature
- 
- -FastGeostats
- 
- -FastGeoTable
- 
- -FastGeosuitability


Extends this to support the additional spatial analysis queries for the spatial intelligence team It uses DUCKDB and OGR FDW + PG_Analytics FDW for Postgres to support reviewing data before input getting metadata information It can connect to any cloud storage or file system supported by httpfs extension other file systems python and box.com official package

it uses LEAFMP https://leafmap.org/ jupyter Noteobook (using it with maplibre and deckgl maps but there are others) with Papermill https://papermill.readthedocs.io/en/latest/ and https://github.com/marimo-team/marimo and https://github.com/teableio/teable is used to able to preview attribute data It uses MARTIN and PG_FeatureServer for NON PRODUTION (DEV/TEST/STAGING) Serving of Geospatial Data for QA and Review to a Internal Web Map and configures the web map to use the dynamic and cached map tiles and GPKG

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

he project includes integration with** GeoDiff and DBFriend** for data conflation and change detection:

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

CDC  - Change Data Capture - wizard interface from the nextjs webapp to configure database information and sync schedule (hourly, daily, weekluy)
DLT KESTRA for all the orchestration.

It is using Google OAUTH2 SSO to authenticate via pocket base (pocket base use it's internal identity provider or any OAUTH2 OIDC Provider.)
pocketbase been setup with collections to have user roles
with some roles:

- Viewer - Can only view data, no modifications
- Analyst - Can run select queries but not modify data
- Project Manager - Can make assignments and manage workflows but not modify data
- Data Engineer - Can upload and modify data Admin - Full access to all features
- do we need other roles


## Features

- **Unified API**: Integrates FastGeospatial, FastImporter, FateGeoFeature, FastGeoTable, and FastGeoSuitability into a single cohesive API
- **PostGIS Integration**: Leverages PostgreSQL with PostGIS for powerful geospatial operations
- **Progressive Web App**: Next.js frontend with PWA capabilities for offline access
- **Configurable Database Connection**: User-friendly interface to configure database settings
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Project Structure

```
integrated-geospatial-api/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── fast_geospatial.py
│   │   │       ├── fast_importer.py
│   │   │       ├── fate_geo_feature.py
│   │   │       ├── fast_geo_table.py
│   │   │       ├── fast_geo_suitability.py
│   │   │       └── integrated.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   ├── models/
│   │   │   ├── base.py
│   │   │   ├── geospatial.py
│   │   │   ├── geo_feature.py
│   │   │   ├── geo_table.py
│   │   │   ├── geo_suitability.py
│   │   │   └── importer.py
│   │   ├── schemas/
│   │   │   ├── base.py
│   │   │   ├── database.py
│   │   │   ├── geospatial.py
│   │   │   ├── geo_feature.py
│   │   │   ├── geo_table.py
│   │   │   ├── geo_suitability.py
│   │   │   └── importer.py
│   │   └── main.py
│   └── requirements.txt
├── frontend/
│   ├── public/
│   │   ├── icons/
│   │   ├── manifest.json
│   │   └── service-worker.js
│   ├── src/
│   │   ├── components/
│   │   │   └── Layout.tsx
│   │   ├── pages/
│   │   │   ├── _app.tsx
│   │   │   ├── index.tsx
│   │   │   ├── geospatial.tsx
│   │   │   └── settings.tsx
│   │   ├── styles/
│   │   │   └── globals.css
│   │   └── utils/
│   │       └── api.ts
│   └── package.json
└── README.md
```

## Prerequisites

- Node.js (v14 or later)
- Python (v3.8 or later)
- PostgreSQL with PostGIS extension

## Getting Started

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd fastapi-nextjs-project/backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the FastAPI application:
   ```
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd fastapi-nextjs-project/frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Run the development server:
   ```
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Database Configuration

1. Make sure PostgreSQL is installed with the PostGIS extension.
2. Create a new database for the application.
3. Use the Settings page in the frontend to configure the database connection.

## API Documentation

Once the backend is running, you can access the API documentation at:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [Next.js](https://nextjs.org/)
- [PostgreSQL](https://www.postgresql.org/)
- [PostGIS](https://postgis.net/)
- [GeoAlchemy2](https://geoalchemy-2.readthedocs.io/)
- [Leaflet](https://leafletjs.com/)
- [mkeller3](https://github.com/mkeller3) - For inspiration and reference
