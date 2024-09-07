from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class ShipMetadata(BaseModel):
    uri: Optional[str] = None
    spawn_name: Optional[str] = None
    spawn_version: Optional[int] = None
    spawn_guid: Optional[str] = None
    solarsystem: Optional[str] = None
    project_guid: Optional[str] = None

class ShipScenes(BaseModel):
    cam: Optional[str] = None
    dship: Optional[str] = None

class ShipObject(BaseModel):
    apiVersion: Optional[str] = None
    kind: Optional[str] = None
    ship_class: Optional[str] = None
    viewer: Optional[str] = None
    scenes: Optional[ShipScenes] = None
    panels: Optional[List[Any]] = []
    metadata: Optional[ShipMetadata] = None

class ShipJob(BaseModel):
    id: Optional[str] = None
    guid: Optional[str] = None
    name: Optional[str] = None

class ShipData(BaseModel):
    object: Optional[ShipObject] = None
    jobs: Optional[List[ShipJob]] = []

class ShipEvent(BaseModel):
    _id: Optional[str] = None
    name: Optional[str] = None
    data: Optional[ShipData] = None
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
