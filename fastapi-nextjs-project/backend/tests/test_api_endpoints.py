import pytest
import json
from fastapi import status
import io
import os


@pytest.mark.asyncio
class TestMetadataAPI:
    """Test metadata API endpoints."""
    
    async def test_create_dataset(self, client, db_session):
        """Test creating a dataset."""
        # Dataset data
        dataset_data = {
            "title": "Test API Dataset",
            "description": "A test dataset created through API",
            "resource_type": "dataset",
            "resource_format": "GeoJSON",
            "bbox": [-10, -10, 10, 10],
            "keywords": ["test", "api", "dataset"],
            "is_published": True
        }
        
        # Create dataset
        response = await client.post(
            "/api/v1/metadata/datasets",
            json=dataset_data
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Check response
        data = response.json()
        assert data["title"] == dataset_data["title"]
        assert data["resource_type"] == dataset_data["resource_type"]
        assert data["bbox"] == dataset_data["bbox"]
        assert len(data["keywords"]) == 3
        assert data["is_published"] == True
        
        # Check ID was created
        assert "id" in data
        dataset_id = data["id"]
        
        # Get dataset
        response = await client.get(f"/api/v1/metadata/datasets/{dataset_id}")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == dataset_id
    
    async def test_update_dataset(self, client, db_session):
        """Test updating a dataset."""
        # Create dataset
        dataset_data = {
            "title": "Dataset to Update",
            "description": "This dataset will be updated",
            "resource_type": "dataset"
        }
        
        response = await client.post(
            "/api/v1/metadata/datasets",
            json=dataset_data
        )
        
        assert response.status_code == status.HTTP_200_OK
        dataset_id = response.json()["id"]
        
        # Update dataset
        update_data = {
            "title": "Updated Dataset",
            "bbox": [0, 0, 1, 1],
            "keywords": ["updated"]
        }
        
        response = await client.put(
            f"/api/v1/metadata/datasets/{dataset_id}",
            json=update_data
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Check updated data
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["description"] == dataset_data["description"]  # Unchanged
        assert data["bbox"] == update_data["bbox"]
        assert len(data["keywords"]) == 1
        assert data["keywords"][0]["name"] == "updated"
    
    async def test_delete_dataset(self, client, db_session):
        """Test deleting a dataset."""
        # Create dataset
        dataset_data = {
            "title": "Dataset to Delete",
            "resource_type": "dataset"
        }
        
        response = await client.post(
            "/api/v1/metadata/datasets",
            json=dataset_data
        )
        
        assert response.status_code == status.HTTP_200_OK
        dataset_id = response.json()["id"]
        
        # Delete dataset
        response = await client.delete(f"/api/v1/metadata/datasets/{dataset_id}")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "success"
        
        # Try to get deleted dataset
        response = await client.get(f"/api/v1/metadata/datasets/{dataset_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    async def test_list_datasets(self, client, db_session):
        """Test listing datasets with filtering and pagination."""
        # Create multiple datasets
        for i in range(5):
            dataset_data = {
                "title": f"Test Dataset {i}",
                "description": f"Description for dataset {i}",
                "resource_type": "dataset" if i % 2 == 0 else "service",
                "keywords": [f"keyword{i}", "test"]
            }
            
            response = await client.post(
                "/api/v1/metadata/datasets",
                json=dataset_data
            )
            
            assert response.status_code == status.HTTP_200_OK
        
        # List all datasets
        response = await client.get("/api/v1/metadata/datasets")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] >= 5
        assert len(data["items"]) <= 10  # Default limit
        
        # Filter by resource type
        response = await client.get(
            "/api/v1/metadata/datasets",
            params={"resource_type": "dataset"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(item["resource_type"] == "dataset" for item in data["items"])
        
        # Search by title
        response = await client.get(
            "/api/v1/metadata/datasets",
            params={"search": "Test Dataset 1"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert any("Test Dataset 1" in item["title"] for item in data["items"])
        
        # Pagination
        response = await client.get(
            "/api/v1/metadata/datasets",
            params={"page": 1, "limit": 2}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) <= 2
        assert data["page"] == 1
        assert data["limit"] == 2
        assert data["total_pages"] >= 3  # At least 5 items with limit 2
    
    async def test_create_contact(self, client, db_session):
        """Test creating a contact."""
        # Contact data
        contact_data = {
            "name": "Test Contact",
            "organization": "Test Organization",
            "email": "test@example.com",
            "phone": "123-456-7890"
        }
        
        # Create contact
        response = await client.post(
            "/api/v1/metadata/contacts",
            json=contact_data
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Check response
        data = response.json()
        assert data["name"] == contact_data["name"]
        assert data["organization"] == contact_data["organization"]
        assert data["email"] == contact_data["email"]
        
        # Check ID was created
        assert "id" in data
    
    async def test_list_contacts(self, client, db_session):
        """Test listing contacts."""
        # Create contacts
        for i in range(3):
            contact_data = {
                "name": f"Contact {i}",
                "organization": f"Organization {i}",
                "email": f"contact{i}@example.com"
            }
            
            response = await client.post(
                "/api/v1/metadata/contacts",
                json=contact_data
            )
            
            assert response.status_code == status.HTTP_200_OK
        
        # List contacts
        response = await client.get("/api/v1/metadata/contacts")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 3
        
        # Search contacts
        response = await client.get(
            "/api/v1/metadata/contacts",
            params={"search": "Contact 1"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert any("Contact 1" in contact["name"] for contact in data)


@pytest.mark.asyncio
class TestHarvestAPI:
    """Test metadata harvest API endpoints."""
    
    async def test_create_harvest_job(self, client, db_session):
        """Test creating a harvest job."""
        # Job data
        job_data = {
            "source_type": "directory",
            "source_path": "/path/to/data",
            "config": {
                "recursive": True,
                "extract_attributes": True,
                "overwrite_existing": False
            }
        }
        
        # Create job
        response = await client.post(
            "/api/v1/metadata/harvest/jobs",
            json=job_data
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Check response
        data = response.json()
        assert data["source_type"] == job_data["source_type"]
        assert data["source_path"] == job_data["source_path"]
        assert data["status"] == "running"  # Should be updated to running
        
        # Check ID was created
        assert "id" in data
        job_id = data["id"]
        
        # Get job
        response = await client.get(f"/api/v1/metadata/harvest/jobs/{job_id}")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == job_id
    
    async def test_list_harvest_jobs(self, client, db_session):
        """Test listing harvest jobs."""
        # Create jobs
        for i in range(3):
            job_data = {
                "source_type": "directory" if i % 2 == 0 else "service",
                "source_path": f"/path/to/data{i}",
                "config": {
                    "recursive": True
                }
            }
            
            response = await client.post(
                "/api/v1/metadata/harvest/jobs",
                json=job_data
            )
            
            assert response.status_code == status.HTTP_200_OK
        
        # List jobs
        response = await client.get("/api/v1/metadata/harvest/jobs")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 3
        
        # Filter by status
        response = await client.get(
            "/api/v1/metadata/harvest/jobs",
            params={"status": "running"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(job["status"] == "running" for job in data)
    
    async def test_harvest_file(self, client, db_session, sample_geojson):
        """Test harvesting metadata from a file."""
        # Create file data
        with open(sample_geojson, "rb") as f:
            file_content = f.read()
        
        # Create form data
        form_data = {
            "extract_attributes": "true",
            "overwrite_existing": "false"
        }
        
        files = {
            "file": ("test.geojson", io.BytesIO(file_content), "application/geo+json")
        }
        
        # Upload file
        response = await client.post(
            "/api/v1/metadata/harvest/file",
            data=form_data,
            files=files
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Check response
        data = response.json()
        assert data["status"] == "success"
        assert "job_id" in data
