import pytest
import os
import json
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon, box
from sqlalchemy import select, func
from geoalchemy2.shape import to_shape, from_shape

from app.models.metadata import MetadataDataset
from app.services.metadata_service import MetadataService
from app.services.duckdb_service import DuckDBService
from app.schemas.ai_geo_models import MetadataExtractorAI, GeoDatasetAI


@pytest.mark.asyncio
class TestFullIntegration:
    """Test full integration between Pydantic AI, GeoAlchemy, DuckDB, and PostGIS."""
    
    async def test_end_to_end_workflow(self, db_session, duckdb_connection, sample_geojson, temp_dir):
        """
        Test end-to-end workflow:
        1. Extract metadata from file using Pydantic AI
        2. Load data into DuckDB for analysis
        3. Store metadata in PostGIS using GeoAlchemy
        4. Query and analyze data
        """
        # Step 1: Extract metadata using Pydantic AI
        extractor = MetadataExtractorAI()
        metadata = extractor.extract_from_file(sample_geojson)
        
        # Check metadata
        assert metadata.title is not None
        assert metadata.data_type == "vector"
        assert metadata.format.lower() == "geojson"
        
        # Step 2: Load data into DuckDB
        duckdb_service = DuckDBService(duckdb_connection)
        table_name = duckdb_service.load_geojson(sample_geojson)
        
        # Check data in DuckDB
        result = duckdb_connection.execute(
            f"SELECT COUNT(*) FROM {table_name}"
        ).fetchone()
        assert result[0] == 2
        
        # Step 3: Analyze data in DuckDB
        # Calculate bounding box
        bbox_result = duckdb_connection.execute(f"""
            SELECT 
                MIN(ST_X(geometry)) as min_x,
                MIN(ST_Y(geometry)) as min_y,
                MAX(ST_X(geometry)) as max_x,
                MAX(ST_Y(geometry)) as max_y
            FROM {table_name}
        """).fetchone()
        
        bbox = [bbox_result[0], bbox_result[1], bbox_result[2], bbox_result[3]]
        
        # Calculate statistics
        stats_result = duckdb_connection.execute(f"""
            SELECT 
                AVG(value) as avg_value,
                MIN(value) as min_value,
                MAX(value) as max_value
            FROM {table_name}
            WHERE value IS NOT NULL
        """).fetchone()
        
        avg_value = stats_result[0]
        min_value = stats_result[1]
        max_value = stats_result[2]
        
        # Step 4: Store metadata in PostGIS
        # Convert metadata to dataset create model
        from app.schemas.metadata import DatasetCreate
        
        dataset_data = {
            "title": metadata.title,
            "description": metadata.description,
            "abstract": metadata.description,
            "resource_type": "dataset",
            "resource_format": metadata.format,
            "resource_path": sample_geojson,
            "bbox": bbox,
            "keywords": metadata.keywords,
            "properties": {
                "feature_count": metadata.properties.get("feature_count", 0),
                "geometry_types": metadata.properties.get("geometry_types", []),
                "property_types": metadata.properties.get("property_types", {}),
                "statistics": {
                    "avg_value": avg_value,
                    "min_value": min_value,
                    "max_value": max_value
                }
            }
        }
        
        dataset_create = DatasetCreate(**dataset_data)
        
        # Create dataset in PostGIS
        dataset = await MetadataService.create_dataset(db_session, dataset_create)
        
        # Check dataset
        assert dataset.id is not None
        assert dataset.title == metadata.title
        assert dataset.bbox == bbox
        assert dataset.geometry is not None
        
        # Step 5: Query dataset from PostGIS
        query = select(MetadataDataset).filter(MetadataDataset.id == dataset.id)
        result = await db_session.execute(query)
        retrieved_dataset = result.scalar_one()
        
        assert retrieved_dataset.id == dataset.id
        assert retrieved_dataset.title == metadata.title
        
        # Step 6: Export data from DuckDB to GeoPackage
        gpkg_path = os.path.join(temp_dir, "exported_data.gpkg")
        duckdb_service.export_to_geopackage(table_name, gpkg_path)
        
        # Check exported file
        assert os.path.exists(gpkg_path)
        gdf = gpd.read_file(gpkg_path)
        assert len(gdf) == 2
        
        # Step 7: Perform spatial query combining PostGIS and DuckDB
        # Get centroid from PostGIS
        centroid_query = select(
            func.ST_AsText(func.ST_Centroid(MetadataDataset.geometry))
        ).filter(MetadataDataset.id == dataset.id)
        
        centroid_result = await db_session.execute(centroid_query)
        centroid_wkt = centroid_result.scalar_one()
        
        # Use centroid in DuckDB query
        buffer_query = f"""
            SELECT COUNT(*) 
            FROM {table_name} 
            WHERE ST_DWithin(
                geometry, 
                ST_GeomFromText('{centroid_wkt}'),
                1.0
            )
        """
        
        buffer_result = duckdb_connection.execute(buffer_query).fetchone()
        assert buffer_result[0] > 0
        
        # Step 8: Update metadata in PostGIS based on DuckDB analysis
        # Get more detailed statistics
        detailed_stats = duckdb_connection.execute(f"""
            SELECT 
                name,
                COUNT(*) as count,
                AVG(value) as avg_value,
                STDDEV(value) as std_value
            FROM {table_name}
            GROUP BY name
        """).fetchall()
        
        # Convert to dictionary
        stats_by_name = {
            row[0]: {
                "count": row[1],
                "avg_value": row[2],
                "std_value": row[3]
            }
            for row in detailed_stats
        }
        
        # Update dataset properties
        from app.schemas.metadata import DatasetUpdate
        
        update_data = DatasetUpdate(
            properties={
                **retrieved_dataset.properties,
                "detailed_statistics": stats_by_name
            }
        )
        
        updated_dataset = await MetadataService.update_dataset(
            db_session, 
            dataset.id, 
            update_data
        )
        
        # Check updated dataset
        assert "detailed_statistics" in updated_dataset.properties
        assert len(updated_dataset.properties["detailed_statistics"]) > 0
