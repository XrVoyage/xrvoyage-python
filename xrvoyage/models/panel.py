from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class PanelPosition(BaseModel):
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None

class PanelScale(BaseModel):
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None

class PanelRotation(BaseModel):
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None

class PanelSpecs(BaseModel):
    pluginGuid: Optional[str] = None
    templateType: Optional[str] = None
    pluginName: Optional[str] = None
    pluginVersion: Optional[str] = None
    templateVersion: Optional[str] = None

class PanelObject(BaseModel):
    apiVersion: Optional[str] = None
    kind: Optional[str] = None
    specs: Optional[PanelSpecs] = None
    inputs: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None
    eventEgress: Optional[list] = None
    eventIngress: Optional[list] = None
    position: Optional[PanelPosition] = None
    scale: Optional[PanelScale] = None
    rotation: Optional[PanelRotation] = None
    uri: Optional[str] = None

class PanelData(BaseModel):
    object: Optional[PanelObject] = None

class PanelEvent(BaseModel):
    _id: Optional[str] = None
    name: Optional[str] = None
    data: Optional[PanelData] = None
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
