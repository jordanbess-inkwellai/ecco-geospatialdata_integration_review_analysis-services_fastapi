import json
from typing import Dict, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.services.process_registry import ProcessRegistry

async def raster_value_at_point_process(inputs: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
    """
    Get the raster value at a point
    """
    raster_table = inputs.get("raster_table")
    raster_column = inputs.get("raster_column", "rast")
    point = inputs.get("point")
    
    if not raster_table or not point:
        raise ValueError("Raster table and point are required")
    
    # Ensure table name is properly quoted to prevent SQL injection
    table_parts = raster_table.split('.')
    quoted_table = '.'.join([f'"{part}"' for part in table_parts])
    
    query = text(f"""
        SELECT ST_Value(
            {raster_column},
            ST_GeomFromGeoJSON(:point)
        ) AS value
        FROM {quoted_table}
        WHERE ST_Intersects(
            {raster_column},
            ST_GeomFromGeoJSON(:point)
        )
        LIMIT 1
    """)
    
    result = await db.execute(query, {"point": json.dumps(point)})
    row = result.fetchone()
    
    if not row:
        return {"value": None}
    
    return {"value": float(row.value) if row.value is not None else None}

async def raster_statistics_process(inputs: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
    """
    Calculate statistics for a raster within a geometry
    """
    raster_table = inputs.get("raster_table")
    raster_column = inputs.get("raster_column", "rast")
    geometry = inputs.get("geometry")
    
    if not raster_table or not geometry:
        raise ValueError("Raster table and geometry are required")
    
    # Ensure table name is properly quoted to prevent SQL injection
    table_parts = raster_table.split('.')
    quoted_table = '.'.join([f'"{part}"' for part in table_parts])
    
    query = text(f"""
        SELECT 
            (stats).min AS min,
            (stats).max AS max,
            (stats).mean AS mean,
            (stats).stddev AS stddev,
            (stats).count AS count
        FROM (
            SELECT ST_SummaryStats(
                ST_Clip(
                    {raster_column},
                    ST_GeomFromGeoJSON(:geometry)
                )
            ) AS stats
            FROM {quoted_table}
            WHERE ST_Intersects(
                {raster_column},
                ST_GeomFromGeoJSON(:geometry)
            )
            LIMIT 1
        ) subquery
    """)
    
    result = await db.execute(query, {"geometry": json.dumps(geometry)})
    row = result.fetchone()
    
    if not row:
        return {
            "min": None,
            "max": None,
            "mean": None,
            "stddev": None,
            "count": 0
        }
    
    return {
        "min": float(row.min) if row.min is not None else None,
        "max": float(row.max) if row.max is not None else None,
        "mean": float(row.mean) if row.mean is not None else None,
        "stddev": float(row.stddev) if row.stddev is not None else None,
        "count": int(row.count) if row.count is not None else 0
    }

async def raster_contour_process(inputs: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
    """
    Generate contour lines from a raster
    """
    raster_table = inputs.get("raster_table")
    raster_column = inputs.get("raster_column", "rast")
    interval = inputs.get("interval", 100)
    geometry = inputs.get("geometry")
    
    if not raster_table:
        raise ValueError("Raster table is required")
    
    # Ensure table name is properly quoted to prevent SQL injection
    table_parts = raster_table.split('.')
    quoted_table = '.'.join([f'"{part}"' for part in table_parts])
    
    # Build the query
    query_text = """
        SELECT jsonb_build_object(
            'type', 'FeatureCollection',
            'features', jsonb_agg(features.feature)
        ) AS geojson
        FROM (
            SELECT jsonb_build_object(
                'type', 'Feature',
                'geometry', ST_AsGeoJSON(geom)::jsonb,
                'properties', jsonb_build_object(
                    'value', value
                )
            ) AS feature
            FROM (
                SELECT (ST_DumpAsPolygons(
    """
    
    # If geometry is provided, clip the raster
    if geometry:
        query_text += f"""
                    ST_ContourLines(
                        ST_Clip(
                            {raster_column},
                            ST_GeomFromGeoJSON(:geometry)
                        ),
                        :interval
                    )
        """
    else:
        query_text += f"""
                    ST_ContourLines(
                        {raster_column},
                        :interval
                    )
        """
    
    # Complete the query
    query_text += f"""
                )).geom AS geom,
                (ST_DumpAsPolygons(
    """
    
    # If geometry is provided, clip the raster
    if geometry:
        query_text += f"""
                    ST_ContourLines(
                        ST_Clip(
                            {raster_column},
                            ST_GeomFromGeoJSON(:geometry)
                        ),
                        :interval
                    )
        """
    else:
        query_text += f"""
                    ST_ContourLines(
                        {raster_column},
                        :interval
                    )
        """
    
    # Complete the query
    query_text += f"""
                )).val AS value
                FROM {quoted_table}
                WHERE {raster_column} IS NOT NULL
    """
    
    # Add geometry filter if provided
    if geometry:
        query_text += f"""
                AND ST_Intersects(
                    {raster_column},
                    ST_GeomFromGeoJSON(:geometry)
                )
        """
    
    # Complete the query
    query_text += """
                LIMIT 1
            ) subquery
        ) features
    """
    
    # Set up parameters
    params = {"interval": interval}
    
    if geometry:
        params["geometry"] = json.dumps(geometry)
    
    # Execute the query
    query = text(query_text)
    result = await db.execute(query, params)
    row = result.fetchone()
    
    if not row or not row.geojson:
        return {
            "type": "FeatureCollection",
            "features": []
        }
    
    return row.geojson

def register_raster_processes(registry: ProcessRegistry):
    """
    Register raster processes with the registry
    
    Args:
        registry: Process registry
    """
    # Raster value at point process
    registry.register_process(
        process_id="raster_value_at_point",
        process_func=raster_value_at_point_process,
        description="Get the raster value at a point",
        inputs={
            "raster_table": {
                "title": "Raster Table",
                "description": "The name of the raster table",
                "schema": {"type": "string"},
                "required": True
            },
            "raster_column": {
                "title": "Raster Column",
                "description": "The name of the raster column",
                "schema": {"type": "string"},
                "required": False,
                "default": "rast"
            },
            "point": {
                "title": "Point",
                "description": "The point to get the value at",
                "schema": {"type": "object"},
                "required": True
            }
        },
        outputs={
            "value": {
                "title": "Value",
                "description": "The raster value at the point",
                "schema": {"type": "number"}
            }
        }
    )
    
    # Raster statistics process
    registry.register_process(
        process_id="raster_statistics",
        process_func=raster_statistics_process,
        description="Calculate statistics for a raster within a geometry",
        inputs={
            "raster_table": {
                "title": "Raster Table",
                "description": "The name of the raster table",
                "schema": {"type": "string"},
                "required": True
            },
            "raster_column": {
                "title": "Raster Column",
                "description": "The name of the raster column",
                "schema": {"type": "string"},
                "required": False,
                "default": "rast"
            },
            "geometry": {
                "title": "Geometry",
                "description": "The geometry to calculate statistics within",
                "schema": {"type": "object"},
                "required": True
            }
        },
        outputs={
            "min": {
                "title": "Minimum",
                "description": "The minimum value",
                "schema": {"type": "number"}
            },
            "max": {
                "title": "Maximum",
                "description": "The maximum value",
                "schema": {"type": "number"}
            },
            "mean": {
                "title": "Mean",
                "description": "The mean value",
                "schema": {"type": "number"}
            },
            "stddev": {
                "title": "Standard Deviation",
                "description": "The standard deviation",
                "schema": {"type": "number"}
            },
            "count": {
                "title": "Count",
                "description": "The number of cells",
                "schema": {"type": "integer"}
            }
        }
    )
    
    # Raster contour process
    registry.register_process(
        process_id="raster_contour",
        process_func=raster_contour_process,
        description="Generate contour lines from a raster",
        inputs={
            "raster_table": {
                "title": "Raster Table",
                "description": "The name of the raster table",
                "schema": {"type": "string"},
                "required": True
            },
            "raster_column": {
                "title": "Raster Column",
                "description": "The name of the raster column",
                "schema": {"type": "string"},
                "required": False,
                "default": "rast"
            },
            "interval": {
                "title": "Interval",
                "description": "The interval between contour lines",
                "schema": {"type": "number"},
                "required": False,
                "default": 100
            },
            "geometry": {
                "title": "Geometry",
                "description": "The geometry to clip the raster to",
                "schema": {"type": "object"},
                "required": False
            }
        },
        outputs={
            "contours": {
                "title": "Contours",
                "description": "The contour lines",
                "schema": {"type": "object"}
            }
        }
    )
