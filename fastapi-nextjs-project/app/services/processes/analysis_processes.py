import json
from typing import Dict, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.services.process_registry import ProcessRegistry

async def buffer_process(inputs: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
    """
    Buffer a geometry by a specified distance
    """
    geometry = inputs.get("geometry")
    distance = inputs.get("distance")
    
    if not geometry or distance is None:
        raise ValueError("Geometry and distance are required")
    
    # Execute the PostGIS buffer function
    query = text("""
        SELECT ST_AsGeoJSON(
            ST_Buffer(
                ST_GeomFromGeoJSON(:geometry),
                :distance
            )
        ) AS buffered_geometry
    """)
    
    result = await db.execute(query, {"geometry": json.dumps(geometry), "distance": distance})
    row = result.fetchone()
    
    if not row:
        raise ValueError("Error creating buffer")
    
    return {
        "buffered_geometry": json.loads(row.buffered_geometry)
    }

async def intersection_process(inputs: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
    """
    Find the intersection of two geometries
    """
    geometry_a = inputs.get("geometry_a")
    geometry_b = inputs.get("geometry_b")
    
    if not geometry_a or not geometry_b:
        raise ValueError("Both geometries are required")
    
    query = text("""
        SELECT ST_AsGeoJSON(
            ST_Intersection(
                ST_GeomFromGeoJSON(:geometry_a),
                ST_GeomFromGeoJSON(:geometry_b)
            )
        ) AS intersection_geometry
    """)
    
    result = await db.execute(query, {
        "geometry_a": json.dumps(geometry_a), 
        "geometry_b": json.dumps(geometry_b)
    })
    row = result.fetchone()
    
    if not row:
        raise ValueError("Error calculating intersection")
    
    return {
        "intersection_geometry": json.loads(row.intersection_geometry)
    }

async def distance_process(inputs: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
    """
    Calculate the distance between two geometries
    """
    geometry_a = inputs.get("geometry_a")
    geometry_b = inputs.get("geometry_b")
    use_spheroid = inputs.get("use_spheroid", True)
    
    if not geometry_a or not geometry_b:
        raise ValueError("Both geometries are required")
    
    query = text("""
        SELECT ST_Distance(
            ST_GeomFromGeoJSON(:geometry_a),
            ST_GeomFromGeoJSON(:geometry_b),
            :use_spheroid
        ) AS distance
    """)
    
    result = await db.execute(query, {
        "geometry_a": json.dumps(geometry_a), 
        "geometry_b": json.dumps(geometry_b),
        "use_spheroid": use_spheroid
    })
    row = result.fetchone()
    
    if not row:
        raise ValueError("Error calculating distance")
    
    return {
        "distance": float(row.distance)
    }

async def area_process(inputs: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
    """
    Calculate the area of a geometry
    """
    geometry = inputs.get("geometry")
    
    if not geometry:
        raise ValueError("Geometry is required")
    
    query = text("""
        SELECT ST_Area(
            ST_GeomFromGeoJSON(:geometry)
        ) AS area
    """)
    
    result = await db.execute(query, {"geometry": json.dumps(geometry)})
    row = result.fetchone()
    
    if not row:
        raise ValueError("Error calculating area")
    
    return {
        "area": float(row.area)
    }

async def convex_hull_process(inputs: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
    """
    Generate a convex hull from a geometry
    """
    geometry = inputs.get("geometry")
    
    if not geometry:
        raise ValueError("Geometry is required")
    
    query = text("""
        SELECT ST_AsGeoJSON(
            ST_ConvexHull(
                ST_GeomFromGeoJSON(:geometry)
            )
        ) AS convex_hull
    """)
    
    result = await db.execute(query, {"geometry": json.dumps(geometry)})
    row = result.fetchone()
    
    if not row:
        raise ValueError("Error generating convex hull")
    
    return {
        "convex_hull": json.loads(row.convex_hull)
    }

async def simplify_process(inputs: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
    """
    Simplify a geometry using the Douglas-Peucker algorithm
    """
    geometry = inputs.get("geometry")
    tolerance = inputs.get("tolerance", 0.0)
    preserve_topology = inputs.get("preserve_topology", True)
    
    if not geometry:
        raise ValueError("Geometry is required")
    
    # Choose the appropriate function based on preserve_topology
    if preserve_topology:
        function = "ST_SimplifyPreserveTopology"
    else:
        function = "ST_Simplify"
    
    query = text(f"""
        SELECT ST_AsGeoJSON(
            {function}(
                ST_GeomFromGeoJSON(:geometry),
                :tolerance
            )
        ) AS simplified_geometry
    """)
    
    result = await db.execute(query, {
        "geometry": json.dumps(geometry),
        "tolerance": tolerance
    })
    row = result.fetchone()
    
    if not row:
        raise ValueError("Error simplifying geometry")
    
    return {
        "simplified_geometry": json.loads(row.simplified_geometry)
    }

async def voronoi_process(inputs: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
    """
    Generate a Voronoi diagram from a set of points
    """
    points = inputs.get("points")
    bounds = inputs.get("bounds")
    tolerance = inputs.get("tolerance", 0.0)
    
    if not points:
        raise ValueError("Points are required")
    
    # Create a query to generate the Voronoi diagram
    query_text = """
        SELECT ST_AsGeoJSON(
            ST_VoronoiPolygons(
                ST_Collect(ST_GeomFromGeoJSON(:point)),
                :tolerance,
                :bounds
            )
        ) AS voronoi_polygons
    """
    
    # If bounds are provided, add them to the query
    params = {
        "point": json.dumps(points),
        "tolerance": tolerance
    }
    
    if bounds:
        params["bounds"] = json.dumps(bounds)
        query = text(query_text)
    else:
        # If no bounds are provided, use a different query
        query_text = """
            SELECT ST_AsGeoJSON(
                ST_VoronoiPolygons(
                    ST_Collect(ST_GeomFromGeoJSON(:point)),
                    :tolerance
                )
            ) AS voronoi_polygons
        """
        query = text(query_text)
    
    result = await db.execute(query, params)
    row = result.fetchone()
    
    if not row:
        raise ValueError("Error generating Voronoi diagram")
    
    return {
        "voronoi_polygons": json.loads(row.voronoi_polygons)
    }

def register_analysis_processes(registry: ProcessRegistry):
    """
    Register analysis processes with the registry
    
    Args:
        registry: Process registry
    """
    # Buffer process
    registry.register_process(
        process_id="buffer",
        process_func=buffer_process,
        description="Buffer a geometry by a specified distance",
        inputs={
            "geometry": {
                "title": "Geometry",
                "description": "The geometry to buffer",
                "schema": {
                    "type": "object"
                },
                "required": True
            },
            "distance": {
                "title": "Distance",
                "description": "Buffer distance in units of the geometry's coordinate system",
                "schema": {
                    "type": "number"
                },
                "required": True
            }
        },
        outputs={
            "buffered_geometry": {
                "title": "Buffered Geometry",
                "description": "The resulting buffered geometry",
                "schema": {
                    "type": "object"
                }
            }
        },
        examples=[
            {
                "title": "Buffer a point by 100 meters",
                "inputs": {
                    "geometry": {
                        "type": "Point",
                        "coordinates": [0, 0]
                    },
                    "distance": 100
                }
            }
        ]
    )
    
    # Intersection process
    registry.register_process(
        process_id="intersection",
        process_func=intersection_process,
        description="Find the intersection of two geometries",
        inputs={
            "geometry_a": {
                "title": "Geometry A",
                "description": "The first geometry",
                "schema": {"type": "object"},
                "required": True
            },
            "geometry_b": {
                "title": "Geometry B",
                "description": "The second geometry",
                "schema": {"type": "object"},
                "required": True
            }
        },
        outputs={
            "intersection_geometry": {
                "title": "Intersection Geometry",
                "description": "The resulting intersection geometry",
                "schema": {"type": "object"}
            }
        }
    )
    
    # Distance process
    registry.register_process(
        process_id="distance",
        process_func=distance_process,
        description="Calculate the distance between two geometries",
        inputs={
            "geometry_a": {
                "title": "Geometry A",
                "description": "The first geometry",
                "schema": {"type": "object"},
                "required": True
            },
            "geometry_b": {
                "title": "Geometry B",
                "description": "The second geometry",
                "schema": {"type": "object"},
                "required": True
            },
            "use_spheroid": {
                "title": "Use Spheroid",
                "description": "Whether to use spheroid for geographic coordinates",
                "schema": {"type": "boolean"},
                "required": False,
                "default": True
            }
        },
        outputs={
            "distance": {
                "title": "Distance",
                "description": "The distance between the geometries",
                "schema": {"type": "number"}
            }
        }
    )
    
    # Area process
    registry.register_process(
        process_id="area",
        process_func=area_process,
        description="Calculate the area of a geometry",
        inputs={
            "geometry": {
                "title": "Geometry",
                "description": "The geometry to calculate area for",
                "schema": {"type": "object"},
                "required": True
            }
        },
        outputs={
            "area": {
                "title": "Area",
                "description": "The area of the geometry",
                "schema": {"type": "number"}
            }
        }
    )
    
    # Convex hull process
    registry.register_process(
        process_id="convex_hull",
        process_func=convex_hull_process,
        description="Generate a convex hull from a geometry",
        inputs={
            "geometry": {
                "title": "Geometry",
                "description": "The geometry to generate the convex hull from",
                "schema": {"type": "object"},
                "required": True
            }
        },
        outputs={
            "convex_hull": {
                "title": "Convex Hull",
                "description": "The resulting convex hull",
                "schema": {"type": "object"}
            }
        }
    )
    
    # Simplify process
    registry.register_process(
        process_id="simplify",
        process_func=simplify_process,
        description="Simplify a geometry using the Douglas-Peucker algorithm",
        inputs={
            "geometry": {
                "title": "Geometry",
                "description": "The geometry to simplify",
                "schema": {"type": "object"},
                "required": True
            },
            "tolerance": {
                "title": "Tolerance",
                "description": "The tolerance for the simplification",
                "schema": {"type": "number"},
                "required": False,
                "default": 0.0
            },
            "preserve_topology": {
                "title": "Preserve Topology",
                "description": "Whether to preserve topology during simplification",
                "schema": {"type": "boolean"},
                "required": False,
                "default": True
            }
        },
        outputs={
            "simplified_geometry": {
                "title": "Simplified Geometry",
                "description": "The resulting simplified geometry",
                "schema": {"type": "object"}
            }
        }
    )
    
    # Voronoi process
    registry.register_process(
        process_id="voronoi",
        process_func=voronoi_process,
        description="Generate a Voronoi diagram from a set of points",
        inputs={
            "points": {
                "title": "Points",
                "description": "The points to generate the Voronoi diagram from",
                "schema": {"type": "object"},
                "required": True
            },
            "bounds": {
                "title": "Bounds",
                "description": "The bounding geometry for the Voronoi diagram",
                "schema": {"type": "object"},
                "required": False
            },
            "tolerance": {
                "title": "Tolerance",
                "description": "The tolerance for the Voronoi diagram",
                "schema": {"type": "number"},
                "required": False,
                "default": 0.0
            }
        },
        outputs={
            "voronoi_polygons": {
                "title": "Voronoi Polygons",
                "description": "The resulting Voronoi polygons",
                "schema": {"type": "object"}
            }
        }
    )
