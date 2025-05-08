import os
import json
import logging
import requests
import subprocess
import shutil
import tempfile
from typing import Dict, List, Any, Optional, Union, Tuple, BinaryIO
from pathlib import Path
from datetime import datetime

from app.core.martin_config import martin_config

logger = logging.getLogger(__name__)

class MartinService:
    """Service for interacting with Martin MapLibre."""
    
    def __init__(self):
        """Initialize the Martin service."""
        self.server_url = martin_config.server_url
        self.pg_connection_string = martin_config.pg_connection_string
        self.cache_directory = martin_config.cache_directory
        self.pmtiles_directory = martin_config.pmtiles_directory
        self.mbtiles_directory = martin_config.mbtiles_directory
        self.raster_directory = martin_config.raster_directory
        self.terrain_directory = martin_config.terrain_directory
        self.default_style_directory = martin_config.default_style_directory
        self.tippecanoe_path = martin_config.tippecanoe_path
        
        # Create directories if they don't exist
        os.makedirs(self.cache_directory, exist_ok=True)
        os.makedirs(self.pmtiles_directory, exist_ok=True)
        os.makedirs(self.mbtiles_directory, exist_ok=True)
        os.makedirs(self.raster_directory, exist_ok=True)
        os.makedirs(self.terrain_directory, exist_ok=True)
        os.makedirs(self.default_style_directory, exist_ok=True)
    
    def get_server_status(self) -> Dict[str, Any]:
        """
        Get the status of the Martin server.
        
        Returns:
            Server status information
        """
        try:
            response = requests.get(f"{self.server_url}/health")
            response.raise_for_status()
            
            return {
                "status": "ok",
                "version": response.headers.get("Server", "Unknown"),
                "url": self.server_url
            }
        except Exception as e:
            logger.error(f"Error getting Martin server status: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "url": self.server_url
            }
    
    def get_available_tables(self) -> List[Dict[str, Any]]:
        """
        Get a list of available tables from the Martin server.
        
        Returns:
            List of available tables
        """
        try:
            response = requests.get(f"{self.server_url}/index.json")
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error getting available tables: {str(e)}")
            return []
    
    def get_table_metadata(self, table_name: str) -> Dict[str, Any]:
        """
        Get metadata for a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Table metadata
        """
        try:
            response = requests.get(f"{self.server_url}/rpc/meta/{table_name}")
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error getting table metadata: {str(e)}")
            return {}
    
    def get_table_tilejson(self, table_name: str) -> Dict[str, Any]:
        """
        Get TileJSON for a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            TileJSON metadata
        """
        try:
            response = requests.get(f"{self.server_url}/rpc/tilejson/{table_name}.json")
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error getting table TileJSON: {str(e)}")
            return {}
    
    def get_tile(self, table_name: str, z: int, x: int, y: int, format: str = "pbf") -> bytes:
        """
        Get a tile for a table.
        
        Args:
            table_name: Name of the table
            z: Zoom level
            x: X coordinate
            y: Y coordinate
            format: Tile format (pbf, mvt, png, jpg, webp)
            
        Returns:
            Tile data
        """
        try:
            response = requests.get(f"{self.server_url}/tiles/{table_name}/{z}/{x}/{y}.{format}")
            response.raise_for_status()
            
            return response.content
        except Exception as e:
            logger.error(f"Error getting tile: {str(e)}")
            return b""
    
    def get_available_pmtiles(self) -> List[Dict[str, Any]]:
        """
        Get a list of available PMTiles.
        
        Returns:
            List of available PMTiles
        """
        try:
            pmtiles_files = []
            
            for file_path in Path(self.pmtiles_directory).glob("*.pmtiles"):
                file_name = file_path.name
                file_size = file_path.stat().st_size
                file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                
                pmtiles_files.append({
                    "name": file_name,
                    "path": str(file_path),
                    "size": file_size,
                    "modified": file_mtime.isoformat(),
                    "url": f"{self.server_url}/pmtiles/{file_name}"
                })
            
            return pmtiles_files
        except Exception as e:
            logger.error(f"Error getting available PMTiles: {str(e)}")
            return []
    
    def get_available_mbtiles(self) -> List[Dict[str, Any]]:
        """
        Get a list of available MBTiles.
        
        Returns:
            List of available MBTiles
        """
        try:
            mbtiles_files = []
            
            for file_path in Path(self.mbtiles_directory).glob("*.mbtiles"):
                file_name = file_path.name
                file_size = file_path.stat().st_size
                file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                
                mbtiles_files.append({
                    "name": file_name,
                    "path": str(file_path),
                    "size": file_size,
                    "modified": file_mtime.isoformat(),
                    "url": f"{self.server_url}/mbtiles/{file_name}"
                })
            
            return mbtiles_files
        except Exception as e:
            logger.error(f"Error getting available MBTiles: {str(e)}")
            return []
    
    def get_available_raster_tiles(self) -> List[Dict[str, Any]]:
        """
        Get a list of available raster tiles.
        
        Returns:
            List of available raster tiles
        """
        try:
            raster_files = []
            
            for file_path in Path(self.raster_directory).glob("*.tif"):
                file_name = file_path.name
                file_size = file_path.stat().st_size
                file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                
                raster_files.append({
                    "name": file_name,
                    "path": str(file_path),
                    "size": file_size,
                    "modified": file_mtime.isoformat(),
                    "url": f"{self.server_url}/raster/{file_name}"
                })
            
            return raster_files
        except Exception as e:
            logger.error(f"Error getting available raster tiles: {str(e)}")
            return []
    
    def get_available_terrain_tiles(self) -> List[Dict[str, Any]]:
        """
        Get a list of available terrain tiles.
        
        Returns:
            List of available terrain tiles
        """
        try:
            terrain_files = []
            
            for file_path in Path(self.terrain_directory).glob("*.terrain"):
                file_name = file_path.name
                file_size = file_path.stat().st_size
                file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                
                terrain_files.append({
                    "name": file_name,
                    "path": str(file_path),
                    "size": file_size,
                    "modified": file_mtime.isoformat(),
                    "url": f"{self.server_url}/terrain/{file_name}"
                })
            
            return terrain_files
        except Exception as e:
            logger.error(f"Error getting available terrain tiles: {str(e)}")
            return []
    
    def get_available_styles(self) -> List[Dict[str, Any]]:
        """
        Get a list of available styles.
        
        Returns:
            List of available styles
        """
        try:
            style_files = []
            
            for file_path in Path(self.default_style_directory).glob("*.json"):
                file_name = file_path.name
                file_size = file_path.stat().st_size
                file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                
                # Read the style file to get the name and version
                try:
                    with open(file_path, "r") as f:
                        style_data = json.load(f)
                        style_name = style_data.get("name", file_name)
                        style_version = style_data.get("version", "1.0.0")
                except Exception:
                    style_name = file_name
                    style_version = "1.0.0"
                
                style_files.append({
                    "name": style_name,
                    "file_name": file_name,
                    "path": str(file_path),
                    "size": file_size,
                    "modified": file_mtime.isoformat(),
                    "version": style_version,
                    "url": f"{self.server_url}/styles/{file_name}"
                })
            
            return style_files
        except Exception as e:
            logger.error(f"Error getting available styles: {str(e)}")
            return []
    
    def upload_pmtiles(self, file: BinaryIO, file_name: str) -> Dict[str, Any]:
        """
        Upload a PMTiles file.
        
        Args:
            file: File object
            file_name: File name
            
        Returns:
            Upload result
        """
        try:
            # Save the file to the PMTiles directory
            file_path = os.path.join(self.pmtiles_directory, file_name)
            
            with open(file_path, "wb") as f:
                f.write(file.read())
            
            return {
                "status": "success",
                "name": file_name,
                "path": file_path,
                "url": f"{self.server_url}/pmtiles/{file_name}"
            }
        except Exception as e:
            logger.error(f"Error uploading PMTiles: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def upload_mbtiles(self, file: BinaryIO, file_name: str) -> Dict[str, Any]:
        """
        Upload an MBTiles file.
        
        Args:
            file: File object
            file_name: File name
            
        Returns:
            Upload result
        """
        try:
            # Save the file to the MBTiles directory
            file_path = os.path.join(self.mbtiles_directory, file_name)
            
            with open(file_path, "wb") as f:
                f.write(file.read())
            
            return {
                "status": "success",
                "name": file_name,
                "path": file_path,
                "url": f"{self.server_url}/mbtiles/{file_name}"
            }
        except Exception as e:
            logger.error(f"Error uploading MBTiles: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def upload_raster_tiles(self, file: BinaryIO, file_name: str) -> Dict[str, Any]:
        """
        Upload a raster tiles file.
        
        Args:
            file: File object
            file_name: File name
            
        Returns:
            Upload result
        """
        try:
            # Save the file to the raster directory
            file_path = os.path.join(self.raster_directory, file_name)
            
            with open(file_path, "wb") as f:
                f.write(file.read())
            
            return {
                "status": "success",
                "name": file_name,
                "path": file_path,
                "url": f"{self.server_url}/raster/{file_name}"
            }
        except Exception as e:
            logger.error(f"Error uploading raster tiles: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def upload_terrain_tiles(self, file: BinaryIO, file_name: str) -> Dict[str, Any]:
        """
        Upload a terrain tiles file.
        
        Args:
            file: File object
            file_name: File name
            
        Returns:
            Upload result
        """
        try:
            # Save the file to the terrain directory
            file_path = os.path.join(self.terrain_directory, file_name)
            
            with open(file_path, "wb") as f:
                f.write(file.read())
            
            return {
                "status": "success",
                "name": file_name,
                "path": file_path,
                "url": f"{self.server_url}/terrain/{file_name}"
            }
        except Exception as e:
            logger.error(f"Error uploading terrain tiles: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def upload_style(self, file: BinaryIO, file_name: str) -> Dict[str, Any]:
        """
        Upload a style file.
        
        Args:
            file: File object
            file_name: File name
            
        Returns:
            Upload result
        """
        try:
            # Save the file to the style directory
            file_path = os.path.join(self.default_style_directory, file_name)
            
            with open(file_path, "wb") as f:
                file_content = file.read()
                f.write(file_content)
            
            # Read the style file to get the name and version
            try:
                style_data = json.loads(file_content.decode("utf-8"))
                style_name = style_data.get("name", file_name)
                style_version = style_data.get("version", "1.0.0")
            except Exception:
                style_name = file_name
                style_version = "1.0.0"
            
            return {
                "status": "success",
                "name": style_name,
                "file_name": file_name,
                "path": file_path,
                "version": style_version,
                "url": f"{self.server_url}/styles/{file_name}"
            }
        except Exception as e:
            logger.error(f"Error uploading style: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def delete_pmtiles(self, file_name: str) -> Dict[str, Any]:
        """
        Delete a PMTiles file.
        
        Args:
            file_name: File name
            
        Returns:
            Delete result
        """
        try:
            # Delete the file from the PMTiles directory
            file_path = os.path.join(self.pmtiles_directory, file_name)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                return {
                    "status": "success",
                    "name": file_name
                }
            else:
                return {
                    "status": "error",
                    "error": f"File {file_name} not found"
                }
        except Exception as e:
            logger.error(f"Error deleting PMTiles: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def delete_mbtiles(self, file_name: str) -> Dict[str, Any]:
        """
        Delete an MBTiles file.
        
        Args:
            file_name: File name
            
        Returns:
            Delete result
        """
        try:
            # Delete the file from the MBTiles directory
            file_path = os.path.join(self.mbtiles_directory, file_name)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                return {
                    "status": "success",
                    "name": file_name
                }
            else:
                return {
                    "status": "error",
                    "error": f"File {file_name} not found"
                }
        except Exception as e:
            logger.error(f"Error deleting MBTiles: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def delete_raster_tiles(self, file_name: str) -> Dict[str, Any]:
        """
        Delete a raster tiles file.
        
        Args:
            file_name: File name
            
        Returns:
            Delete result
        """
        try:
            # Delete the file from the raster directory
            file_path = os.path.join(self.raster_directory, file_name)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                return {
                    "status": "success",
                    "name": file_name
                }
            else:
                return {
                    "status": "error",
                    "error": f"File {file_name} not found"
                }
        except Exception as e:
            logger.error(f"Error deleting raster tiles: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def delete_terrain_tiles(self, file_name: str) -> Dict[str, Any]:
        """
        Delete a terrain tiles file.
        
        Args:
            file_name: File name
            
        Returns:
            Delete result
        """
        try:
            # Delete the file from the terrain directory
            file_path = os.path.join(self.terrain_directory, file_name)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                return {
                    "status": "success",
                    "name": file_name
                }
            else:
                return {
                    "status": "error",
                    "error": f"File {file_name} not found"
                }
        except Exception as e:
            logger.error(f"Error deleting terrain tiles: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def delete_style(self, file_name: str) -> Dict[str, Any]:
        """
        Delete a style file.
        
        Args:
            file_name: File name
            
        Returns:
            Delete result
        """
        try:
            # Delete the file from the style directory
            file_path = os.path.join(self.default_style_directory, file_name)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                return {
                    "status": "success",
                    "name": file_name
                }
            else:
                return {
                    "status": "error",
                    "error": f"File {file_name} not found"
                }
        except Exception as e:
            logger.error(f"Error deleting style: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def create_pmtiles_from_geojson(self, geojson_data: Dict[str, Any], output_name: str, min_zoom: int = 0, max_zoom: int = 14) -> Dict[str, Any]:
        """
        Create PMTiles from GeoJSON data using Tippecanoe.
        
        Args:
            geojson_data: GeoJSON data
            output_name: Output file name
            min_zoom: Minimum zoom level
            max_zoom: Maximum zoom level
            
        Returns:
            Creation result
        """
        if not martin_config.is_tippecanoe_available:
            return {
                "status": "error",
                "error": "Tippecanoe is not available"
            }
        
        try:
            # Create a temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Write the GeoJSON data to a temporary file
                geojson_path = os.path.join(temp_dir, "data.geojson")
                with open(geojson_path, "w") as f:
                    json.dump(geojson_data, f)
                
                # Create the output path
                output_path = os.path.join(self.pmtiles_directory, output_name)
                
                # Run Tippecanoe to create PMTiles
                cmd = [
                    self.tippecanoe_path,
                    "-o", output_path,
                    "-z", str(max_zoom),
                    "-Z", str(min_zoom),
                    "--force",
                    geojson_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    return {
                        "status": "error",
                        "error": f"Tippecanoe error: {result.stderr}"
                    }
                
                return {
                    "status": "success",
                    "name": output_name,
                    "path": output_path,
                    "url": f"{self.server_url}/pmtiles/{output_name}"
                }
        except Exception as e:
            logger.error(f"Error creating PMTiles from GeoJSON: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def create_style_from_source(self, source_url: str, source_type: str, source_name: str, output_name: str) -> Dict[str, Any]:
        """
        Create a MapLibre style from a source.
        
        Args:
            source_url: Source URL
            source_type: Source type (vector, raster, terrain)
            source_name: Source name
            output_name: Output file name
            
        Returns:
            Creation result
        """
        try:
            # Create a basic style
            style = {
                "version": 8,
                "name": source_name,
                "sources": {
                    source_name: {
                        "type": source_type,
                        "url": source_url
                    }
                },
                "layers": []
            }
            
            # Add default layers based on source type
            if source_type == "vector":
                # Get the TileJSON to get the vector layers
                try:
                    response = requests.get(source_url)
                    response.raise_for_status()
                    
                    tilejson = response.json()
                    vector_layers = tilejson.get("vector_layers", [])
                    
                    for layer in vector_layers:
                        layer_id = layer.get("id")
                        layer_type = "fill"
                        
                        if "point" in layer_id.lower():
                            layer_type = "circle"
                        elif "line" in layer_id.lower():
                            layer_type = "line"
                        
                        style["layers"].append({
                            "id": layer_id,
                            "type": layer_type,
                            "source": source_name,
                            "source-layer": layer_id,
                            "paint": {}
                        })
                except Exception as e:
                    logger.warning(f"Error getting TileJSON for vector source: {str(e)}")
                    
                    # Add a default layer
                    style["layers"].append({
                        "id": "default",
                        "type": "fill",
                        "source": source_name,
                        "paint": {}
                    })
            elif source_type == "raster":
                style["layers"].append({
                    "id": "raster",
                    "type": "raster",
                    "source": source_name,
                    "paint": {}
                })
            elif source_type == "terrain":
                style["layers"].append({
                    "id": "terrain",
                    "type": "hillshade",
                    "source": source_name,
                    "paint": {}
                })
            
            # Save the style to the style directory
            output_path = os.path.join(self.default_style_directory, output_name)
            
            with open(output_path, "w") as f:
                json.dump(style, f, indent=2)
            
            return {
                "status": "success",
                "name": source_name,
                "file_name": output_name,
                "path": output_path,
                "version": "8",
                "url": f"{self.server_url}/styles/{output_name}"
            }
        except Exception as e:
            logger.error(f"Error creating style from source: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

# Create a global instance of MartinService
martin_service = MartinService()
