import json
from typing import Dict, Any, Optional
from pydantic import BaseModel, ValidationError, validator
from app.core.exceptions import ValidationException

class GeometryValidator(BaseModel):
    """Validator for GeoJSON geometry objects."""
    
    type: str
    coordinates: Any
    
    @validator('type')
    def validate_type(cls, v):
        valid_types = ['Point', 'LineString', 'Polygon', 'MultiPoint', 'MultiLineString', 'MultiPolygon', 'GeometryCollection']
        if v not in valid_types:
            raise ValueError(f"Invalid geometry type: {v}. Must be one of {valid_types}")
        return v
    
    @validator('coordinates')
    def validate_coordinates(cls, v, values):
        if 'type' not in values:
            return v
        
        geometry_type = values['type']
        
        if geometry_type == 'Point':
            if not isinstance(v, list) or len(v) < 2:
                raise ValueError("Point coordinates must be a list of at least 2 numbers")
        
        elif geometry_type == 'LineString':
            if not isinstance(v, list) or len(v) < 2:
                raise ValueError("LineString coordinates must be a list of at least 2 points")
            
            for point in v:
                if not isinstance(point, list) or len(point) < 2:
                    raise ValueError("Each point in a LineString must be a list of at least 2 numbers")
        
        elif geometry_type == 'Polygon':
            if not isinstance(v, list) or len(v) < 1:
                raise ValueError("Polygon coordinates must be a list of at least 1 ring")
            
            for ring in v:
                if not isinstance(ring, list) or len(ring) < 4:
                    raise ValueError("Each ring in a Polygon must be a list of at least 4 points")
                
                for point in ring:
                    if not isinstance(point, list) or len(point) < 2:
                        raise ValueError("Each point in a Polygon ring must be a list of at least 2 numbers")
                
                # Check if the ring is closed
                if ring[0] != ring[-1]:
                    raise ValueError("Each ring in a Polygon must be closed (first point equals last point)")
        
        elif geometry_type == 'MultiPoint':
            if not isinstance(v, list):
                raise ValueError("MultiPoint coordinates must be a list of points")
            
            for point in v:
                if not isinstance(point, list) or len(point) < 2:
                    raise ValueError("Each point in a MultiPoint must be a list of at least 2 numbers")
        
        elif geometry_type == 'MultiLineString':
            if not isinstance(v, list):
                raise ValueError("MultiLineString coordinates must be a list of linestrings")
            
            for linestring in v:
                if not isinstance(linestring, list) or len(linestring) < 2:
                    raise ValueError("Each linestring in a MultiLineString must be a list of at least 2 points")
                
                for point in linestring:
                    if not isinstance(point, list) or len(point) < 2:
                        raise ValueError("Each point in a MultiLineString must be a list of at least 2 numbers")
        
        elif geometry_type == 'MultiPolygon':
            if not isinstance(v, list):
                raise ValueError("MultiPolygon coordinates must be a list of polygons")
            
            for polygon in v:
                if not isinstance(polygon, list) or len(polygon) < 1:
                    raise ValueError("Each polygon in a MultiPolygon must be a list of at least 1 ring")
                
                for ring in polygon:
                    if not isinstance(ring, list) or len(ring) < 4:
                        raise ValueError("Each ring in a MultiPolygon must be a list of at least 4 points")
                    
                    for point in ring:
                        if not isinstance(point, list) or len(point) < 2:
                            raise ValueError("Each point in a MultiPolygon must be a list of at least 2 numbers")
                    
                    # Check if the ring is closed
                    if ring[0] != ring[-1]:
                        raise ValueError("Each ring in a MultiPolygon must be closed (first point equals last point)")
        
        return v

def validate_geometry(geometry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Validate a GeoJSON geometry object.
    
    Args:
        geometry: GeoJSON geometry object
        
    Returns:
        Validated geometry object
        
    Raises:
        ValidationException: If the geometry is invalid
    """
    try:
        validator = GeometryValidator(**geometry)
        return validator.dict()
    except ValidationError as e:
        raise ValidationException(str(e))

def validate_process_inputs(process: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate process inputs against the process definition.
    
    Args:
        process: Process definition
        inputs: Process inputs
        
    Returns:
        Validated inputs
        
    Raises:
        ValidationException: If the inputs are invalid
    """
    process_inputs = process.get("inputs", {})
    validated_inputs = {}
    
    # Check for missing required inputs
    for name, input_def in process_inputs.items():
        if input_def.get("required", False) and name not in inputs:
            raise ValidationException(f"Required input '{name}' is missing")
    
    # Validate each input
    for name, value in inputs.items():
        if name not in process_inputs:
            raise ValidationException(f"Unknown input '{name}'")
        
        input_def = process_inputs[name]
        schema = input_def.get("schema", {})
        
        # Validate based on schema type
        schema_type = schema.get("type")
        
        if schema_type == "string":
            if not isinstance(value, str):
                raise ValidationException(f"Input '{name}' must be a string")
            
            # Check enum values
            if "enum" in schema and value not in schema["enum"]:
                raise ValidationException(f"Input '{name}' must be one of {schema['enum']}")
            
            validated_inputs[name] = value
        
        elif schema_type == "number":
            try:
                value = float(value)
            except (ValueError, TypeError):
                raise ValidationException(f"Input '{name}' must be a number")
            
            # Check range
            if "minimum" in schema and value < schema["minimum"]:
                raise ValidationException(f"Input '{name}' must be at least {schema['minimum']}")
            
            if "maximum" in schema and value > schema["maximum"]:
                raise ValidationException(f"Input '{name}' must be at most {schema['maximum']}")
            
            validated_inputs[name] = value
        
        elif schema_type == "integer":
            try:
                value = int(value)
            except (ValueError, TypeError):
                raise ValidationException(f"Input '{name}' must be an integer")
            
            # Check range
            if "minimum" in schema and value < schema["minimum"]:
                raise ValidationException(f"Input '{name}' must be at least {schema['minimum']}")
            
            if "maximum" in schema and value > schema["maximum"]:
                raise ValidationException(f"Input '{name}' must be at most {schema['maximum']}")
            
            validated_inputs[name] = value
        
        elif schema_type == "boolean":
            if not isinstance(value, bool):
                if isinstance(value, str):
                    if value.lower() in ["true", "1", "yes"]:
                        value = True
                    elif value.lower() in ["false", "0", "no"]:
                        value = False
                    else:
                        raise ValidationException(f"Input '{name}' must be a boolean")
                elif isinstance(value, (int, float)):
                    value = bool(value)
                else:
                    raise ValidationException(f"Input '{name}' must be a boolean")
            
            validated_inputs[name] = value
        
        elif schema_type == "array":
            if not isinstance(value, list):
                if isinstance(value, str):
                    try:
                        value = json.loads(value)
                        if not isinstance(value, list):
                            value = value.split(",")
                    except json.JSONDecodeError:
                        value = value.split(",")
                else:
                    raise ValidationException(f"Input '{name}' must be an array")
            
            validated_inputs[name] = value
        
        elif schema_type == "object":
            if not isinstance(value, dict):
                if isinstance(value, str):
                    try:
                        value = json.loads(value)
                    except json.JSONDecodeError:
                        raise ValidationException(f"Input '{name}' must be a valid JSON object")
                else:
                    raise ValidationException(f"Input '{name}' must be an object")
            
            # Special handling for geometry objects
            if name.lower() in ["geometry", "geometry_a", "geometry_b", "point", "start_point", "end_point"]:
                try:
                    validate_geometry(value)
                except ValidationException as e:
                    raise ValidationException(f"Input '{name}' is not a valid geometry: {str(e)}")
            
            validated_inputs[name] = value
        
        else:
            # For unknown types, just pass through
            validated_inputs[name] = value
    
    return validated_inputs
