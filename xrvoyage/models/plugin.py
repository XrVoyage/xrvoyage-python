from pydantic import BaseModel, Field
from typing import Optional
import base64

class PluginObject(BaseModel):
    file: Optional[str] = Field(None, alias='file')

    @property
    def file_content(self) -> Optional[str]:
        if self.file:
            return base64.b64decode(self.file).decode('utf-8')
        return None

    @file_content.setter
    def file_content(self, value: str):
        self.file = base64.b64encode(value.encode('utf-8')).decode('utf-8')

class PluginData(BaseModel):
    apiVersion: Optional[str] = None
    fileLanguage: Optional[str] = None
    object: Optional[PluginObject] = None

class PluginEvent(BaseModel):
    _id: Optional[str] = None
    data: Optional[PluginData] = None
    name: Optional[str] = None
    token_username: Optional[str] = None
    token_sub: Optional[str] = None
    guid: Optional[str] = None
    created_utc: Optional[str] = None
    updated_utc: Optional[str] = None

    class Config:
        from_attributes = True
        use_enum_values = True
        str_strip_whitespace = True
        json_encoders = {
            str: lambda v: v.isoformat() if isinstance(v, str) else v,
        }
        exclude_unset = True
        exclude_none = True
