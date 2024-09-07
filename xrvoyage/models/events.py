from typing import Any, Dict, List
import pydantic


class ClientInfo(pydantic.BaseModel):
    session: str
    timestamp_utc: str

    class Config:
        from_attributes = True
        use_enum_values = True
        str_strip_whitespace = True
        json_encoders = {
            str: lambda v: v.isoformat() if isinstance(v, str) else v,
        }
        exclude_unset = True
        exclude_none = True


class XRWebhookEvent(pydantic.BaseModel):
    source: str | None = None
    type: str
    args: Dict[str, Any] | None = None
    sender_sub: str | None = None
    sender_username: str | None = None
    guid: str | None = None  # <- Some events don't have a guid since they are not saved in Mongo
    created_utc: str | None = None  # <- Some events don't have a created_utc since they are not saved in Mongo

    # client info fields
    client: ClientInfo | None = None

    # all events should have the ship_guid property, so that we know where to route them
    # this is optional to avoid breaking existing code.
    ship_guid: str | None = None
    project_guid: str | None = None

    class Config:
        from_attributes = True
        use_enum_values = True
        str_strip_whitespace = True
        json_encoders = {
            str: lambda v: v.isoformat() if isinstance(v, str) else v,
        }
        exclude_unset = True
        exclude_none = True


class XRWebhookEventBatch(pydantic.BaseModel):
    xr_rt: List[XRWebhookEvent] = pydantic.Field(
        alias='xr.rt',
        default_factory=lambda: []
    )
    xr_data: List[XRWebhookEvent] = pydantic.Field(
        alias='xr.data',
        default_factory=lambda: []
    )
    xr_nrt: List[XRWebhookEvent] = pydantic.Field(
        alias='xr.nrt',
        default_factory=lambda: []
    )

    class Config:
        from_attributes = True
        use_enum_values = True
        str_strip_whitespace = True
        json_encoders = {
            str: lambda v: v.isoformat() if isinstance(v, str) else v,
        }
        exclude_unset = True
        exclude_none = True
