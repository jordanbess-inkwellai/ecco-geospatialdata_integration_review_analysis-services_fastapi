import pytest
from sqlalchemy import select, func
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import Point, Polygon, box
import json

from app.models.metadata import MetadataDataset
from app.services.metadata_service import MetadataService


@pytest.mark.asyncio
class TestGeoAlchemyPostGIS:
    """Test GeoAlchemy integration with PostGIS."""
    
    async def test_create_dataset_with_geometry(self, db_session):
        """Test creating a dataset with geometry."""
        # Create a dataset with point geometry
        point = Point(0, 0)
        
        dataset = MetadataDataset(
            title="Test Dataset with Point",
            description="A test dataset with point geometry",
            resource_type="dataset",
            geometry=from_shape(point, srid=4326)
        )
        
        db_session.add(dataset)
        await db_session.commit()
        await db_session.refresh(dataset)
        
        # Query the dataset
        query = select(MetadataDataset).filter(MetadataDataset.id == dataset.id)
        result = await db_session.execute(query)
        retrieved_dataset = result.scalar_one()
        
        # Check geometry
        retrieved_point = to_shape(retrieved_dataset.geometry)
        assert isinstance(retrieved_point, Point)
        assert retrieved_point.x == 0
        assert retrieved_point.y == 0
    
    async def test_create_dataset_with_bbox(self, db_session):
        """Test creating a dataset with bounding box."""
        # Create a dataset with bbox
        bbox = [-10, -10, 10, 10]
        polygon = box(*bbox)
        
        dataset = MetadataDataset(
            title="Test Dataset with BBox",
            description="A test dataset with bounding box",
            resource_type="dataset",
            bbox=bbox,
            geometry=from_shape(polygon, srid=4326)
        )
        
        db_session.add(dataset)
        await db_session.commit()
        await db_session.refresh(dataset)
        
        # Query the dataset
        query = select(MetadataDataset).filter(MetadataDataset.id == dataset.id)
        result = await db_session.execute(query)
        retrieved_dataset = result.scalar_one()
        
        # Check bbox
        assert retrieved_dataset.bbox == bbox
        
        # Check geometry
        retrieved_polygon = to_shape(retrieved_dataset.geometry)
        assert isinstance(retrieved_polygon, Polygon)
        assert retrieved_polygon.bounds == tuple(bbox)
    
    async def test_spatial_query(self, db_session):
        """Test spatial queries with PostGIS."""
        # Create datasets with different geometries
        datasets = [
            MetadataDataset(
                title=f"Dataset {i}",
                description=f"Dataset at point ({i}, {i})",
                resource_type="dataset",
                geometry=from_shape(Point(i, i), srid=4326)
            )
            for i in range(5)
        ]
        
        db_session.add_all(datasets)
        await db_session.commit()
        
        # Query datasets within a bounding box
        search_box = box(1.5, 1.5, 3.5, 3.5)
        search_wkt = search_box.wkt
        
        query = select(MetadataDataset).filter(
            func.ST_Intersects(
                MetadataDataset.geometry,
                func.ST_GeomFromText(search_wkt, 4326)
            )
        )
        
        result = await db_session.execute(query)
        filtered_datasets = result.scalars().all()
        
        # Should return datasets at points (2, 2) and (3, 3)
        assert len(filtered_datasets) == 2
        assert sorted([d.title for d in filtered_datasets]) == ["Dataset 2", "Dataset 3"]
    
    async def test_spatial_functions(self, db_session):
        """Test PostGIS spatial functions."""
        # Create a dataset with polygon geometry
        polygon = Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])
        
        dataset = MetadataDataset(
            title="Test Polygon Dataset",
            description="A test dataset with polygon geometry",
            resource_type="dataset",
            geometry=from_shape(polygon, srid=4326)
        )
        
        db_session.add(dataset)
        await db_session.commit()
        await db_session.refresh(dataset)
        
        # Calculate area using PostGIS
        query = select(
            func.ST_Area(
                func.ST_Transform(
                    MetadataDataset.geometry,
                    3857  # Web Mercator for area calculation
                )
            )
        ).filter(MetadataDataset.id == dataset.id)
        
        result = await db_session.execute(query)
        area = result.scalar_one()
        
        # Area should be approximately 12,308,778 square meters (at equator)
        assert area > 12000000
        assert area < 13000000
        
        # Calculate centroid
        query = select(
            func.ST_AsGeoJSON(
                func.ST_Centroid(MetadataDataset.geometry)
            )
        ).filter(MetadataDataset.id == dataset.id)
        
        result = await db_session.execute(query)
        centroid_json = result.scalar_one()
        centroid = json.loads(centroid_json)
        
        # Centroid should be at (0.5, 0.5)
        assert abs(centroid["coordinates"][0] - 0.5) < 0.0001
        assert abs(centroid["coordinates"][1] - 0.5) < 0.0001
    
    async def test_metadata_service_with_geometry(self, db_session):
        """Test MetadataService with geometry handling."""
        # Create dataset with bbox
        dataset_data = {
            "title": "Test Service Dataset",
            "description": "A test dataset created through service",
            "resource_type": "dataset",
            "bbox": [0, 0, 1, 1]
        }
        
        # Convert to Pydantic model
        from app.schemas.metadata import DatasetCreate
        dataset_create = DatasetCreate(**dataset_data)
        
        # Create dataset through service
        dataset = await MetadataService.create_dataset(db_session, dataset_create)
        
        # Check bbox
        assert dataset.bbox == [0, 0, 1, 1]
        
        # Check geometry was created from bbox
        assert dataset.geometry is not None
        
        # Convert to shapely and check
        polygon = to_shape(dataset.geometry)
        assert isinstance(polygon, Polygon)
        assert polygon.bounds == tuple(dataset.bbox)
