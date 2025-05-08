import os
import json
import logging
import tempfile
import uuid
import shutil
import pandas as pd
import geopandas as gpd
import duckdb
from typing import Dict, List, Any, Optional, Union, Tuple, BinaryIO
from pathlib import Path
from datetime import datetime

from app.core.duckdb_config import duckdb_config

logger = logging.getLogger(__name__)

class DuckDBService:
    """Service for interacting with DuckDB."""

    def __init__(self):
        """Initialize the DuckDB service."""
        self.data_dir = duckdb_config.data_dir
        self.temp_dir = duckdb_config.temp_dir
        self.memory_limit = duckdb_config.memory_limit
        self.extensions = duckdb_config.extensions

        # Create directories if they don't exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)

        # Initialize connection pool
        self.connections = {}

    def get_connection(self, db_path: Optional[str] = None) -> duckdb.DuckDBPyConnection:
        """
        Get a DuckDB connection.

        Args:
            db_path: Path to the database file (optional, uses in-memory database if not provided)

        Returns:
            DuckDB connection
        """
        # Generate a connection key
        conn_key = db_path or ":memory:"

        # Check if connection already exists
        if conn_key in self.connections:
            return self.connections[conn_key]

        # Create a new connection
        if db_path:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
            conn = duckdb.connect(db_path)
        else:
            conn = duckdb.connect(":memory:")

        # Configure the connection
        conn.execute(f"SET memory_limit='{self.memory_limit}'")
        conn.execute(f"SET temp_directory='{self.temp_dir}'")

        # Load extensions
        for extension in self.extensions:
            try:
                conn.execute(f"INSTALL {extension}")
                conn.execute(f"LOAD {extension}")
            except Exception as e:
                logger.warning(f"Failed to load extension {extension}: {str(e)}")

        # Configure cloud storage if available
        if duckdb_config.is_s3_configured:
            conn.execute(f"SET s3_region='{duckdb_config.s3_region}'")
            conn.execute(f"SET s3_access_key_id='{duckdb_config.s3_access_key_id}'")
            conn.execute(f"SET s3_secret_access_key='{duckdb_config.s3_secret_access_key}'")

        # Configure HostFS if available
        try:
            if "hostfs" in self.extensions:
                # Set allowed directories for security
                allowed_dirs = [
                    os.path.abspath(self.data_dir),
                    os.path.abspath(self.temp_dir),
                    os.path.abspath(os.path.join(os.getcwd(), "data")),
                    os.path.abspath(os.path.join(os.getcwd(), "uploads"))
                ]

                # Add environment variable defined directories if available
                hostfs_allowed_dirs = os.environ.get("HOSTFS_ALLOWED_DIRS", "")
                if hostfs_allowed_dirs:
                    allowed_dirs.extend([os.path.abspath(d.strip()) for d in hostfs_allowed_dirs.split(",")])

                # Set allowed directories
                for directory in allowed_dirs:
                    if os.path.exists(directory):
                        conn.execute(f"CALL hostfs_allow_directory('{directory}')")
                        logger.info(f"HostFS allowed directory: {directory}")
        except Exception as e:
            logger.warning(f"Failed to configure HostFS: {str(e)}")

        if duckdb_config.is_azure_configured:
            conn.execute(f"SET azure_storage_account='{duckdb_config.azure_storage_account}'")
            conn.execute(f"SET azure_storage_key='{duckdb_config.azure_storage_key}'")

        if duckdb_config.is_gcs_configured:
            conn.execute(f"SET gcs_project_id='{duckdb_config.gcs_project_id}'")
            conn.execute(f"SET gcs_credentials_path='{duckdb_config.gcs_credentials_path}'")

        # Configure Nanodbc if available
        try:
            if "nanodbc" in self.extensions:
                # Set ODBC driver paths if configured
                if duckdb_config.odbc_driver_paths:
                    conn.execute(f"SET odbc_driver_paths='{duckdb_config.odbc_driver_paths}'")
                    logger.info(f"Nanodbc driver paths set: {duckdb_config.odbc_driver_paths}")

                # Create connections for predefined ODBC data sources
                for name, connection_string in duckdb_config.odbc_connections.items():
                    try:
                        conn.execute(f"ATTACH '{connection_string}' AS {name} (TYPE ODBC)")
                        logger.info(f"Nanodbc connection created: {name}")
                    except Exception as e:
                        logger.warning(f"Failed to create Nanodbc connection {name}: {str(e)}")
        except Exception as e:
            logger.warning(f"Failed to configure Nanodbc: {str(e)}")

        # Store the connection
        self.connections[conn_key] = conn

        return conn

    def close_connection(self, db_path: Optional[str] = None):
        """
        Close a DuckDB connection.

        Args:
            db_path: Path to the database file (optional, uses in-memory database if not provided)
        """
        conn_key = db_path or ":memory:"

        if conn_key in self.connections:
            self.connections[conn_key].close()
            del self.connections[conn_key]

    def close_all_connections(self):
        """Close all DuckDB connections."""
        for conn in self.connections.values():
            conn.close()

        self.connections = {}

    def execute_query(self, query: str, db_path: Optional[str] = None, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a SQL query.

        Args:
            query: SQL query to execute
            db_path: Path to the database file (optional)
            params: Query parameters (optional)

        Returns:
            Query results as a list of dictionaries
        """
        conn = self.get_connection(db_path)

        try:
            # Execute the query
            if params:
                result = conn.execute(query, params).fetchdf()
            else:
                result = conn.execute(query).fetchdf()

            # Convert to list of dictionaries
            return result.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise

    def execute_query_df(self, query: str, db_path: Optional[str] = None, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Execute a SQL query and return the results as a pandas DataFrame.

        Args:
            query: SQL query to execute
            db_path: Path to the database file (optional)
            params: Query parameters (optional)

        Returns:
            Query results as a pandas DataFrame
        """
        conn = self.get_connection(db_path)

        try:
            # Execute the query
            if params:
                result = conn.execute(query, params).fetchdf()
            else:
                result = conn.execute(query).fetchdf()

            return result
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise

    def execute_query_geo_df(self, query: str, db_path: Optional[str] = None, params: Optional[Dict[str, Any]] = None) -> gpd.GeoDataFrame:
        """
        Execute a SQL query and return the results as a GeoPandas GeoDataFrame.

        Args:
            query: SQL query to execute
            db_path: Path to the database file (optional)
            params: Query parameters (optional)

        Returns:
            Query results as a GeoPandas GeoDataFrame
        """
        conn = self.get_connection(db_path)

        try:
            # Execute the query
            if params:
                result = conn.execute(query, params).fetchdf()
            else:
                result = conn.execute(query).fetchdf()

            # Convert to GeoDataFrame
            if 'geometry' in result.columns:
                return gpd.GeoDataFrame(result, geometry='geometry')
            else:
                logger.warning("Query result does not contain a geometry column")
                return gpd.GeoDataFrame(result)
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise

    def create_table_from_file(self, file_path: str, table_name: str, db_path: Optional[str] = None, use_hostfs: bool = False) -> bool:
        """
        Create a table from a file.

        Args:
            file_path: Path to the file
            table_name: Name of the table to create
            db_path: Path to the database file (optional)
            use_hostfs: Whether to use HostFS to access the file

        Returns:
            True if successful, False otherwise
        """
        conn = self.get_connection(db_path)

        try:
            # Determine the file type
            file_ext = os.path.splitext(file_path)[1].lower()

            # Prepare the file path (use hostfs_file_path if requested)
            path_expr = f"hostfs_file_path('{file_path}')" if use_hostfs else f"'{file_path}'"

            # Create the table based on the file type
            if file_ext in ['.csv', '.txt']:
                conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM read_csv({path_expr}, auto_detect=TRUE)")
            elif file_ext == '.parquet':
                conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM read_parquet({path_expr})")
            elif file_ext == '.json':
                conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM read_json({path_expr}, auto_detect=TRUE)")
            elif file_ext in ['.xls', '.xlsx']:
                conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM read_excel({path_expr})")
            elif file_ext == '.shp':
                conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM ST_Read({path_expr})")
            elif file_ext == '.gpkg':
                conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM ST_Read({path_expr})")
            elif file_ext == '.geojson':
                conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM ST_Read({path_expr})")
            else:
                logger.error(f"Unsupported file type: {file_ext}")
                return False

            return True
        except Exception as e:
            logger.error(f"Error creating table from file: {str(e)}")
            return False

    def create_table_from_dataframe(self, df: Union[pd.DataFrame, gpd.GeoDataFrame], table_name: str, db_path: Optional[str] = None) -> bool:
        """
        Create a table from a pandas DataFrame or GeoPandas GeoDataFrame.

        Args:
            df: DataFrame or GeoDataFrame
            table_name: Name of the table to create
            db_path: Path to the database file (optional)

        Returns:
            True if successful, False otherwise
        """
        conn = self.get_connection(db_path)

        try:
            # Register the DataFrame as a view
            conn.register(table_name, df)

            # Create a table from the view
            conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM {table_name}")

            return True
        except Exception as e:
            logger.error(f"Error creating table from DataFrame: {str(e)}")
            return False

    def create_table_from_uploaded_file(self, file: BinaryIO, file_name: str, table_name: str, db_path: Optional[str] = None) -> bool:
        """
        Create a table from an uploaded file.

        Args:
            file: File object
            file_name: Original file name
            table_name: Name of the table to create
            db_path: Path to the database file (optional)

        Returns:
            True if successful, False otherwise
        """
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp(dir=self.temp_dir)

        try:
            # Save the file to the temporary directory
            file_path = os.path.join(temp_dir, file_name)

            with open(file_path, 'wb') as f:
                f.write(file.read())

            # Create the table
            result = self.create_table_from_file(file_path, table_name, db_path)

            return result
        except Exception as e:
            logger.error(f"Error creating table from uploaded file: {str(e)}")
            return False
        finally:
            # Clean up the temporary directory
            shutil.rmtree(temp_dir)

    def export_table(self, table_name: str, output_format: str, output_path: Optional[str] = None, db_path: Optional[str] = None) -> Optional[str]:
        """
        Export a table to a file.

        Args:
            table_name: Name of the table to export
            output_format: Output format (csv, parquet, json, geojson, etc.)
            output_path: Path to the output file (optional)
            db_path: Path to the database file (optional)

        Returns:
            Path to the exported file, or None if export failed
        """
        conn = self.get_connection(db_path)

        try:
            # Generate a default output path if not provided
            if not output_path:
                output_dir = os.path.join(self.data_dir, 'exports')
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, f"{table_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{output_format}")

            # Export the table based on the output format
            if output_format == 'csv':
                conn.execute(f"COPY {table_name} TO '{output_path}' (FORMAT CSV, HEADER)")
            elif output_format == 'parquet':
                conn.execute(f"COPY {table_name} TO '{output_path}' (FORMAT PARQUET)")
            elif output_format == 'json':
                conn.execute(f"COPY {table_name} TO '{output_path}' (FORMAT JSON)")
            elif output_format in ['geojson', 'shp', 'gpkg']:
                # For geospatial formats, we need to use GeoPandas
                df = self.execute_query_df(f"SELECT * FROM {table_name}", db_path)

                # Check if the table has a geometry column
                if 'geometry' in df.columns:
                    gdf = gpd.GeoDataFrame(df, geometry='geometry')

                    if output_format == 'geojson':
                        gdf.to_file(output_path, driver='GeoJSON')
                    elif output_format == 'shp':
                        gdf.to_file(output_path, driver='ESRI Shapefile')
                    elif output_format == 'gpkg':
                        gdf.to_file(output_path, driver='GPKG')
                else:
                    logger.warning(f"Table {table_name} does not have a geometry column")
                    return None
            else:
                logger.error(f"Unsupported output format: {output_format}")
                return None

            return output_path
        except Exception as e:
            logger.error(f"Error exporting table: {str(e)}")
            return None

    def get_table_schema(self, table_name: str, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get the schema of a table.

        Args:
            table_name: Name of the table
            db_path: Path to the database file (optional)

        Returns:
            Table schema as a list of dictionaries
        """
        conn = self.get_connection(db_path)

        try:
            # Get the table schema
            result = conn.execute(f"PRAGMA table_info({table_name})").fetchdf()

            # Convert to list of dictionaries
            return result.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Error getting table schema: {str(e)}")
            raise

    def get_tables(self, db_path: Optional[str] = None) -> List[str]:
        """
        Get a list of tables in the database.

        Args:
            db_path: Path to the database file (optional)

        Returns:
            List of table names
        """
        conn = self.get_connection(db_path)

        try:
            # Get the list of tables
            result = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchdf()

            # Convert to list
            return result['name'].tolist()
        except Exception as e:
            logger.error(f"Error getting tables: {str(e)}")
            raise

    def get_table_preview(self, table_name: str, limit: int = 10, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get a preview of a table.

        Args:
            table_name: Name of the table
            limit: Maximum number of rows to return
            db_path: Path to the database file (optional)

        Returns:
            Table preview as a list of dictionaries
        """
        return self.execute_query(f"SELECT * FROM {table_name} LIMIT {limit}", db_path)

    def get_table_statistics(self, table_name: str, db_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics for a table.

        Args:
            table_name: Name of the table
            db_path: Path to the database file (optional)

        Returns:
            Table statistics
        """
        conn = self.get_connection(db_path)

        try:
            # Get the table schema
            schema = self.get_table_schema(table_name, db_path)

            # Get the number of rows
            row_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]

            # Get statistics for each column
            column_stats = []

            for column in schema:
                column_name = column['name']
                column_type = column['type']

                # Get basic statistics
                stats = {
                    'name': column_name,
                    'type': column_type,
                    'null_count': conn.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {column_name} IS NULL").fetchone()[0]
                }

                # Get type-specific statistics
                if column_type in ['INTEGER', 'FLOAT', 'DOUBLE', 'DECIMAL', 'REAL']:
                    # Numeric column
                    numeric_stats = conn.execute(f"""
                        SELECT
                            MIN({column_name}) AS min,
                            MAX({column_name}) AS max,
                            AVG({column_name}) AS mean,
                            STDDEV({column_name}) AS std
                        FROM {table_name}
                        WHERE {column_name} IS NOT NULL
                    """).fetchone()

                    stats.update({
                        'min': numeric_stats[0],
                        'max': numeric_stats[1],
                        'mean': numeric_stats[2],
                        'std': numeric_stats[3]
                    })
                elif column_type in ['VARCHAR', 'CHAR', 'TEXT', 'STRING']:
                    # String column
                    string_stats = conn.execute(f"""
                        SELECT
                            MIN(LENGTH({column_name})) AS min_length,
                            MAX(LENGTH({column_name})) AS max_length,
                            AVG(LENGTH({column_name})) AS mean_length
                        FROM {table_name}
                        WHERE {column_name} IS NOT NULL
                    """).fetchone()

                    stats.update({
                        'min_length': string_stats[0],
                        'max_length': string_stats[1],
                        'mean_length': string_stats[2]
                    })

                column_stats.append(stats)

            return {
                'row_count': row_count,
                'column_count': len(schema),
                'columns': column_stats
            }
        except Exception as e:
            logger.error(f"Error getting table statistics: {str(e)}")
            raise

    def create_database(self, db_name: str) -> str:
        """
        Create a new DuckDB database.

        Args:
            db_name: Name of the database

        Returns:
            Path to the database file
        """
        # Generate a database path
        db_path = os.path.join(self.data_dir, f"{db_name}.duckdb")

        # Create the database
        conn = self.get_connection(db_path)

        return db_path

    def delete_database(self, db_path: str) -> bool:
        """
        Delete a DuckDB database.

        Args:
            db_path: Path to the database file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Close the connection if it exists
            self.close_connection(db_path)

            # Delete the database file
            if os.path.exists(db_path):
                os.remove(db_path)

            return True
        except Exception as e:
            logger.error(f"Error deleting database: {str(e)}")
            return False

    def connect_to_postgres(self, connection_string: str, db_path: Optional[str] = None) -> bool:
        """
        Connect to a PostgreSQL database.

        Args:
            connection_string: PostgreSQL connection string
            db_path: Path to the DuckDB database file (optional)

        Returns:
            True if successful, False otherwise
        """
        conn = self.get_connection(db_path)

        try:
            # Connect to PostgreSQL
            conn.execute(f"ATTACH '{connection_string}' AS postgres (TYPE POSTGRES)")
            return True
        except Exception as e:
            logger.error(f"Error connecting to PostgreSQL: {str(e)}")
            return False

    def connect_to_mysql(self, connection_string: str, db_path: Optional[str] = None) -> bool:
        """
        Connect to a MySQL database.

        Args:
            connection_string: MySQL connection string
            db_path: Path to the DuckDB database file (optional)

        Returns:
            True if successful, False otherwise
        """
        conn = self.get_connection(db_path)

        try:
            # Connect to MySQL
            conn.execute(f"ATTACH '{connection_string}' AS mysql (TYPE MYSQL)")
            return True
        except Exception as e:
            logger.error(f"Error connecting to MySQL: {str(e)}")
            return False

    def connect_to_sqlite(self, connection_string: str, db_path: Optional[str] = None) -> bool:
        """
        Connect to a SQLite database.

        Args:
            connection_string: SQLite connection string
            db_path: Path to the DuckDB database file (optional)

        Returns:
            True if successful, False otherwise
        """
        conn = self.get_connection(db_path)

        try:
            # Connect to SQLite
            conn.execute(f"ATTACH '{connection_string}' AS sqlite (TYPE SQLITE)")
            return True
        except Exception as e:
            logger.error(f"Error connecting to SQLite: {str(e)}")
            return False

    def spatial_query(self, query: str, db_path: Optional[str] = None) -> gpd.GeoDataFrame:
        """
        Execute a spatial query.

        Args:
            query: SQL query to execute
            db_path: Path to the database file (optional)

        Returns:
            Query results as a GeoPandas GeoDataFrame
        """
        return self.execute_query_geo_df(query, db_path)

    def reproject_geometry(self, table_name: str, geometry_column: str, source_srid: int, target_srid: int, db_path: Optional[str] = None) -> bool:
        """
        Reproject a geometry column.

        Args:
            table_name: Name of the table
            geometry_column: Name of the geometry column
            source_srid: Source SRID
            target_srid: Target SRID
            db_path: Path to the database file (optional)

        Returns:
            True if successful, False otherwise
        """
        conn = self.get_connection(db_path)

        try:
            # Reproject the geometry column
            conn.execute(f"""
                UPDATE {table_name}
                SET {geometry_column} = ST_Transform({geometry_column}, {source_srid}, {target_srid})
            """)

            return True
        except Exception as e:
            logger.error(f"Error reprojecting geometry: {str(e)}")
            return False

    def convert_to_postgis(self, table_name: str, geometry_column: str, srid: int, db_path: Optional[str] = None) -> str:
        """
        Convert a table to PostGIS SQL.

        Args:
            table_name: Name of the table
            geometry_column: Name of the geometry column
            srid: SRID of the geometry
            db_path: Path to the database file (optional)

        Returns:
            PostGIS SQL
        """
        conn = self.get_connection(db_path)

        try:
            # Get the table schema
            schema = self.get_table_schema(table_name, db_path)

            # Generate the CREATE TABLE statement
            columns = []

            for column in schema:
                column_name = column['name']
                column_type = column['type']

                if column_name == geometry_column:
                    # Skip the geometry column, we'll add it later
                    continue

                # Map DuckDB types to PostgreSQL types
                if column_type in ['INTEGER', 'INT']:
                    pg_type = 'INTEGER'
                elif column_type in ['FLOAT', 'DOUBLE', 'DECIMAL', 'REAL']:
                    pg_type = 'NUMERIC'
                elif column_type in ['VARCHAR', 'CHAR', 'TEXT', 'STRING']:
                    pg_type = 'TEXT'
                elif column_type == 'BOOLEAN':
                    pg_type = 'BOOLEAN'
                elif column_type in ['DATE', 'TIMESTAMP']:
                    pg_type = column_type
                else:
                    pg_type = 'TEXT'

                columns.append(f'"{column_name}" {pg_type}')

            # Add the geometry column
            columns.append(f'"{geometry_column}" GEOMETRY')

            # Generate the CREATE TABLE statement
            create_table = f"""
                CREATE TABLE "{table_name}" (
                    {', '.join(columns)}
                );

                SELECT AddGeometryColumn('{table_name}', '{geometry_column}', {srid}, 'GEOMETRY', 2);
            """

            # Generate the INSERT statements
            df = self.execute_query_df(f"SELECT * FROM {table_name}", db_path)

            insert_statements = []

            for _, row in df.iterrows():
                values = []

                for column in schema:
                    column_name = column['name']

                    if column_name == geometry_column:
                        # Skip the geometry column, we'll add it later
                        continue

                    value = row[column_name]

                    if value is None:
                        values.append('NULL')
                    elif isinstance(value, (int, float)):
                        values.append(str(value))
                    elif isinstance(value, bool):
                        values.append('TRUE' if value else 'FALSE')
                    else:
                        values.append(f"'{str(value)}'")

                # Add the geometry value
                geometry_value = row[geometry_column]

                if geometry_value is None:
                    values.append('NULL')
                else:
                    values.append(f"ST_GeomFromText('{geometry_value}', {srid})")

                insert_statements.append(f"""
                    INSERT INTO "{table_name}" VALUES ({', '.join(values)});
                """)

            # Combine the statements
            sql = create_table + '\n'.join(insert_statements)

            return sql
        except Exception as e:
            logger.error(f"Error converting to PostGIS: {str(e)}")
            raise

# Create a global instance of DuckDBService
duckdb_service = DuckDBService()
