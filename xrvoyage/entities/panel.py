from ..handlers.auth import TokenStrategy
from ..models.panel import PanelEvent  # Assuming a PanelEvent model exists
from ..common.config import get_app_config
from ..common.exceptions import ApiError
from ..handlers.http import HttpHandler

class PanelHandler:
    def __init__(self, token_strategy: TokenStrategy):
        """
        Panel Handler Constructor

        Args:
            token_strategy (TokenStrategy): The strategy to get the auth token
        """
        self._http_handler = HttpHandler(token_strategy)

    def put_panel(self, panel_event: PanelEvent) -> dict:
        """
        Update a panel.

        Args:
            panel_event (PanelEvent): The event to be sent to update the panel.

        Returns:
            dict: The JSON response from the server.
        """
        settings = get_app_config()
        api_base_url = settings.XRVOYAGE_API_BASE_URL.removesuffix('/')
        url = f'{api_base_url}/panel'
        response = self._http_handler.put(url, json=panel_event)
        return response

    def get_panel_by_guid(self, guid: str) -> dict:
        """
        Get a panel by its GUID.

        Args:
            guid (str): The panel GUID.

        Returns:
            dict: The JSON response from the server.
        """
        settings = get_app_config()
        api_base_url = settings.XRVOYAGE_API_BASE_URL.removesuffix('/')
        url = f'{api_base_url}/panel/{guid}'
        response = self._http_handler.get(url)
        return response

    def post_panel(self, guid: str, panel_event: PanelEvent) -> dict:
        """
        Create or update a panel with a given GUID.

        Args:
            guid (str): The panel GUID.
            panel_event (PanelEvent): The event to be sent to create/update the panel.

        Returns:
            dict: The JSON response from the server.
        """
        settings = get_app_config()
        api_base_url = settings.XRVOYAGE_API_BASE_URL.removesuffix('/')
        url = f'{api_base_url}/panel/{guid}'
        response = self._http_handler.post(url, json=panel_event)
        return response

    def delete_panel(self, guid: str) -> dict:
        """
        Delete a panel by its GUID.

        Args:
            guid (str): The panel GUID.

        Returns:
            dict: The JSON response from the server.
        """
        settings = get_app_config()
        api_base_url = settings.XRVOYAGE_API_BASE_URL.removesuffix('/')
        url = f'{api_base_url}/panel/{guid}'
        response = self._http_handler.delete(url)
        return response
