import os
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from app.core.config import settings

class MartinConfig(BaseModel):
    """Configuration for Martin MapLibre integration."""
    
    # Martin server settings
    server_url: str = os.getenv("MARTIN_SERVER_URL", "http://localhost:3000")
    
    # Database connection settings
    pg_connection_string: str = os.getenv(
        "MARTIN_PG_CONNECTION_STRING", 
        "postgresql://postgres:postgres@localhost:5432/postgres"
    )
    
    # Tile cache settings
    cache_directory: str = os.getenv(
        "MARTIN_CACHE_DIRECTORY", 
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data/martin/cache")
    )
    
    # Tile settings
    default_tile_format: str = os.getenv("MARTIN_DEFAULT_TILE_FORMAT", "pbf")
    
    # PMTiles settings
    pmtiles_directory: str = os.getenv(
        "MARTIN_PMTILES_DIRECTORY", 
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data/martin/pmtiles")
    )
    
    # MBTiles settings
    mbtiles_directory: str = os.getenv(
        "MARTIN_MBTILES_DIRECTORY", 
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data/martin/mbtiles")
    )
    
    # Raster tiles settings
    raster_directory: str = os.getenv(
        "MARTIN_RASTER_DIRECTORY", 
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data/martin/raster")
    )
    
    # Terrain tiles settings
    terrain_directory: str = os.getenv(
        "MARTIN_TERRAIN_DIRECTORY", 
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data/martin/terrain")
    )
    
    # Default style settings
    default_style_directory: str = os.getenv(
        "MARTIN_DEFAULT_STYLE_DIRECTORY", 
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data/martin/styles")
    )
    
    # Tippecanoe settings
    tippecanoe_path: str = os.getenv("TIPPECANOE_PATH", "tippecanoe")
    
    # Function to check if Martin is configured
    @property
    def is_configured(self) -> bool:
        """Check if Martin is configured."""
        return bool(self.server_url and self.pg_connection_string)
    
    # Function to check if Tippecanoe is available
    @property
    def is_tippecanoe_available(self) -> bool:
        """Check if Tippecanoe is available."""
        try:
            import subprocess
            result = subprocess.run([self.tippecanoe_path, "--version"], capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False

# Create a global instance of MartinConfig
martin_config = MartinConfig()

# Create required directories
os.makedirs(martin_config.cache_directory, exist_ok=True)
os.makedirs(martin_config.pmtiles_directory, exist_ok=True)
os.makedirs(martin_config.mbtiles_directory, exist_ok=True)
os.makedirs(martin_config.raster_directory, exist_ok=True)
os.makedirs(martin_config.terrain_directory, exist_ok=True)
os.makedirs(martin_config.default_style_directory, exist_ok=True)
