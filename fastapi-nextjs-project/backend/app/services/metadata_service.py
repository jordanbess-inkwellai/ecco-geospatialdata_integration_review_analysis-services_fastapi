import os
import json
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from geoalchemy2.shape import from_shape
from shapely.geometry import box

from app.models.metadata import (
    MetadataDataset, 
    MetadataKeyword, 
    MetadataContact, 
    MetadataAttribute,
    MetadataHarvestJob,
    dataset_keyword,
    dataset_contact
)
from app.schemas.metadata import DatasetCreate, DatasetUpdate

logger = logging.getLogger(__name__)

class MetadataService:
    """
    Service for metadata management
    """
    
    @staticmethod
    async def get_dataset(db: AsyncSession, dataset_id: int) -> Optional[MetadataDataset]:
        """
        Get a dataset by ID
        
        Args:
            db: Database session
            dataset_id: Dataset ID
            
        Returns:
            Dataset or None if not found
        """
        query = select(MetadataDataset).options(
            selectinload(MetadataDataset.keywords),
            selectinload(MetadataDataset.contacts),
            selectinload(MetadataDataset.attributes)
        ).filter(MetadataDataset.id == dataset_id)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_dataset(db: AsyncSession, dataset_data: DatasetCreate) -> MetadataDataset:
        """
        Create a new dataset
        
        Args:
            db: Database session
            dataset_data: Dataset data
            
        Returns:
            Created dataset
        """
        # Create dataset
        new_dataset = MetadataDataset(
            title=dataset_data.title,
            description=dataset_data.description,
            abstract=dataset_data.abstract,
            resource_type=dataset_data.resource_type,
            resource_format=dataset_data.resource_format,
            resource_size=dataset_data.resource_size,
            resource_url=dataset_data.resource_url,
            resource_path=dataset_data.resource_path,
            bbox=dataset_data.bbox,
            srid=dataset_data.srid,
            temporal_start=dataset_data.temporal_start,
            temporal_end=dataset_data.temporal_end,
            metadata_language=dataset_data.metadata_language,
            metadata_standard_name=dataset_data.metadata_standard_name,
            metadata_standard_version=dataset_data.metadata_standard_version,
            is_published=dataset_data.is_published,
            identifier=dataset_data.identifier,
            file_identifier=dataset_data.file_identifier,
            parent_identifier=dataset_data.parent_identifier,
            properties=dataset_data.properties
        )
        
        # Add geometry if bbox is provided
        if dataset_data.bbox and len(dataset_data.bbox) == 4:
            minx, miny, maxx, maxy = dataset_data.bbox
            geometry = box(minx, miny, maxx, maxy)
            new_dataset.geometry = from_shape(geometry, srid=4326)
        
        db.add(new_dataset)
        await db.flush()
        
        # Add keywords
        if dataset_data.keywords:
            await MetadataService.update_dataset_keywords(db, new_dataset, dataset_data.keywords)
        
        # Add contacts
        if dataset_data.contacts:
            await MetadataService.update_dataset_contacts(db, new_dataset, dataset_data.contacts)
        
        # Add attributes
        if dataset_data.attributes:
            await MetadataService.update_dataset_attributes(db, new_dataset, dataset_data.attributes)
        
        await db.commit()
        await db.refresh(new_dataset)
        
        return new_dataset
    
    @staticmethod
    async def update_dataset(db: AsyncSession, dataset_id: int, dataset_data: DatasetUpdate) -> MetadataDataset:
        """
        Update a dataset
        
        Args:
            db: Database session
            dataset_id: Dataset ID
            dataset_data: Dataset data
            
        Returns:
            Updated dataset
        """
        # Get dataset
        dataset = await MetadataService.get_dataset(db, dataset_id)
        
        if not dataset:
            raise HTTPException(status_code=404, detail=f"Dataset not found: {dataset_id}")
        
        # Update dataset fields
        for field, value in dataset_data.dict(exclude_unset=True).items():
            if field not in ['keywords', 'contacts', 'attributes']:
                setattr(dataset, field, value)
        
        # Update geometry if bbox is provided
        if dataset_data.bbox and len(dataset_data.bbox) == 4:
            minx, miny, maxx, maxy = dataset_data.bbox
            geometry = box(minx, miny, maxx, maxy)
            dataset.geometry = from_shape(geometry, srid=4326)
        
        # Update keywords
        if dataset_data.keywords is not None:
            await MetadataService.update_dataset_keywords(db, dataset, dataset_data.keywords)
        
        # Update contacts
        if dataset_data.contacts is not None:
            await MetadataService.update_dataset_contacts(db, dataset, dataset_data.contacts)
        
        # Update attributes
        if dataset_data.attributes is not None:
            await MetadataService.update_dataset_attributes(db, dataset, dataset_data.attributes)
        
        # Update timestamp
        dataset.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(dataset)
        
        return dataset
    
    @staticmethod
    async def delete_dataset(db: AsyncSession, dataset_id: int) -> None:
        """
        Delete a dataset
        
        Args:
            db: Database session
            dataset_id: Dataset ID
        """
        # Get dataset
        dataset = await MetadataService.get_dataset(db, dataset_id)
        
        if not dataset:
            raise HTTPException(status_code=404, detail=f"Dataset not found: {dataset_id}")
        
        # Delete dataset
        await db.delete(dataset)
        await db.commit()
    
    @staticmethod
    async def update_dataset_keywords(db: AsyncSession, dataset: MetadataDataset, keywords: List[Union[str, Dict[str, Any]]]) -> None:
        """
        Update dataset keywords
        
        Args:
            db: Database session
            dataset: Dataset
            keywords: List of keywords (strings or dictionaries)
        """
        # Clear existing keywords
        dataset.keywords = []
        
        # Add keywords
        for keyword_data in keywords:
            keyword_name = keyword_data if isinstance(keyword_data, str) else keyword_data.get('name')
            
            if not keyword_name:
                continue
            
            # Check if keyword exists
            query = select(MetadataKeyword).filter(MetadataKeyword.name == keyword_name)
            result = await db.execute(query)
            keyword = result.scalar_one_or_none()
            
            if not keyword:
                # Create keyword
                thesaurus = None
                if isinstance(keyword_data, dict) and 'thesaurus' in keyword_data:
                    thesaurus = keyword_data['thesaurus']
                
                keyword = MetadataKeyword(name=keyword_name, thesaurus=thesaurus)
                db.add(keyword)
                await db.flush()
            
            # Add keyword to dataset
            dataset.keywords.append(keyword)
    
    @staticmethod
    async def update_dataset_contacts(db: AsyncSession, dataset: MetadataDataset, contacts: List[Dict[str, Any]]) -> None:
        """
        Update dataset contacts
        
        Args:
            db: Database session
            dataset: Dataset
            contacts: List of contacts
        """
        # Clear existing contacts
        dataset.contacts = []
        
        # Add contacts
        for contact_data in contacts:
            contact_id = contact_data.get('id')
            contact_role = contact_data.get('role', 'pointOfContact')
            
            if contact_id:
                # Get existing contact
                query = select(MetadataContact).filter(MetadataContact.id == contact_id)
                result = await db.execute(query)
                contact = result.scalar_one_or_none()
                
                if not contact:
                    continue
            else:
                # Create new contact
                contact = MetadataContact(
                    name=contact_data.get('name'),
                    organization=contact_data.get('organization'),
                    position=contact_data.get('position'),
                    email=contact_data.get('email'),
                    phone=contact_data.get('phone'),
                    address=contact_data.get('address'),
                    city=contact_data.get('city'),
                    state=contact_data.get('state'),
                    postal_code=contact_data.get('postal_code'),
                    country=contact_data.get('country'),
                    website=contact_data.get('website')
                )
                
                db.add(contact)
                await db.flush()
            
            # Add contact to dataset with role
            await db.execute(
                dataset_contact.insert().values(
                    dataset_id=dataset.id,
                    contact_id=contact.id,
                    role=contact_role
                )
            )
    
    @staticmethod
    async def update_dataset_attributes(db: AsyncSession, dataset: MetadataDataset, attributes: List[Dict[str, Any]]) -> None:
        """
        Update dataset attributes
        
        Args:
            db: Database session
            dataset: Dataset
            attributes: List of attributes
        """
        # Delete existing attributes
        await db.execute(
            delete(MetadataAttribute).where(MetadataAttribute.dataset_id == dataset.id)
        )
        
        # Add attributes
        for attr_data in attributes:
            attribute = MetadataAttribute(
                dataset_id=dataset.id,
                name=attr_data.get('name'),
                description=attr_data.get('description'),
                data_type=attr_data.get('data_type'),
                unit=attr_data.get('unit'),
                domain=attr_data.get('domain')
            )
            
            db.add(attribute)
    
    @staticmethod
    async def extract_metadata_from_file(file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from a file
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with extracted metadata
        """
        # This is a placeholder for actual metadata extraction
        # In a real implementation, this would use libraries like GDAL, Fiona, etc.
        
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_name)[1].lower()
        
        # Mock metadata based on file extension
        if file_ext in ['.shp', '.geojson', '.json', '.gpkg']:
            return {
                "title": file_name,
                "description": f"Metadata extracted from {file_name}",
                "resource_type": "dataset",
                "resource_format": file_ext[1:].upper(),
                "bbox": [-180, -90, 180, 90],
                "keywords": ["extracted", file_ext[1:].lower()],
                "attributes": [
                    {
                        "name": "id",
                        "data_type": "integer",
                        "description": "Feature identifier"
                    },
                    {
                        "name": "name",
                        "data_type": "string",
                        "description": "Feature name"
                    }
                ]
            }
        elif file_ext in ['.tif', '.tiff']:
            return {
                "title": file_name,
                "description": f"Metadata extracted from {file_name}",
                "resource_type": "dataset",
                "resource_format": "GeoTIFF",
                "bbox": [-180, -90, 180, 90],
                "keywords": ["extracted", "raster", "geotiff"]
            }
        else:
            return {
                "title": file_name,
                "description": f"Metadata extracted from {file_name}",
                "resource_type": "dataset",
                "resource_format": file_ext[1:].upper() if file_ext else "Unknown",
                "keywords": ["extracted"]
            }
    
    @staticmethod
    async def extract_metadata_from_service(service_url: str, service_type: str) -> Dict[str, Any]:
        """
        Extract metadata from a service
        
        Args:
            service_url: Service URL
            service_type: Service type (WMS, WFS, etc.)
            
        Returns:
            Dictionary with extracted metadata
        """
        # This is a placeholder for actual metadata extraction
        # In a real implementation, this would make requests to the service
        
        return {
            "title": f"{service_type} Service",
            "description": f"Metadata extracted from {service_url}",
            "resource_type": "service",
            "resource_url": service_url,
            "keywords": ["extracted", "service", service_type.lower()]
        }
    
    @staticmethod
    async def export_metadata_to_iso19139(dataset: MetadataDataset) -> str:
        """
        Export metadata to ISO 19139 XML
        
        Args:
            dataset: Dataset
            
        Returns:
            ISO 19139 XML string
        """
        # This is a placeholder for actual XML generation
        # In a real implementation, this would generate valid ISO 19139 XML
        
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<gmd:MD_Metadata xmlns:gmd="http://www.isotc211.org/2005/gmd"
                 xmlns:gco="http://www.isotc211.org/2005/gco"
                 xmlns:gml="http://www.opengis.net/gml">
  <gmd:fileIdentifier>
    <gco:CharacterString>{dataset.identifier or dataset.id}</gco:CharacterString>
  </gmd:fileIdentifier>
  <gmd:language>
    <gco:CharacterString>{dataset.metadata_language}</gco:CharacterString>
  </gmd:language>
  <gmd:identificationInfo>
    <gmd:MD_DataIdentification>
      <gmd:citation>
        <gmd:CI_Citation>
          <gmd:title>
            <gco:CharacterString>{dataset.title}</gco:CharacterString>
          </gmd:title>
        </gmd:CI_Citation>
      </gmd:citation>
      <gmd:abstract>
        <gco:CharacterString>{dataset.abstract or dataset.description or ''}</gco:CharacterString>
      </gmd:abstract>
    </gmd:MD_DataIdentification>
  </gmd:identificationInfo>
</gmd:MD_Metadata>
"""
        
        return xml
    
    @staticmethod
    async def export_metadata_to_dcat(dataset: MetadataDataset) -> Dict[str, Any]:
        """
        Export metadata to DCAT JSON-LD
        
        Args:
            dataset: Dataset
            
        Returns:
            DCAT JSON-LD dictionary
        """
        # This is a placeholder for actual DCAT generation
        # In a real implementation, this would generate valid DCAT JSON-LD
        
        dcat = {
            "@context": "https://www.w3.org/ns/dcat2.jsonld",
            "@type": "Dataset",
            "@id": dataset.identifier or f"urn:uuid:{dataset.id}",
            "title": dataset.title,
            "description": dataset.abstract or dataset.description or "",
            "keyword": [k.name for k in dataset.keywords],
            "issued": dataset.created_at.isoformat() if dataset.created_at else None,
            "modified": dataset.updated_at.isoformat() if dataset.updated_at else None,
            "publisher": {
                "@type": "Organization",
                "name": dataset.contacts[0].organization if dataset.contacts and dataset.contacts[0].organization else "Unknown"
            } if dataset.contacts else None
        }
        
        return dcat
