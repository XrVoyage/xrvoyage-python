from logzero import logger
from ..handlers.auth import TokenStrategy
from ..models.plugin import PluginEvent  # Correct import path
from ..common.config import get_app_config
from ..common.exceptions import ApiError
from ..handlers.http import HttpHandler

class PluginHandler:
    def __init__(self, token_strategy: TokenStrategy):
        """
        Plugin Handler Constructor

        Args:
            token_strategy (TokenStrategy): The strategy to get the auth token
        """
        self._http_handler = HttpHandler(token_strategy)
        self.settings = get_app_config()  # Moved here

    def get_plugin_by_guid(self, guid: str) -> dict:
        """
        Get a plugin by its GUID.

        Args:
            guid (str): The plugin GUID.

        Returns:
            dict: The JSON response from the server.
        """
        
        try:
            response = self._http_handler.get(f'{self.settings.XRVOYAGE_API_BASE_URL}/plugin/{guid}')
            return response
        except ApiError as e:
            logger.error(f"API error occurred: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}")
            raise


    def put_plugin(self, plugin_event: PluginEvent) -> dict:
        """
        Update a plugin.

        Args:
            plugin_event (PluginEvent): The event to be sent to update the plugin.

        Returns:
            dict: The JSON response from the server.
        """
        settings = get_app_config()
        api_base_url = settings.XRVOYAGE_API_BASE_URL.removesuffix('/')
        url = f'{api_base_url}/plugin'
        response = self._http_handler.put(url, json=plugin_event)
        return response



    def post_plugin(self, guid: str, plugin_event: PluginEvent) -> dict:
        """
        Create or update a plugin with a given GUID.

        Args:
            guid (str): The plugin GUID.
            plugin_event (PluginEvent): The event to be sent to create/update the plugin.

        Returns:
            dict: The JSON response from the server.
        """
        settings = get_app_config()
        api_base_url = settings.XRVOYAGE_API_BASE_URL.removesuffix('/')
        url = f'{api_base_url}/plugin/{guid}'
        response = self._http_handler.post(url, json=plugin_event)
        return response

    def delete_plugin(self, guid: str) -> dict:
        """
        Delete a plugin by its GUID.

        Args:
            guid (str): The plugin GUID.

        Returns:
            dict: The JSON response from the server.
        """
        settings = get_app_config()
        api_base_url = settings.XRVOYAGE_API_BASE_URL.removesuffix('/')
        url = f'{api_base_url}/plugin/{guid}'
        response = self._http_handler.delete(url)
        return response
