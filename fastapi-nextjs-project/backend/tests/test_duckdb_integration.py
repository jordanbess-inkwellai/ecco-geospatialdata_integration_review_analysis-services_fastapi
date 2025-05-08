import pytest
import duckdb
import pandas as pd
import geopandas as gpd
import json
import os
from shapely.geometry import Point, Polygon

from app.services.duckdb_service import DuckDBService


class TestDuckDBIntegration:
    """Test DuckDB integration for geospatial data."""
    
    def test_duckdb_spatial_extension(self, duckdb_connection):
        """Test that the spatial extension is loaded and working."""
        # Create a simple point
        result = duckdb_connection.execute(
            "SELECT ST_AsText(ST_Point(0, 0)) as wkt"
        ).fetchone()
        
        assert result[0] == "POINT (0 0)"
    
    def test_load_geojson(self, duckdb_connection, sample_geojson):
        """Test loading GeoJSON into DuckDB."""
        # Load GeoJSON file
        duckdb_connection.execute(
            f"CREATE TABLE test_geojson AS SELECT * FROM ST_Read('{sample_geojson}')"
        )
        
        # Check that the table was created
        result = duckdb_connection.execute(
            "SELECT COUNT(*) FROM test_geojson"
        ).fetchone()
        
        assert result[0] == 2
        
        # Check geometry column
        result = duckdb_connection.execute(
            "SELECT ST_AsText(geometry) FROM test_geojson ORDER BY name"
        ).fetchall()
        
        assert "POINT" in result[0][0]
        assert "POLYGON" in result[1][0]
        
        # Check properties
        result = duckdb_connection.execute(
            "SELECT name, value FROM test_geojson ORDER BY name"
        ).fetchall()
        
        assert result[0][0] == "Test Point"
        assert result[0][1] == 42
        assert result[1][0] == "Test Polygon"
        assert result[1][1] == 100
    
    def test_spatial_query(self, duckdb_connection, sample_geojson):
        """Test spatial queries in DuckDB."""
        # Load GeoJSON file
        duckdb_connection.execute(
            f"CREATE OR REPLACE TABLE test_geojson AS SELECT * FROM ST_Read('{sample_geojson}')"
        )
        
        # Query features that intersect with a box
        result = duckdb_connection.execute("""
            SELECT name 
            FROM test_geojson 
            WHERE ST_Intersects(
                geometry, 
                ST_GeomFromText('POLYGON((0 0, 0.5 0, 0.5 0.5, 0 0.5, 0 0))')
            )
            ORDER BY name
        """).fetchall()
        
        # Both features should intersect
        assert len(result) == 2
        assert result[0][0] == "Test Point"
        assert result[1][0] == "Test Polygon"
        
        # Query features with a specific property
        result = duckdb_connection.execute("""
            SELECT name 
            FROM test_geojson 
            WHERE value > 50
        """).fetchall()
        
        assert len(result) == 1
        assert result[0][0] == "Test Polygon"
    
    def test_duckdb_service(self, duckdb_connection, sample_geojson, temp_dir):
        """Test DuckDBService for geospatial operations."""
        # Initialize service
        service = DuckDBService(duckdb_connection)
        
        # Load GeoJSON
        table_name = service.load_geojson(sample_geojson)
        
        # Check table exists
        assert service.table_exists(table_name)
        
        # Get table info
        table_info = service.get_table_info(table_name)
        assert "geometry" in table_info["columns"]
        assert table_info["row_count"] == 2
        
        # Run spatial query
        query_result = service.execute_spatial_query(
            f"SELECT name, ST_AsText(geometry) as wkt FROM {table_name} WHERE value > 50"
        )
        
        assert len(query_result) == 1
        assert query_result[0]["name"] == "Test Polygon"
        assert "POLYGON" in query_result[0]["wkt"]
        
        # Export to GeoPackage
        gpkg_path = os.path.join(temp_dir, "test_export.gpkg")
        service.export_to_geopackage(table_name, gpkg_path)
        
        # Check that the file was created
        assert os.path.exists(gpkg_path)
        
        # Read back with GeoPandas to verify
        gdf = gpd.read_file(gpkg_path)
        assert len(gdf) == 2
        assert "Test Point" in gdf["name"].values
        assert "Test Polygon" in gdf["name"].values
    
    def test_duckdb_postgis_integration(self, duckdb_connection, db_session, sample_geojson):
        """Test integration between DuckDB and PostGIS."""
        # This test would normally use a real connection to PostGIS
        # For this example, we'll mock the integration
        
        # Initialize service
        service = DuckDBService(duckdb_connection)
        
        # Load GeoJSON
        table_name = service.load_geojson(sample_geojson)
        
        # Export to SQL statements for PostGIS
        sql_path = os.path.join(os.path.dirname(sample_geojson), "export.sql")
        service.export_to_postgis_sql(
            table_name, 
            sql_path, 
            table_name="exported_features",
            schema="public",
            srid=4326
        )
        
        # Check that the SQL file was created
        assert os.path.exists(sql_path)
        
        # Read SQL file and check content
        with open(sql_path, "r") as f:
            sql_content = f.read()
        
        # Check SQL content
        assert "CREATE TABLE" in sql_content
        assert "public.exported_features" in sql_content
        assert "geometry" in sql_content
        assert "INSERT INTO" in sql_content
        
        # In a real test, we would execute this SQL against PostGIS
        # and verify the results
