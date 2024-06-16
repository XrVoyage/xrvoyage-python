from ..handlers.auth import TokenStrategy
from ..models.data import DataWebhookEvent
from ..common.config import get_app_config
from ..common.exceptions import ApiError
from ..handlers.http import HttpHandler

class DataWebhookHandler:
    def __init__(self, token_strategy: TokenStrategy):
        """
        Data Handler Constructor

        Args:
            token_strategy (TokenStrategy): The strategy to get the auth token
        """
        self._http_handler = HttpHandler(token_strategy)

    def post_webhook(self, webhook_id: str, event: DataWebhookEvent) -> None:
        """
        Send an event payload to a data webhook endpoint.

        Args:
            webhook_id (str): The webhook id.
            event (DataWebhookEvent): the event to be sent to the webhook.
        """
        settings = get_app_config()
        api_base_url = settings.XRVOYAGE_API_BASE_URL.removesuffix('/')
        url = f'{api_base_url}/data/webhook/{webhook_id}'
        response = self._http_handler.post(url, json=event.dict())
        return response
