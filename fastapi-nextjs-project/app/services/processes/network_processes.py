import json
from typing import Dict, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.services.process_registry import ProcessRegistry

async def shortest_path_process(inputs: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
    """
    Find the shortest path between two points using pgRouting
    """
    network_table = inputs.get("network_table")
    start_point = inputs.get("start_point")
    end_point = inputs.get("end_point")
    directed = inputs.get("directed", True)
    
    if not network_table or not start_point or not end_point:
        raise ValueError("Network table, start point, and end point are required")
    
    # Ensure table name is properly quoted to prevent SQL injection
    table_parts = network_table.split('.')
    quoted_table = '.'.join([f'"{part}"' for part in table_parts])
    
    # Find the nearest vertices to the start and end points
    query = text(f"""
        WITH
        start_vertex AS (
            SELECT id FROM {quoted_table}_vertices_pgr
            ORDER BY the_geom <-> ST_GeomFromGeoJSON(:start_point)
            LIMIT 1
        ),
        end_vertex AS (
            SELECT id FROM {quoted_table}_vertices_pgr
            ORDER BY the_geom <-> ST_GeomFromGeoJSON(:end_point)
            LIMIT 1
        ),
        path AS (
            SELECT * FROM pgr_dijkstra(
                'SELECT id, source, target, cost, reverse_cost FROM {quoted_table}',
                (SELECT id FROM start_vertex),
                (SELECT id FROM end_vertex),
                :directed
            )
        ),
        path_edges AS (
            SELECT
                path.edge,
                path.cost,
                network.the_geom
            FROM path
            JOIN {quoted_table} network ON path.edge = network.id
            WHERE path.edge != -1
        )
        SELECT jsonb_build_object(
            'type', 'FeatureCollection',
            'features', jsonb_agg(features.feature)
        ) AS geojson
        FROM (
            SELECT jsonb_build_object(
                'type', 'Feature',
                'geometry', ST_AsGeoJSON(the_geom)::jsonb,
                'properties', jsonb_build_object(
                    'edge', edge,
                    'cost', cost
                )
            ) AS feature
            FROM path_edges
        ) features
    """)
    
    result = await db.execute(query, {
        "start_point": json.dumps(start_point),
        "end_point": json.dumps(end_point),
        "directed": directed
    })
    row = result.fetchone()
    
    if not row or not row.geojson:
        return {
            "type": "FeatureCollection",
            "features": []
        }
    
    return row.geojson

async def service_area_process(inputs: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
    """
    Find the service area around a point using pgRouting
    """
    network_table = inputs.get("network_table")
    point = inputs.get("point")
    max_cost = inputs.get("max_cost", 1000)
    directed = inputs.get("directed", True)
    
    if not network_table or not point:
        raise ValueError("Network table and point are required")
    
    # Ensure table name is properly quoted to prevent SQL injection
    table_parts = network_table.split('.')
    quoted_table = '.'.join([f'"{part}"' for part in table_parts])
    
    # Find the nearest vertex to the point
    query = text(f"""
        WITH
        start_vertex AS (
            SELECT id FROM {quoted_table}_vertices_pgr
            ORDER BY the_geom <-> ST_GeomFromGeoJSON(:point)
            LIMIT 1
        ),
        service_area AS (
            SELECT * FROM pgr_drivingDistance(
                'SELECT id, source, target, cost, reverse_cost FROM {quoted_table}',
                (SELECT id FROM start_vertex),
                :max_cost,
                :directed
            )
        ),
        service_edges AS (
            SELECT
                service_area.edge,
                service_area.cost,
                network.the_geom
            FROM service_area
            JOIN {quoted_table} network ON service_area.edge = network.id
            WHERE service_area.edge != -1
        )
        SELECT jsonb_build_object(
            'type', 'FeatureCollection',
            'features', jsonb_agg(features.feature)
        ) AS geojson
        FROM (
            SELECT jsonb_build_object(
                'type', 'Feature',
                'geometry', ST_AsGeoJSON(the_geom)::jsonb,
                'properties', jsonb_build_object(
                    'edge', edge,
                    'cost', cost
                )
            ) AS feature
            FROM service_edges
        ) features
    """)
    
    result = await db.execute(query, {
        "point": json.dumps(point),
        "max_cost": max_cost,
        "directed": directed
    })
    row = result.fetchone()
    
    if not row or not row.geojson:
        return {
            "type": "FeatureCollection",
            "features": []
        }
    
    return row.geojson

def register_network_processes(registry: ProcessRegistry):
    """
    Register network processes with the registry
    
    Args:
        registry: Process registry
    """
    # Shortest path process
    registry.register_process(
        process_id="shortest_path",
        process_func=shortest_path_process,
        description="Find the shortest path between two points using pgRouting",
        inputs={
            "network_table": {
                "title": "Network Table",
                "description": "The name of the network table",
                "schema": {"type": "string"},
                "required": True
            },
            "start_point": {
                "title": "Start Point",
                "description": "The starting point",
                "schema": {"type": "object"},
                "required": True
            },
            "end_point": {
                "title": "End Point",
                "description": "The ending point",
                "schema": {"type": "object"},
                "required": True
            },
            "directed": {
                "title": "Directed",
                "description": "Whether the network is directed",
                "schema": {"type": "boolean"},
                "required": False,
                "default": True
            }
        },
        outputs={
            "path": {
                "title": "Path",
                "description": "The shortest path",
                "schema": {"type": "object"}
            }
        }
    )
    
    # Service area process
    registry.register_process(
        process_id="service_area",
        process_func=service_area_process,
        description="Find the service area around a point using pgRouting",
        inputs={
            "network_table": {
                "title": "Network Table",
                "description": "The name of the network table",
                "schema": {"type": "string"},
                "required": True
            },
            "point": {
                "title": "Point",
                "description": "The center point",
                "schema": {"type": "object"},
                "required": True
            },
            "max_cost": {
                "title": "Maximum Cost",
                "description": "The maximum cost for the service area",
                "schema": {"type": "number"},
                "required": False,
                "default": 1000
            },
            "directed": {
                "title": "Directed",
                "description": "Whether the network is directed",
                "schema": {"type": "boolean"},
                "required": False,
                "default": True
            }
        },
        outputs={
            "service_area": {
                "title": "Service Area",
                "description": "The service area",
                "schema": {"type": "object"}
            }
        }
    )
