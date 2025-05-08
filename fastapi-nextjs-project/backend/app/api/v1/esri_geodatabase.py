from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, Body
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
import os
import logging
from pydantic import BaseModel

from app.core.database import get_db
from app.services.esri_geodatabase_converter import ESRIGeodatabaseConverter

router = APIRouter()
logger = logging.getLogger(__name__)


class ConvertToGeoJSONRequest(BaseModel):
    geodatabase_path: str
    feature_class_name: str
    output_path: Optional[str] = None


class ConvertToGpkgRequest(BaseModel):
    geodatabase_path: str
    feature_class_names: List[str]
    output_path: Optional[str] = None


class ConvertToDuckDBRequest(BaseModel):
    geodatabase_path: str
    feature_class_names: List[str]
    db_name: str
    spatial_index: bool = True
    overwrite: bool = False


class ConvertToPostGISSchemaRequest(BaseModel):
    geodatabase_path: str
    feature_class_names: List[str]
    schema_name: Optional[str] = None
    spatial_index: bool = True
    drop_if_exists: bool = False
    include_comments: bool = True


class ConvertRemoteGeodatabaseRequest(BaseModel):
    remote_path: str
    feature_class_names: Optional[List[str]] = None
    output_format: str = "geojson"
    schema_name: Optional[str] = None
    spatial_index: bool = True
    drop_if_exists: bool = False
    include_comments: bool = True


@router.post("/list-feature-classes")
async def list_feature_classes(
    geodatabase_path: str = Body(..., description="Path to the ESRI Mobile Geodatabase file"),
    db: AsyncSession = Depends(get_db)
):
    """
    List all feature classes in an ESRI Mobile Geodatabase
    """
    try:
        result = ESRIGeodatabaseConverter.list_feature_classes(geodatabase_path)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing feature classes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing feature classes: {str(e)}")


@router.post("/convert-to-geojson")
async def convert_to_geojson(
    request: ConvertToGeoJSONRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Convert an ESRI Mobile Geodatabase feature class to GeoJSON
    """
    try:
        result = await ESRIGeodatabaseConverter.convert_to_geojson(
            geodatabase_path=request.geodatabase_path,
            feature_class_name=request.feature_class_name,
            output_path=request.output_path
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error converting to GeoJSON: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error converting to GeoJSON: {str(e)}")


@router.post("/convert-to-gpkg")
async def convert_to_gpkg(
    request: ConvertToGpkgRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Convert ESRI Mobile Geodatabase feature classes to GeoPackage
    """
    try:
        result = await ESRIGeodatabaseConverter.convert_to_gpkg(
            geodatabase_path=request.geodatabase_path,
            feature_class_names=request.feature_class_names,
            output_path=request.output_path
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error converting to GeoPackage: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error converting to GeoPackage: {str(e)}")


@router.post("/convert-to-duckdb")
async def convert_to_duckdb(
    request: ConvertToDuckDBRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Convert ESRI Mobile Geodatabase feature classes to DuckDB
    """
    try:
        result = await ESRIGeodatabaseConverter.convert_to_duckdb(
            geodatabase_path=request.geodatabase_path,
            feature_class_names=request.feature_class_names,
            db_name=request.db_name,
            spatial_index=request.spatial_index,
            overwrite=request.overwrite
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error converting to DuckDB: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error converting to DuckDB: {str(e)}")


@router.post("/upload-geodatabase")
async def upload_geodatabase(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload an ESRI Mobile Geodatabase file
    """
    try:
        # Define upload directory
        upload_dir = os.path.join(os.getcwd(), "data", "geodatabases")
        os.makedirs(upload_dir, exist_ok=True)

        # Save the uploaded file
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # List feature classes
        feature_classes = ESRIGeodatabaseConverter.list_feature_classes(file_path)

        return {
            "file_name": file.filename,
            "file_path": file_path,
            "size_bytes": os.path.getsize(file_path),
            "feature_class_count": len(feature_classes),
            "feature_classes": feature_classes
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading geodatabase: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading geodatabase: {str(e)}")


@router.get("/download-geojson/{feature_class_name}")
async def download_geojson(
    feature_class_name: str,
    geodatabase_path: str = Query(..., description="Path to the ESRI Mobile Geodatabase file"),
    db: AsyncSession = Depends(get_db)
):
    """
    Convert and download a feature class as GeoJSON
    """
    try:
        # Convert to GeoJSON
        result = await ESRIGeodatabaseConverter.convert_to_geojson(
            geodatabase_path=geodatabase_path,
            feature_class_name=feature_class_name
        )

        # Return the file
        return FileResponse(
            path=result["output_path"],
            filename=f"{feature_class_name}.geojson",
            media_type="application/geo+json"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading GeoJSON: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error downloading GeoJSON: {str(e)}")


@router.get("/download-gpkg")
async def download_gpkg(
    geodatabase_path: str = Query(..., description="Path to the ESRI Mobile Geodatabase file"),
    feature_class_names: str = Query(..., description="Comma-separated list of feature class names"),
    db: AsyncSession = Depends(get_db)
):
    """
    Convert and download feature classes as GeoPackage
    """
    try:
        # Parse feature class names
        feature_classes = feature_class_names.split(",")

        # Convert to GeoPackage
        result = await ESRIGeodatabaseConverter.convert_to_gpkg(
            geodatabase_path=geodatabase_path,
            feature_class_names=feature_classes
        )

        # Return the file
        return FileResponse(
            path=result["output_path"],
            filename=os.path.basename(result["output_path"]),
            media_type="application/geopackage+sqlite3"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading GeoPackage: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error downloading GeoPackage: {str(e)}")


@router.post("/convert-to-postgis-schema")
async def convert_to_postgis_schema(
    request: ConvertToPostGISSchemaRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Convert ESRI Mobile Geodatabase feature classes to PostGIS schema SQL
    """
    try:
        result = await ESRIGeodatabaseConverter.convert_to_postgis_schema(
            geodatabase_path=request.geodatabase_path,
            feature_class_names=request.feature_class_names,
            schema_name=request.schema_name,
            spatial_index=request.spatial_index,
            drop_if_exists=request.drop_if_exists,
            include_comments=request.include_comments
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error converting to PostGIS schema: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error converting to PostGIS schema: {str(e)}")


@router.get("/download-postgis-schema")
async def download_postgis_schema(
    geodatabase_path: str = Query(..., description="Path to the ESRI Mobile Geodatabase file"),
    feature_class_names: str = Query(..., description="Comma-separated list of feature class names"),
    schema_name: Optional[str] = Query(None, description="PostgreSQL schema name"),
    spatial_index: bool = Query(True, description="Whether to create spatial indexes"),
    drop_if_exists: bool = Query(False, description="Whether to include DROP TABLE statements"),
    include_comments: bool = Query(True, description="Whether to include comments in the SQL")
):
    """
    Convert ESRI Mobile Geodatabase feature classes to PostGIS schema SQL and download as a file
    """
    try:
        # Parse feature class names
        feature_classes = feature_class_names.split(",")

        # Convert to PostGIS schema
        result = await ESRIGeodatabaseConverter.convert_to_postgis_schema(
            geodatabase_path=geodatabase_path,
            feature_class_names=feature_classes,
            schema_name=schema_name,
            spatial_index=spatial_index,
            drop_if_exists=drop_if_exists,
            include_comments=include_comments
        )

        # Create a temporary file with the SQL
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".sql", mode="w")
        temp_file.write(result["sql"])
        temp_file.close()

        # Generate filename
        if schema_name:
            filename = f"{schema_name}_schema.sql"
        else:
            filename = f"postgis_schema.sql"

        # Return the file
        return FileResponse(
            path=temp_file.name,
            filename=filename,
            media_type="application/sql"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading PostGIS schema: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error downloading PostGIS schema: {str(e)}")


@router.post("/convert-remote-geodatabase")
async def convert_remote_geodatabase(
    request: ConvertRemoteGeodatabaseRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Convert a remote ESRI Mobile Geodatabase to the specified format
    """
    try:
        result = await ESRIGeodatabaseConverter.convert_remote_geodatabase(
            remote_path=request.remote_path,
            feature_class_names=request.feature_class_names,
            output_format=request.output_format,
            schema_name=request.schema_name,
            spatial_index=request.spatial_index,
            drop_if_exists=request.drop_if_exists,
            include_comments=request.include_comments
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error converting remote geodatabase: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error converting remote geodatabase: {str(e)}")


@router.get("/download-remote-geodatabase")
async def download_remote_geodatabase(
    remote_path: str = Query(..., description="Remote path in the format 'remote:path/to/file.geodatabase'"),
    feature_class_names: Optional[str] = Query(None, description="Comma-separated list of feature class names (optional)"),
    output_format: str = Query("geojson", description="Output format (geojson, gpkg, postgis_schema)"),
    schema_name: Optional[str] = Query(None, description="PostgreSQL schema name (for postgis_schema format)")
):
    """
    Convert a remote ESRI Mobile Geodatabase to the specified format and download the result
    """
    try:
        # Parse feature class names if provided
        parsed_feature_classes = None
        if feature_class_names:
            parsed_feature_classes = feature_class_names.split(",")

        # Convert the remote geodatabase
        result = await ESRIGeodatabaseConverter.convert_remote_geodatabase(
            remote_path=remote_path,
            feature_class_names=parsed_feature_classes,
            output_format=output_format,
            schema_name=schema_name
        )

        # Return the appropriate file based on the output format
        if output_format == "geojson":
            return FileResponse(
                path=result["output_path"],
                filename=f"{os.path.basename(remote_path).split('.')[0]}.geojson",
                media_type="application/geo+json"
            )
        elif output_format == "gpkg":
            return FileResponse(
                path=result["output_path"],
                filename=os.path.basename(result["output_path"]),
                media_type="application/geopackage+sqlite3"
            )
        elif output_format == "postgis_schema":
            # Create a temporary file with the SQL
            import tempfile
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".sql", mode="w")
            temp_file.write(result["sql"])
            temp_file.close()

            # Generate filename
            if schema_name:
                filename = f"{schema_name}_schema.sql"
            else:
                filename = f"postgis_schema.sql"

            return FileResponse(
                path=temp_file.name,
                filename=filename,
                media_type="application/sql"
            )
        else:
            return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading remote geodatabase: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error downloading remote geodatabase: {str(e)}")
