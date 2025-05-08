from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, Body
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from typing import List, Dict, Any, Optional
import os
import logging
import json
from datetime import datetime

from app.core.database import get_db
from app.models.metadata import (
    MetadataDataset, 
    MetadataKeyword, 
    MetadataContact, 
    MetadataAttribute,
    MetadataHarvestJob,
    dataset_keyword,
    dataset_contact
)
from app.services.metadata_service import MetadataService
from app.schemas.metadata import (
    DatasetCreate,
    DatasetUpdate,
    DatasetResponse,
    KeywordCreate,
    KeywordResponse,
    ContactCreate,
    ContactResponse,
    HarvestJobCreate,
    HarvestJobResponse
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/datasets", response_model=Dict[str, Any])
async def get_datasets(
    search: Optional[str] = None,
    resource_type: Optional[str] = None,
    keyword: Optional[str] = None,
    is_published: Optional[bool] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a list of metadata datasets with pagination
    """
    # Calculate offset
    offset = (page - 1) * limit
    
    # Build query
    query = select(MetadataDataset).options(
        selectinload(MetadataDataset.keywords),
        selectinload(MetadataDataset.contacts)
    )
    
    # Apply filters
    if search:
        query = query.filter(
            or_(
                MetadataDataset.title.ilike(f"%{search}%"),
                MetadataDataset.description.ilike(f"%{search}%"),
                MetadataDataset.abstract.ilike(f"%{search}%")
            )
        )
    
    if resource_type:
        query = query.filter(MetadataDataset.resource_type == resource_type)
    
    if is_published is not None:
        query = query.filter(MetadataDataset.is_published == is_published)
    
    if keyword:
        # Join with keywords
        query = query.join(dataset_keyword).join(MetadataKeyword).filter(
            MetadataKeyword.name.ilike(f"%{keyword}%")
        )
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    # Apply pagination
    query = query.order_by(MetadataDataset.updated_at.desc()).offset(offset).limit(limit)
    
    # Execute query
    result = await db.execute(query)
    datasets = result.scalars().all()
    
    # Calculate total pages
    total_pages = (total + limit - 1) // limit
    
    return {
        "items": datasets,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages
    }


@router.post("/datasets", response_model=DatasetResponse)
async def create_dataset(
    dataset: DatasetCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new metadata dataset
    """
    try:
        # Create dataset
        new_dataset = await MetadataService.create_dataset(db, dataset)
        return new_dataset
    except Exception as e:
        logger.error(f"Error creating dataset: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating dataset: {str(e)}")


@router.get("/datasets/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific metadata dataset
    """
    dataset = await MetadataService.get_dataset(db, dataset_id)
    
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset not found: {dataset_id}")
    
    return dataset


@router.put("/datasets/{dataset_id}", response_model=DatasetResponse)
async def update_dataset(
    dataset_id: int,
    dataset: DatasetUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a metadata dataset
    """
    try:
        # Check if dataset exists
        existing_dataset = await MetadataService.get_dataset(db, dataset_id)
        
        if not existing_dataset:
            raise HTTPException(status_code=404, detail=f"Dataset not found: {dataset_id}")
        
        # Update dataset
        updated_dataset = await MetadataService.update_dataset(db, dataset_id, dataset)
        return updated_dataset
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating dataset: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating dataset: {str(e)}")


@router.delete("/datasets/{dataset_id}")
async def delete_dataset(
    dataset_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a metadata dataset
    """
    try:
        # Check if dataset exists
        existing_dataset = await MetadataService.get_dataset(db, dataset_id)
        
        if not existing_dataset:
            raise HTTPException(status_code=404, detail=f"Dataset not found: {dataset_id}")
        
        # Delete dataset
        await MetadataService.delete_dataset(db, dataset_id)
        
        return {"status": "success", "message": f"Dataset {dataset_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting dataset: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting dataset: {str(e)}")


@router.get("/keywords", response_model=List[KeywordResponse])
async def get_keywords(
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a list of metadata keywords
    """
    # Build query
    query = select(MetadataKeyword)
    
    # Apply filters
    if search:
        query = query.filter(MetadataKeyword.name.ilike(f"%{search}%"))
    
    # Execute query
    result = await db.execute(query)
    keywords = result.scalars().all()
    
    return keywords


@router.post("/keywords", response_model=KeywordResponse)
async def create_keyword(
    keyword: KeywordCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new metadata keyword
    """
    try:
        # Check if keyword already exists
        query = select(MetadataKeyword).filter(MetadataKeyword.name == keyword.name)
        result = await db.execute(query)
        existing_keyword = result.scalar_one_or_none()
        
        if existing_keyword:
            return existing_keyword
        
        # Create keyword
        new_keyword = MetadataKeyword(
            name=keyword.name,
            thesaurus=keyword.thesaurus
        )
        
        db.add(new_keyword)
        await db.commit()
        await db.refresh(new_keyword)
        
        return new_keyword
    except Exception as e:
        logger.error(f"Error creating keyword: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating keyword: {str(e)}")


@router.get("/contacts", response_model=List[ContactResponse])
async def get_contacts(
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a list of metadata contacts
    """
    # Build query
    query = select(MetadataContact)
    
    # Apply filters
    if search:
        query = query.filter(
            or_(
                MetadataContact.name.ilike(f"%{search}%"),
                MetadataContact.organization.ilike(f"%{search}%"),
                MetadataContact.email.ilike(f"%{search}%")
            )
        )
    
    # Execute query
    result = await db.execute(query)
    contacts = result.scalars().all()
    
    return contacts


@router.post("/contacts", response_model=ContactResponse)
async def create_contact(
    contact: ContactCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new metadata contact
    """
    try:
        # Create contact
        new_contact = MetadataContact(
            name=contact.name,
            organization=contact.organization,
            position=contact.position,
            email=contact.email,
            phone=contact.phone,
            address=contact.address,
            city=contact.city,
            state=contact.state,
            postal_code=contact.postal_code,
            country=contact.country,
            website=contact.website
        )
        
        db.add(new_contact)
        await db.commit()
        await db.refresh(new_contact)
        
        return new_contact
    except Exception as e:
        logger.error(f"Error creating contact: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating contact: {str(e)}")


@router.post("/harvest/file", response_model=Dict[str, Any])
async def harvest_metadata_from_file(
    file: UploadFile = File(...),
    extract_attributes: bool = Form(True),
    overwrite_existing: bool = Form(False),
    db: AsyncSession = Depends(get_db)
):
    """
    Harvest metadata from a file
    """
    try:
        # Save file to temporary location
        temp_file_path = f"temp_{file.filename}"
        
        with open(temp_file_path, "wb") as buffer:
            buffer.write(await file.read())
        
        # Create harvest job
        harvest_job = MetadataHarvestJob(
            source_type="file",
            source_path=file.filename,
            status="running",
            config={
                "extract_attributes": extract_attributes,
                "overwrite_existing": overwrite_existing
            }
        )
        
        db.add(harvest_job)
        await db.commit()
        await db.refresh(harvest_job)
        
        # Process file in background
        # In a real implementation, this would be done asynchronously
        # For this example, we'll simulate a successful harvest
        
        # Update harvest job
        harvest_job.status = "completed"
        harvest_job.completed_at = datetime.utcnow()
        harvest_job.total_records = 1
        harvest_job.processed_records = 1
        harvest_job.success_records = 1
        
        await db.commit()
        
        # Clean up temporary file
        os.remove(temp_file_path)
        
        return {
            "status": "success",
            "message": "Metadata harvested successfully",
            "job_id": harvest_job.id
        }
    except Exception as e:
        logger.error(f"Error harvesting metadata: {str(e)}")
        
        # Update harvest job with error
        if 'harvest_job' in locals():
            harvest_job.status = "failed"
            harvest_job.completed_at = datetime.utcnow()
            harvest_job.error_message = str(e)
            
            await db.commit()
        
        # Clean up temporary file
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        
        raise HTTPException(status_code=500, detail=f"Error harvesting metadata: {str(e)}")


@router.post("/harvest/jobs", response_model=HarvestJobResponse)
async def create_harvest_job(
    job: HarvestJobCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new metadata harvest job
    """
    try:
        # Create harvest job
        new_job = MetadataHarvestJob(
            source_type=job.source_type,
            source_path=job.source_path,
            status="pending",
            config=job.config
        )
        
        db.add(new_job)
        await db.commit()
        await db.refresh(new_job)
        
        # In a real implementation, this would trigger a background task
        # For this example, we'll simulate a successful job
        
        # Update job status
        new_job.status = "running"
        await db.commit()
        
        # Simulate processing
        # In a real implementation, this would be done asynchronously
        
        return new_job
    except Exception as e:
        logger.error(f"Error creating harvest job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating harvest job: {str(e)}")


@router.get("/harvest/jobs", response_model=List[HarvestJobResponse])
async def get_harvest_jobs(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a list of metadata harvest jobs
    """
    # Build query
    query = select(MetadataHarvestJob)
    
    # Apply filters
    if status:
        query = query.filter(MetadataHarvestJob.status == status)
    
    # Execute query
    query = query.order_by(MetadataHarvestJob.started_at.desc())
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    return jobs


@router.get("/harvest/jobs/{job_id}", response_model=HarvestJobResponse)
async def get_harvest_job(
    job_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific metadata harvest job
    """
    # Get job
    query = select(MetadataHarvestJob).filter(MetadataHarvestJob.id == job_id)
    result = await db.execute(query)
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Harvest job not found: {job_id}")
    
    return job
