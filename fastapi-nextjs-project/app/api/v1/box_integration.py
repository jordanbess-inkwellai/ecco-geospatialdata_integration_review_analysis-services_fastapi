from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, Path, Body
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse
from typing import Dict, List, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import os
import json
from datetime import datetime

from app.core.database import get_db
from app.core.box_config import box_config
from app.services.box_service import box_service
from app.schemas.box_schemas import (
    BoxFolderContents,
    BoxFileInfo,
    BoxMetadata,
    BoxSearchQuery,
    BoxUploadResponse,
    BoxSharedLinkResponse
)

router = APIRouter()

@router.get("/status", response_model=Dict[str, Any])
async def get_box_status():
    """
    Get the status of the Box.com integration.
    
    Returns:
        Status information
    """
    return {
        "configured": box_config.is_configured,
        "jwt_configured": box_config.is_jwt_configured,
        "oauth_configured": box_config.is_oauth_configured,
        "client_initialized": box_service.client is not None,
        "metadata_template_initialized": box_service.metadata_template is not None
    }

@router.get("/auth/url", response_model=Dict[str, str])
async def get_auth_url():
    """
    Get the OAuth2 authorization URL for Box.com.
    
    Returns:
        Authorization URL
    """
    if not box_config.is_oauth_configured:
        raise HTTPException(status_code=400, detail="Box.com OAuth2 is not configured")
    
    try:
        auth_url = box_service.get_oauth_authorize_url()
        return {"auth_url": auth_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting authorization URL: {str(e)}")

@router.get("/oauth2callback")
async def oauth2_callback(code: str = Query(...), state: Optional[str] = Query(None)):
    """
    Handle the OAuth2 callback from Box.com.
    
    Args:
        code: Authorization code
        state: State parameter (optional)
        
    Returns:
        Redirect to the frontend
    """
    if not box_config.is_oauth_configured:
        raise HTTPException(status_code=400, detail="Box.com OAuth2 is not configured")
    
    try:
        success = box_service.complete_oauth_flow(code)
        
        # Redirect to the frontend with success/failure status
        redirect_url = f"{box_config.redirect_uri.split('/api')[0]}?box_auth_success={success}"
        return RedirectResponse(url=redirect_url)
    except Exception as e:
        # Redirect to the frontend with error
        redirect_url = f"{box_config.redirect_uri.split('/api')[0]}?box_auth_error={str(e)}"
        return RedirectResponse(url=redirect_url)

@router.get("/folders/{folder_id}", response_model=BoxFolderContents)
async def get_folder_contents(folder_id: str = Path("0")):
    """
    Get the contents of a Box folder.
    
    Args:
        folder_id: ID of the folder to list (default: "0" for root folder)
        
    Returns:
        Folder contents
    """
    if not box_service.client:
        raise HTTPException(status_code=400, detail="Box.com client is not initialized")
    
    try:
        items = box_service.list_folder_contents(folder_id)
        return {"folder_id": folder_id, "items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing folder contents: {str(e)}")

@router.get("/files/{file_id}", response_model=BoxFileInfo)
async def get_file_info(file_id: str):
    """
    Get information about a Box file.
    
    Args:
        file_id: ID of the file
        
    Returns:
        File information
    """
    if not box_service.client:
        raise HTTPException(status_code=400, detail="Box.com client is not initialized")
    
    try:
        file_obj = box_service.client.file(file_id=file_id).get()
        
        file_info = {
            "id": file_obj.id,
            "name": file_obj.name,
            "type": file_obj.type,
            "size": file_obj.size,
            "created_at": file_obj.created_at,
            "modified_at": file_obj.modified_at,
            "has_metadata": False
        }
        
        # Check if file has geospatial metadata
        try:
            metadata = file_obj.metadata(
                scope=box_config.metadata_template_scope,
                template=box_config.metadata_template_name
            ).get()
            if metadata:
                file_info["has_metadata"] = True
                file_info["metadata"] = metadata
        except Exception:
            # Ignore errors getting metadata
            pass
        
        return file_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting file info: {str(e)}")

@router.get("/files/{file_id}/download")
async def download_file(file_id: str, background_tasks: BackgroundTasks):
    """
    Download a file from Box.
    
    Args:
        file_id: ID of the file to download
        
    Returns:
        The downloaded file
    """
    if not box_service.client:
        raise HTTPException(status_code=400, detail="Box.com client is not initialized")
    
    try:
        # Get file info
        file_obj = box_service.client.file(file_id=file_id).get()
        file_name = file_obj.name
        
        # Download the file to a temporary location
        local_path = box_service.download_file(file_id)
        
        # Schedule cleanup of the temporary file
        background_tasks.add_task(os.unlink, local_path)
        
        return FileResponse(
            path=local_path,
            filename=file_name,
            media_type="application/octet-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")

@router.post("/files/{file_id}/metadata", response_model=BoxMetadata)
async def update_file_metadata(file_id: str, metadata: Dict[str, Any] = Body(...)):
    """
    Update the geospatial metadata for a file.
    
    Args:
        file_id: ID of the file to update
        metadata: Metadata to apply to the file
        
    Returns:
        Updated metadata
    """
    if not box_service.client or not box_service.metadata_template:
        raise HTTPException(status_code=400, detail="Box.com client or metadata template is not initialized")
    
    try:
        updated_metadata = box_service.update_metadata(file_id, metadata)
        return updated_metadata
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating metadata: {str(e)}")

@router.post("/search", response_model=List[BoxFileInfo])
async def search_files(query: BoxSearchQuery):
    """
    Search for files in Box.
    
    Args:
        query: Search parameters
        
    Returns:
        List of matching files
    """
    if not box_service.client:
        raise HTTPException(status_code=400, detail="Box.com client is not initialized")
    
    try:
        results = box_service.search_files(
            query=query.query,
            file_extensions=query.file_extensions,
            metadata_query=query.metadata_query,
            limit=query.limit
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching files: {str(e)}")

@router.post("/folders/{folder_id}/upload", response_model=BoxUploadResponse)
async def upload_file(
    folder_id: str,
    background_tasks: BackgroundTasks,
    file: bytes = Body(...),
    file_name: str = Query(...),
    extract_metadata: bool = Query(False)
):
    """
    Upload a file to Box.
    
    Args:
        folder_id: ID of the folder to upload to
        file: File content
        file_name: Name to give the file in Box
        extract_metadata: Whether to extract and update metadata
        
    Returns:
        Information about the uploaded file
    """
    if not box_service.client:
        raise HTTPException(status_code=400, detail="Box.com client is not initialized")
    
    try:
        # Save the file to a temporary location
        temp_file_path = os.path.join(box_config.cache_dir, file_name)
        with open(temp_file_path, "wb") as f:
            f.write(file)
        
        # Upload the file to Box
        uploaded_file = box_service.upload_file(folder_id, temp_file_path, file_name)
        
        # Extract and update metadata if requested
        if extract_metadata:
            metadata = box_service.extract_metadata_from_file(temp_file_path)
            updated_metadata = box_service.update_metadata(uploaded_file["id"], metadata)
            uploaded_file["metadata"] = updated_metadata
        
        # Schedule cleanup of the temporary file
        background_tasks.add_task(os.unlink, temp_file_path)
        
        return uploaded_file
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@router.post("/files/{file_id}/share", response_model=BoxSharedLinkResponse)
async def create_shared_link(
    file_id: str,
    access: str = Query("open"),
    password: Optional[str] = Query(None),
    expires_days: Optional[int] = Query(None)
):
    """
    Create a shared link for a file.
    
    Args:
        file_id: ID of the file to share
        access: Access level ("open", "company", or "collaborators")
        password: Optional password to protect the link
        expires_days: Optional number of days until the link expires
        
    Returns:
        Shared link URL
    """
    if not box_service.client:
        raise HTTPException(status_code=400, detail="Box.com client is not initialized")
    
    try:
        # Calculate expiration date if specified
        expires_at = None
        if expires_days:
            expires_at = datetime.now() + datetime.timedelta(days=expires_days)
        
        shared_link = box_service.create_shared_link(
            file_id=file_id,
            access=access,
            password=password,
            expires_at=expires_at
        )
        
        return {"shared_link": shared_link}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating shared link: {str(e)}")

@router.post("/files/{file_id}/import", response_model=BoxFileInfo)
async def import_file(
    file_id: str,
    background_tasks: BackgroundTasks,
    destination_path: Optional[str] = Query(None)
):
    """
    Import a file from Box, download it, and extract its metadata.
    
    Args:
        file_id: ID of the file to import
        destination_path: Path where the file should be saved (optional)
        
    Returns:
        Information about the imported file including metadata
    """
    if not box_service.client:
        raise HTTPException(status_code=400, detail="Box.com client is not initialized")
    
    try:
        file_info = box_service.import_file_with_metadata(file_id, destination_path)
        
        # If no destination path was provided, schedule cleanup of the temporary file
        if not destination_path and "local_path" in file_info:
            background_tasks.add_task(os.unlink, file_info["local_path"])
        
        return file_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error importing file: {str(e)}")

@router.post("/webhook", response_model=Dict[str, Any])
async def handle_webhook(payload: Dict[str, Any] = Body(...), headers: Dict[str, str] = Body(...)):
    """
    Handle Box.com webhook events.
    
    Args:
        payload: Webhook payload
        headers: Webhook headers
        
    Returns:
        Acknowledgement
    """
    if not box_service.client:
        raise HTTPException(status_code=400, detail="Box.com client is not initialized")
    
    try:
        # Verify webhook signature if configured
        if box_config.webhook_signature_key:
            # TODO: Implement webhook signature verification
            pass
        
        # Process the webhook event
        event_type = payload.get("trigger", {}).get("trigger_type")
        
        if event_type == "FILE.UPLOADED" or event_type == "FILE.PREVIEWED":
            # Extract file ID from the webhook payload
            file_id = payload.get("source", {}).get("id")
            
            if file_id:
                # Process the file asynchronously
                # TODO: Implement background task for processing files
                pass
        
        return {"status": "success", "event_type": event_type}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error handling webhook: {str(e)}")
