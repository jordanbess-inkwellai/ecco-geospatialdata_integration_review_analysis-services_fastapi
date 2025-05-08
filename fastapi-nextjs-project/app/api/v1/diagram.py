from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.eralchemy_service import eralchemy_service
from app.services.pgmodeler_service import pgmodeler_service

router = APIRouter()

@router.post("/eralchemy/generate-from-db", response_class=FileResponse)
async def generate_eralchemy_diagram_from_db(
    connection_string: str = Form(...),
    output_format: str = Form("png"),
    exclude_tables: Optional[List[str]] = Form(None),
    exclude_columns: Optional[List[str]] = Form(None)
):
    """Generate ER diagram from database using ERAlchemy"""
    try:
        output_file = eralchemy_service.generate_diagram_from_db(
            connection_string=connection_string,
            output_format=output_format,
            exclude_tables=exclude_tables,
            exclude_columns=exclude_columns
        )
        
        return FileResponse(
            path=output_file,
            filename=f"eralchemy_diagram.{output_format}",
            media_type=f"image/{output_format}" if output_format != "pdf" else "application/pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pgmodeler/import-db", response_class=FileResponse)
async def import_database_with_pgmodeler(
    connection_string: str = Form(...),
    import_system_objects: bool = Form(False),
    import_extension_objects: bool = Form(True)
):
    """Import database schema using PgModeler"""
    try:
        output_file = pgmodeler_service.import_database(
            connection_string=connection_string,
            import_system_objects=import_system_objects,
            import_extension_objects=import_extension_objects
        )
        
        return FileResponse(
            path=output_file,
            filename="pgmodeler_model.dbm",
            media_type="application/octet-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pgmodeler/export-model", response_class=FileResponse)
async def export_pgmodeler_model(
    model_file: UploadFile = File(...),
    output_format: str = Form("png")
):
    """Export PgModeler model to different formats"""
    try:
        # Save uploaded file
        temp_model_path = f"/tmp/{model_file.filename}"
        with open(temp_model_path, "wb") as f:
            f.write(await model_file.read())
        
        # Export model
        output_file = pgmodeler_service.export_model(
            model_file=temp_model_path,
            output_format=output_format
        )
        
        # Determine media type
        media_type = {
            "png": "image/png",
            "svg": "image/svg+xml",
            "pdf": "application/pdf",
            "sql": "text/plain",
            "data-dict": "text/html"
        }.get(output_format, "application/octet-stream")
        
        return FileResponse(
            path=output_file,
            filename=f"pgmodeler_export.{output_format}",
            media_type=media_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
