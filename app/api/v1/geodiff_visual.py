from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from typing import List, Optional, Dict, Any
import os
import tempfile

from app.services.geodiff_visual_service import geodiff_visual_service

router = APIRouter()

@router.post("/static-diff-map", response_class=FileResponse)
async def generate_static_diff_map(
    base_file: UploadFile = File(...),
    modified_file: UploadFile = File(...),
    layer_name: Optional[str] = Form(None),
    output_format: str = Form("png"),
    width: int = Form(1200),
    height: int = Form(800),
    basemap: bool = Form(True)
):
    """Generate a static map showing differences between two GeoPackage files"""
    try:
        # Save uploaded files
        temp_dir = tempfile.mkdtemp()
        base_path = os.path.join(temp_dir, base_file.filename)
        modified_path = os.path.join(temp_dir, modified_file.filename)
        
        with open(base_path, "wb") as f:
            f.write(await base_file.read())
        
        with open(modified_path, "wb") as f:
            f.write(await modified_file.read())
        
        # Generate static diff map
        output_file = geodiff_visual_service.generate_static_diff_map(
            base_file=base_path,
            modified_file=modified_path,
            layer_name=layer_name,
            output_format=output_format,
            width=width,
            height=height,
            basemap=basemap
        )
        
        # Determine media type
        media_type = {
            "png": "image/png",
            "jpg": "image/jpeg",
            "pdf": "application/pdf",
            "svg": "image/svg+xml"
        }.get(output_format, "application/octet-stream")
        
        return FileResponse(
            path=output_file,
            filename=f"diff_map.{output_format}",
            media_type=media_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/interactive-diff-map", response_class=HTMLResponse)
async def generate_interactive_diff_map(
    base_file: UploadFile = File(...),
    modified_file: UploadFile = File(...),
    changeset_file: Optional[UploadFile] = File(None),
    layer_name: Optional[str] = Form(None)
):
    """Generate an interactive HTML map showing differences between two GeoPackage files"""
    try:
        # Save uploaded files
        temp_dir = tempfile.mkdtemp()
        base_path = os.path.join(temp_dir, base_file.filename)
        modified_path = os.path.join(temp_dir, modified_file.filename)
        
        with open(base_path, "wb") as f:
            f.write(await base_file.read())
        
        with open(modified_path, "wb") as f:
            f.write(await modified_file.read())
        
        changeset_path = None
        if changeset_file:
            changeset_path = os.path.join(temp_dir, changeset_file.filename)
            with open(changeset_path, "wb") as f:
                f.write(await changeset_file.read())
        
        # Generate interactive diff map
        output_file = geodiff_visual_service.generate_interactive_diff_map(
            base_file=base_path,
            modified_file=modified_path,
            changeset_file=changeset_path,
            layer_name=layer_name
        )
        
        # Read HTML file
        with open(output_file, "r") as f:
            html_content = f.read()
        
        return HTMLResponse(content=html_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/change-statistics", response_model=Dict[str, Any])
async def generate_change_statistics(
    changeset_file: UploadFile = File(...)
):
    """Generate statistics about changes in a changeset"""
    try:
        # Save uploaded file
        temp_dir = tempfile.mkdtemp()
        changeset_path = os.path.join(temp_dir, changeset_file.filename)
        
        with open(changeset_path, "wb") as f:
            f.write(await changeset_file.read())
        
        # Generate statistics
        statistics = geodiff_visual_service.generate_change_statistics(changeset_path)
        
        return statistics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/diff-report", response_class=HTMLResponse)
async def generate_diff_report(
    base_file: UploadFile = File(...),
    modified_file: UploadFile = File(...),
    changeset_file: UploadFile = File(...),
    layer_name: Optional[str] = Form(None)
):
    """Generate a comprehensive HTML report about differences"""
    try:
        # Save uploaded files
        temp_dir = tempfile.mkdtemp()
        base_path = os.path.join(temp_dir, base_file.filename)
        modified_path = os.path.join(temp_dir, modified_file.filename)
        changeset_path = os.path.join(temp_dir, changeset_file.filename)
        
        with open(base_path, "wb") as f:
            f.write(await base_file.read())
        
        with open(modified_path, "wb") as f:
            f.write(await modified_file.read())
        
        with open(changeset_path, "wb") as f:
            f.write(await changeset_file.read())
        
        # Generate diff report
        output_file = geodiff_visual_service.generate_diff_report(
            base_file=base_path,
            modified_file=modified_path,
            changeset_file=changeset_path,
            layer_name=layer_name
        )
        
        # Read HTML file
        with open(output_file, "r") as f:
            html_content = f.read()
        
        return HTMLResponse(content=html_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
