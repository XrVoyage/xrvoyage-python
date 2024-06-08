from ..handlers.auth import TokenStrategy
from ..models.events import XRWebhookEventBatch, XRWebhookEvent
from ..common.config import get_app_config
from ..common.exceptions import ApiError
from ..handlers.http import HttpHandler

class Webhooks_XRWebHandler:
    def __init__(self, token_strategy: TokenStrategy):
        """
        Constructor for the XR Events Handler

        Args:
            token_strategy (TokenStrategy): The strategy to get the auth token
        """
        self._http_handler = HttpHandler(token_strategy)

    def post_event_as_batch(self, event_batch: XRWebhookEventBatch) -> dict:
        """
        Send an event to the API

        Args:
            event_batch (XRWebhookEventBatch): the event batch to be sent to the API
        """
        settings = get_app_config()
        api_base_url = settings.XRVOYAGE_API_BASE_URL
        url = f'{api_base_url}/webhooks/xrweb'
        response = self._http_handler.post(url, json=event_batch.model_dump(by_alias=True))
        return response

    def post_event(self, event: XRWebhookEvent) -> dict:
        """
        Send an event to the API

        Args:
            event (XRWebhookEvent): the event to be sent to the API
        """
        settings = get_app_config()
        api_base_url = settings.XRVOYAGE_API_BASE_URL
        url = f'{api_base_url}/webhooks/xrweb'
        response = self._http_handler.post(url, json=event.model_dump(by_alias=True))
        return response
