import os
import sys
import json
import shutil
import logging
import subprocess
import tempfile
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import asyncio
import duckdb
import pandas as pd
from fastapi import HTTPException, UploadFile

logger = logging.getLogger(__name__)

# Define storage paths
GEOJSON_DIR = os.environ.get("GEOJSON_DIR", "./data/geojson")
DUCKDB_DIR = os.environ.get("DUCKDB_DIR", "./data/duckdb")
PMTILES_DIR = os.environ.get("PMTILES_DIR", "./data/pmtiles")
MBTILES_DIR = os.environ.get("MBTILES_DIR", "./data/mbtiles")
TEMP_DIR = os.environ.get("TEMP_DIR", "./data/temp")

# Ensure directories exist
os.makedirs(GEOJSON_DIR, exist_ok=True)
os.makedirs(DUCKDB_DIR, exist_ok=True)
os.makedirs(PMTILES_DIR, exist_ok=True)
os.makedirs(MBTILES_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)


class GeospatialProcessingService:
    """Service for processing geospatial data with DuckDB and Tippecanoe"""
    
    @staticmethod
    async def import_to_duckdb(
        input_files: List[str],
        db_name: str,
        spatial_index: bool = True,
        overwrite: bool = False
    ) -> Dict[str, Any]:
        """
        Import geospatial files into DuckDB for fast inspection and querying
        
        Args:
            input_files: List of input file paths
            db_name: Name for the DuckDB database
            spatial_index: Whether to create spatial indexes
            overwrite: Whether to overwrite existing tables
            
        Returns:
            Dictionary with information about the import process
        """
        # Validate input files
        for file_path in input_files:
            if not os.path.exists(file_path):
                raise HTTPException(status_code=400, detail=f"Input file not found: {file_path}")
        
        # Sanitize database name
        safe_name = "".join(c if c.isalnum() or c in ['-', '_'] else '_' for c in db_name)
        db_path = os.path.join(DUCKDB_DIR, f"{safe_name}.duckdb")
        
        # Check if database exists
        db_exists = os.path.exists(db_path)
        
        try:
            # Connect to DuckDB
            conn = duckdb.connect(db_path)
            
            # Install and load extensions
            conn.execute("INSTALL spatial;")
            conn.execute("LOAD spatial;")
            conn.execute("INSTALL httpfs;")
            conn.execute("LOAD httpfs;")
            
            # Track imported tables
            imported_tables = []
            
            # Process each input file
            for file_path in input_files:
                file_ext = os.path.splitext(file_path)[1].lower()
                file_name = os.path.basename(file_path)
                table_name = os.path.splitext(file_name)[0]
                
                # Sanitize table name
                table_name = "".join(c if c.isalnum() or c == '_' else '_' for c in table_name)
                
                # Check if table exists
                table_exists = False
                try:
                    conn.execute(f"SELECT * FROM {table_name} LIMIT 0")
                    table_exists = True
                except:
                    pass
                
                if table_exists and not overwrite:
                    logger.warning(f"Table {table_name} already exists and overwrite=False")
                    imported_tables.append({
                        "table_name": table_name,
                        "file_path": file_path,
                        "status": "skipped",
                        "reason": "Table already exists"
                    })
                    continue
                
                # Drop table if it exists and overwrite is True
                if table_exists and overwrite:
                    conn.execute(f"DROP TABLE IF EXISTS {table_name}")
                
                # Import based on file type
                if file_ext in ['.geojson', '.json']:
                    # GeoJSON import
                    conn.execute(f"""
                        CREATE TABLE {table_name} AS 
                        SELECT * FROM ST_Read('{file_path}')
                    """)
                    
                elif file_ext in ['.shp']:
                    # Shapefile import
                    conn.execute(f"""
                        CREATE TABLE {table_name} AS 
                        SELECT * FROM ST_Read('{file_path}')
                    """)
                    
                elif file_ext in ['.gpkg']:
                    # GeoPackage import - need to list layers first
                    layers_query = f"SELECT * FROM ST_Layers('{file_path}')"
                    layers = conn.execute(layers_query).fetchall()
                    
                    for layer in layers:
                        layer_name = layer[0]
                        layer_table = f"{table_name}_{layer_name}"
                        
                        conn.execute(f"""
                            CREATE TABLE {layer_table} AS 
                            SELECT * FROM ST_Read('{file_path}', layer='{layer_name}')
                        """)
                        
                        imported_tables.append({
                            "table_name": layer_table,
                            "file_path": file_path,
                            "layer": layer_name,
                            "status": "imported"
                        })
                    
                    # Skip the rest of the loop since we've handled all layers
                    continue
                    
                elif file_ext in ['.csv']:
                    # CSV import - try to detect geometry column
                    conn.execute(f"""
                        CREATE TABLE {table_name} AS 
                        SELECT * FROM read_csv('{file_path}', auto_detect=TRUE)
                    """)
                    
                    # Check for geometry columns (WKT or lat/lon)
                    columns = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
                    column_names = [col[1] for col in columns]
                    
                    # Look for common geometry column names
                    geom_col = None
                    for col in ['geom', 'geometry', 'wkt', 'the_geom']:
                        if col in column_names:
                            geom_col = col
                            break
                    
                    # Look for lat/lon pairs
                    lat_col = None
                    lon_col = None
                    for lat in ['lat', 'latitude', 'y']:
                        if lat in column_names:
                            lat_col = lat
                            break
                    
                    for lon in ['lon', 'lng', 'longitude', 'x']:
                        if lon in column_names:
                            lon_col = lon
                            break
                    
                    # Convert to geometry if possible
                    if geom_col:
                        conn.execute(f"""
                            ALTER TABLE {table_name} 
                            ADD COLUMN geometry GEOMETRY;
                            
                            UPDATE {table_name} 
                            SET geometry = ST_GeomFromText({geom_col});
                        """)
                    elif lat_col and lon_col:
                        conn.execute(f"""
                            ALTER TABLE {table_name} 
                            ADD COLUMN geometry GEOMETRY;
                            
                            UPDATE {table_name} 
                            SET geometry = ST_Point({lon_col}, {lat_col});
                        """)
                
                elif file_ext in ['.parquet', '.pq']:
                    # Parquet import
                    conn.execute(f"""
                        CREATE TABLE {table_name} AS 
                        SELECT * FROM read_parquet('{file_path}')
                    """)
                
                else:
                    # Unsupported format
                    imported_tables.append({
                        "table_name": table_name,
                        "file_path": file_path,
                        "status": "error",
                        "reason": f"Unsupported file format: {file_ext}"
                    })
                    continue
                
                # Create spatial index if requested
                if spatial_index:
                    try:
                        conn.execute(f"""
                            CREATE SPATIAL INDEX ON {table_name} (geometry);
                        """)
                    except Exception as e:
                        logger.warning(f"Could not create spatial index on {table_name}: {str(e)}")
                
                # Add to imported tables
                imported_tables.append({
                    "table_name": table_name,
                    "file_path": file_path,
                    "status": "imported"
                })
            
            # Get database summary
            tables = conn.execute("SHOW TABLES").fetchall()
            table_names = [table[0] for table in tables]
            
            # Get row counts for each table
            table_stats = []
            for table in table_names:
                row_count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                columns = conn.execute(f"PRAGMA table_info({table})").fetchall()
                column_names = [col[1] for col in columns]
                
                # Check for geometry column
                has_geometry = False
                for col in columns:
                    if col[2].upper() == 'GEOMETRY':
                        has_geometry = True
                        break
                
                table_stats.append({
                    "table_name": table,
                    "row_count": row_count,
                    "column_count": len(columns),
                    "columns": column_names,
                    "has_geometry": has_geometry
                })
            
            # Close connection
            conn.close()
            
            return {
                "database_name": safe_name,
                "database_path": db_path,
                "database_exists": db_exists,
                "imported_tables": imported_tables,
                "table_stats": table_stats
            }
            
        except Exception as e:
            logger.error(f"Error importing to DuckDB: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error importing to DuckDB: {str(e)}")
    
    @staticmethod
    async def query_duckdb(
        db_name: str,
        query: str,
        export_format: Optional[str] = None,
        export_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a query on a DuckDB database
        
        Args:
            db_name: Name of the DuckDB database
            query: SQL query to execute
            export_format: Optional format to export results (csv, geojson, parquet)
            export_path: Optional path to save exported results
            
        Returns:
            Dictionary with query results
        """
        # Sanitize database name
        safe_name = "".join(c if c.isalnum() or c in ['-', '_'] else '_' for c in db_name)
        db_path = os.path.join(DUCKDB_DIR, f"{safe_name}.duckdb")
        
        # Check if database exists
        if not os.path.exists(db_path):
            raise HTTPException(status_code=404, detail=f"Database not found: {db_name}")
        
        try:
            # Connect to DuckDB
            conn = duckdb.connect(db_path)
            
            # Load extensions
            conn.execute("INSTALL spatial;")
            conn.execute("LOAD spatial;")
            
            # Execute query
            result = conn.execute(query).fetchdf()
            
            # Export results if requested
            exported_path = None
            if export_format and export_path:
                if export_format == 'csv':
                    result.to_csv(export_path, index=False)
                    exported_path = export_path
                elif export_format == 'geojson':
                    # Check if result has geometry column
                    if 'geometry' in result.columns:
                        # Convert to GeoJSON
                        conn.execute(f"""
                            COPY (
                                SELECT ST_AsGeoJSON(geometry) as geometry, 
                                       * EXCLUDE (geometry)
                                FROM ({query})
                            ) TO '{export_path}' WITH (FORMAT 'JSON');
                        """)
                        exported_path = export_path
                    else:
                        raise HTTPException(status_code=400, detail="Query result has no geometry column")
                elif export_format == 'parquet':
                    result.to_parquet(export_path, index=False)
                    exported_path = export_path
                else:
                    raise HTTPException(status_code=400, detail=f"Unsupported export format: {export_format}")
            
            # Convert result to JSON-serializable format
            result_json = json.loads(result.to_json(orient='records'))
            
            # Close connection
            conn.close()
            
            return {
                "database_name": safe_name,
                "query": query,
                "row_count": len(result),
                "column_count": len(result.columns),
                "columns": list(result.columns),
                "results": result_json[:100],  # Limit to first 100 rows
                "truncated": len(result) > 100,
                "exported_format": export_format,
                "exported_path": exported_path
            }
            
        except Exception as e:
            logger.error(f"Error querying DuckDB: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error querying DuckDB: {str(e)}")
    
    @staticmethod
    async def batch_tippecanoe(
        input_dir: str,
        output_format: str = "pmtiles",
        output_dir: Optional[str] = None,
        min_zoom: Optional[int] = None,
        max_zoom: Optional[int] = None,
        layer_name: Optional[str] = None,
        simplification: Optional[float] = None,
        drop_rate: Optional[float] = None,
        buffer_size: Optional[int] = None,
        additional_args: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Run Tippecanoe on a batch of GeoJSON files
        
        Args:
            input_dir: Directory containing GeoJSON files
            output_format: Output format ('pmtiles' or 'mbtiles')
            output_dir: Directory to save output files (defaults to PMTILES_DIR or MBTILES_DIR)
            min_zoom: Minimum zoom level
            max_zoom: Maximum zoom level
            layer_name: Layer name
            simplification: Simplification factor
            drop_rate: Rate at which to drop features
            buffer_size: Buffer size in pixels
            additional_args: Additional arguments to pass to Tippecanoe
            
        Returns:
            Dictionary with information about the generated tiles
        """
        if output_format not in ["pmtiles", "mbtiles"]:
            raise HTTPException(status_code=400, detail=f"Unsupported output format: {output_format}")
        
        # Validate input directory
        if not os.path.exists(input_dir) or not os.path.isdir(input_dir):
            raise HTTPException(status_code=400, detail=f"Input directory not found: {input_dir}")
        
        # Find GeoJSON files
        geojson_files = []
        for file in os.listdir(input_dir):
            if file.endswith('.geojson') or file.endswith('.json'):
                geojson_files.append(os.path.join(input_dir, file))
        
        if not geojson_files:
            raise HTTPException(status_code=400, detail=f"No GeoJSON files found in {input_dir}")
        
        # Determine output directory
        if output_dir is None:
            output_dir = PMTILES_DIR if output_format == "pmtiles" else MBTILES_DIR
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Process each file
        results = []
        for file_path in geojson_files:
            try:
                # Get file name without extension
                file_name = os.path.basename(file_path)
                name = os.path.splitext(file_name)[0]
                
                # Sanitize name
                safe_name = "".join(c if c.isalnum() or c in ['-', '_'] else '_' for c in name)
                
                # Determine output file path
                output_extension = ".pmtiles" if output_format == "pmtiles" else ".mbtiles"
                output_path = os.path.join(output_dir, f"{safe_name}{output_extension}")
                
                # Build Tippecanoe command
                cmd = ["tippecanoe"]
                
                # Add output format
                if output_format == "pmtiles":
                    cmd.append("--output-to-directory=temp_tiles")
                
                # Add output file
                if output_format == "mbtiles":
                    cmd.extend(["-o", output_path])
                
                # Add zoom levels
                if min_zoom is not None:
                    cmd.extend(["-z", str(min_zoom)])
                if max_zoom is not None:
                    cmd.extend(["-Z", str(max_zoom)])
                
                # Add layer name
                if layer_name:
                    cmd.extend(["-l", layer_name])
                else:
                    # Use file name as layer name
                    cmd.extend(["-l", safe_name])
                
                # Add simplification
                if simplification is not None:
                    cmd.extend(["-S", str(simplification)])
                
                # Add drop rate
                if drop_rate is not None:
                    cmd.extend(["-r", str(drop_rate)])
                
                # Add buffer size
                if buffer_size is not None:
                    cmd.extend(["-b", str(buffer_size)])
                
                # Add additional arguments
                if additional_args:
                    cmd.extend(additional_args)
                
                # Add input file
                cmd.append(file_path)
                
                # Create temporary directory for PMTiles output
                temp_dir = None
                if output_format == "pmtiles":
                    temp_dir = tempfile.mkdtemp(dir=TEMP_DIR)
                    cmd[1] = f"--output-to-directory={temp_dir}"
                
                # Run Tippecanoe
                logger.info(f"Running Tippecanoe command: {' '.join(cmd)}")
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                
                if process.returncode != 0:
                    error_message = stderr.decode() if stderr else "Unknown error"
                    logger.error(f"Tippecanoe error for {file_path}: {error_message}")
                    results.append({
                        "file_path": file_path,
                        "output_path": output_path,
                        "status": "error",
                        "error": error_message
                    })
                    continue
                
                # For PMTiles, convert the output directory to a PMTiles file
                if output_format == "pmtiles":
                    pmtiles_cmd = ["pmtiles", "convert", temp_dir, output_path]
                    pmtiles_process = await asyncio.create_subprocess_exec(
                        *pmtiles_cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    pmtiles_stdout, pmtiles_stderr = await pmtiles_process.communicate()
                    
                    if pmtiles_process.returncode != 0:
                        error_message = pmtiles_stderr.decode() if pmtiles_stderr else "Unknown error"
                        logger.error(f"PMTiles conversion error for {file_path}: {error_message}")
                        results.append({
                            "file_path": file_path,
                            "output_path": output_path,
                            "status": "error",
                            "error": error_message
                        })
                        continue
                    
                    # Clean up temporary directory
                    shutil.rmtree(temp_dir)
                
                # Add to results
                results.append({
                    "file_path": file_path,
                    "output_path": output_path,
                    "output_format": output_format,
                    "status": "success",
                    "size_bytes": os.path.getsize(output_path)
                })
                
            except Exception as e:
                logger.error(f"Error processing {file_path}: {str(e)}")
                results.append({
                    "file_path": file_path,
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "input_dir": input_dir,
            "output_dir": output_dir,
            "output_format": output_format,
            "file_count": len(geojson_files),
            "success_count": sum(1 for r in results if r["status"] == "success"),
            "error_count": sum(1 for r in results if r["status"] == "error"),
            "results": results
        }
    
    @staticmethod
    async def generate_kestra_workflow(
        workflow_name: str,
        input_dir: str,
        output_format: str = "pmtiles",
        output_dir: Optional[str] = None,
        min_zoom: Optional[int] = None,
        max_zoom: Optional[int] = None,
        simplification: Optional[float] = None,
        drop_rate: Optional[float] = None,
        buffer_size: Optional[int] = None,
        schedule: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a Kestra.io workflow for batch Tippecanoe processing
        
        Args:
            workflow_name: Name for the workflow
            input_dir: Directory containing GeoJSON files
            output_format: Output format ('pmtiles' or 'mbtiles')
            output_dir: Directory to save output files
            min_zoom: Minimum zoom level
            max_zoom: Maximum zoom level
            simplification: Simplification factor
            drop_rate: Rate at which to drop features
            buffer_size: Buffer size in pixels
            schedule: Cron schedule for the workflow
            
        Returns:
            Dictionary with the Kestra workflow definition
        """
        # Sanitize workflow name
        safe_name = "".join(c if c.isalnum() or c in ['-', '_'] else '_' for c in workflow_name)
        
        # Build Tippecanoe command
        tippecanoe_cmd = ["tippecanoe"]
        
        # Add output format
        if output_format == "pmtiles":
            tippecanoe_cmd.append("--output-to-directory={{ outputs.directory }}")
        else:
            tippecanoe_cmd.extend(["-o", "{{ outputs.file }}"])
        
        # Add zoom levels
        if min_zoom is not None:
            tippecanoe_cmd.extend(["-z", str(min_zoom)])
        if max_zoom is not None:
            tippecanoe_cmd.extend(["-Z", str(max_zoom)])
        
        # Add simplification
        if simplification is not None:
            tippecanoe_cmd.extend(["-S", str(simplification)])
        
        # Add drop rate
        if drop_rate is not None:
            tippecanoe_cmd.extend(["-r", str(drop_rate)])
        
        # Add buffer size
        if buffer_size is not None:
            tippecanoe_cmd.extend(["-b", str(buffer_size)])
        
        # Add common options
        tippecanoe_cmd.extend(["--force", "--read-parallel"])
        
        # Create Kestra workflow
        workflow = {
            "id": safe_name,
            "namespace": "geospatial",
            "description": f"Batch Tippecanoe processing of GeoJSON files in {input_dir}",
            "tasks": [
                {
                    "id": "list_files",
                    "type": "io.kestra.core.tasks.flows.EachFile",
                    "from": input_dir,
                    "filter": ".*\\.geojson$",
                    "tasks": [
                        {
                            "id": "process_file",
                            "type": "io.kestra.core.tasks.flows.Switch",
                            "value": "{{ outputs.extension }}",
                            "cases": {
                                ".geojson": [
                                    {
                                        "id": "create_output_dir",
                                        "type": "io.kestra.core.tasks.scripts.Bash",
                                        "commands": [
                                            f"mkdir -p {output_dir or '/tmp/tippecanoe_output'}"
                                        ]
                                    },
                                    {
                                        "id": "run_tippecanoe",
                                        "type": "io.kestra.core.tasks.scripts.Bash",
                                        "commands": [
                                            " ".join(tippecanoe_cmd) + " {{ outputs.file }}"
                                        ],
                                        "outputFiles": [
                                            {
                                                "name": "tiles",
                                                "path": output_dir or "/tmp/tippecanoe_output"
                                            }
                                        ]
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        
        # Add PMTiles conversion if needed
        if output_format == "pmtiles":
            workflow["tasks"].append({
                "id": "convert_to_pmtiles",
                "type": "io.kestra.core.tasks.scripts.Bash",
                "commands": [
                    "for dir in {{ outputs.list_files.files }}; do",
                    "  name=$(basename \"$dir\" .geojson)",
                    f"  pmtiles convert \"$dir\" \"{output_dir or '/tmp/tippecanoe_output'}/$name.pmtiles\"",
                    "done"
                ]
            })
        
        # Add schedule if provided
        if schedule:
            workflow["schedule"] = {
                "cron": schedule
            }
        
        # Save workflow to file
        workflow_path = os.path.join(TEMP_DIR, f"{safe_name}.yml")
        with open(workflow_path, 'w') as f:
            import yaml
            yaml.dump(workflow, f)
        
        return {
            "workflow_name": safe_name,
            "workflow_path": workflow_path,
            "workflow": workflow,
            "input_dir": input_dir,
            "output_dir": output_dir or "/tmp/tippecanoe_output",
            "output_format": output_format
        }
