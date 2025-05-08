from typing import List, Dict, Any, Optional, Union, Tuple, Literal
from pydantic import BaseModel, Field, validator
from shapely.geometry import Point, LineString, Polygon, shape
from datetime import datetime


class GeoPoint(BaseModel):
    """GeoJSON Point geometry"""
    type: Literal["Point"] = "Point"
    coordinates: List[float] = Field(..., min_items=2, max_items=2)
    
    @validator("coordinates")
    def validate_coordinates(cls, v):
        """Validate coordinates are within valid range"""
        x, y = v
        if not -180 <= x <= 180:
            raise ValueError(f"Longitude must be between -180 and 180, got {x}")
        if not -90 <= y <= 90:
            raise ValueError(f"Latitude must be between -90 and 90, got {y}")
        return v
    
    def to_shapely(self) -> Point:
        """Convert to shapely Point"""
        return Point(self.coordinates)


class GeoLineString(BaseModel):
    """GeoJSON LineString geometry"""
    type: Literal["LineString"] = "LineString"
    coordinates: List[List[float]] = Field(..., min_items=2)
    
    @validator("coordinates")
    def validate_coordinates(cls, v):
        """Validate coordinates format"""
        if not all(len(point) == 2 for point in v):
            raise ValueError("All points must have exactly 2 coordinates")
        return v
    
    def to_shapely(self) -> LineString:
        """Convert to shapely LineString"""
        return LineString(self.coordinates)


class GeoPolygon(BaseModel):
    """GeoJSON Polygon geometry"""
    type: Literal["Polygon"] = "Polygon"
    coordinates: List[List[List[float]]] = Field(..., min_items=1)
    
    @validator("coordinates")
    def validate_coordinates(cls, v):
        """Validate polygon coordinates"""
        # Check each ring has at least 4 points (closed ring)
        for ring in v:
            if len(ring) < 4:
                raise ValueError("Each polygon ring must have at least 4 points")
            
            # Check ring is closed (first point equals last point)
            if ring[0] != ring[-1]:
                raise ValueError("Each polygon ring must be closed (first point equals last point)")
            
            # Check each point has exactly 2 coordinates
            if not all(len(point) == 2 for point in ring):
                raise ValueError("All points must have exactly 2 coordinates")
        
        return v
    
    def to_shapely(self) -> Polygon:
        """Convert to shapely Polygon"""
        return Polygon(self.coordinates[0], [ring for ring in self.coordinates[1:]])


class GeoFeature(BaseModel):
    """GeoJSON Feature"""
    type: Literal["Feature"] = "Feature"
    geometry: Union[GeoPoint, GeoLineString, GeoPolygon]
    properties: Dict[str, Any] = Field(default_factory=dict)
    id: Optional[str] = None


class FeatureCollection(BaseModel):
    """GeoJSON FeatureCollection"""
    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: List[GeoFeature]


class SpatialExtent(BaseModel):
    """Spatial extent with bounding box and CRS"""
    bbox: List[float] = Field(..., min_items=4, max_items=4)
    crs: str = "EPSG:4326"
    
    @validator("bbox")
    def validate_bbox(cls, v):
        """Validate bounding box coordinates"""
        minx, miny, maxx, maxy = v
        
        # Check coordinates are within valid range for EPSG:4326
        if not -180 <= minx <= 180:
            raise ValueError(f"Min longitude must be between -180 and 180, got {minx}")
        if not -90 <= miny <= 90:
            raise ValueError(f"Min latitude must be between -90 and 90, got {miny}")
        if not -180 <= maxx <= 180:
            raise ValueError(f"Max longitude must be between -180 and 180, got {maxx}")
        if not -90 <= maxy <= 90:
            raise ValueError(f"Max latitude must be between -90 and 90, got {maxy}")
        
        # Check min <= max
        if minx > maxx:
            raise ValueError(f"Min longitude ({minx}) must be <= max longitude ({maxx})")
        if miny > maxy:
            raise ValueError(f"Min latitude ({miny}) must be <= max latitude ({maxy})")
        
        return v


class GeoDataset(BaseModel):
    """Geospatial dataset metadata"""
    title: str
    description: Optional[str] = None
    spatial_extent: SpatialExtent
    temporal_extent: Optional[List[str]] = None
    data_type: str = Field(..., description="Type of data (vector, raster, etc.)")
    format: str = Field(..., description="Data format (GeoJSON, Shapefile, GeoTIFF, etc.)")
    created: Optional[datetime] = None
    modified: Optional[datetime] = None
    keywords: List[str] = Field(default_factory=list)
    license: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @validator("temporal_extent")
    def validate_temporal_extent(cls, v):
        """Validate temporal extent"""
        if v is not None:
            if len(v) != 2:
                raise ValueError("Temporal extent must have exactly 2 elements (start and end)")
            
            # Parse dates to check validity
            try:
                start = datetime.fromisoformat(v[0].replace("Z", "+00:00"))
                end = datetime.fromisoformat(v[1].replace("Z", "+00:00"))
                
                # Check start <= end
                if start > end:
                    raise ValueError(f"Start date ({v[0]}) must be <= end date ({v[1]})")
            except ValueError as e:
                raise ValueError(f"Invalid date format in temporal extent: {e}")
        
        return v
