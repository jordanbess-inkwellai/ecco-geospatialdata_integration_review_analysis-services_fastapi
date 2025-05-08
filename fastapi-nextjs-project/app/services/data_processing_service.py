import os
import json
import tempfile
import shutil
from typing import Dict, List, Any, Optional, Union
import geopandas as gpd
import pandas as pd
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from shapely.geometry import shape, mapping
import fiona
from fiona.crs import from_epsg
import pyproj
from pyproj import CRS
import numpy as np
from fastapi import UploadFile, HTTPException
import logging

logger = logging.getLogger(__name__)

class DataProcessingService:
    """Service for processing geospatial data."""
    
    def __init__(self, upload_dir: str = None):
        """
        Initialize the data processing service.
        
        Args:
            upload_dir: Directory for temporary file uploads
        """
        self.upload_dir = upload_dir or os.path.join(tempfile.gettempdir(), "geospatial_uploads")
        os.makedirs(self.upload_dir, exist_ok=True)
    
    async def save_upload_file(self, file: UploadFile) -> str:
        """
        Save an uploaded file to the upload directory.
        
        Args:
            file: Uploaded file
            
        Returns:
            Path to the saved file
        """
        file_path = os.path.join(self.upload_dir, file.filename)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        return file_path
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get information about a geospatial file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File information
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext in ['.shp', '.geojson', '.json', '.gpkg', '.kml', '.gml']:
            return self._get_vector_info(file_path)
        elif file_ext in ['.tif', '.tiff', '.img', '.jp2', '.j2k']:
            return self._get_raster_info(file_path)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file format: {file_ext}")
    
    def _get_vector_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get information about a vector file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Vector file information
        """
        try:
            gdf = gpd.read_file(file_path)
            
            # Get basic information
            info = {
                "type": "vector",
                "driver": self._get_driver_from_path(file_path),
                "crs": gdf.crs.to_string() if gdf.crs else None,
                "feature_count": len(gdf),
                "geometry_types": list(gdf.geom_type.unique()),
                "attribute_count": len(gdf.columns) - 1,  # Subtract geometry column
                "attributes": [col for col in gdf.columns if col != 'geometry'],
                "bounds": list(gdf.total_bounds),
                "sample_features": json.loads(gdf.head(5).to_json())
            }
            
            return info
        except Exception as e:
            logger.error(f"Error getting vector info: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error reading vector file: {str(e)}")
    
    def _get_raster_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get information about a raster file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Raster file information
        """
        try:
            with rasterio.open(file_path) as src:
                info = {
                    "type": "raster",
                    "driver": src.driver,
                    "crs": src.crs.to_string() if src.crs else None,
                    "width": src.width,
                    "height": src.height,
                    "count": src.count,
                    "dtype": str(src.dtypes[0]),
                    "nodata": src.nodata,
                    "bounds": [src.bounds.left, src.bounds.bottom, src.bounds.right, src.bounds.top],
                    "transform": list(src.transform),
                    "res": [src.res[0], src.res[1]]
                }
                
                # Get band statistics for the first band
                if src.count > 0:
                    band = src.read(1, masked=True)
                    stats = {
                        "min": float(band.min()) if band.min() is not None else None,
                        "max": float(band.max()) if band.max() is not None else None,
                        "mean": float(band.mean()) if band.mean() is not None else None,
                        "std": float(band.std()) if band.std() is not None else None
                    }
                    info["band_1_stats"] = stats
                
                return info
        except Exception as e:
            logger.error(f"Error getting raster info: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error reading raster file: {str(e)}")
    
    def _get_driver_from_path(self, file_path: str) -> str:
        """
        Get the appropriate driver for a file path.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Driver name
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.shp':
            return 'ESRI Shapefile'
        elif file_ext in ['.geojson', '.json']:
            return 'GeoJSON'
        elif file_ext == '.gpkg':
            return 'GPKG'
        elif file_ext == '.kml':
            return 'KML'
        elif file_ext == '.gml':
            return 'GML'
        else:
            return 'Unknown'
    
    def convert_vector(self, input_path: str, output_format: str, output_path: Optional[str] = None) -> str:
        """
        Convert a vector file to another format.
        
        Args:
            input_path: Path to the input file
            output_format: Output format (shp, geojson, gpkg, kml)
            output_path: Path to the output file (optional)
            
        Returns:
            Path to the output file
        """
        try:
            # Read the input file
            gdf = gpd.read_file(input_path)
            
            # Determine the output path if not provided
            if not output_path:
                input_name = os.path.splitext(os.path.basename(input_path))[0]
                output_path = os.path.join(self.upload_dir, f"{input_name}.{output_format}")
            
            # Convert to the output format
            if output_format == 'shp':
                gdf.to_file(output_path, driver='ESRI Shapefile')
            elif output_format == 'geojson':
                gdf.to_file(output_path, driver='GeoJSON')
            elif output_format == 'gpkg':
                gdf.to_file(output_path, driver='GPKG')
            elif output_format == 'kml':
                gdf.to_file(output_path, driver='KML')
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported output format: {output_format}")
            
            return output_path
        except Exception as e:
            logger.error(f"Error converting vector: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error converting vector file: {str(e)}")
    
    def reproject_vector(self, input_path: str, target_crs: str, output_path: Optional[str] = None) -> str:
        """
        Reproject a vector file to another coordinate reference system.
        
        Args:
            input_path: Path to the input file
            target_crs: Target CRS (e.g., 'EPSG:4326')
            output_path: Path to the output file (optional)
            
        Returns:
            Path to the output file
        """
        try:
            # Read the input file
            gdf = gpd.read_file(input_path)
            
            # Determine the output path if not provided
            if not output_path:
                input_name = os.path.splitext(os.path.basename(input_path))[0]
                input_ext = os.path.splitext(input_path)[1]
                output_path = os.path.join(self.upload_dir, f"{input_name}_reprojected{input_ext}")
            
            # Reproject to the target CRS
            gdf_reprojected = gdf.to_crs(target_crs)
            
            # Save the reprojected file
            driver = self._get_driver_from_path(output_path)
            gdf_reprojected.to_file(output_path, driver=driver)
            
            return output_path
        except Exception as e:
            logger.error(f"Error reprojecting vector: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error reprojecting vector file: {str(e)}")
    
    def reproject_raster(self, input_path: str, target_crs: str, output_path: Optional[str] = None) -> str:
        """
        Reproject a raster file to another coordinate reference system.
        
        Args:
            input_path: Path to the input file
            target_crs: Target CRS (e.g., 'EPSG:4326')
            output_path: Path to the output file (optional)
            
        Returns:
            Path to the output file
        """
        try:
            # Determine the output path if not provided
            if not output_path:
                input_name = os.path.splitext(os.path.basename(input_path))[0]
                output_path = os.path.join(self.upload_dir, f"{input_name}_reprojected.tif")
            
            # Open the input raster
            with rasterio.open(input_path) as src:
                # Check if the source CRS is defined
                if not src.crs:
                    raise HTTPException(status_code=400, detail="Source raster has no defined CRS")
                
                # Parse the target CRS
                dst_crs = CRS.from_string(target_crs)
                
                # Calculate the ideal dimensions and transformation for the new raster
                transform, width, height = calculate_default_transform(
                    src.crs, dst_crs, src.width, src.height, *src.bounds
                )
                
                # Create the output raster
                kwargs = src.meta.copy()
                kwargs.update({
                    'crs': dst_crs,
                    'transform': transform,
                    'width': width,
                    'height': height
                })
                
                with rasterio.open(output_path, 'w', **kwargs) as dst:
                    for i in range(1, src.count + 1):
                        reproject(
                            source=rasterio.band(src, i),
                            destination=rasterio.band(dst, i),
                            src_transform=src.transform,
                            src_crs=src.crs,
                            dst_transform=transform,
                            dst_crs=dst_crs,
                            resampling=Resampling.nearest
                        )
            
            return output_path
        except Exception as e:
            logger.error(f"Error reprojecting raster: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error reprojecting raster file: {str(e)}")
    
    def clip_vector(self, input_path: str, clip_geometry: Dict[str, Any], output_path: Optional[str] = None) -> str:
        """
        Clip a vector file with a geometry.
        
        Args:
            input_path: Path to the input file
            clip_geometry: GeoJSON geometry to clip with
            output_path: Path to the output file (optional)
            
        Returns:
            Path to the output file
        """
        try:
            # Read the input file
            gdf = gpd.read_file(input_path)
            
            # Convert the clip geometry to a shapely geometry
            clip_shape = shape(clip_geometry)
            
            # Create a GeoDataFrame from the clip geometry
            clip_gdf = gpd.GeoDataFrame(geometry=[clip_shape], crs=gdf.crs)
            
            # Perform the clip
            clipped_gdf = gpd.clip(gdf, clip_gdf)
            
            # Determine the output path if not provided
            if not output_path:
                input_name = os.path.splitext(os.path.basename(input_path))[0]
                input_ext = os.path.splitext(input_path)[1]
                output_path = os.path.join(self.upload_dir, f"{input_name}_clipped{input_ext}")
            
            # Save the clipped file
            driver = self._get_driver_from_path(output_path)
            clipped_gdf.to_file(output_path, driver=driver)
            
            return output_path
        except Exception as e:
            logger.error(f"Error clipping vector: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error clipping vector file: {str(e)}")
    
    def clip_raster(self, input_path: str, clip_geometry: Dict[str, Any], output_path: Optional[str] = None) -> str:
        """
        Clip a raster file with a geometry.
        
        Args:
            input_path: Path to the input file
            clip_geometry: GeoJSON geometry to clip with
            output_path: Path to the output file (optional)
            
        Returns:
            Path to the output file
        """
        try:
            # Determine the output path if not provided
            if not output_path:
                input_name = os.path.splitext(os.path.basename(input_path))[0]
                output_path = os.path.join(self.upload_dir, f"{input_name}_clipped.tif")
            
            # Convert the clip geometry to a shapely geometry
            clip_shape = shape(clip_geometry)
            
            # Create a temporary shapefile for the clip geometry
            temp_dir = tempfile.mkdtemp()
            temp_shp = os.path.join(temp_dir, "clip.shp")
            
            # Create a GeoDataFrame from the clip geometry
            with rasterio.open(input_path) as src:
                clip_gdf = gpd.GeoDataFrame(geometry=[clip_shape], crs=src.crs)
            
            # Save the clip geometry to a shapefile
            clip_gdf.to_file(temp_shp)
            
            # Use rasterio's mask function to clip the raster
            import rasterio.mask
            
            with rasterio.open(input_path) as src:
                # Read the clip geometry as a list of geometries
                with fiona.open(temp_shp, "r") as shapefile:
                    shapes = [feature["geometry"] for feature in shapefile]
                
                # Perform the clip
                out_image, out_transform = rasterio.mask.mask(src, shapes, crop=True)
                
                # Update the metadata
                out_meta = src.meta.copy()
                out_meta.update({
                    "driver": "GTiff",
                    "height": out_image.shape[1],
                    "width": out_image.shape[2],
                    "transform": out_transform
                })
                
                # Write the clipped raster
                with rasterio.open(output_path, "w", **out_meta) as dest:
                    dest.write(out_image)
            
            # Clean up the temporary directory
            shutil.rmtree(temp_dir)
            
            return output_path
        except Exception as e:
            logger.error(f"Error clipping raster: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error clipping raster file: {str(e)}")
    
    def buffer_vector(self, input_path: str, distance: float, output_path: Optional[str] = None) -> str:
        """
        Buffer a vector file.
        
        Args:
            input_path: Path to the input file
            distance: Buffer distance in the units of the input file's CRS
            output_path: Path to the output file (optional)
            
        Returns:
            Path to the output file
        """
        try:
            # Read the input file
            gdf = gpd.read_file(input_path)
            
            # Perform the buffer
            buffered_gdf = gdf.copy()
            buffered_gdf['geometry'] = gdf.geometry.buffer(distance)
            
            # Determine the output path if not provided
            if not output_path:
                input_name = os.path.splitext(os.path.basename(input_path))[0]
                input_ext = os.path.splitext(input_path)[1]
                output_path = os.path.join(self.upload_dir, f"{input_name}_buffered{input_ext}")
            
            # Save the buffered file
            driver = self._get_driver_from_path(output_path)
            buffered_gdf.to_file(output_path, driver=driver)
            
            return output_path
        except Exception as e:
            logger.error(f"Error buffering vector: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error buffering vector file: {str(e)}")
    
    def dissolve_vector(self, input_path: str, dissolve_field: Optional[str] = None, output_path: Optional[str] = None) -> str:
        """
        Dissolve a vector file.
        
        Args:
            input_path: Path to the input file
            dissolve_field: Field to dissolve by (optional)
            output_path: Path to the output file (optional)
            
        Returns:
            Path to the output file
        """
        try:
            # Read the input file
            gdf = gpd.read_file(input_path)
            
            # Perform the dissolve
            if dissolve_field:
                dissolved_gdf = gdf.dissolve(by=dissolve_field, as_index=True)
                dissolved_gdf = dissolved_gdf.reset_index()
            else:
                dissolved_gdf = gdf.dissolve()
                dissolved_gdf = dissolved_gdf.reset_index(drop=True)
            
            # Determine the output path if not provided
            if not output_path:
                input_name = os.path.splitext(os.path.basename(input_path))[0]
                input_ext = os.path.splitext(input_path)[1]
                output_path = os.path.join(self.upload_dir, f"{input_name}_dissolved{input_ext}")
            
            # Save the dissolved file
            driver = self._get_driver_from_path(output_path)
            dissolved_gdf.to_file(output_path, driver=driver)
            
            return output_path
        except Exception as e:
            logger.error(f"Error dissolving vector: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error dissolving vector file: {str(e)}")
    
    def get_available_operations(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get a list of available data processing operations.
        
        Returns:
            Dictionary of operation categories and their operations
        """
        return {
            "vector": [
                {
                    "id": "convert_vector",
                    "name": "Convert Vector Format",
                    "description": "Convert a vector file to another format",
                    "inputs": [
                        {"name": "input_file", "type": "file", "description": "Input vector file"},
                        {"name": "output_format", "type": "select", "description": "Output format", "options": ["shp", "geojson", "gpkg", "kml"]}
                    ]
                },
                {
                    "id": "reproject_vector",
                    "name": "Reproject Vector",
                    "description": "Reproject a vector file to another coordinate reference system",
                    "inputs": [
                        {"name": "input_file", "type": "file", "description": "Input vector file"},
                        {"name": "target_crs", "type": "text", "description": "Target CRS (e.g., 'EPSG:4326')"}
                    ]
                },
                {
                    "id": "clip_vector",
                    "name": "Clip Vector",
                    "description": "Clip a vector file with a geometry",
                    "inputs": [
                        {"name": "input_file", "type": "file", "description": "Input vector file"},
                        {"name": "clip_geometry", "type": "geometry", "description": "Geometry to clip with"}
                    ]
                },
                {
                    "id": "buffer_vector",
                    "name": "Buffer Vector",
                    "description": "Buffer a vector file",
                    "inputs": [
                        {"name": "input_file", "type": "file", "description": "Input vector file"},
                        {"name": "distance", "type": "number", "description": "Buffer distance in the units of the input file's CRS"}
                    ]
                },
                {
                    "id": "dissolve_vector",
                    "name": "Dissolve Vector",
                    "description": "Dissolve a vector file",
                    "inputs": [
                        {"name": "input_file", "type": "file", "description": "Input vector file"},
                        {"name": "dissolve_field", "type": "text", "description": "Field to dissolve by (optional)", "required": False}
                    ]
                }
            ],
            "raster": [
                {
                    "id": "reproject_raster",
                    "name": "Reproject Raster",
                    "description": "Reproject a raster file to another coordinate reference system",
                    "inputs": [
                        {"name": "input_file", "type": "file", "description": "Input raster file"},
                        {"name": "target_crs", "type": "text", "description": "Target CRS (e.g., 'EPSG:4326')"}
                    ]
                },
                {
                    "id": "clip_raster",
                    "name": "Clip Raster",
                    "description": "Clip a raster file with a geometry",
                    "inputs": [
                        {"name": "input_file", "type": "file", "description": "Input raster file"},
                        {"name": "clip_geometry", "type": "geometry", "description": "Geometry to clip with"}
                    ]
                }
            ],
            "info": [
                {
                    "id": "get_file_info",
                    "name": "Get File Info",
                    "description": "Get information about a geospatial file",
                    "inputs": [
                        {"name": "input_file", "type": "file", "description": "Input geospatial file"}
                    ]
                }
            ]
        }
