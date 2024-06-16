from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class PlanetPosition(BaseModel):
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None

class PlanetPOI(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    default: Optional[bool] = None
    position: Optional[PlanetPosition] = None

class PlanetPanel(BaseModel):
    name: Optional[str] = None
    guid: Optional[str] = None

class PlanetMetadata(BaseModel):
    uri: Optional[str] = None
    spawn_name: Optional[str] = None
    spawn_version: Optional[int] = None
    spawn_guid: Optional[str] = None
    solarsystem: Optional[str] = None

class PlanetScenes(BaseModel):
    dgeo: Optional[str] = None

class PlanetObject(BaseModel):
    apiVersion: Optional[str] = None
    kind: Optional[str] = None
    scenes: Optional[PlanetScenes] = None
    poi: Optional[List[PlanetPOI]] = []
    project_guid: Optional[str] = None
    panels: Optional[List[PlanetPanel]] = []
    metadata: Optional[PlanetMetadata] = None

class PlanetSourceData(BaseModel):
    guid: Optional[str] = None
    name: Optional[str] = None
    uri: Optional[str] = None

class PlanetSource(BaseModel):
    data: Optional[List[PlanetSourceData]] = []

class PlanetData(BaseModel):
    object: Optional[PlanetObject] = None
    source: Optional[PlanetSource] = None

class PlanetEvent(BaseModel):
    _id: Optional[str] = None
    name: Optional[str] = None
    data: Optional[PlanetData] = None
    token_username: Optional[str] = None
    token_sub: Optional[str] = None
    guid: Optional[str] = None
    created_utc: Optional[datetime] = None
    updated_utc: Optional[datetime] = None

    class Config:
        from_attributes = True
        use_enum_values = True
        str_strip_whitespace = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
        }
        exclude_unset = True
        exclude_none = True
