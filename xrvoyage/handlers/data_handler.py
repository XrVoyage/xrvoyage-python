import requests

from .auth import TokenStrategy
from ..models.data import DataWebhookEvent
from ..config.config import get_app_config
from .exceptions import ApiError


class DataHandler:
    def __init__(self, token_strategy: TokenStrategy):
        """
        Data Handler Constructor

        Args:
            token_strategy (TokenStrategy): The strategy to get the auth token
        """
        self._token_strategy = token_strategy

    def post_webook(self, webhook_id: str, event: DataWebhookEvent) -> None:
        """
        Send an event payload to a data webhook endpoint.

        Args:
            webhook_id (str): The webhook id.
            event (DataWebhookEvent): the event to be sent to the webhook.
        """
        settings = get_app_config()
        api_base_url = settings.XRVOYAGE_API_BASE_URL.removesuffix('/')
        url = f'{api_base_url}/data/webhook/{webhook_id}'
        token = self._token_strategy.get_token()
        response = requests.post(
            url,
            headers={'Authorization': f'Bearer {token}'},
            json=event.model_dump()
        )
        if not response.ok:
            raise ApiError(status_code=response.status_code, body=response.text)
