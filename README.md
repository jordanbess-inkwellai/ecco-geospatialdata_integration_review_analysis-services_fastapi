# ecco-geospatialdata_integration_review_analysis-services_fastapi
python fast API microservices and kestra orchestration for reviewing geospatial data sources and importing into POSTGIS, GeoServer and executing spatial functions and queries

as a starting point this project leverages the existing great https://github.com/mkeller3

-FastImporter  - Import GIS Data to PostGIS

-FastGeospatial

-FastGeofeature

-FastGeostats

-FastGeoTable

-FastGeosuitability

Extends this to support the additional spatial analysis queries for the spatial intelligence team
It uses DUCKDB and OGR FDW + PG_Analytics FDW for Postgres 
to support reviewing data before input
getting metadata information
It can connect to any cloud storage or file system supported by httpfs extension other file systems python and box.com official package

it uses LEAFMP https://leafmap.org/ jupyter Noteobook (using it with maplibre and deckgl maps but there are others)
with Papermill https://papermill.readthedocs.io/en/latest/ and https://github.com/marimo-team/marimo
and https://github.com/teableio/teable is used to able to preview attribute data 
It uses MARTIN and PG_FeatureServer for NON PRODUTION (DEV/TEST/STAGING) Serving of Geospatial Data for QA and Review to a Internal Web Map
and configures the web map to use the dynamic and cached map tiles and GPKG

To create cached map tiles of vector GIS Data as PMTILES or MBTILES this package is used
https://github.com/felt/tippecanoe
Then jordan wrote a python script to convert MBTILES or folder of tiles to GPKG vector tiles as another storage container

There is a NEXTJS PWA Web App for internal Developer/Data Engineer use to manage this import process and preview data and metadata
before executing a workflow
