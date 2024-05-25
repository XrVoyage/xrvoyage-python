from .events import XRWebhookEvent


class DataWebhookEvent(XRWebhookEvent):
    project_guid: str
