import os
import sqlite3
import json
import logging
import struct
import binascii
from typing import List, Dict, Any, Optional, Tuple, Union
import tempfile
import duckdb
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString, Polygon, MultiPoint, MultiLineString, MultiPolygon
from shapely.wkb import loads as wkb_loads
from fastapi import HTTPException

# Import the rclone service
try:
    from app.services.rclone_service import rclone_service
except ImportError:
    rclone_service = None
    logger = logging.getLogger(__name__)
    logger.warning("Rclone service not available. Remote geodatabase functionality will be limited.")

logger = logging.getLogger(__name__)

# Define storage paths
TEMP_DIR = os.environ.get("TEMP_DIR", "./data/temp")
GEOJSON_DIR = os.environ.get("GEOJSON_DIR", "./data/geojson")
GPKG_DIR = os.environ.get("GPKG_DIR", "./data/gpkg")
DUCKDB_DIR = os.environ.get("DUCKDB_DIR", "./data/duckdb")

# Ensure directories exist
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(GEOJSON_DIR, exist_ok=True)
os.makedirs(GPKG_DIR, exist_ok=True)
os.makedirs(DUCKDB_DIR, exist_ok=True)


class ESRIGeodatabaseConverter:
    """
    Converter for ESRI Mobile Geodatabase (SQLite) files

    This class handles the conversion of ESRI Mobile Geodatabase files to standard formats
    like GeoJSON, GeoPackage, DuckDB, or PostGIS schema. It extracts the geometry data from the binary format
    and converts it to standard WKB/WKT formats.
    """

    # ESRI geometry types
    ESRI_POINT = 1
    ESRI_MULTIPOINT = 2
    ESRI_POLYLINE = 3
    ESRI_POLYGON = 4

    # ESRI spatial reference IDs
    ESRI_WGS84 = 4326
    ESRI_WEB_MERCATOR = 3857

    # ESRI to PostGIS type mapping
    ESRI_TO_POSTGIS_TYPE_MAP = {
        "esriFieldTypeOID": "SERIAL PRIMARY KEY",
        "esriFieldTypeGlobalID": "UUID",
        "esriFieldTypeGUID": "UUID",
        "esriFieldTypeString": "VARCHAR",
        "esriFieldTypeInteger": "INTEGER",
        "esriFieldTypeSmallInteger": "SMALLINT",
        "esriFieldTypeBigInteger": "BIGINT",
        "esriFieldTypeSingle": "REAL",
        "esriFieldTypeDouble": "DOUBLE PRECISION",
        "esriFieldTypeDate": "TIMESTAMP",
        "esriFieldTypeBlob": "BYTEA",
        "esriFieldTypeRaster": "BYTEA",
        "esriFieldTypeXML": "XML",
        "esriFieldTypeGeometry": "GEOMETRY"
    }

    # ESRI geometry type to PostGIS geometry type mapping
    ESRI_TO_POSTGIS_GEOM_TYPE_MAP = {
        ESRI_POINT: "POINT",
        ESRI_MULTIPOINT: "MULTIPOINT",
        ESRI_POLYLINE: "MULTILINESTRING",
        ESRI_POLYGON: "MULTIPOLYGON"
    }

    @staticmethod
    def list_feature_classes(geodatabase_path: str) -> List[Dict[str, Any]]:
        """
        List all feature classes in an ESRI Mobile Geodatabase

        Args:
            geodatabase_path: Path to the ESRI Mobile Geodatabase file

        Returns:
            List of feature classes with metadata
        """
        if not os.path.exists(geodatabase_path):
            raise HTTPException(status_code=404, detail=f"Geodatabase file not found: {geodatabase_path}")

        try:
            # Connect to the SQLite database
            conn = sqlite3.connect(geodatabase_path)
            cursor = conn.cursor()

            # Check if this is an ESRI Geodatabase
            try:
                cursor.execute("SELECT * FROM GDB_Items LIMIT 1")
            except sqlite3.OperationalError:
                raise HTTPException(status_code=400, detail="Not a valid ESRI Mobile Geodatabase")

            # Get all feature classes
            cursor.execute("""
                SELECT GDB_Items.Name, GDB_Items.Type, GDB_Items.Path, GDB_ItemTypes.Name as TypeName
                FROM GDB_Items
                JOIN GDB_ItemTypes ON GDB_Items.Type = GDB_ItemTypes.UUID
                WHERE GDB_ItemTypes.Name = 'Feature Class'
            """)

            feature_classes = []
            for row in cursor.fetchall():
                name, type_id, path, type_name = row

                # Get feature class details
                try:
                    # Get the actual table name
                    table_name = f"{name}"

                    # Check if the table exists
                    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                    if not cursor.fetchone():
                        # Try with different casing
                        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND LOWER(name)=LOWER('{table_name}')")
                        result = cursor.fetchone()
                        if result:
                            table_name = result[0]
                        else:
                            continue

                    # Get column information
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = cursor.fetchall()

                    # Find geometry column
                    geometry_column = None
                    for col in columns:
                        col_name = col[1]
                        if col_name.lower() == 'shape':
                            geometry_column = col_name
                            break

                    # Get row count
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    row_count = cursor.fetchone()[0]

                    # Get spatial reference
                    spatial_ref_id = None
                    try:
                        cursor.execute(f"SELECT SRID FROM GDB_Items WHERE Name='{name}'")
                        result = cursor.fetchone()
                        if result:
                            spatial_ref_id = result[0]
                    except:
                        pass

                    # Get geometry type
                    geometry_type = None
                    try:
                        cursor.execute(f"SELECT GeometryType FROM GDB_GeomColumns WHERE TableName='{table_name}'")
                        result = cursor.fetchone()
                        if result:
                            geometry_type = result[0]
                    except:
                        # Try to determine from the first row
                        if geometry_column and row_count > 0:
                            cursor.execute(f"SELECT {geometry_column} FROM {table_name} LIMIT 1")
                            geom_blob = cursor.fetchone()[0]
                            if geom_blob:
                                try:
                                    # Parse the binary data to get geometry type
                                    geom_type = struct.unpack("<L", geom_blob[0:4])[0]
                                    if geom_type == ESRIGeodatabaseConverter.ESRI_POINT:
                                        geometry_type = "Point"
                                    elif geom_type == ESRIGeodatabaseConverter.ESRI_MULTIPOINT:
                                        geometry_type = "MultiPoint"
                                    elif geom_type == ESRIGeodatabaseConverter.ESRI_POLYLINE:
                                        geometry_type = "MultiLineString"
                                    elif geom_type == ESRIGeodatabaseConverter.ESRI_POLYGON:
                                        geometry_type = "MultiPolygon"
                                except:
                                    pass

                    feature_classes.append({
                        "name": name,
                        "table_name": table_name,
                        "type": type_name,
                        "path": path,
                        "geometry_column": geometry_column,
                        "geometry_type": geometry_type,
                        "spatial_reference_id": spatial_ref_id,
                        "column_count": len(columns),
                        "row_count": row_count,
                        "columns": [col[1] for col in columns]
                    })
                except Exception as e:
                    logger.warning(f"Error getting details for feature class {name}: {str(e)}")

            conn.close()
            return feature_classes

        except Exception as e:
            logger.error(f"Error listing feature classes: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error listing feature classes: {str(e)}")

    @staticmethod
    def parse_esri_geometry(geom_blob: bytes) -> Tuple[int, Any]:
        """
        Parse ESRI geometry binary data

        Args:
            geom_blob: Binary geometry data from ESRI Geodatabase

        Returns:
            Tuple of (geometry_type, shapely_geometry)
        """
        if not geom_blob:
            return (0, None)

        try:
            # Parse the binary data
            geom_type = struct.unpack("<L", geom_blob[0:4])[0]

            if geom_type == ESRIGeodatabaseConverter.ESRI_POINT:
                # Point: x, y, z, m (8 bytes each)
                x, y = struct.unpack("<dd", geom_blob[4:20])
                return (geom_type, Point(x, y))

            elif geom_type == ESRIGeodatabaseConverter.ESRI_MULTIPOINT:
                # MultiPoint: count, points
                count = struct.unpack("<L", geom_blob[4:8])[0]
                points = []
                for i in range(count):
                    offset = 8 + (i * 16)  # 16 bytes per point (x, y)
                    x, y = struct.unpack("<dd", geom_blob[offset:offset+16])
                    points.append((x, y))
                return (geom_type, MultiPoint(points))

            elif geom_type == ESRIGeodatabaseConverter.ESRI_POLYLINE:
                # Polyline: count, parts, points
                parts_count = struct.unpack("<L", geom_blob[4:8])[0]
                points_count = struct.unpack("<L", geom_blob[8:12])[0]

                # Read part indices
                parts = []
                for i in range(parts_count):
                    offset = 12 + (i * 4)
                    part_index = struct.unpack("<L", geom_blob[offset:offset+4])[0]
                    parts.append(part_index)

                # Read points
                points_offset = 12 + (parts_count * 4)
                points = []
                for i in range(points_count):
                    offset = points_offset + (i * 16)  # 16 bytes per point (x, y)
                    x, y = struct.unpack("<dd", geom_blob[offset:offset+16])
                    points.append((x, y))

                # Create line strings for each part
                lines = []
                for i in range(parts_count):
                    start_idx = parts[i]
                    end_idx = points_count if i == parts_count - 1 else parts[i+1]
                    part_points = points[start_idx:end_idx]
                    lines.append(LineString(part_points))

                return (geom_type, MultiLineString(lines))

            elif geom_type == ESRIGeodatabaseConverter.ESRI_POLYGON:
                # Polygon: count, parts, points
                parts_count = struct.unpack("<L", geom_blob[4:8])[0]
                points_count = struct.unpack("<L", geom_blob[8:12])[0]

                # Read part indices
                parts = []
                for i in range(parts_count):
                    offset = 12 + (i * 4)
                    part_index = struct.unpack("<L", geom_blob[offset:offset+4])[0]
                    parts.append(part_index)

                # Read points
                points_offset = 12 + (parts_count * 4)
                points = []
                for i in range(points_count):
                    offset = points_offset + (i * 16)  # 16 bytes per point (x, y)
                    x, y = struct.unpack("<dd", geom_blob[offset:offset+16])
                    points.append((x, y))

                # Create polygons for each part
                polygons = []
                for i in range(parts_count):
                    start_idx = parts[i]
                    end_idx = points_count if i == parts_count - 1 else parts[i+1]
                    part_points = points[start_idx:end_idx]
                    # Ensure the polygon is closed
                    if part_points[0] != part_points[-1]:
                        part_points.append(part_points[0])
                    polygons.append(Polygon(part_points))

                return (geom_type, MultiPolygon(polygons))

            else:
                # Unsupported geometry type
                return (geom_type, None)

        except Exception as e:
            logger.error(f"Error parsing ESRI geometry: {str(e)}")
            return (0, None)

    @staticmethod
    async def convert_to_geojson(
        geodatabase_path: str,
        feature_class_name: str,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convert an ESRI Mobile Geodatabase feature class to GeoJSON

        Args:
            geodatabase_path: Path to the ESRI Mobile Geodatabase file
            feature_class_name: Name of the feature class to convert
            output_path: Path to save the GeoJSON file (optional)

        Returns:
            Dictionary with information about the conversion
        """
        if not os.path.exists(geodatabase_path):
            raise HTTPException(status_code=404, detail=f"Geodatabase file not found: {geodatabase_path}")

        try:
            # Connect to the SQLite database
            conn = sqlite3.connect(geodatabase_path)
            cursor = conn.cursor()

            # Check if the feature class exists
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{feature_class_name}'")
            if not cursor.fetchone():
                # Try with different casing
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND LOWER(name)=LOWER('{feature_class_name}')")
                result = cursor.fetchone()
                if result:
                    feature_class_name = result[0]
                else:
                    raise HTTPException(status_code=404, detail=f"Feature class not found: {feature_class_name}")

            # Get column information
            cursor.execute(f"PRAGMA table_info({feature_class_name})")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]

            # Find geometry column
            geometry_column = None
            for col in columns:
                col_name = col[1]
                if col_name.lower() == 'shape':
                    geometry_column = col_name
                    break

            if not geometry_column:
                raise HTTPException(status_code=400, detail=f"No geometry column found in feature class: {feature_class_name}")

            # Get spatial reference
            spatial_ref_id = ESRIGeodatabaseConverter.ESRI_WGS84  # Default to WGS84
            try:
                cursor.execute(f"SELECT SRID FROM GDB_Items WHERE Name='{feature_class_name}'")
                result = cursor.fetchone()
                if result and result[0]:
                    spatial_ref_id = result[0]
            except:
                pass

            # Get all features
            cursor.execute(f"SELECT * FROM {feature_class_name}")
            rows = cursor.fetchall()

            # Create GeoJSON features
            features = []
            geometry_index = column_names.index(geometry_column)

            for row in rows:
                # Extract properties
                properties = {}
                for i, col_name in enumerate(column_names):
                    if i != geometry_index:
                        properties[col_name] = row[i]

                # Parse geometry
                geom_blob = row[geometry_index]
                if geom_blob:
                    geom_type, shapely_geom = ESRIGeodatabaseConverter.parse_esri_geometry(geom_blob)

                    if shapely_geom:
                        # Create GeoJSON feature
                        feature = {
                            "type": "Feature",
                            "properties": properties,
                            "geometry": json.loads(shapely_geom.wkt)
                        }
                        features.append(feature)

            # Create GeoJSON object
            geojson = {
                "type": "FeatureCollection",
                "features": features,
                "crs": {
                    "type": "name",
                    "properties": {
                        "name": f"EPSG:{spatial_ref_id}"
                    }
                }
            }

            # Save to file if output path provided
            if output_path:
                with open(output_path, 'w') as f:
                    json.dump(geojson, f)
            else:
                # Generate output path
                output_dir = GEOJSON_DIR
                output_filename = f"{feature_class_name}.geojson"
                output_path = os.path.join(output_dir, output_filename)

                with open(output_path, 'w') as f:
                    json.dump(geojson, f)

            conn.close()

            return {
                "feature_class": feature_class_name,
                "output_path": output_path,
                "feature_count": len(features),
                "spatial_reference_id": spatial_ref_id,
                "properties": list(properties.keys()) if features else []
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error converting to GeoJSON: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error converting to GeoJSON: {str(e)}")

    @staticmethod
    async def convert_to_gpkg(
        geodatabase_path: str,
        feature_class_names: List[str],
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convert ESRI Mobile Geodatabase feature classes to GeoPackage

        Args:
            geodatabase_path: Path to the ESRI Mobile Geodatabase file
            feature_class_names: List of feature class names to convert
            output_path: Path to save the GeoPackage file (optional)

        Returns:
            Dictionary with information about the conversion
        """
        if not os.path.exists(geodatabase_path):
            raise HTTPException(status_code=404, detail=f"Geodatabase file not found: {geodatabase_path}")

        try:
            # Generate output path if not provided
            if not output_path:
                output_dir = GPKG_DIR
                output_filename = f"{os.path.splitext(os.path.basename(geodatabase_path))[0]}.gpkg"
                output_path = os.path.join(output_dir, output_filename)

            # Create temporary directory for GeoJSON files
            temp_dir = tempfile.mkdtemp(dir=TEMP_DIR)

            # Convert each feature class to GeoJSON
            converted_classes = []
            for feature_class_name in feature_class_names:
                geojson_path = os.path.join(temp_dir, f"{feature_class_name}.geojson")

                # Convert to GeoJSON
                result = await ESRIGeodatabaseConverter.convert_to_geojson(
                    geodatabase_path=geodatabase_path,
                    feature_class_name=feature_class_name,
                    output_path=geojson_path
                )

                # Read GeoJSON with GeoPandas
                gdf = gpd.read_file(geojson_path)

                # Write to GeoPackage
                gdf.to_file(output_path, layer=feature_class_name, driver="GPKG")

                converted_classes.append({
                    "feature_class": feature_class_name,
                    "feature_count": result["feature_count"],
                    "spatial_reference_id": result["spatial_reference_id"]
                })

            return {
                "output_path": output_path,
                "converted_classes": converted_classes,
                "class_count": len(converted_classes)
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error converting to GeoPackage: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error converting to GeoPackage: {str(e)}")

    @staticmethod
    async def convert_to_duckdb(
        geodatabase_path: str,
        feature_class_names: List[str],
        db_name: str,
        spatial_index: bool = True,
        overwrite: bool = False
    ) -> Dict[str, Any]:
        """
        Convert ESRI Mobile Geodatabase feature classes to DuckDB

        Args:
            geodatabase_path: Path to the ESRI Mobile Geodatabase file
            feature_class_names: List of feature class names to convert
            db_name: Name for the DuckDB database
            spatial_index: Whether to create spatial indexes
            overwrite: Whether to overwrite existing tables

        Returns:
            Dictionary with information about the conversion
        """
        if not os.path.exists(geodatabase_path):
            raise HTTPException(status_code=404, detail=f"Geodatabase file not found: {geodatabase_path}")

        try:
            # Sanitize database name
            safe_name = "".join(c if c.isalnum() or c in ['-', '_'] else '_' for c in db_name)
            db_path = os.path.join(DUCKDB_DIR, f"{safe_name}.duckdb")

            # Check if database exists
            db_exists = os.path.exists(db_path)

            # Create temporary directory for GeoJSON files
            temp_dir = tempfile.mkdtemp(dir=TEMP_DIR)

            # Connect to DuckDB
            conn = duckdb.connect(db_path)

            # Install and load extensions
            conn.execute("INSTALL spatial;")
            conn.execute("LOAD spatial;")

            # Convert each feature class
            converted_classes = []
            for feature_class_name in feature_class_names:
                # Check if table exists
                table_exists = False
                try:
                    conn.execute(f"SELECT * FROM {feature_class_name} LIMIT 0")
                    table_exists = True
                except:
                    pass

                if table_exists and not overwrite:
                    logger.warning(f"Table {feature_class_name} already exists and overwrite=False")
                    converted_classes.append({
                        "feature_class": feature_class_name,
                        "status": "skipped",
                        "reason": "Table already exists"
                    })
                    continue

                # Drop table if it exists and overwrite is True
                if table_exists and overwrite:
                    conn.execute(f"DROP TABLE IF EXISTS {feature_class_name}")

                # Convert to GeoJSON
                geojson_path = os.path.join(temp_dir, f"{feature_class_name}.geojson")
                result = await ESRIGeodatabaseConverter.convert_to_geojson(
                    geodatabase_path=geodatabase_path,
                    feature_class_name=feature_class_name,
                    output_path=geojson_path
                )

                # Import GeoJSON to DuckDB
                conn.execute(f"""
                    CREATE TABLE {feature_class_name} AS
                    SELECT * FROM ST_Read('{geojson_path}')
                """)

                # Create spatial index if requested
                if spatial_index:
                    try:
                        conn.execute(f"""
                            CREATE SPATIAL INDEX ON {feature_class_name} (geometry);
                        """)
                    except Exception as e:
                        logger.warning(f"Could not create spatial index on {feature_class_name}: {str(e)}")

                converted_classes.append({
                    "feature_class": feature_class_name,
                    "feature_count": result["feature_count"],
                    "spatial_reference_id": result["spatial_reference_id"],
                    "status": "imported"
                })

            # Close connection
            conn.close()

            return {
                "database_name": safe_name,
                "database_path": db_path,
                "database_exists": db_exists,
                "converted_classes": converted_classes,
                "class_count": len(converted_classes)
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error converting to DuckDB: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error converting to DuckDB: {str(e)}")

    @staticmethod
    async def convert_to_postgis_schema(
        geodatabase_path: str,
        feature_class_names: List[str],
        schema_name: Optional[str] = None,
        spatial_index: bool = True,
        drop_if_exists: bool = False,
        include_comments: bool = True
    ) -> Dict[str, Any]:
        """
        Convert ESRI Mobile Geodatabase feature classes to PostGIS schema SQL

        Args:
            geodatabase_path: Path to the ESRI Mobile Geodatabase file
            feature_class_names: List of feature class names to convert
            schema_name: PostgreSQL schema name (optional)
            spatial_index: Whether to create spatial indexes
            drop_if_exists: Whether to include DROP TABLE statements
            include_comments: Whether to include comments in the SQL

        Returns:
            Dictionary with SQL statements and information about the conversion
        """
        if not os.path.exists(geodatabase_path):
            raise HTTPException(status_code=404, detail=f"Geodatabase file not found: {geodatabase_path}")

        try:
            # Connect to the SQLite database
            conn = sqlite3.connect(geodatabase_path)
            cursor = conn.cursor()

            # Check if this is an ESRI Geodatabase
            try:
                cursor.execute("SELECT * FROM GDB_Items LIMIT 1")
            except sqlite3.OperationalError:
                raise HTTPException(status_code=400, detail="Not a valid ESRI Mobile Geodatabase")

            # Get ESRI field types
            field_types = {}
            try:
                cursor.execute("SELECT Name, FieldType FROM GDB_FieldInfo")
                for row in cursor.fetchall():
                    field_name, field_type = row
                    field_types[field_name] = field_type
            except sqlite3.OperationalError:
                # GDB_FieldInfo table might not exist in all geodatabases
                pass

            # Generate SQL statements
            sql_statements = []
            table_statements = []
            index_statements = []
            comment_statements = []

            # Add schema creation if provided
            if schema_name:
                sql_statements.append(f"-- Create schema if it doesn't exist\nCREATE SCHEMA IF NOT EXISTS {schema_name};\n")

            # Process each feature class
            converted_classes = []
            for feature_class_name in feature_class_names:
                # Check if the feature class exists
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{feature_class_name}'")
                if not cursor.fetchone():
                    # Try with different casing
                    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND LOWER(name)=LOWER('{feature_class_name}')")
                    result = cursor.fetchone()
                    if result:
                        feature_class_name = result[0]
                    else:
                        logger.warning(f"Feature class not found: {feature_class_name}")
                        continue

                # Get column information
                cursor.execute(f"PRAGMA table_info({feature_class_name})")
                columns = cursor.fetchall()

                # Find geometry column
                geometry_column = None
                for col in columns:
                    col_name = col[1]
                    if col_name.lower() == 'shape':
                        geometry_column = col_name
                        break

                if not geometry_column:
                    logger.warning(f"No geometry column found in feature class: {feature_class_name}")
                    continue

                # Get spatial reference
                spatial_ref_id = ESRIGeodatabaseConverter.ESRI_WGS84  # Default to WGS84
                try:
                    cursor.execute(f"SELECT SRID FROM GDB_Items WHERE Name='{feature_class_name}'")
                    result = cursor.fetchone()
                    if result and result[0]:
                        spatial_ref_id = result[0]
                except:
                    pass

                # Get geometry type
                geometry_type = "GEOMETRY"
                try:
                    cursor.execute(f"SELECT GeometryType FROM GDB_GeomColumns WHERE TableName='{feature_class_name}'")
                    result = cursor.fetchone()
                    if result and result[0]:
                        esri_geom_type = result[0]
                        # Map ESRI geometry type to PostGIS geometry type
                        if esri_geom_type == 1:  # Point
                            geometry_type = "POINT"
                        elif esri_geom_type == 2:  # Multipoint
                            geometry_type = "MULTIPOINT"
                        elif esri_geom_type == 3:  # Polyline
                            geometry_type = "MULTILINESTRING"
                        elif esri_geom_type == 4:  # Polygon
                            geometry_type = "MULTIPOLYGON"
                except:
                    # Try to determine from the first row
                    if geometry_column:
                        try:
                            cursor.execute(f"SELECT {geometry_column} FROM {feature_class_name} LIMIT 1")
                            geom_blob = cursor.fetchone()
                            if geom_blob and geom_blob[0]:
                                # Parse the binary data to get geometry type
                                geom_type = struct.unpack("<L", geom_blob[0][0:4])[0]
                                geometry_type = ESRIGeodatabaseConverter.ESRI_TO_POSTGIS_GEOM_TYPE_MAP.get(geom_type, "GEOMETRY")
                        except:
                            pass

                # Generate table name
                table_name = feature_class_name
                if schema_name:
                    table_name = f"{schema_name}.{feature_class_name}"

                # Start building CREATE TABLE statement
                if drop_if_exists:
                    table_sql = f"-- Drop table if it exists\nDROP TABLE IF EXISTS {table_name};\n\n"
                else:
                    table_sql = ""

                table_sql += f"-- Create table for feature class {feature_class_name}\nCREATE TABLE {table_name} (\n"

                # Add columns
                column_defs = []
                primary_key = None

                for col in columns:
                    col_id, col_name, col_type, col_notnull, col_default, col_pk = col

                    # Skip geometry column, we'll add it with AddGeometryColumn
                    if col_name == geometry_column:
                        continue

                    # Determine PostgreSQL data type
                    pg_type = "TEXT"  # Default to TEXT

                    # Check if this is a primary key
                    if col_pk == 1:
                        primary_key = col_name
                        pg_type = "SERIAL PRIMARY KEY"
                    else:
                        # Map SQLite type to PostgreSQL type
                        if col_type.upper() == "INTEGER":
                            pg_type = "INTEGER"
                        elif col_type.upper() == "REAL":
                            pg_type = "DOUBLE PRECISION"
                        elif col_type.upper() == "TEXT":
                            pg_type = "TEXT"
                        elif col_type.upper() == "BLOB":
                            pg_type = "BYTEA"

                        # Check if we have more specific ESRI field type information
                        if col_name in field_types:
                            esri_type = field_types[col_name]
                            pg_type = ESRIGeodatabaseConverter.ESRI_TO_POSTGIS_TYPE_MAP.get(esri_type, pg_type)

                    # Add NOT NULL constraint if needed
                    if col_notnull == 1 and col_pk != 1:
                        pg_type += " NOT NULL"

                    # Add default value if provided
                    if col_default is not None and col_pk != 1:
                        pg_type += f" DEFAULT {col_default}"

                    column_defs.append(f"    {col_name} {pg_type}")

                # Add column definitions to table SQL
                table_sql += ",\n".join(column_defs)
                table_sql += "\n);\n"

                # Add AddGeometryColumn statement
                table_sql += f"\n-- Add geometry column\nSELECT AddGeometryColumn('{schema_name or 'public'}', '{feature_class_name}', '{geometry_column}', {spatial_ref_id}, '{geometry_type}', 2);\n"

                # Add spatial index if requested
                if spatial_index:
                    index_sql = f"\n-- Create spatial index\nCREATE INDEX idx_{feature_class_name}_geom ON {table_name} USING GIST ({geometry_column});\n"
                    index_statements.append(index_sql)

                # Add comments if requested
                if include_comments:
                    comment_sql = f"\n-- Add table comment\nCOMMENT ON TABLE {table_name} IS 'Converted from ESRI Geodatabase feature class {feature_class_name}';\n"
                    comment_sql += f"COMMENT ON COLUMN {table_name}.{geometry_column} IS 'Geometry column with type {geometry_type} and SRID {spatial_ref_id}';\n"
                    comment_statements.append(comment_sql)

                # Add to table statements
                table_statements.append(table_sql)

                # Add to converted classes
                converted_classes.append({
                    "feature_class": feature_class_name,
                    "table_name": table_name,
                    "geometry_column": geometry_column,
                    "geometry_type": geometry_type,
                    "spatial_reference_id": spatial_ref_id,
                    "column_count": len(columns) - 1,  # Exclude geometry column
                    "primary_key": primary_key
                })

            # Combine all SQL statements
            sql_statements.extend(table_statements)
            sql_statements.extend(index_statements)
            sql_statements.extend(comment_statements)

            # Generate complete SQL
            complete_sql = "\n".join(sql_statements)

            # Close connection
            conn.close()

            return {
                "sql": complete_sql,
                "converted_classes": converted_classes,
                "class_count": len(converted_classes),
                "schema_name": schema_name or "public"
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error converting to PostGIS schema: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error converting to PostGIS schema: {str(e)}")

    @staticmethod
    async def convert_remote_geodatabase(
        remote_path: str,
        feature_class_names: List[str] = None,
        output_format: str = "geojson",
        output_path: Optional[str] = None,
        schema_name: Optional[str] = None,
        spatial_index: bool = True,
        drop_if_exists: bool = False,
        include_comments: bool = True
    ) -> Dict[str, Any]:
        """
        Convert a remote ESRI Mobile Geodatabase to the specified format

        Args:
            remote_path: Remote path in the format 'remote:path/to/file.geodatabase'
            feature_class_names: List of feature class names to convert (if None, all will be converted)
            output_format: Output format ('geojson', 'gpkg', 'duckdb', or 'postgis_schema')
            output_path: Path for the output file (optional)
            schema_name: PostgreSQL schema name (for postgis_schema format)
            spatial_index: Whether to create spatial indexes
            drop_if_exists: Whether to include DROP TABLE statements (for postgis_schema format)
            include_comments: Whether to include comments in the SQL (for postgis_schema format)

        Returns:
            Dictionary with information about the conversion
        """
        if rclone_service is None:
            raise HTTPException(status_code=500, detail="Rclone service not available. Cannot convert remote geodatabase.")

        try:
            # Download the geodatabase
            download_result = await rclone_service.download_file(remote_path)

            if not download_result["success"]:
                raise HTTPException(status_code=500, detail=f"Failed to download geodatabase: {download_result.get('error', 'Unknown error')}")

            local_path = download_result["local_path"]

            # List feature classes if not provided
            if feature_class_names is None:
                feature_classes = ESRIGeodatabaseConverter.list_feature_classes(local_path)
                feature_class_names = [fc["name"] for fc in feature_classes]

            # Perform the conversion based on the output format
            if output_format == "geojson":
                if len(feature_class_names) != 1:
                    raise HTTPException(status_code=400, detail="GeoJSON format requires exactly one feature class")

                result = await ESRIGeodatabaseConverter.convert_to_geojson(
                    geodatabase_path=local_path,
                    feature_class_name=feature_class_names[0],
                    output_path=output_path
                )
            elif output_format == "gpkg":
                result = await ESRIGeodatabaseConverter.convert_to_gpkg(
                    geodatabase_path=local_path,
                    feature_class_names=feature_class_names,
                    output_path=output_path
                )
            elif output_format == "duckdb":
                # Generate a database name from the remote path
                db_name = os.path.basename(remote_path).split(".")[0]

                result = await ESRIGeodatabaseConverter.convert_to_duckdb(
                    geodatabase_path=local_path,
                    feature_class_names=feature_class_names,
                    db_name=db_name,
                    spatial_index=spatial_index
                )
            elif output_format == "postgis_schema":
                result = await ESRIGeodatabaseConverter.convert_to_postgis_schema(
                    geodatabase_path=local_path,
                    feature_class_names=feature_class_names,
                    schema_name=schema_name,
                    spatial_index=spatial_index,
                    drop_if_exists=drop_if_exists,
                    include_comments=include_comments
                )
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported output format: {output_format}")

            # Add information about the remote source
            result["remote_source"] = {
                "path": remote_path,
                "local_path": local_path
            }

            return result
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error converting remote geodatabase: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error converting remote geodatabase: {str(e)}")
