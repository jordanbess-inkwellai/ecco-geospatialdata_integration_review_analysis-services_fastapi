import pytest
from pydantic import ValidationError
from shapely.geometry import Point, Polygon, LineString
import json
from datetime import datetime

from app.schemas.geo_models import (
    GeoFeature,
    GeoPoint,
    GeoPolygon,
    GeoLineString,
    FeatureCollection,
    SpatialExtent,
    GeoDataset
)


class TestPydanticGeoModels:
    """Test Pydantic models with geospatial validation."""
    
    def test_geo_point_validation(self):
        """Test GeoPoint validation."""
        # Valid point
        point = GeoPoint(type="Point", coordinates=[0, 0])
        assert point.coordinates == [0, 0]
        
        # Invalid point - wrong type
        with pytest.raises(ValidationError):
            GeoPoint(type="Polygon", coordinates=[0, 0])
        
        # Invalid point - wrong coordinates format
        with pytest.raises(ValidationError):
            GeoPoint(type="Point", coordinates=[0, 0, 0])
        
        # Convert to shapely
        shapely_point = point.to_shapely()
        assert isinstance(shapely_point, Point)
        assert shapely_point.x == 0
        assert shapely_point.y == 0
    
    def test_geo_polygon_validation(self):
        """Test GeoPolygon validation."""
        # Valid polygon
        polygon = GeoPolygon(
            type="Polygon", 
            coordinates=[[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]
        )
        
        # Invalid polygon - not closed
        with pytest.raises(ValidationError):
            GeoPolygon(
                type="Polygon", 
                coordinates=[[[0, 0], [1, 0], [1, 1], [0, 1]]]
            )
        
        # Invalid polygon - wrong type
        with pytest.raises(ValidationError):
            GeoPolygon(
                type="Point", 
                coordinates=[[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]
            )
        
        # Convert to shapely
        shapely_polygon = polygon.to_shapely()
        assert isinstance(shapely_polygon, Polygon)
        assert shapely_polygon.is_valid
    
    def test_geo_linestring_validation(self):
        """Test GeoLineString validation."""
        # Valid linestring
        linestring = GeoLineString(
            type="LineString", 
            coordinates=[[0, 0], [1, 1], [2, 2]]
        )
        
        # Invalid linestring - not enough points
        with pytest.raises(ValidationError):
            GeoLineString(
                type="LineString", 
                coordinates=[[0, 0]]
            )
        
        # Convert to shapely
        shapely_linestring = linestring.to_shapely()
        assert isinstance(shapely_linestring, LineString)
        assert shapely_linestring.is_valid
    
    def test_geo_feature_validation(self):
        """Test GeoFeature validation."""
        # Valid feature with point
        feature = GeoFeature(
            type="Feature",
            geometry=GeoPoint(type="Point", coordinates=[0, 0]),
            properties={"name": "Test Point", "value": 42}
        )
        
        assert feature.geometry.coordinates == [0, 0]
        assert feature.properties["name"] == "Test Point"
        
        # Valid feature with polygon
        feature = GeoFeature(
            type="Feature",
            geometry=GeoPolygon(
                type="Polygon", 
                coordinates=[[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]
            ),
            properties={"name": "Test Polygon", "value": 100}
        )
        
        # Invalid feature - wrong type
        with pytest.raises(ValidationError):
            GeoFeature(
                type="FeatureCollection",
                geometry=GeoPoint(type="Point", coordinates=[0, 0]),
                properties={"name": "Test Point"}
            )
    
    def test_feature_collection_validation(self):
        """Test FeatureCollection validation."""
        # Valid feature collection
        collection = FeatureCollection(
            type="FeatureCollection",
            features=[
                GeoFeature(
                    type="Feature",
                    geometry=GeoPoint(type="Point", coordinates=[0, 0]),
                    properties={"name": "Test Point"}
                ),
                GeoFeature(
                    type="Feature",
                    geometry=GeoPolygon(
                        type="Polygon", 
                        coordinates=[[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]
                    ),
                    properties={"name": "Test Polygon"}
                )
            ]
        )
        
        assert len(collection.features) == 2
        assert collection.features[0].geometry.type == "Point"
        assert collection.features[1].geometry.type == "Polygon"
        
        # Invalid feature collection - wrong type
        with pytest.raises(ValidationError):
            FeatureCollection(
                type="Feature",
                features=[
                    GeoFeature(
                        type="Feature",
                        geometry=GeoPoint(type="Point", coordinates=[0, 0]),
                        properties={"name": "Test Point"}
                    )
                ]
            )
    
    def test_spatial_extent_validation(self):
        """Test SpatialExtent validation."""
        # Valid spatial extent
        extent = SpatialExtent(
            bbox=[-180, -90, 180, 90],
            crs="EPSG:4326"
        )
        
        assert extent.bbox == [-180, -90, 180, 90]
        assert extent.crs == "EPSG:4326"
        
        # Invalid spatial extent - wrong bbox format
        with pytest.raises(ValidationError):
            SpatialExtent(
                bbox=[-180, -90, 180],
                crs="EPSG:4326"
            )
        
        # Invalid spatial extent - invalid bbox values
        with pytest.raises(ValidationError):
            SpatialExtent(
                bbox=[-181, -90, 180, 90],
                crs="EPSG:4326"
            )
    
    def test_geo_dataset_validation(self):
        """Test GeoDataset validation."""
        # Valid dataset
        dataset = GeoDataset(
            title="Test Dataset",
            description="A test dataset",
            spatial_extent=SpatialExtent(
                bbox=[-180, -90, 180, 90],
                crs="EPSG:4326"
            ),
            temporal_extent=["2020-01-01T00:00:00Z", "2020-12-31T23:59:59Z"],
            data_type="vector",
            format="GeoJSON",
            created=datetime.now(),
            modified=datetime.now(),
            keywords=["test", "dataset"],
            license="CC-BY-4.0",
            metadata={
                "source": "Test",
                "accuracy": "High"
            }
        )
        
        assert dataset.title == "Test Dataset"
        assert dataset.spatial_extent.bbox == [-180, -90, 180, 90]
        assert dataset.data_type == "vector"
        assert "test" in dataset.keywords
        
        # Invalid dataset - missing required fields
        with pytest.raises(ValidationError):
            GeoDataset(
                description="A test dataset",
                spatial_extent=SpatialExtent(
                    bbox=[-180, -90, 180, 90],
                    crs="EPSG:4326"
                )
            )
    
    def test_json_serialization(self):
        """Test JSON serialization of models."""
        # Create a feature
        feature = GeoFeature(
            type="Feature",
            geometry=GeoPoint(type="Point", coordinates=[0, 0]),
            properties={"name": "Test Point", "value": 42}
        )
        
        # Serialize to JSON
        feature_json = feature.model_dump_json()
        feature_dict = json.loads(feature_json)
        
        # Check serialization
        assert feature_dict["type"] == "Feature"
        assert feature_dict["geometry"]["type"] == "Point"
        assert feature_dict["geometry"]["coordinates"] == [0, 0]
        assert feature_dict["properties"]["name"] == "Test Point"
        
        # Deserialize from JSON
        feature2 = GeoFeature.model_validate_json(feature_json)
        
        # Check deserialization
        assert feature2.type == "Feature"
        assert feature2.geometry.type == "Point"
        assert feature2.geometry.coordinates == [0, 0]
        assert feature2.properties["name"] == "Test Point"
