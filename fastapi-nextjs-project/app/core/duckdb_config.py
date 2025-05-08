import os
import json
from typing import Optional, List, Dict
from pydantic import BaseModel
from app.core.config import settings

class DuckDBConfig(BaseModel):
    """Configuration for DuckDB integration."""

    # DuckDB settings
    data_dir: str = os.getenv("DUCKDB_DATA_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data/duckdb"))

    # Extensions to load
    extensions: List[str] = [
        "httpfs",
        "spatial",
        "postgres",
        "mysql",
        "sqlite",
        "excel",
        "odbc",
        "hostfs",
        "pivot_table",
        "nanodbc"
    ]

    # Memory limit for DuckDB
    memory_limit: str = os.getenv("DUCKDB_MEMORY_LIMIT", "4GB")

    # Temporary directory for DuckDB
    temp_dir: str = os.getenv("DUCKDB_TEMP_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data/duckdb/temp"))

    # Default output format
    default_output_format: str = os.getenv("DUCKDB_DEFAULT_OUTPUT_FORMAT", "json")

    # Cloud storage settings
    s3_region: Optional[str] = os.getenv("S3_REGION", None)
    s3_access_key_id: Optional[str] = os.getenv("S3_ACCESS_KEY_ID", None)
    s3_secret_access_key: Optional[str] = os.getenv("S3_SECRET_ACCESS_KEY", None)

    azure_storage_account: Optional[str] = os.getenv("AZURE_STORAGE_ACCOUNT", None)
    azure_storage_key: Optional[str] = os.getenv("AZURE_STORAGE_KEY", None)

    gcs_project_id: Optional[str] = os.getenv("GCS_PROJECT_ID", None)
    gcs_credentials_path: Optional[str] = os.getenv("GCS_CREDENTIALS_PATH", None)

    # Connection settings
    postgres_connection_string: Optional[str] = os.getenv("POSTGRES_CONNECTION_STRING", None)
    mysql_connection_string: Optional[str] = os.getenv("MYSQL_CONNECTION_STRING", None)
    sqlite_connection_string: Optional[str] = os.getenv("SQLITE_CONNECTION_STRING", None)

    # ODBC settings for Nanodbc extension
    odbc_driver_paths: Optional[str] = os.getenv("ODBC_DRIVER_PATHS", None)
    odbc_connection_strings: Optional[str] = os.getenv("ODBC_CONNECTION_STRINGS", None)

    @property
    def odbc_connections(self) -> Dict[str, str]:
        """Get ODBC connection strings as a dictionary."""
        if not self.odbc_connection_strings:
            return {}

        try:
            return json.loads(self.odbc_connection_strings)
        except json.JSONDecodeError:
            return {}

    @property
    def is_s3_configured(self) -> bool:
        """Check if S3 is configured."""
        return bool(self.s3_region and self.s3_access_key_id and self.s3_secret_access_key)

    @property
    def is_azure_configured(self) -> bool:
        """Check if Azure is configured."""
        return bool(self.azure_storage_account and self.azure_storage_key)

    @property
    def is_gcs_configured(self) -> bool:
        """Check if GCS is configured."""
        return bool(self.gcs_project_id and self.gcs_credentials_path)

    @property
    def is_postgres_configured(self) -> bool:
        """Check if PostgreSQL is configured."""
        return bool(self.postgres_connection_string)

    @property
    def is_mysql_configured(self) -> bool:
        """Check if MySQL is configured."""
        return bool(self.mysql_connection_string)

    @property
    def is_sqlite_configured(self) -> bool:
        """Check if SQLite is configured."""
        return bool(self.sqlite_connection_string)

# Create a global instance of DuckDBConfig
duckdb_config = DuckDBConfig()

# Create required directories
os.makedirs(duckdb_config.data_dir, exist_ok=True)
os.makedirs(duckdb_config.temp_dir, exist_ok=True)
