from typing import Any, Dict, List
import pydantic


class ClientInfo(pydantic.BaseModel):
    session: str
    timestamp_utc: str


class XRWebhookEvent(pydantic.BaseModel):
    source: str | None = None
    type: str
    args: Dict[str, Any]
    sender_sub: str | None = None
    sender_username: str | None = None
    guid: str | None = None  # <- Some events don't have a guid since they are not saved in Mongo
    created_utc: str | None = None  # <- Some events don't have a created_utc since they are not saved in Mongo

    # client info fields
    client: ClientInfo | None = None

    # all events should have the ship_guid property, so that we know where to route them
    # this is optional to avoid breaking existing code.
    ship_guid: str | None = None


class XRWebhookEventBatch(pydantic.BaseModel):
    xr_rt: List[XRWebhookEvent] | None = pydantic.Field(
        alias='xr.rt',
        default=None
    )
    xr_data: List[XRWebhookEvent] | None = pydantic.Field(
        alias='xr.data',
        default=None
    )
    xr_nrt: List[XRWebhookEvent] | None = pydantic.Field(
        alias='xr.nrt',
        default=None
    )
