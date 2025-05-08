import os
import shutil
import json
import logging
import aiofiles
import subprocess
from typing import List, Dict, Any, Optional
from fastapi import UploadFile, HTTPException
from pathlib import Path

logger = logging.getLogger(__name__)

# Define tile storage paths
PMTILES_DIR = os.environ.get("PMTILES_DIR", "./data/pmtiles")
MBTILES_DIR = os.environ.get("MBTILES_DIR", "./data/mbtiles")
MARTIN_CONFIG_DIR = os.environ.get("MARTIN_CONFIG_DIR", "./config/martin")
MARTIN_URL = os.environ.get("MARTIN_URL", "http://localhost:3001")

# Ensure directories exist
os.makedirs(PMTILES_DIR, exist_ok=True)
os.makedirs(MBTILES_DIR, exist_ok=True)
os.makedirs(MARTIN_CONFIG_DIR, exist_ok=True)


class TileService:
    """Service for managing tile files (PMTiles, MBTiles)"""
    
    @staticmethod
    async def upload_tile_file(
        file: UploadFile,
        tile_type: str,
        name: str,
        description: Optional[str] = None,
        attribution: Optional[str] = None,
        min_zoom: Optional[int] = None,
        max_zoom: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Upload a tile file (PMTiles or MBTiles)
        
        Args:
            file: The uploaded file
            tile_type: Type of tile file ('pmtiles' or 'mbtiles')
            name: Name for the tile source
            description: Description of the tile source
            attribution: Attribution for the tile source
            min_zoom: Minimum zoom level
            max_zoom: Maximum zoom level
            
        Returns:
            Dictionary with metadata about the uploaded tile file
        """
        if tile_type not in ["pmtiles", "mbtiles"]:
            raise HTTPException(status_code=400, detail=f"Unsupported tile type: {tile_type}")
        
        # Determine target directory
        target_dir = PMTILES_DIR if tile_type == "pmtiles" else MBTILES_DIR
        
        # Sanitize filename
        safe_name = "".join(c if c.isalnum() or c in ['-', '_'] else '_' for c in name)
        file_extension = ".pmtiles" if tile_type == "pmtiles" else ".mbtiles"
        filename = f"{safe_name}{file_extension}"
        file_path = os.path.join(target_dir, filename)
        
        # Check if file already exists
        if os.path.exists(file_path):
            raise HTTPException(status_code=400, detail=f"A tile file with name '{name}' already exists")
        
        try:
            # Save the uploaded file
            async with aiofiles.open(file_path, 'wb') as out_file:
                content = await file.read()
                await out_file.write(content)
            
            # Extract metadata from the tile file
            metadata = await TileService.extract_tile_metadata(file_path, tile_type)
            
            # Update metadata with provided values
            if description:
                metadata["description"] = description
            if attribution:
                metadata["attribution"] = attribution
            if min_zoom is not None:
                metadata["minzoom"] = min_zoom
            if max_zoom is not None:
                metadata["maxzoom"] = max_zoom
            
            # Add to Martin configuration
            await TileService.update_martin_config(safe_name, tile_type, metadata)
            
            return {
                "name": safe_name,
                "original_name": name,
                "file_path": file_path,
                "tile_type": tile_type,
                "size_bytes": os.path.getsize(file_path),
                "url": f"{MARTIN_URL}/tiles/{safe_name}/{{z}}/{{x}}/{{y}}.pbf" if tile_type == "pmtiles" or metadata.get("format") == "pbf" else f"{MARTIN_URL}/tiles/{safe_name}/{{z}}/{{x}}/{{y}}.png",
                "metadata": metadata
            }
        
        except Exception as e:
            # Clean up on error
            if os.path.exists(file_path):
                os.remove(file_path)
            logger.error(f"Error uploading tile file: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error uploading tile file: {str(e)}")
    
    @staticmethod
    async def extract_tile_metadata(file_path: str, tile_type: str) -> Dict[str, Any]:
        """
        Extract metadata from a tile file
        
        Args:
            file_path: Path to the tile file
            tile_type: Type of tile file ('pmtiles' or 'mbtiles')
            
        Returns:
            Dictionary with metadata
        """
        metadata = {
            "name": os.path.basename(file_path).split('.')[0],
            "type": tile_type
        }
        
        try:
            if tile_type == "pmtiles":
                # Use pmtiles CLI tool to extract metadata
                # This requires pmtiles to be installed: npm install -g pmtiles
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
            
            elif tile_type == "mbtiles":
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
    async def update_martin_config(name: str, tile_type: str, metadata: Dict[str, Any]) -> None:
        """
        Update Martin configuration to include the new tile source
        
        Args:
            name: Name of the tile source
            tile_type: Type of tile file ('pmtiles' or 'mbtiles')
            metadata: Metadata for the tile source
        """
        config_file = os.path.join(MARTIN_CONFIG_DIR, "config.json")
        
        # Load existing config or create new one
        config = {}
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
            except:
                config = {}
        
        # Initialize sections if they don't exist
        if "pmtiles" not in config:
            config["pmtiles"] = {}
        if "mbtiles" not in config:
            config["mbtiles"] = {}
        
        # Add the new source
        source_config = {
            "path": os.path.join(PMTILES_DIR if tile_type == "pmtiles" else MBTILES_DIR, f"{name}.{tile_type}"),
            "type": metadata.get("tile_type", "vector"),
            "attribution": metadata.get("attribution", ""),
            "minzoom": metadata.get("minzoom", 0),
            "maxzoom": metadata.get("maxzoom", 14)
        }
        
        config[tile_type][name] = source_config
        
        # Save the updated config
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    @staticmethod
    async def list_tile_sources() -> List[Dict[str, Any]]:
        """
        List all available tile sources
        
        Returns:
            List of dictionaries with tile source information
        """
        sources = []
        
        # List PMTiles sources
        for filename in os.listdir(PMTILES_DIR):
            if filename.endswith(".pmtiles"):
                file_path = os.path.join(PMTILES_DIR, filename)
                name = filename.split('.')[0]
                
                try:
                    metadata = await TileService.extract_tile_metadata(file_path, "pmtiles")
                    
                    sources.append({
                        "name": name,
                        "file_path": file_path,
                        "tile_type": "pmtiles",
                        "size_bytes": os.path.getsize(file_path),
                        "url": f"{MARTIN_URL}/tiles/{name}/{{z}}/{{x}}/{{y}}.pbf" if metadata.get("tile_type") == "vector" else f"{MARTIN_URL}/tiles/{name}/{{z}}/{{x}}/{{y}}.png",
                        "metadata": metadata
                    })
                except Exception as e:
                    logger.error(f"Error processing PMTiles file {filename}: {str(e)}")
        
        # List MBTiles sources
        for filename in os.listdir(MBTILES_DIR):
            if filename.endswith(".mbtiles"):
                file_path = os.path.join(MBTILES_DIR, filename)
                name = filename.split('.')[0]
                
                try:
                    metadata = await TileService.extract_tile_metadata(file_path, "mbtiles")
                    
                    sources.append({
                        "name": name,
                        "file_path": file_path,
                        "tile_type": "mbtiles",
                        "size_bytes": os.path.getsize(file_path),
                        "url": f"{MARTIN_URL}/tiles/{name}/{{z}}/{{x}}/{{y}}.pbf" if metadata.get("tile_type") == "vector" else f"{MARTIN_URL}/tiles/{name}/{{z}}/{{x}}/{{y}}.png",
                        "metadata": metadata
                    })
                except Exception as e:
                    logger.error(f"Error processing MBTiles file {filename}: {str(e)}")
        
        return sources
    
    @staticmethod
    async def delete_tile_source(name: str) -> Dict[str, Any]:
        """
        Delete a tile source
        
        Args:
            name: Name of the tile source
            
        Returns:
            Dictionary with result information
        """
        # Check PMTiles
        pmtiles_path = os.path.join(PMTILES_DIR, f"{name}.pmtiles")
        if os.path.exists(pmtiles_path):
            os.remove(pmtiles_path)
            await TileService.remove_from_martin_config(name, "pmtiles")
            return {"success": True, "name": name, "tile_type": "pmtiles"}
        
        # Check MBTiles
        mbtiles_path = os.path.join(MBTILES_DIR, f"{name}.mbtiles")
        if os.path.exists(mbtiles_path):
            os.remove(mbtiles_path)
            await TileService.remove_from_martin_config(name, "mbtiles")
            return {"success": True, "name": name, "tile_type": "mbtiles"}
        
        raise HTTPException(status_code=404, detail=f"Tile source '{name}' not found")
    
    @staticmethod
    async def remove_from_martin_config(name: str, tile_type: str) -> None:
        """
        Remove a tile source from Martin configuration
        
        Args:
            name: Name of the tile source
            tile_type: Type of tile file ('pmtiles' or 'mbtiles')
        """
        config_file = os.path.join(MARTIN_CONFIG_DIR, "config.json")
        
        if not os.path.exists(config_file):
            return
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            if tile_type in config and name in config[tile_type]:
                del config[tile_type][name]
                
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Error removing tile source from Martin config: {str(e)}")
    
    @staticmethod
    async def get_tile_source(name: str) -> Dict[str, Any]:
        """
        Get information about a specific tile source
        
        Args:
            name: Name of the tile source
            
        Returns:
            Dictionary with tile source information
        """
        # Check PMTiles
        pmtiles_path = os.path.join(PMTILES_DIR, f"{name}.pmtiles")
        if os.path.exists(pmtiles_path):
            metadata = await TileService.extract_tile_metadata(pmtiles_path, "pmtiles")
            
            return {
                "name": name,
                "file_path": pmtiles_path,
                "tile_type": "pmtiles",
                "size_bytes": os.path.getsize(pmtiles_path),
                "url": f"{MARTIN_URL}/tiles/{name}/{{z}}/{{x}}/{{y}}.pbf" if metadata.get("tile_type") == "vector" else f"{MARTIN_URL}/tiles/{name}/{{z}}/{{x}}/{{y}}.png",
                "metadata": metadata
            }
        
        # Check MBTiles
        mbtiles_path = os.path.join(MBTILES_DIR, f"{name}.mbtiles")
        if os.path.exists(mbtiles_path):
            metadata = await TileService.extract_tile_metadata(mbtiles_path, "mbtiles")
            
            return {
                "name": name,
                "file_path": mbtiles_path,
                "tile_type": "mbtiles",
                "size_bytes": os.path.getsize(mbtiles_path),
                "url": f"{MARTIN_URL}/tiles/{name}/{{z}}/{{x}}/{{y}}.pbf" if metadata.get("tile_type") == "vector" else f"{MARTIN_URL}/tiles/{name}/{{z}}/{{x}}/{{y}}.png",
                "metadata": metadata
            }
        
        raise HTTPException(status_code=404, detail=f"Tile source '{name}' not found")
