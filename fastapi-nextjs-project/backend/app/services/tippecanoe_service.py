import os
import json
import subprocess
import tempfile
import logging
import shutil
from typing import List, Dict, Any, Optional, Union
from fastapi import HTTPException, UploadFile
import asyncio
from pathlib import Path

logger = logging.getLogger(__name__)

# Define storage paths
TIPPECANOE_OUTPUT_DIR = os.environ.get("TIPPECANOE_OUTPUT_DIR", "./data/tippecanoe")
GEOJSON_DIR = os.environ.get("GEOJSON_DIR", "./data/geojson")
PMTILES_DIR = os.environ.get("PMTILES_DIR", "./data/pmtiles")
MBTILES_DIR = os.environ.get("MBTILES_DIR", "./data/mbtiles")
GPKG_DIR = os.environ.get("GPKG_DIR", "./data/gpkg")

# Ensure directories exist
os.makedirs(TIPPECANOE_OUTPUT_DIR, exist_ok=True)
os.makedirs(GEOJSON_DIR, exist_ok=True)
os.makedirs(PMTILES_DIR, exist_ok=True)
os.makedirs(MBTILES_DIR, exist_ok=True)
os.makedirs(GPKG_DIR, exist_ok=True)


class TippecanoeService:
    """Service for Tippecanoe operations and tile format conversions"""
    
    @staticmethod
    async def run_tippecanoe(
        input_files: List[str],
        output_format: str = "pmtiles",
        output_name: str = "output",
        min_zoom: Optional[int] = None,
        max_zoom: Optional[int] = None,
        layer_name: Optional[str] = None,
        simplification: Optional[float] = None,
        drop_rate: Optional[float] = None,
        buffer_size: Optional[int] = None,
        additional_args: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Run Tippecanoe to generate vector tiles
        
        Args:
            input_files: List of input GeoJSON file paths
            output_format: Output format ('pmtiles' or 'mbtiles')
            output_name: Name for the output file
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
        
        # Validate input files
        for file_path in input_files:
            if not os.path.exists(file_path):
                raise HTTPException(status_code=400, detail=f"Input file not found: {file_path}")
            
            if not file_path.endswith(".geojson") and not file_path.endswith(".json"):
                raise HTTPException(status_code=400, detail=f"Input file must be GeoJSON: {file_path}")
        
        # Sanitize output name
        safe_name = "".join(c if c.isalnum() or c in ['-', '_'] else '_' for c in output_name)
        
        # Determine output file path
        output_dir = PMTILES_DIR if output_format == "pmtiles" else MBTILES_DIR
        output_extension = ".pmtiles" if output_format == "pmtiles" else ".mbtiles"
        output_path = os.path.join(output_dir, f"{safe_name}{output_extension}")
        
        # Check if output file already exists
        if os.path.exists(output_path):
            raise HTTPException(status_code=400, detail=f"Output file already exists: {output_path}")
        
        try:
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
            
            # Add input files
            cmd.extend(input_files)
            
            # Create temporary directory for PMTiles output
            temp_dir = None
            if output_format == "pmtiles":
                temp_dir = tempfile.mkdtemp(dir=TIPPECANOE_OUTPUT_DIR)
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
                logger.error(f"Tippecanoe error: {error_message}")
                raise HTTPException(status_code=500, detail=f"Tippecanoe error: {error_message}")
            
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
                    logger.error(f"PMTiles conversion error: {error_message}")
                    raise HTTPException(status_code=500, detail=f"PMTiles conversion error: {error_message}")
                
                # Clean up temporary directory
                shutil.rmtree(temp_dir)
            
            # Extract metadata
            metadata = await TippecanoeService.extract_tile_metadata(output_path, output_format)
            
            return {
                "name": safe_name,
                "output_format": output_format,
                "output_path": output_path,
                "size_bytes": os.path.getsize(output_path),
                "input_files": input_files,
                "metadata": metadata
            }
        
        except Exception as e:
            # Clean up on error
            if output_format == "pmtiles" and temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            
            if os.path.exists(output_path):
                os.remove(output_path)
            
            logger.error(f"Error running Tippecanoe: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error running Tippecanoe: {str(e)}")
    
    @staticmethod
    async def upload_geojson(
        file: UploadFile,
        name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload a GeoJSON file for processing with Tippecanoe
        
        Args:
            file: The uploaded GeoJSON file
            name: Optional name for the file (defaults to the uploaded filename)
            
        Returns:
            Dictionary with information about the uploaded file
        """
        if not file.filename.endswith((".geojson", ".json")):
            raise HTTPException(status_code=400, detail="File must have .geojson or .json extension")
        
        # Determine file name
        if name:
            safe_name = "".join(c if c.isalnum() or c in ['-', '_'] else '_' for c in name)
            file_name = f"{safe_name}.geojson"
        else:
            file_name = file.filename
        
        file_path = os.path.join(GEOJSON_DIR, file_name)
        
        # Check if file already exists
        if os.path.exists(file_path):
            raise HTTPException(status_code=400, detail=f"File already exists: {file_path}")
        
        try:
            # Save the uploaded file
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            # Validate GeoJSON
            try:
                with open(file_path, "r") as f:
                    geojson = json.load(f)
                
                if "type" not in geojson or geojson["type"] not in ["FeatureCollection", "Feature"]:
                    raise ValueError("Invalid GeoJSON: missing or invalid 'type' field")
                
                if geojson["type"] == "FeatureCollection" and "features" not in geojson:
                    raise ValueError("Invalid FeatureCollection: missing 'features' field")
                
                # Count features
                feature_count = len(geojson["features"]) if geojson["type"] == "FeatureCollection" else 1
                
                # Get bounding box
                bbox = geojson.get("bbox")
                
                return {
                    "name": os.path.splitext(file_name)[0],
                    "file_path": file_path,
                    "size_bytes": os.path.getsize(file_path),
                    "feature_count": feature_count,
                    "bbox": bbox
                }
            
            except json.JSONDecodeError:
                os.remove(file_path)
                raise HTTPException(status_code=400, detail="Invalid JSON file")
            except ValueError as e:
                os.remove(file_path)
                raise HTTPException(status_code=400, detail=str(e))
        
        except Exception as e:
            # Clean up on error
            if os.path.exists(file_path):
                os.remove(file_path)
            
            logger.error(f"Error uploading GeoJSON: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error uploading GeoJSON: {str(e)}")
    
    @staticmethod
    async def convert_to_gpkg(
        source_path: str,
        source_type: str,
        output_name: Optional[str] = None,
        zoom_levels: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Convert MBTiles or PMTiles to GeoPackage
        
        Args:
            source_path: Path to the source tile file
            source_type: Type of source file ('pmtiles' or 'mbtiles')
            output_name: Name for the output GeoPackage file
            zoom_levels: List of zoom levels to include
            
        Returns:
            Dictionary with information about the generated GeoPackage
        """
        if source_type not in ["pmtiles", "mbtiles"]:
            raise HTTPException(status_code=400, detail=f"Unsupported source type: {source_type}")
        
        if not os.path.exists(source_path):
            raise HTTPException(status_code=400, detail=f"Source file not found: {source_path}")
        
        # Determine output name
        if output_name:
            safe_name = "".join(c if c.isalnum() or c in ['-', '_'] else '_' for c in output_name)
        else:
            safe_name = os.path.splitext(os.path.basename(source_path))[0]
        
        output_path = os.path.join(GPKG_DIR, f"{safe_name}.gpkg")
        
        # Check if output file already exists
        if os.path.exists(output_path):
            raise HTTPException(status_code=400, detail=f"Output file already exists: {output_path}")
        
        try:
            # For PMTiles, first convert to MBTiles
            temp_mbtiles_path = None
            if source_type == "pmtiles":
                temp_mbtiles_path = os.path.join(TIPPECANOE_OUTPUT_DIR, f"{safe_name}_temp.mbtiles")
                
                pmtiles_cmd = ["pmtiles", "convert", source_path, temp_mbtiles_path]
                pmtiles_process = await asyncio.create_subprocess_exec(
                    *pmtiles_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                pmtiles_stdout, pmtiles_stderr = await pmtiles_process.communicate()
                
                if pmtiles_process.returncode != 0:
                    error_message = pmtiles_stderr.decode() if pmtiles_stderr else "Unknown error"
                    logger.error(f"PMTiles to MBTiles conversion error: {error_message}")
                    raise HTTPException(status_code=500, detail=f"PMTiles to MBTiles conversion error: {error_message}")
                
                source_path = temp_mbtiles_path
            
            # Run the tiles_to_gpkg.py script
            script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "gpkg", "tiles_to_gpkg.py")
            
            cmd = ["python", script_path, source_path, output_path]
            
            # Add zoom levels if specified
            if zoom_levels:
                cmd.extend(["--zoom-levels", ",".join(map(str, zoom_levels))])
            
            # Run the conversion script
            logger.info(f"Running conversion command: {' '.join(cmd)}")
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_message = stderr.decode() if stderr else "Unknown error"
                logger.error(f"Conversion error: {error_message}")
                raise HTTPException(status_code=500, detail=f"Conversion error: {error_message}")
            
            # Clean up temporary MBTiles file
            if temp_mbtiles_path and os.path.exists(temp_mbtiles_path):
                os.remove(temp_mbtiles_path)
            
            # Get GeoPackage metadata
            metadata = await TippecanoeService.extract_gpkg_metadata(output_path)
            
            return {
                "name": safe_name,
                "source_type": source_type,
                "source_path": source_path if source_type == "mbtiles" else source_path,
                "output_path": output_path,
                "size_bytes": os.path.getsize(output_path),
                "metadata": metadata
            }
        
        except Exception as e:
            # Clean up on error
            if temp_mbtiles_path and os.path.exists(temp_mbtiles_path):
                os.remove(temp_mbtiles_path)
            
            if os.path.exists(output_path):
                os.remove(output_path)
            
            logger.error(f"Error converting to GeoPackage: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error converting to GeoPackage: {str(e)}")
    
    @staticmethod
    async def extract_tile_metadata(file_path: str, file_type: str) -> Dict[str, Any]:
        """
        Extract metadata from a tile file
        
        Args:
            file_path: Path to the tile file
            file_type: Type of tile file ('pmtiles' or 'mbtiles')
            
        Returns:
            Dictionary with metadata
        """
        metadata = {
            "name": os.path.basename(file_path).split('.')[0],
            "type": file_type
        }
        
        try:
            if file_type == "pmtiles":
                # Use pmtiles CLI tool to extract metadata
                result = subprocess.run(
                    ["pmtiles", "info", file_path],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                # Parse JSON output
                info = json.loads(result.stdout)
                
                # Extract relevant metadata
                metadata.update({
                    "minzoom": info.get("minzoom", 0),
                    "maxzoom": info.get("maxzoom", 14),
                    "center": info.get("center", [0, 0, 0]),
                    "bounds": info.get("bounds", [-180, -85.0511, 180, 85.0511]),
                    "format": info.get("tileType", "pbf"),
                    "description": info.get("description", ""),
                    "attribution": info.get("attribution", ""),
                    "tile_type": "vector" if info.get("tileType") == "pbf" else "raster",
                    "layers": info.get("vector_layers", [])
                })
            
            elif file_type == "mbtiles":
                # Use sqlite3 to extract metadata
                import sqlite3
                
                conn = sqlite3.connect(file_path)
                cursor = conn.cursor()
                
                # Get metadata table
                cursor.execute("SELECT name, value FROM metadata")
                rows = cursor.fetchall()
                
                for name, value in rows:
                    if name in ["name", "description", "attribution", "minzoom", "maxzoom", "center", "bounds", "format", "json"]:
                        if name in ["minzoom", "maxzoom"]:
                            metadata[name] = int(value)
                        elif name in ["center", "bounds"]:
                            metadata[name] = [float(x) for x in value.split(",")]
                        elif name == "json":
                            try:
                                json_data = json.loads(value)
                                if "vector_layers" in json_data:
                                    metadata["layers"] = json_data["vector_layers"]
                            except:
                                pass
                        else:
                            metadata[name] = value
                
                # Determine tile type (vector or raster)
                cursor.execute("SELECT value FROM metadata WHERE name='format'")
                format_row = cursor.fetchone()
                if format_row:
                    format_value = format_row[0]
                    metadata["format"] = format_value
                    metadata["tile_type"] = "vector" if format_value == "pbf" else "raster"
                else:
                    metadata["tile_type"] = "raster"  # Default to raster if not specified
                
                conn.close()
            
            return metadata
        
        except Exception as e:
            logger.error(f"Error extracting metadata from tile file: {str(e)}")
            return metadata
    
    @staticmethod
    async def extract_gpkg_metadata(file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from a GeoPackage file
        
        Args:
            file_path: Path to the GeoPackage file
            
        Returns:
            Dictionary with metadata
        """
        metadata = {
            "name": os.path.basename(file_path).split('.')[0],
            "type": "gpkg"
        }
        
        try:
            import sqlite3
            
            conn = sqlite3.connect(file_path)
            cursor = conn.cursor()
            
            # Check if this is a tile GeoPackage
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='gpkg_tile_matrix_set'")
            if cursor.fetchone():
                metadata["has_tiles"] = True
                
                # Get tile matrix sets
                cursor.execute("SELECT table_name, srs_id, min_x, min_y, max_x, max_y FROM gpkg_tile_matrix_set")
                tile_matrix_sets = []
                for row in cursor.fetchall():
                    table_name, srs_id, min_x, min_y, max_x, max_y = row
                    
                    # Get zoom levels for this tile matrix set
                    cursor.execute("SELECT zoom_level, matrix_width, matrix_height, tile_width, tile_height FROM gpkg_tile_matrix WHERE table_name=? ORDER BY zoom_level", (table_name,))
                    zoom_levels = []
                    for zoom_row in cursor.fetchall():
                        zoom_level, matrix_width, matrix_height, tile_width, tile_height = zoom_row
                        zoom_levels.append({
                            "zoom_level": zoom_level,
                            "matrix_width": matrix_width,
                            "matrix_height": matrix_height,
                            "tile_width": tile_width,
                            "tile_height": tile_height
                        })
                    
                    tile_matrix_sets.append({
                        "table_name": table_name,
                        "srs_id": srs_id,
                        "bounds": [min_x, min_y, max_x, max_y],
                        "zoom_levels": zoom_levels
                    })
                
                metadata["tile_matrix_sets"] = tile_matrix_sets
                
                # Get min/max zoom
                if tile_matrix_sets and tile_matrix_sets[0]["zoom_levels"]:
                    metadata["minzoom"] = min(level["zoom_level"] for tms in tile_matrix_sets for level in tms["zoom_levels"])
                    metadata["maxzoom"] = max(level["zoom_level"] for tms in tile_matrix_sets for level in tms["zoom_levels"])
            else:
                metadata["has_tiles"] = False
            
            # Check if this is a feature GeoPackage
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='gpkg_geometry_columns'")
            if cursor.fetchone():
                metadata["has_features"] = True
                
                # Get feature tables
                cursor.execute("SELECT table_name, column_name, geometry_type_name, srs_id, z, m FROM gpkg_geometry_columns")
                feature_tables = []
                for row in cursor.fetchall():
                    table_name, column_name, geometry_type_name, srs_id, z, m = row
                    
                    # Get feature count
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        feature_count = cursor.fetchone()[0]
                    except:
                        feature_count = None
                    
                    feature_tables.append({
                        "table_name": table_name,
                        "geometry_column": column_name,
                        "geometry_type": geometry_type_name,
                        "srs_id": srs_id,
                        "feature_count": feature_count
                    })
                
                metadata["feature_tables"] = feature_tables
            else:
                metadata["has_features"] = False
            
            conn.close()
            
            return metadata
        
        except Exception as e:
            logger.error(f"Error extracting metadata from GeoPackage: {str(e)}")
            return metadata
