import os
import tempfile
import json
import matplotlib.pyplot as plt
import geopandas as gpd
import contextily as ctx
from shapely.geometry import shape
from typing import Dict, List, Optional, Union, Any
import base64
from io import BytesIO
import folium
from folium.plugins import MarkerCluster
import branca.colormap as cm
import numpy as np
import fiona

class GeoDiffVisualService:
    def __init__(self):
        """Initialize GeoDiff Visual service"""
        self.temp_dir = tempfile.mkdtemp()
        
    def generate_static_diff_map(self, 
                                base_file: str, 
                                modified_file: str,
                                layer_name: Optional[str] = None,
                                output_format: str = "png",
                                width: int = 1200,
                                height: int = 800,
                                basemap: bool = True) -> str:
        """
        Generate a static map showing differences between two GeoPackage files
        
        Args:
            base_file: Path to base GeoPackage file
            modified_file: Path to modified GeoPackage file
            layer_name: Layer name to compare (if None, uses the first layer)
            output_format: Output format (png, jpg, pdf, svg)
            width: Width of the output image in pixels
            height: Height of the output image in pixels
            basemap: Whether to include a basemap
            
        Returns:
            Path to the output image file
        """
        try:
            # Read GeoPackage files
            base_gdf = self._read_gpkg(base_file, layer_name)
            modified_gdf = self._read_gpkg(modified_file, layer_name)
            
            # Create figure
            fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
            
            # Plot base features in blue
            base_gdf.plot(ax=ax, color='blue', alpha=0.5, label='Original')
            
            # Plot modified features in red
            modified_gdf.plot(ax=ax, color='red', alpha=0.5, label='Modified')
            
            # Add basemap if requested
            if basemap:
                try:
                    ctx.add_basemap(ax, crs=base_gdf.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)
                except Exception as e:
                    print(f"Warning: Could not add basemap: {str(e)}")
            
            # Add legend
            ax.legend()
            
            # Add title
            layer = layer_name or "Unknown Layer"
            ax.set_title(f"Differences in {layer}")
            
            # Save to file
            output_file = os.path.join(self.temp_dir, f"diff_map.{output_format}")
            plt.savefig(output_file, bbox_inches='tight', dpi=100)
            plt.close(fig)
            
            return output_file
        except Exception as e:
            raise Exception(f"Error generating static diff map: {str(e)}")
    
    def generate_interactive_diff_map(self, 
                                     base_file: str, 
                                     modified_file: str,
                                     changeset_file: Optional[str] = None,
                                     layer_name: Optional[str] = None) -> str:
        """
        Generate an interactive HTML map showing differences between two GeoPackage files
        
        Args:
            base_file: Path to base GeoPackage file
            modified_file: Path to modified GeoPackage file
            changeset_file: Path to GeoDiff changeset file (optional)
            layer_name: Layer name to compare (if None, uses the first layer)
            
        Returns:
            Path to the output HTML file
        """
        try:
            # Read GeoPackage files
            base_gdf = self._read_gpkg(base_file, layer_name)
            modified_gdf = self._read_gpkg(modified_file, layer_name)
            
            # Convert to EPSG:4326 for Folium
            if base_gdf.crs and base_gdf.crs != "EPSG:4326":
                base_gdf = base_gdf.to_crs("EPSG:4326")
            if modified_gdf.crs and modified_gdf.crs != "EPSG:4326":
                modified_gdf = modified_gdf.to_crs("EPSG:4326")
            
            # Calculate center of the map
            if not base_gdf.empty:
                center = [base_gdf.geometry.centroid.y.mean(), base_gdf.geometry.centroid.x.mean()]
            elif not modified_gdf.empty:
                center = [modified_gdf.geometry.centroid.y.mean(), modified_gdf.geometry.centroid.x.mean()]
            else:
                center = [0, 0]
            
            # Create map
            m = folium.Map(location=center, zoom_start=10, tiles='OpenStreetMap')
            
            # Add base features
            folium.GeoJson(
                base_gdf.__geo_interface__,
                name='Original',
                style_function=lambda x: {
                    'fillColor': 'blue',
                    'color': 'blue',
                    'weight': 1,
                    'fillOpacity': 0.5
                },
                tooltip=folium.GeoJsonTooltip(fields=self._get_tooltip_fields(base_gdf))
            ).add_to(m)
            
            # Add modified features
            folium.GeoJson(
                modified_gdf.__geo_interface__,
                name='Modified',
                style_function=lambda x: {
                    'fillColor': 'red',
                    'color': 'red',
                    'weight': 1,
                    'fillOpacity': 0.5
                },
                tooltip=folium.GeoJsonTooltip(fields=self._get_tooltip_fields(modified_gdf))
            ).add_to(m)
            
            # Add changeset information if provided
            if changeset_file:
                self._add_changeset_to_map(m, changeset_file, base_gdf, modified_gdf)
            
            # Add layer control
            folium.LayerControl().add_to(m)
            
            # Save to file
            output_file = os.path.join(self.temp_dir, "diff_map.html")
            m.save(output_file)
            
            return output_file
        except Exception as e:
            raise Exception(f"Error generating interactive diff map: {str(e)}")
    
    def generate_change_statistics(self, 
                                  changeset_file: str) -> Dict[str, Any]:
        """
        Generate statistics about changes in a changeset
        
        Args:
            changeset_file: Path to GeoDiff changeset file
            
        Returns:
            Dictionary with change statistics
        """
        try:
            # Read changeset
            with open(changeset_file, 'rb') as f:
                # This is a placeholder - in a real implementation, you would parse the changeset file
                # For now, we'll simulate reading the changeset
                changes = {
                    "total_changes": 0,
                    "tables": {},
                    "changes_by_type": {
                        "inserts": 0,
                        "updates": 0,
                        "deletes": 0
                    },
                    "changes_by_geometry_type": {
                        "point": 0,
                        "linestring": 0,
                        "polygon": 0,
                        "other": 0
                    }
                }
            
            # Generate statistics
            # In a real implementation, you would analyze the changeset
            # For now, we'll return placeholder statistics
            return changes
        except Exception as e:
            raise Exception(f"Error generating change statistics: {str(e)}")
    
    def generate_diff_report(self, 
                            base_file: str, 
                            modified_file: str,
                            changeset_file: str,
                            layer_name: Optional[str] = None) -> str:
        """
        Generate a comprehensive HTML report about differences
        
        Args:
            base_file: Path to base GeoPackage file
            modified_file: Path to modified GeoPackage file
            changeset_file: Path to GeoDiff changeset file
            layer_name: Layer name to compare (if None, uses the first layer)
            
        Returns:
            Path to the output HTML report
        """
        try:
            # Read GeoPackage files
            base_gdf = self._read_gpkg(base_file, layer_name)
            modified_gdf = self._read_gpkg(modified_file, layer_name)
            
            # Generate static map
            static_map_file = self.generate_static_diff_map(base_file, modified_file, layer_name)
            
            # Generate statistics
            statistics = self.generate_change_statistics(changeset_file)
            
            # Create HTML report
            with open(os.path.join(self.temp_dir, "diff_report.html"), "w") as f:
                f.write(self._generate_html_report(base_gdf, modified_gdf, statistics, static_map_file))
            
            return os.path.join(self.temp_dir, "diff_report.html")
        except Exception as e:
            raise Exception(f"Error generating diff report: {str(e)}")
    
    def _read_gpkg(self, gpkg_file: str, layer_name: Optional[str] = None) -> gpd.GeoDataFrame:
        """Read a layer from a GeoPackage file"""
        try:
            if layer_name:
                return gpd.read_file(gpkg_file, layer=layer_name)
            else:
                # Get the first layer
                layers = fiona.listlayers(gpkg_file)
                if not layers:
                    raise ValueError(f"No layers found in {gpkg_file}")
                return gpd.read_file(gpkg_file, layer=layers[0])
        except Exception as e:
            raise Exception(f"Error reading GeoPackage file: {str(e)}")
    
    def _get_tooltip_fields(self, gdf: gpd.GeoDataFrame) -> List[str]:
        """Get fields for tooltips"""
        # Exclude geometry column and limit to first 5 columns
        columns = [col for col in gdf.columns if col != 'geometry']
        return columns[:5]
    
    def _add_changeset_to_map(self, 
                             m: folium.Map, 
                             changeset_file: str,
                             base_gdf: gpd.GeoDataFrame,
                             modified_gdf: gpd.GeoDataFrame) -> None:
        """Add changeset information to the map"""
        try:
            # Read changeset
            with open(changeset_file, 'rb') as f:
                # This is a placeholder - in a real implementation, you would parse the changeset file
                # For now, we'll simulate reading the changeset
                pass
            
            # Create feature groups for different change types
            inserts = folium.FeatureGroup(name='Inserts')
            updates = folium.FeatureGroup(name='Updates')
            deletes = folium.FeatureGroup(name='Deletes')
            
            # Add to map
            inserts.add_to(m)
            updates.add_to(m)
            deletes.add_to(m)
        except Exception as e:
            print(f"Warning: Could not add changeset to map: {str(e)}")
    
    def _generate_html_report(self, 
                             base_gdf: gpd.GeoDataFrame,
                             modified_gdf: gpd.GeoDataFrame,
                             statistics: Dict[str, Any],
                             static_map_file: str) -> str:
        """Generate HTML report"""
        # Read static map as base64
        with open(static_map_file, 'rb') as f:
            map_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Create HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>GeoDiff Visual Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2, h3 {{ color: #333; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .map-container {{ margin: 20px 0; text-align: center; }}
                .stats-container {{ display: flex; flex-wrap: wrap; }}
                .stat-box {{ background-color: #f5f5f5; border-radius: 5px; padding: 15px; margin: 10px; flex: 1; min-width: 200px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>GeoDiff Visual Report</h1>
                
                <div class="map-container">
                    <h2>Difference Map</h2>
                    <img src="data:image/png;base64,{map_data}" alt="Difference Map" style="max-width: 100%;">
                </div>
                
                <h2>Change Statistics</h2>
                <div class="stats-container">
                    <div class="stat-box">
                        <h3>Total Changes</h3>
                        <p>{statistics.get('total_changes', 0)}</p>
                    </div>
                    <div class="stat-box">
                        <h3>Changes by Type</h3>
                        <p>Inserts: {statistics.get('changes_by_type', {}).get('inserts', 0)}</p>
                        <p>Updates: {statistics.get('changes_by_type', {}).get('updates', 0)}</p>
                        <p>Deletes: {statistics.get('changes_by_type', {}).get('deletes', 0)}</p>
                    </div>
                    <div class="stat-box">
                        <h3>Changes by Geometry Type</h3>
                        <p>Points: {statistics.get('changes_by_geometry_type', {}).get('point', 0)}</p>
                        <p>Lines: {statistics.get('changes_by_geometry_type', {}).get('linestring', 0)}</p>
                        <p>Polygons: {statistics.get('changes_by_geometry_type', {}).get('polygon', 0)}</p>
                        <p>Other: {statistics.get('changes_by_geometry_type', {}).get('other', 0)}</p>
                    </div>
                </div>
                
                <h2>Dataset Information</h2>
                <div class="stats-container">
                    <div class="stat-box">
                        <h3>Original Dataset</h3>
                        <p>Features: {len(base_gdf)}</p>
                        <p>Columns: {len(base_gdf.columns)}</p>
                        <p>CRS: {base_gdf.crs}</p>
                    </div>
                    <div class="stat-box">
                        <h3>Modified Dataset</h3>
                        <p>Features: {len(modified_gdf)}</p>
                        <p>Columns: {len(modified_gdf.columns)}</p>
                        <p>CRS: {modified_gdf.crs}</p>
                    </div>
                </div>
                
                <h2>Tables Affected</h2>
                <table>
                    <tr>
                        <th>Table</th>
                        <th>Inserts</th>
                        <th>Updates</th>
                        <th>Deletes</th>
                    </tr>
                    {self._generate_table_rows(statistics.get('tables', {}))}
                </table>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _generate_table_rows(self, tables: Dict[str, Dict[str, int]]) -> str:
        """Generate HTML table rows for tables statistics"""
        rows = ""
        for table_name, stats in tables.items():
            rows += f"""
            <tr>
                <td>{table_name}</td>
                <td>{stats.get('inserts', 0)}</td>
                <td>{stats.get('updates', 0)}</td>
                <td>{stats.get('deletes', 0)}</td>
            </tr>
            """
        return rows

geodiff_visual_service = GeoDiffVisualService()
