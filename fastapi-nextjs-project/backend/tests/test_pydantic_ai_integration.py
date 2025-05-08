import pytest
import json
from pydantic import ValidationError
from typing import List, Dict, Any, Optional
import os

from app.schemas.ai_geo_models import (
    GeoFeatureAI,
    GeoDatasetAI,
    SpatialExtentAI,
    FeatureCollectionAI,
    MetadataExtractorAI
)


class TestPydanticAIIntegration:
    """Test Pydantic AI integration with geospatial models."""
    
    def test_geo_feature_ai_validation(self):
        """Test GeoFeatureAI validation with AI-powered validation."""
        # Valid feature with point
        feature = GeoFeatureAI(
            type="Feature",
            geometry={
                "type": "Point",
                "coordinates": [0, 0]
            },
            properties={
                "name": "Test Point",
                "value": 42
            }
        )
        
        assert feature.geometry["coordinates"] == [0, 0]
        assert feature.properties["name"] == "Test Point"
        
        # Test AI-powered validation for invalid geometry
        with pytest.raises(ValidationError) as exc_info:
            GeoFeatureAI(
                type="Feature",
                geometry={
                    "type": "Point",
                    "coordinates": [200, 100]  # Invalid coordinates
                },
                properties={"name": "Invalid Point"}
            )
        
        # Check error message
        error_msg = str(exc_info.value)
        assert "Invalid coordinates" in error_msg
        
        # Test AI-powered property validation
        with pytest.raises(ValidationError) as exc_info:
            GeoFeatureAI(
                type="Feature",
                geometry={
                    "type": "Point",
                    "coordinates": [0, 0]
                },
                properties={
                    "name": "Test Point",
                    "population": -100  # Invalid population
                }
            )
        
        # Check error message
        error_msg = str(exc_info.value)
        assert "population" in error_msg.lower()
        assert "negative" in error_msg.lower()
    
    def test_spatial_extent_ai_validation(self):
        """Test SpatialExtentAI validation with AI-powered validation."""
        # Valid spatial extent
        extent = SpatialExtentAI(
            bbox=[-180, -90, 180, 90],
            crs="EPSG:4326"
        )
        
        assert extent.bbox == [-180, -90, 180, 90]
        assert extent.crs == "EPSG:4326"
        
        # Test AI-powered validation for invalid CRS
        with pytest.raises(ValidationError) as exc_info:
            SpatialExtentAI(
                bbox=[-180, -90, 180, 90],
                crs="INVALID:1234"  # Invalid CRS
            )
        
        # Check error message
        error_msg = str(exc_info.value)
        assert "crs" in error_msg.lower()
        assert "invalid" in error_msg.lower()
        
        # Test AI-powered validation for invalid bbox (min > max)
        with pytest.raises(ValidationError) as exc_info:
            SpatialExtentAI(
                bbox=[180, 90, -180, -90],  # minX > maxX, minY > maxY
                crs="EPSG:4326"
            )
        
        # Check error message
        error_msg = str(exc_info.value)
        assert "bbox" in error_msg.lower()
        assert "minimum" in error_msg.lower() or "maximum" in error_msg.lower()
    
    def test_geo_dataset_ai_validation(self):
        """Test GeoDatasetAI validation with AI-powered validation."""
        # Valid dataset
        dataset = GeoDatasetAI(
            title="Test Dataset",
            description="A test dataset",
            spatial_extent={
                "bbox": [-180, -90, 180, 90],
                "crs": "EPSG:4326"
            },
            temporal_extent=["2020-01-01T00:00:00Z", "2020-12-31T23:59:59Z"],
            data_type="vector",
            format="GeoJSON",
            keywords=["test", "dataset"],
            license="CC-BY-4.0"
        )
        
        assert dataset.title == "Test Dataset"
        assert dataset.data_type == "vector"
        assert dataset.spatial_extent["bbox"] == [-180, -90, 180, 90]
        
        # Test AI-powered validation for invalid temporal extent
        with pytest.raises(ValidationError) as exc_info:
            GeoDatasetAI(
                title="Test Dataset",
                description="A test dataset",
                spatial_extent={
                    "bbox": [-180, -90, 180, 90],
                    "crs": "EPSG:4326"
                },
                temporal_extent=["2020-12-31T23:59:59Z", "2020-01-01T00:00:00Z"],  # End before start
                data_type="vector",
                format="GeoJSON"
            )
        
        # Check error message
        error_msg = str(exc_info.value)
        assert "temporal" in error_msg.lower()
        assert "start" in error_msg.lower() or "end" in error_msg.lower()
        
        # Test AI-powered validation for invalid license
        with pytest.raises(ValidationError) as exc_info:
            GeoDatasetAI(
                title="Test Dataset",
                description="A test dataset",
                spatial_extent={
                    "bbox": [-180, -90, 180, 90],
                    "crs": "EPSG:4326"
                },
                data_type="vector",
                format="GeoJSON",
                license="INVALID-LICENSE"  # Invalid license
            )
        
        # Check error message
        error_msg = str(exc_info.value)
        assert "license" in error_msg.lower()
    
    def test_feature_collection_ai_validation(self):
        """Test FeatureCollectionAI validation with AI-powered validation."""
        # Valid feature collection
        collection = FeatureCollectionAI(
            type="FeatureCollection",
            features=[
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [0, 0]
                    },
                    "properties": {
                        "name": "Test Point"
                    }
                },
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [0, 0],
                                [1, 0],
                                [1, 1],
                                [0, 1],
                                [0, 0]
                            ]
                        ]
                    },
                    "properties": {
                        "name": "Test Polygon"
                    }
                }
            ]
        )
        
        assert len(collection.features) == 2
        assert collection.features[0]["geometry"]["type"] == "Point"
        assert collection.features[1]["geometry"]["type"] == "Polygon"
        
        # Test AI-powered validation for mixed CRS
        with pytest.raises(ValidationError) as exc_info:
            FeatureCollectionAI(
                type="FeatureCollection",
                features=[
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [0, 0]
                        },
                        "properties": {
                            "name": "EPSG:4326 Point",
                            "crs": "EPSG:4326"
                        }
                    },
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [0, 0]
                        },
                        "properties": {
                            "name": "EPSG:3857 Point",
                            "crs": "EPSG:3857"
                        }
                    }
                ]
            )
        
        # Check error message
        error_msg = str(exc_info.value)
        assert "crs" in error_msg.lower() or "coordinate" in error_msg.lower()
        assert "mixed" in error_msg.lower() or "different" in error_msg.lower()
    
    def test_metadata_extractor_ai(self, sample_geojson):
        """Test MetadataExtractorAI for extracting metadata from files."""
        # Initialize extractor
        extractor = MetadataExtractorAI()
        
        # Extract metadata from GeoJSON
        metadata = extractor.extract_from_file(sample_geojson)
        
        # Check basic metadata
        assert metadata.title is not None
        assert metadata.data_type == "vector"
        assert metadata.format.lower() == "geojson"
        assert metadata.spatial_extent is not None
        assert len(metadata.keywords) > 0
        
        # Check AI-generated description
        assert metadata.description is not None
        assert len(metadata.description) > 10
        
        # Check feature properties extraction
        assert metadata.properties is not None
        assert "feature_count" in metadata.properties
        assert metadata.properties["feature_count"] == 2
        
        # Check property types detection
        assert "property_types" in metadata.properties
        assert "name" in metadata.properties["property_types"]
        assert metadata.properties["property_types"]["name"] == "string"
        assert "value" in metadata.properties["property_types"]
        assert metadata.properties["property_types"]["value"] == "number"
        
        # Check geometry types detection
        assert "geometry_types" in metadata.properties
        assert "Point" in metadata.properties["geometry_types"]
        assert "Polygon" in metadata.properties["geometry_types"]
    
    def test_ai_schema_generation(self):
        """Test AI-powered schema generation for geospatial data."""
        # Sample GeoJSON data
        geojson_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [0, 0]
                    },
                    "properties": {
                        "name": "Test Point",
                        "value": 42,
                        "category": "A"
                    }
                },
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [1, 1]
                    },
                    "properties": {
                        "name": "Another Point",
                        "value": 100,
                        "category": "B"
                    }
                }
            ]
        }
        
        # Generate schema
        schema = GeoFeatureAI.generate_schema(geojson_data)
        
        # Check schema
        assert "properties" in schema
        assert "geometry" in schema["properties"]
        assert "properties" in schema["properties"]
        
        # Check property schema
        property_schema = schema["properties"]["properties"]["properties"]
        assert "name" in property_schema
        assert property_schema["name"]["type"] == "string"
        assert "value" in property_schema
        assert property_schema["value"]["type"] == "number"
        assert "category" in property_schema
        assert property_schema["category"]["type"] == "string"
        assert "enum" in property_schema["category"]
        assert set(property_schema["category"]["enum"]) == {"A", "B"}
