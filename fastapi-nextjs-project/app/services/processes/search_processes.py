import json
from typing import Dict, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.services.process_registry import ProcessRegistry

async def bbox_search_process(inputs: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
    """
    Search for features within a bounding box
    """
    bbox = inputs.get("bbox")
    table_name = inputs.get("table_name")
    geometry_column = inputs.get("geometry_column", "geom")
    limit = inputs.get("limit", 100)
    
    if not bbox or not table_name:
        raise ValueError("Bounding box and table name are required")
    
    # Ensure table name is properly quoted to prevent SQL injection
    table_parts = table_name.split('.')
    quoted_table = '.'.join([f'"{part}"' for part in table_parts])
    
    query = text(f"""
        SELECT jsonb_build_object(
            'type', 'FeatureCollection',
            'features', jsonb_agg(features.feature)
        ) AS geojson
        FROM (
            SELECT jsonb_build_object(
                'type', 'Feature',
                'id', id,
                'geometry', ST_AsGeoJSON({geometry_column})::jsonb,
                'properties', to_jsonb(row) - '{geometry_column}'
            ) AS feature
            FROM (
                SELECT *
                FROM {quoted_table}
                WHERE {geometry_column} && ST_MakeEnvelope(:xmin, :ymin, :xmax, :ymax, 4326)
                LIMIT :limit
            ) row
        ) features
    """)
    
    result = await db.execute(query, {
        "xmin": bbox[0],
        "ymin": bbox[1],
        "xmax": bbox[2],
        "ymax": bbox[3],
        "limit": limit
    })
    row = result.fetchone()
    
    if not row or not row.geojson:
        return {
            "type": "FeatureCollection",
            "features": []
        }
    
    return row.geojson

async def spatial_relationship_search_process(inputs: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
    """
    Search for features with a specific spatial relationship to a geometry
    """
    geometry = inputs.get("geometry")
    table_name = inputs.get("table_name")
    geometry_column = inputs.get("geometry_column", "geom")
    relationship = inputs.get("relationship", "intersects")
    limit = inputs.get("limit", 100)
    
    if not geometry or not table_name:
        raise ValueError("Geometry and table name are required")
    
    # Map relationship to PostGIS function
    relationship_functions = {
        "intersects": "ST_Intersects",
        "contains": "ST_Contains",
        "within": "ST_Within",
        "touches": "ST_Touches",
        "overlaps": "ST_Overlaps"
    }
    
    if relationship not in relationship_functions:
        raise ValueError(f"Unsupported relationship: {relationship}")
    
    rel_function = relationship_functions[relationship]
    
    # Ensure table name is properly quoted to prevent SQL injection
    table_parts = table_name.split('.')
    quoted_table = '.'.join([f'"{part}"' for part in table_parts])
    
    query = text(f"""
        SELECT jsonb_build_object(
            'type', 'FeatureCollection',
            'features', jsonb_agg(features.feature)
        ) AS geojson
        FROM (
            SELECT jsonb_build_object(
                'type', 'Feature',
                'id', id,
                'geometry', ST_AsGeoJSON({geometry_column})::jsonb,
                'properties', to_jsonb(row) - '{geometry_column}'
            ) AS feature
            FROM (
                SELECT *
                FROM {quoted_table}
                WHERE {rel_function}({geometry_column}, ST_GeomFromGeoJSON(:geometry))
                LIMIT :limit
            ) row
        ) features
    """)
    
    result = await db.execute(query, {
        "geometry": json.dumps(geometry),
        "limit": limit
    })
    row = result.fetchone()
    
    if not row or not row.geojson:
        return {
            "type": "FeatureCollection",
            "features": []
        }
    
    return row.geojson

async def nearest_neighbor_process(inputs: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
    """
    Find the nearest neighbors to a geometry
    """
    geometry = inputs.get("geometry")
    table_name = inputs.get("table_name")
    geometry_column = inputs.get("geometry_column", "geom")
    max_distance = inputs.get("max_distance")
    limit = inputs.get("limit", 5)
    
    if not geometry or not table_name:
        raise ValueError("Geometry and table name are required")
    
    # Ensure table name is properly quoted to prevent SQL injection
    table_parts = table_name.split('.')
    quoted_table = '.'.join([f'"{part}"' for part in table_parts])
    
    # Build the query
    query_text = f"""
        SELECT jsonb_build_object(
            'type', 'FeatureCollection',
            'features', jsonb_agg(features.feature)
        ) AS geojson
        FROM (
            SELECT jsonb_build_object(
                'type', 'Feature',
                'id', id,
                'geometry', ST_AsGeoJSON({geometry_column})::jsonb,
                'properties', to_jsonb(row) - '{geometry_column}'
            ) AS feature
            FROM (
                SELECT *,
                    ST_Distance(
                        {geometry_column},
                        ST_GeomFromGeoJSON(:geometry)
                    ) AS distance
                FROM {quoted_table}
    """
    
    # Add distance filter if provided
    if max_distance is not None:
        query_text += f"""
                WHERE ST_DWithin(
                    {geometry_column},
                    ST_GeomFromGeoJSON(:geometry),
                    :max_distance
                )
        """
    
    # Complete the query
    query_text += f"""
                ORDER BY {geometry_column} <-> ST_GeomFromGeoJSON(:geometry)
                LIMIT :limit
            ) row
        ) features
    """
    
    # Set up parameters
    params = {
        "geometry": json.dumps(geometry),
        "limit": limit
    }
    
    if max_distance is not None:
        params["max_distance"] = max_distance
    
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

async def attribute_spatial_filter_process(inputs: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
    """
    Filter features by attribute and spatial criteria
    """
    table_name = inputs.get("table_name")
    geometry_column = inputs.get("geometry_column", "geom")
    geometry = inputs.get("geometry")
    spatial_relationship = inputs.get("spatial_relationship", "intersects")
    attribute_filters = inputs.get("attribute_filters", [])
    limit = inputs.get("limit", 100)
    
    if not table_name:
        raise ValueError("Table name is required")
    
    # Ensure table name is properly quoted to prevent SQL injection
    table_parts = table_name.split('.')
    quoted_table = '.'.join([f'"{part}"' for part in table_parts])
    
    # Map relationship to PostGIS function
    relationship_functions = {
        "intersects": "ST_Intersects",
        "contains": "ST_Contains",
        "within": "ST_Within",
        "touches": "ST_Touches",
        "overlaps": "ST_Overlaps"
    }
    
    if spatial_relationship not in relationship_functions:
        raise ValueError(f"Unsupported spatial relationship: {spatial_relationship}")
    
    rel_function = relationship_functions[spatial_relationship]
    
    # Build the query
    query_text = f"""
        SELECT jsonb_build_object(
            'type', 'FeatureCollection',
            'features', jsonb_agg(features.feature)
        ) AS geojson
        FROM (
            SELECT jsonb_build_object(
                'type', 'Feature',
                'id', id,
                'geometry', ST_AsGeoJSON({geometry_column})::jsonb,
                'properties', to_jsonb(row) - '{geometry_column}'
            ) AS feature
            FROM (
                SELECT *
                FROM {quoted_table}
                WHERE 1=1
    """
    
    # Add spatial filter if geometry is provided
    params = {"limit": limit}
    
    if geometry:
        query_text += f"""
                AND {rel_function}({geometry_column}, ST_GeomFromGeoJSON(:geometry))
        """
        params["geometry"] = json.dumps(geometry)
    
    # Add attribute filters
    for i, filter_def in enumerate(attribute_filters):
        column = filter_def.get("column")
        operator = filter_def.get("operator", "=")
        value = filter_def.get("value")
        
        if not column or value is None:
            continue
        
        # Ensure column name is properly quoted
        quoted_column = f'"{column}"'
        
        # Map operator to SQL
        operator_map = {
            "=": "=",
            "!=": "!=",
            ">": ">",
            ">=": ">=",
            "<": "<",
            "<=": "<=",
            "like": "LIKE",
            "ilike": "ILIKE",
            "in": "IN"
        }
        
        if operator not in operator_map:
            continue
        
        sql_operator = operator_map[operator]
        
        # Handle different operators
        if operator in ["in"]:
            if not isinstance(value, list):
                value = [value]
            
            placeholders = [f":value_{i}_{j}" for j in range(len(value))]
            query_text += f"""
                AND {quoted_column} IN ({', '.join(placeholders)})
            """
            
            for j, val in enumerate(value):
                params[f"value_{i}_{j}"] = val
        else:
            query_text += f"""
                AND {quoted_column} {sql_operator} :value_{i}
            """
            params[f"value_{i}"] = value
    
    # Complete the query
    query_text += f"""
                ORDER BY id
                LIMIT :limit
            ) row
        ) features
    """
    
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

def register_search_processes(registry: ProcessRegistry):
    """
    Register search processes with the registry
    
    Args:
        registry: Process registry
    """
    # Bounding box search process
    registry.register_process(
        process_id="bbox_search",
        process_func=bbox_search_process,
        description="Search for features within a bounding box",
        inputs={
            "bbox": {
                "title": "Bounding Box",
                "description": "The bounding box to search within [xmin, ymin, xmax, ymax]",
                "schema": {
                    "type": "array",
                    "items": {"type": "number"},
                    "minItems": 4,
                    "maxItems": 4
                },
                "required": True
            },
            "table_name": {
                "title": "Table Name",
                "description": "The name of the table to search",
                "schema": {"type": "string"},
                "required": True
            },
            "geometry_column": {
                "title": "Geometry Column",
                "description": "The name of the geometry column",
                "schema": {"type": "string"},
                "required": False,
                "default": "geom"
            },
            "limit": {
                "title": "Limit",
                "description": "Maximum number of features to return",
                "schema": {"type": "integer"},
                "required": False,
                "default": 100
            }
        },
        outputs={
            "features": {
                "title": "Features",
                "description": "The features found within the bounding box",
                "schema": {"type": "object"}
            }
        }
    )
    
    # Spatial relationship search process
    registry.register_process(
        process_id="spatial_relationship_search",
        process_func=spatial_relationship_search_process,
        description="Search for features with a specific spatial relationship to a geometry",
        inputs={
            "geometry": {
                "title": "Geometry",
                "description": "The geometry to search with",
                "schema": {"type": "object"},
                "required": True
            },
            "table_name": {
                "title": "Table Name",
                "description": "The name of the table to search",
                "schema": {"type": "string"},
                "required": True
            },
            "relationship": {
                "title": "Relationship",
                "description": "The spatial relationship to check",
                "schema": {
                    "type": "string",
                    "enum": ["intersects", "contains", "within", "touches", "overlaps"]
                },
                "required": False,
                "default": "intersects"
            },
            "geometry_column": {
                "title": "Geometry Column",
                "description": "The name of the geometry column",
                "schema": {"type": "string"},
                "required": False,
                "default": "geom"
            },
            "limit": {
                "title": "Limit",
                "description": "Maximum number of features to return",
                "schema": {"type": "integer"},
                "required": False,
                "default": 100
            }
        },
        outputs={
            "features": {
                "title": "Features",
                "description": "The features with the specified spatial relationship",
                "schema": {"type": "object"}
            }
        }
    )
    
    # Nearest neighbor search process
    registry.register_process(
        process_id="nearest_neighbor",
        process_func=nearest_neighbor_process,
        description="Find the nearest neighbors to a geometry",
        inputs={
            "geometry": {
                "title": "Geometry",
                "description": "The geometry to find neighbors for",
                "schema": {"type": "object"},
                "required": True
            },
            "table_name": {
                "title": "Table Name",
                "description": "The name of the table to search",
                "schema": {"type": "string"},
                "required": True
            },
            "geometry_column": {
                "title": "Geometry Column",
                "description": "The name of the geometry column",
                "schema": {"type": "string"},
                "required": False,
                "default": "geom"
            },
            "max_distance": {
                "title": "Maximum Distance",
                "description": "The maximum distance to search",
                "schema": {"type": "number"},
                "required": False
            },
            "limit": {
                "title": "Limit",
                "description": "Maximum number of neighbors to return",
                "schema": {"type": "integer"},
                "required": False,
                "default": 5
            }
        },
        outputs={
            "features": {
                "title": "Features",
                "description": "The nearest neighbor features",
                "schema": {"type": "object"}
            }
        }
    )
    
    # Attribute and spatial filter process
    registry.register_process(
        process_id="attribute_spatial_filter",
        process_func=attribute_spatial_filter_process,
        description="Filter features by attribute and spatial criteria",
        inputs={
            "table_name": {
                "title": "Table Name",
                "description": "The name of the table to search",
                "schema": {"type": "string"},
                "required": True
            },
            "geometry_column": {
                "title": "Geometry Column",
                "description": "The name of the geometry column",
                "schema": {"type": "string"},
                "required": False,
                "default": "geom"
            },
            "geometry": {
                "title": "Geometry",
                "description": "The geometry to filter with",
                "schema": {"type": "object"},
                "required": False
            },
            "spatial_relationship": {
                "title": "Spatial Relationship",
                "description": "The spatial relationship to check",
                "schema": {
                    "type": "string",
                    "enum": ["intersects", "contains", "within", "touches", "overlaps"]
                },
                "required": False,
                "default": "intersects"
            },
            "attribute_filters": {
                "title": "Attribute Filters",
                "description": "Filters for attribute values",
                "schema": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "column": {"type": "string"},
                            "operator": {"type": "string"},
                            "value": {"type": "any"}
                        }
                    }
                },
                "required": False,
                "default": []
            },
            "limit": {
                "title": "Limit",
                "description": "Maximum number of features to return",
                "schema": {"type": "integer"},
                "required": False,
                "default": 100
            }
        },
        outputs={
            "features": {
                "title": "Features",
                "description": "The filtered features",
                "schema": {"type": "object"}
            }
        }
    )
