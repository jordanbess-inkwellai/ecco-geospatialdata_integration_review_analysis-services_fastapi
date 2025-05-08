from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel

router = APIRouter()

class GeoFeature(BaseModel):
    id: int
    name: str
    description: str
    coordinates: List[float]

geo_features = []

@router.post("/geo_features/", response_model=GeoFeature)
async def create_geo_feature(geo_feature: GeoFeature):
    geo_features.append(geo_feature)
    return geo_feature

@router.get("/geo_features/", response_model=List[GeoFeature])
async def read_geo_features():
    return geo_features

@router.get("/geo_features/{geo_feature_id}", response_model=GeoFeature)
async def read_geo_feature(geo_feature_id: int):
    for geo_feature in geo_features:
        if geo_feature.id == geo_feature_id:
            return geo_feature
    raise HTTPException(status_code=404, detail="GeoFeature not found")

@router.put("/geo_features/{geo_feature_id}", response_model=GeoFeature)
async def update_geo_feature(geo_feature_id: int, updated_geo_feature: GeoFeature):
    for index, geo_feature in enumerate(geo_features):
        if geo_feature.id == geo_feature_id:
            geo_features[index] = updated_geo_feature
            return updated_geo_feature
    raise HTTPException(status_code=404, detail="GeoFeature not found")

@router.delete("/geo_features/{geo_feature_id}", response_model=GeoFeature)
async def delete_geo_feature(geo_feature_id: int):
    for index, geo_feature in enumerate(geo_features):
        if geo_feature.id == geo_feature_id:
            return geo_features.pop(index)
    raise HTTPException(status_code=404, detail="GeoFeature not found")