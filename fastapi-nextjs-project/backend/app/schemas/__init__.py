# Import all schemas to make them available when importing from app.schemas
from app.schemas.base import BaseSchema
from app.schemas.database import DatabaseConnectionSettings, DatabaseConnectionResponse
from app.schemas.geospatial import (
    GeometrySchema, PropertiesSchema,
    GeospatialDataCreate, GeospatialDataUpdate, GeospatialDataResponse,
    GeospatialLayerCreate, GeospatialLayerUpdate, GeospatialLayerResponse
)
from app.schemas.geo_feature import (
    GeoFeatureCreate, GeoFeatureUpdate, GeoFeatureResponse
)
from app.schemas.geo_table import (
    GeoTableColumnCreate, GeoTableColumnUpdate, GeoTableColumnResponse,
    GeoTableCreate, GeoTableUpdate, GeoTableResponse
)
from app.schemas.geo_suitability import (
    SuitabilityCriterionCreate, SuitabilityCriterionUpdate, SuitabilityCriterionResponse,
    GeoSuitabilityCreate, GeoSuitabilityUpdate, GeoSuitabilityResponse
)
from app.schemas.importer import (
    ImportLogCreate, ImportLogResponse,
    ImportJobCreate, ImportJobUpdate, ImportJobResponse
)

# Export all schemas
__all__ = [
    'BaseSchema',
    'DatabaseConnectionSettings', 'DatabaseConnectionResponse',
    'GeometrySchema', 'PropertiesSchema',
    'GeospatialDataCreate', 'GeospatialDataUpdate', 'GeospatialDataResponse',
    'GeospatialLayerCreate', 'GeospatialLayerUpdate', 'GeospatialLayerResponse',
    'GeoFeatureCreate', 'GeoFeatureUpdate', 'GeoFeatureResponse',
    'GeoTableColumnCreate', 'GeoTableColumnUpdate', 'GeoTableColumnResponse',
    'GeoTableCreate', 'GeoTableUpdate', 'GeoTableResponse',
    'SuitabilityCriterionCreate', 'SuitabilityCriterionUpdate', 'SuitabilityCriterionResponse',
    'GeoSuitabilityCreate', 'GeoSuitabilityUpdate', 'GeoSuitabilityResponse',
    'ImportLogCreate', 'ImportLogResponse',
    'ImportJobCreate', 'ImportJobUpdate', 'ImportJobResponse',
]