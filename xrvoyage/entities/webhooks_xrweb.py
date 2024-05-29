import requests

from ..handlers.auth import TokenStrategy
from ..models.events import XRWebhookEventBatch, XRWebhookEvent
from ..common.config import get_app_config
from ..common.exceptions import ApiError


class Webhooks_XRWebHandler:
    def __init__(self, token_strategy: TokenStrategy):
        """
        Constructor for the XR Events Handler

        Args:
            token_strategy (TokenStrategy): The strategy to get the auth token
        """
        self._token_strategy = token_strategy

    def post_event_as_batch(self, event_batch: XRWebhookEventBatch) -> None:
        """
        Send an event to the API

        Args:
            event_batch (XRWebhookEventBatch): the event batch to be sent to the API
        """
        settings = get_app_config()
        api_base_url = settings.XRVOYAGE_API_BASE_URL.removesuffix('/')
        url = f'{api_base_url}/webhooks/xrweb'
        token = self._token_strategy.get_token()
        response = requests.post(
            url,
            headers={'Authorization': f'Bearer {token}'},
            json=event_batch.model_dump(by_alias=True)
        )
        if not response.ok:
            raise ApiError(status_code=response.status_code, body=response.text)
        return response.json()
    
    def post_event(self, event: XRWebhookEvent) -> None:
        """
        Send an event to the API

        Args:
            event_batch (XRWebhookEventBatch): the event batch to be sent to the API
        """
        settings = get_app_config()
        api_base_url = settings.XRVOYAGE_API_BASE_URL.removesuffix('/')
        url = f'{api_base_url}/webhooks/xrweb'
        token = self._token_strategy.get_token()
        response = requests.post(
            url,
            headers={'Authorization': f'Bearer {token}'},
            json=event.model_dump(by_alias=True)
        )
        if not response.ok:
            raise ApiError(status_code=response.status_code, body=response.text)
        return response.json()
