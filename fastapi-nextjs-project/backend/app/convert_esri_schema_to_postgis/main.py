"""Main module for the core functionality."""
from osgeo import ogr
import os
import asyncio
import logging
from typing import Dict, List, Any, Optional

# Import the ESRIGeodatabaseConverter
try:
    from app.services.esri_geodatabase_converter import ESRIGeodatabaseConverter
except ImportError:
    # For standalone usage
    ESRIGeodatabaseConverter = None

logger = logging.getLogger(__name__)

class Report:
    """
    This class is responsible for generating a report of the conversion process.
    """

    def __init__(self):
        """Initialize the Report with an empty list of messages."""
        self.messages = []

    def add_message(self, message):
        """
        Add a message to the report.
        Args:
            message (str): The message to add to the report.
        """
        self.messages.append(message)
        logger.info(message)

    def generate_report(self):
        """
        Generate a string with all the messages in the report, one message per line.
        Returns:
            str: A string with all the messages in the report, each on a new line.
        """
        return "\n".join(self.messages)
class FileAgent:
    """
    This class is responsible for handling FileGDB files.
    """
    def __init__(self):
        """
        Initialize the FileAgent with a Report instance.
        """
        self.report = Report()

    def handle(self, file_path):
        """
        Handle a FileGDB file.
        Args:
            file_path (str): The path to the FileGDB file.
        Returns:
            dict: Dictionary with feature class information.
        """
        if not os.path.exists(file_path):
            self.report.add_message(f"Error: File not found: {file_path}")
            return {}

        self.report.add_message(f"Attempting to handle FileGDB: {file_path}")

        try:
            # Try using ESRIGeodatabaseConverter if available
            if ESRIGeodatabaseConverter is not None:
                # List feature classes in the geodatabase
                feature_classes = ESRIGeodatabaseConverter.list_feature_classes(file_path)
                self.report.add_message(f"Found {len(feature_classes)} feature classes using ESRIGeodatabaseConverter")

                return {
                    "file_path": file_path,
                    "feature_classes": feature_classes
                }
            else:
                # Fallback to using ogr directly
                driver = ogr.GetDriverByName("OpenFileGDB")
                data_source = driver.Open(file_path, 0)

                if data_source is None:
                    self.report.add_message(f"Error: Could not open FileGDB: {file_path}")
                    return {}

                # Get layer count
                layer_count = data_source.GetLayerCount()
                self.report.add_message(f"Found {layer_count} layers in FileGDB")

                # Get layer names
                feature_classes = []
                for i in range(layer_count):
                    layer = data_source.GetLayerByIndex(i)
                    feature_classes.append(layer.GetName())

                self.report.add_message(f"Successfully handled FileGDB: {file_path}")

                return {
                    "file_path": file_path,
                    "feature_classes": feature_classes
                }
        except Exception as e:
            self.report.add_message(f"Error: Could not handle FileGDB: {file_path}. {str(e)}")
            return {}

    def get_report(self):
        """
        Get the conversion report and clear the internal messages.
        Returns:
            str: The conversion report as a string.
        """
        report_str = self.report.generate_report()
        self.report.messages = []
        return report_str

class PostgisAgent():
    """
    Agent for handling PostGIS operations.
    """
    def __init__(self, schema_name=None, spatial_index=True, drop_if_exists=False, include_comments=True):
        """
        Initialize the PostgisAgent with a Report instance.

        Args:
            schema_name (str, optional): PostgreSQL schema name. Defaults to None.
            spatial_index (bool, optional): Whether to create spatial indexes. Defaults to True.
            drop_if_exists (bool, optional): Whether to include DROP TABLE statements. Defaults to False.
            include_comments (bool, optional): Whether to include comments in the SQL. Defaults to True.
        """
        self.report = Report()
        self.schema_name = schema_name
        self.spatial_index = spatial_index
        self.drop_if_exists = drop_if_exists
        self.include_comments = include_comments

    async def handle_async(self, file_agent_result):
        """
        Generate PostGIS schema from FileGDB data asynchronously.

        Args:
            file_agent_result (dict): Result from FileAgent.handle()

        Returns:
            str: SQL statements for creating PostGIS schema
        """
        try:
            # Check if we have a valid file agent result
            if not file_agent_result or "file_path" not in file_agent_result or "feature_classes" not in file_agent_result:
                self.report.add_message("Error: Invalid file agent result")
                return "-- Error: Invalid file agent result"

            # Extract information from file agent result
            geodatabase_path = file_agent_result["file_path"]
            feature_classes = file_agent_result["feature_classes"]

            if not feature_classes:
                self.report.add_message("Error: No feature classes found in the geodatabase")
                return "-- Error: No feature classes found in the geodatabase"

            self.report.add_message(f"Attempting to create PostGIS schema for {len(feature_classes)} feature classes...")

            # Check if ESRIGeodatabaseConverter is available
            if ESRIGeodatabaseConverter is not None:
                # Convert to PostGIS schema
                result = await ESRIGeodatabaseConverter.convert_to_postgis_schema(
                    geodatabase_path=geodatabase_path,
                    feature_class_names=feature_classes,
                    schema_name=self.schema_name,
                    spatial_index=self.spatial_index,
                    drop_if_exists=self.drop_if_exists,
                    include_comments=self.include_comments
                )

                self.report.add_message(f"Successfully created PostGIS schema for {result['class_count']} feature classes")
                return result["sql"]
            else:
                self.report.add_message("Error: ESRIGeodatabaseConverter is not available")
                return self.handle(file_agent_result)  # Fall back to synchronous method
        except Exception as e:
            self.report.add_message(f"Error generating PostGIS schema: {str(e)}")
            return f"-- Error generating PostGIS schema: {str(e)}"

    def handle(self, file_agent_result=None) -> str:
        """
        Create the PostGIS schema.

        Args:
            file_agent_result (dict, optional): Result from FileAgent.handle(). Defaults to None.

        Returns:
            str: The SQL code for the PostGIS schema.
        """
        self.report.add_message("Attempting to create PostGIS schema...")

        # If we have file agent result, try to generate schema based on it
        if file_agent_result and "feature_classes" in file_agent_result and file_agent_result["feature_classes"]:
            feature_classes = file_agent_result["feature_classes"]

            # Generate a basic schema for each feature class
            sql_parts = []

            # Add schema creation if provided
            if self.schema_name:
                sql_parts.append(f"-- Create schema if it doesn't exist\nCREATE SCHEMA IF NOT EXISTS {self.schema_name};\n")

            # Process each feature class
            for feature_class in feature_classes:
                table_name = feature_class
                if self.schema_name:
                    table_name = f"{self.schema_name}.{feature_class}"

                # Start building CREATE TABLE statement
                if self.drop_if_exists:
                    sql_parts.append(f"-- Drop table if it exists\nDROP TABLE IF EXISTS {table_name};\n")

                sql_parts.append(f"-- Create table for feature class {feature_class}\nCREATE TABLE {table_name} (\n")
                sql_parts.append("    id SERIAL PRIMARY KEY,\n")
                sql_parts.append("    name TEXT,\n")
                sql_parts.append("    description TEXT\n")
                sql_parts.append(");\n")

                # Add geometry column
                sql_parts.append(f"\n-- Add geometry column\nSELECT AddGeometryColumn('{self.schema_name or 'public'}', '{feature_class}', 'geom', 4326, 'GEOMETRY', 2);\n")

                # Add spatial index if requested
                if self.spatial_index:
                    sql_parts.append(f"\n-- Create spatial index\nCREATE INDEX idx_{feature_class}_geom ON {table_name} USING GIST (geom);\n")

                # Add comments if requested
                if self.include_comments:
                    sql_parts.append(f"\n-- Add table comment\nCOMMENT ON TABLE {table_name} IS 'Converted from ESRI Geodatabase feature class {feature_class}';\n")
                    sql_parts.append(f"COMMENT ON COLUMN {table_name}.geom IS 'Geometry column with SRID 4326';\n")

            sql = "\n".join(sql_parts)
            self.report.add_message(f"Successfully created PostGIS schema for {len(feature_classes)} feature classes")
            return sql
        else:
            # Fallback to a dummy table
            sql = "-- No feature classes provided, creating a dummy table\n"

            if self.schema_name:
                sql += f"CREATE SCHEMA IF NOT EXISTS {self.schema_name};\n\n"
                sql += f"CREATE TABLE {self.schema_name}.dummy_table (id SERIAL PRIMARY KEY, name TEXT, geom geometry(Geometry, 4326));"
            else:
                sql += "CREATE TABLE dummy_table (id SERIAL PRIMARY KEY, name TEXT, geom geometry(Geometry, 4326));"

            self.report.add_message("Created a dummy PostGIS schema (no feature classes provided)")
            return sql

    def get_report(self) -> str:
        """
        Get the conversion report and clear the internal messages.

        Returns:
            str: The conversion report as a string.
        """
        report_str = self.report.generate_report()
        self.report.messages = []
        return report_str

