import os
import json
import requests
from typing import Dict, List, Any, Optional, Union
from qgis.core import QgsMessageLog, Qgis
import urllib.parse

class APIClient:
    """
    Client for interacting with the FastAPI backend services.
    This client handles all API communication for the QGIS plugin.
    """

    def __init__(self, base_url: str = None):
        """
        Initialize the API client.

        Args:
            base_url: Base URL for the API. If None, uses the environment variable or default.
        """
        self.base_url = base_url or os.environ.get("API_BASE_URL", "http://localhost:8000/api/v1")
        self.token = None
        self.headers = {
            "Content-Type": "application/json"
        }
        self.log_tag = "PostGIS Microservices"

    def set_token(self, token: str):
        """
        Set the authentication token.

        Args:
            token: Authentication token
        """
        self.token = token
        if token:
            self.headers["Authorization"] = f"Bearer {token}"
        elif "Authorization" in self.headers:
            del self.headers["Authorization"]

    def log(self, message: str, level: Qgis.MessageLevel = Qgis.Info):
        """
        Log a message to the QGIS message log.

        Args:
            message: Message to log
            level: Message level (Info, Warning, Critical, Success)
        """
        QgsMessageLog.logMessage(message, self.log_tag, level)

    def _handle_response(self, response: requests.Response) -> Any:
        """
        Handle API response and check for errors.

        Args:
            response: Response object from requests

        Returns:
            Response data (usually JSON)

        Raises:
            Exception: If the response contains an error
        """
        try:
            response.raise_for_status()

            # Check if response is JSON
            if response.headers.get("Content-Type", "").startswith("application/json"):
                return response.json()
            else:
                return response.content
        except requests.exceptions.HTTPError as e:
            error_msg = str(e)
            try:
                error_data = response.json()
                if "detail" in error_data:
                    error_msg = error_data["detail"]
            except:
                pass

            self.log(f"API Error: {error_msg}", Qgis.Critical)
            raise Exception(f"API Error: {error_msg}")
        except Exception as e:
            self.log(f"Error processing response: {str(e)}", Qgis.Critical)
            raise

    def _get(self, endpoint: str, params: Dict = None) -> Any:
        """
        Make a GET request to the API.

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            Response data
        """
        url = f"{self.base_url}/{endpoint}"
        self.log(f"GET {url}", Qgis.Info)

        try:
            response = requests.get(url, headers=self.headers, params=params)
            return self._handle_response(response)
        except Exception as e:
            self.log(f"GET request failed: {str(e)}", Qgis.Critical)
            raise

    def _post(self, endpoint: str, data: Dict = None, files: Dict = None) -> Any:
        """
        Make a POST request to the API.

        Args:
            endpoint: API endpoint
            data: Request data
            files: Files to upload

        Returns:
            Response data
        """
        url = f"{self.base_url}/{endpoint}"
        self.log(f"POST {url}", Qgis.Info)

        headers = self.headers.copy()

        try:
            if files:
                # Remove Content-Type for multipart/form-data
                if "Content-Type" in headers:
                    del headers["Content-Type"]

                response = requests.post(url, headers=headers, data=data, files=files)
            else:
                response = requests.post(url, headers=headers, json=data)

            return self._handle_response(response)
        except Exception as e:
            self.log(f"POST request failed: {str(e)}", Qgis.Critical)
            raise

    def _put(self, endpoint: str, data: Dict) -> Any:
        """
        Make a PUT request to the API.

        Args:
            endpoint: API endpoint
            data: Request data

        Returns:
            Response data
        """
        url = f"{self.base_url}/{endpoint}"
        self.log(f"PUT {url}", Qgis.Info)

        try:
            response = requests.put(url, headers=self.headers, json=data)
            return self._handle_response(response)
        except Exception as e:
            self.log(f"PUT request failed: {str(e)}", Qgis.Critical)
            raise

    def _delete(self, endpoint: str) -> Any:
        """
        Make a DELETE request to the API.

        Args:
            endpoint: API endpoint

        Returns:
            Response data
        """
        url = f"{self.base_url}/{endpoint}"
        self.log(f"DELETE {url}", Qgis.Info)

        try:
            response = requests.delete(url, headers=self.headers)
            return self._handle_response(response)
        except Exception as e:
            self.log(f"DELETE request failed: {str(e)}", Qgis.Critical)
            raise

    # ===== Integrated API Endpoints =====

    def connect_database(self, connection_settings: Dict) -> Dict:
        """
        Connect to a database.

        Args:
            connection_settings: Database connection settings

        Returns:
            Connection response
        """
        return self._post("integrated/database/connect", connection_settings)

    def get_geospatial_data(self, params: Dict = None) -> List[Dict]:
        """
        Get geospatial data.

        Args:
            params: Query parameters

        Returns:
            List of geospatial data
        """
        return self._get("integrated/geospatial/data", params)

    def get_geospatial_data_by_id(self, data_id: int) -> Dict:
        """
        Get geospatial data by ID.

        Args:
            data_id: Data ID

        Returns:
            Geospatial data
        """
        return self._get(f"integrated/geospatial/data/{data_id}")

    def create_geospatial_data(self, data: Dict) -> Dict:
        """
        Create geospatial data.

        Args:
            data: Geospatial data

        Returns:
            Created data
        """
        return self._post("integrated/geospatial/data", data)

    def update_geospatial_data(self, data_id: int, data: Dict) -> Dict:
        """
        Update geospatial data.

        Args:
            data_id: Data ID
            data: Updated data

        Returns:
            Updated data
        """
        return self._put(f"integrated/geospatial/data/{data_id}", data)

    def delete_geospatial_data(self, data_id: int) -> Dict:
        """
        Delete geospatial data.

        Args:
            data_id: Data ID

        Returns:
            Deletion response
        """
        return self._delete(f"integrated/geospatial/data/{data_id}")

    def query_within_geometry(self, geometry: Dict) -> List[Dict]:
        """
        Query data within a geometry.

        Args:
            geometry: GeoJSON geometry

        Returns:
            List of data within the geometry
        """
        params = {"geometry": json.dumps(geometry)}
        return self._get("integrated/spatial/within", params)

    def buffer_geometry(self, geometry: Dict, distance: float) -> Dict:
        """
        Buffer a geometry.

        Args:
            geometry: GeoJSON geometry
            distance: Buffer distance in meters

        Returns:
            Buffered geometry
        """
        params = {
            "geometry": json.dumps(geometry),
            "distance": distance
        }
        return self._get("integrated/spatial/buffer", params)

    # ===== Geospatial Processing Endpoints =====

    def import_to_duckdb(self, file_path: str, db_name: str, table_name: str) -> Dict:
        """
        Import a file to DuckDB.

        Args:
            file_path: Path to the file
            db_name: DuckDB database name
            table_name: Table name

        Returns:
            Import response
        """
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f)}
            data = {
                'table_name': table_name
            }
            return self._post(f"geospatial-processing/import-to-duckdb/{db_name}", data=data, files=files)

    def query_duckdb(self, db_name: str, query: str, export_format: str = None, export_path: str = None) -> Dict:
        """
        Query a DuckDB database.

        Args:
            db_name: DuckDB database name
            query: SQL query
            export_format: Optional export format
            export_path: Optional export path

        Returns:
            Query response
        """
        data = {
            "query": query,
            "export_format": export_format,
            "export_path": export_path
        }
        return self._post(f"geospatial-processing/query-duckdb/{db_name}", data)

    # ===== Tippecanoe Endpoints =====

    def run_tippecanoe(self, input_files: List[str], output_format: str, output_name: str,
                      min_zoom: int = 0, max_zoom: int = 14, layer_name: str = None,
                      simplification: float = None, drop_rate: float = None,
                      buffer_size: int = None) -> Dict:
        """
        Run Tippecanoe to generate vector tiles.

        Args:
            input_files: List of input file paths
            output_format: Output format (mbtiles, pmtiles)
            output_name: Output file name
            min_zoom: Minimum zoom level
            max_zoom: Maximum zoom level
            layer_name: Layer name
            simplification: Simplification factor
            drop_rate: Drop rate
            buffer_size: Buffer size

        Returns:
            Tippecanoe response
        """
        files = {}
        for i, file_path in enumerate(input_files):
            with open(file_path, 'rb') as f:
                files[f'input_files_{i}'] = (os.path.basename(file_path), f)

        data = {
            'output_format': output_format,
            'output_name': output_name,
            'min_zoom': min_zoom,
            'max_zoom': max_zoom
        }

        if layer_name:
            data['layer_name'] = layer_name

        if simplification is not None:
            data['simplification'] = simplification

        if drop_rate is not None:
            data['drop_rate'] = drop_rate

        if buffer_size is not None:
            data['buffer_size'] = buffer_size

        return self._post("tippecanoe/run", data=data, files=files)

    # ===== Cloud SQL Monitoring Endpoints =====

    def get_database_status(self, instance_config: Dict) -> Dict:
        """
        Get database status.

        Args:
            instance_config: Instance configuration

        Returns:
            Database status
        """
        return self._post("cloudsql/status", instance_config)

    def get_performance_metrics(self, instance_config: Dict) -> Dict:
        """
        Get performance metrics.

        Args:
            instance_config: Instance configuration

        Returns:
            Performance metrics
        """
        return self._post("cloudsql/metrics", instance_config)

    def get_postgis_stats(self, instance_config: Dict) -> Dict:
        """
        Get PostGIS statistics.

        Args:
            instance_config: Instance configuration

        Returns:
            PostGIS statistics
        """
        return self._post("cloudsql/postgis-stats", instance_config)

    # ===== Kestra Integration Endpoints =====

    def get_workflows(self, namespace: str = None) -> List[Dict]:
        """
        Get workflows from Kestra.

        Args:
            namespace: Optional namespace to filter workflows

        Returns:
            List of workflows
        """
        params = {}
        if namespace:
            params["namespace"] = namespace

        return self._get("kestra/workflows", params)

    def get_workflow(self, namespace: str, flow_id: str) -> Dict:
        """
        Get a specific workflow from Kestra.

        Args:
            namespace: Workflow namespace
            flow_id: Workflow ID

        Returns:
            Workflow details
        """
        return self._get(f"kestra/workflows/{namespace}/{flow_id}")

    def trigger_workflow(self, namespace: str, flow_id: str, inputs: Dict = None) -> Dict:
        """
        Trigger a workflow execution.

        Args:
            namespace: Workflow namespace
            flow_id: Workflow ID
            inputs: Optional inputs for the workflow

        Returns:
            Execution details
        """
        return self._post(f"kestra/workflows/trigger/{namespace}/{flow_id}", inputs or {})

    def get_executions(self, namespace: str = None, flow_id: str = None,
                      state: str = None, limit: int = 100) -> List[Dict]:
        """
        Get workflow executions.

        Args:
            namespace: Optional namespace to filter executions
            flow_id: Optional workflow ID to filter executions
            state: Optional state to filter executions
            limit: Maximum number of executions to return

        Returns:
            List of executions
        """
        params = {"limit": limit}

        if namespace:
            params["namespace"] = namespace

        if flow_id:
            params["flow_id"] = flow_id

        if state:
            params["state"] = state

        return self._get("kestra/executions", params)

    def get_execution(self, execution_id: str) -> Dict:
        """
        Get a specific execution.

        Args:
            execution_id: Execution ID

        Returns:
            Execution details
        """
        return self._get(f"kestra/executions/{execution_id}")

    def restart_execution(self, execution_id: str) -> Dict:
        """
        Restart a failed execution.

        Args:
            execution_id: Execution ID

        Returns:
            New execution details
        """
        return self._post(f"kestra/executions/{execution_id}/restart")

    def stop_execution(self, execution_id: str) -> Dict:
        """
        Stop a running execution.

        Args:
            execution_id: Execution ID

        Returns:
            Execution details
        """
        return self._post(f"kestra/executions/{execution_id}/stop")

    # ===== DLT-Kestra Integration Endpoints =====

    def generate_dlt_workflow(self, workflow_name: str, source_type: str, destination_type: str,
                             source_config: Dict, destination_config: Dict, schedule: str = None,
                             namespace: str = "default", description: str = None,
                             tags: List[str] = None, python_version: str = "3.10") -> Dict:
        """
        Generate a Kestra workflow YAML for a DLT pipeline.

        Args:
            workflow_name: Name of the workflow
            source_type: Type of source
            destination_type: Type of destination
            source_config: Configuration for the source
            destination_config: Configuration for the destination
            schedule: Optional cron schedule for the workflow
            namespace: Kestra namespace
            description: Optional workflow description
            tags: Optional tags for the workflow
            python_version: Python version to use

        Returns:
            Generated workflow definition
        """
        data = {
            "workflow_name": workflow_name,
            "source_type": source_type,
            "destination_type": destination_type,
            "source_config": source_config,
            "destination_config": destination_config,
            "namespace": namespace,
            "python_version": python_version
        }

        if schedule:
            data["schedule"] = schedule

        if description:
            data["description"] = description

        if tags:
            data["tags"] = tags

        return self._post("dlt-kestra/workflows/generate", data)

    def create_dlt_workflow(self, workflow_name: str, source_type: str, destination_type: str,
                           source_config: Dict, destination_config: Dict, schedule: str = None,
                           namespace: str = "default", description: str = None,
                           tags: List[str] = None, python_version: str = "3.10") -> Dict:
        """
        Create a DLT workflow in Kestra.

        Args:
            workflow_name: Name of the workflow
            source_type: Type of source
            destination_type: Type of destination
            source_config: Configuration for the source
            destination_config: Configuration for the destination
            schedule: Optional cron schedule for the workflow
            namespace: Kestra namespace
            description: Optional workflow description
            tags: Optional tags for the workflow
            python_version: Python version to use

        Returns:
            Created workflow information
        """
        data = {
            "workflow_name": workflow_name,
            "source_type": source_type,
            "destination_type": destination_type,
            "source_config": source_config,
            "destination_config": destination_config,
            "namespace": namespace,
            "python_version": python_version
        }

        if schedule:
            data["schedule"] = schedule

        if description:
            data["description"] = description

        if tags:
            data["tags"] = tags

        return self._post("dlt-kestra/workflows/create", data)

    def run_dlt_workflow(self, workflow_id: str, namespace: str, source_credentials: Dict,
                        destination_credentials: Dict, slack_webhook_url: str = None) -> Dict:
        """
        Run a DLT workflow in Kestra.

        Args:
            workflow_id: ID of the workflow
            namespace: Kestra namespace
            source_credentials: Credentials for the source
            destination_credentials: Credentials for the destination
            slack_webhook_url: Optional Slack webhook URL for notifications

        Returns:
            Execution information
        """
        data = {
            "workflow_id": workflow_id,
            "namespace": namespace,
            "source_credentials": source_credentials,
            "destination_credentials": destination_credentials
        }

        if slack_webhook_url:
            data["slack_webhook_url"] = slack_webhook_url

        return self._post("dlt-kestra/workflows/run", data)

    def create_postgres_to_postgres_workflow(self, workflow_name: str, source_connection: str,
                                           source_query: str, destination_connection: str,
                                           destination_schema: str, destination_table: str,
                                           primary_key: str = None, schedule: str = None,
                                           namespace: str = "default") -> Dict:
        """
        Create a workflow for Postgres to Postgres data transfer.

        Args:
            workflow_name: Name of the workflow
            source_connection: PostgreSQL connection string for source
            source_query: SQL query to extract data
            destination_connection: PostgreSQL connection string for destination
            destination_schema: Destination schema
            destination_table: Destination table
            primary_key: Primary key column(s), comma-separated
            schedule: Optional cron schedule
            namespace: Kestra namespace

        Returns:
            Created workflow information
        """
        data = {
            "workflow_name": workflow_name,
            "source_connection": source_connection,
            "source_query": source_query,
            "destination_connection": destination_connection,
            "destination_schema": destination_schema,
            "destination_table": destination_table,
            "namespace": namespace
        }

        if primary_key:
            data["primary_key"] = primary_key

        if schedule:
            data["schedule"] = schedule

        return self._post("dlt-kestra/templates/postgres-to-postgres", data)

    def create_api_to_duckdb_workflow(self, workflow_name: str, api_url: str, api_method: str = "GET",
                                    api_headers: Dict = None, api_params: Dict = None,
                                    duckdb_path: str = "data/analytics.duckdb", table_name: str = None,
                                    schedule: str = None, namespace: str = "default") -> Dict:
        """
        Create a workflow for API to DuckDB data transfer.

        Args:
            workflow_name: Name of the workflow
            api_url: API URL
            api_method: HTTP method
            api_headers: Optional HTTP headers
            api_params: Optional query parameters
            duckdb_path: Path to DuckDB database
            table_name: Table name
            schedule: Optional cron schedule
            namespace: Kestra namespace

        Returns:
            Created workflow information
        """
        data = {
            "workflow_name": workflow_name,
            "api_url": api_url,
            "api_method": api_method,
            "duckdb_path": duckdb_path,
            "table_name": table_name,
            "namespace": namespace
        }

        if api_headers:
            data["api_headers"] = api_headers

        if api_params:
            data["api_params"] = api_params

        if schedule:
            data["schedule"] = schedule

        return self._post("dlt-kestra/templates/api-to-duckdb", data)

    def get_source_types(self) -> List[Dict]:
        """
        Get available DLT source types.

        Returns:
            List of source types
        """
        return self._get("dlt-kestra/source-types")

    def get_destination_types(self) -> List[Dict]:
        """
        Get available DLT destination types.

        Returns:
            List of destination types
        """
        return self._get("dlt-kestra/destination-types")

    # ===== OGC API Processes Endpoints =====

    def get_processes(self) -> Dict[str, List[Dict]]:
        """
        Get all available processes.

        Returns:
            Dictionary with list of processes
        """
        return self._get("processes")

    def get_process(self, process_id: str) -> Dict:
        """
        Get details about a specific process.

        Args:
            process_id: Process ID

        Returns:
            Process details
        """
        return self._get(f"processes/{process_id}")

    def execute_process(self, process_id: str, inputs: Dict) -> Dict:
        """
        Execute a process with the provided inputs.

        Args:
            process_id: Process ID
            inputs: Process inputs

        Returns:
            Process result
        """
        return self._post(f"processes/{process_id}/execution", inputs)
