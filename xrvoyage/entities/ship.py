from ..handlers.auth import TokenStrategy
from ..models.ship import ShipEvent
from ..common.config import get_app_config
from ..common.exceptions import ApiError
from ..handlers.http import HttpHandler

class ShipHandler:
    def __init__(self, token_strategy: TokenStrategy):
        """
        Ship Handler Constructor

        Args:
            token_strategy (TokenStrategy): The strategy to get the auth token
        """
        self._http_handler = HttpHandler(token_strategy)

    def put_ship(self, ship_event: ShipEvent) -> dict:
        """
        Update a ship.

        Args:
            ship_event (ShipEvent): The event to be sent to update the ship.

        Returns:
            dict: The JSON response from the server.
        """
        settings = get_app_config()
        api_base_url = settings.XRVOYAGE_API_BASE_URL.removesuffix('/')
        url = f'{api_base_url}/ship'
        response = self._http_handler.put(url, json=ship_event.dict())
        return response

    def get_ship_by_guid(self, guid: str) -> dict:
        """
        Get a ship by its GUID.

        Args:
            guid (str): The ship GUID.

        Returns:
            dict: The JSON response from the server.
        """
        settings = get_app_config()
        api_base_url = settings.XRVOYAGE_API_BASE_URL.removesuffix('/')
        url = f'{api_base_url}/ship/{guid}'
        response = self._http_handler.get(url)
        return response

    def post_ship(self, guid: str, ship_event: ShipEvent) -> dict:
        """
        Create or update a ship with a given GUID.

        Args:
            guid (str): The ship GUID.
            ship_event (ShipEvent): The event to be sent to create/update the ship.

        Returns:
            dict: The JSON response from the server.
        """
        settings = get_app_config()
        api_base_url = settings.XRVOYAGE_API_BASE_URL.removesuffix('/')
        url = f'{api_base_url}/ship/{guid}'
        response = self._http_handler.post(url, json=ship_event.dict())
        return response

    def delete_ship(self, guid: str) -> dict:
        """
        Delete a ship by its GUID.

        Args:
            guid (str): The ship GUID.

        Returns:
            dict: The JSON response from the server.
        """
        settings = get_app_config()
        api_base_url = settings.XRVOYAGE_API_BASE_URL.removesuffix('/')
        url = f'{api_base_url}/ship/{guid}'
        response = self._http_handler.delete(url)
        return response
