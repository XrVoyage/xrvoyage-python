from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class Metadata(BaseModel):
    solarsystem_guid: str
    solarsystem_name: str
    type: str

class DataObject(BaseModel):
    metadata: Metadata

class DataModel(BaseModel):
    object: DataObject
    response: Dict[str, Any]

class PutDataRequestDTO(BaseModel):
    name: str
    data: DataModel

    class Config:
        from_attributes = True
        use_enum_values = True
        str_strip_whitespace = True
        json_encoders = {
            str: lambda v: v.isoformat() if isinstance(v, str) else v,
        }
        exclude_unset = True
        exclude_none = True

class DataWebhookEvent(BaseModel):
    event_id: Optional[str]
    event_type: Optional[str]
    data: Optional[Dict[str, Any]]
    timestamp: Optional[datetime]

    class Config:
        from_attributes = True
        use_enum_values = True
        str_strip_whitespace = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
        }
        exclude_unset = True
        exclude_none = True
