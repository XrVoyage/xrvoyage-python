from ..handlers.auth import TokenStrategy
from ..models.planet import PlanetEvent
from ..common.config import get_app_config
from ..common.exceptions import ApiError
from ..handlers.http import HttpHandler

class PlanetHandler:
    def __init__(self, token_strategy: TokenStrategy):
        """
        Planet Handler Constructor

        Args:
            token_strategy (TokenStrategy): The strategy to get the auth token
        """
        self._http_handler = HttpHandler(token_strategy)

    def put_planet(self, planet_event: PlanetEvent) -> dict:
        """
        Update a planet.

        Args:
            planet_event (PlanetEvent): The event to be sent to update the planet.

        Returns:
            dict: The JSON response from the server.
        """
        settings = get_app_config()
        api_base_url = settings.XRVOYAGE_API_BASE_URL.removesuffix('/')
        url = f'{api_base_url}/planet'
        response = self._http_handler.put(url, json=planet_event.dict())
        return response

    def get_planet_by_guid(self, guid: str) -> dict:
        """
        Get a planet by its GUID.

        Args:
            guid (str): The planet GUID.

        Returns:
            dict: The JSON response from the server.
        """
        settings = get_app_config()
        api_base_url = settings.XRVOYAGE_API_BASE_URL.removesuffix('/')
        url = f'{api_base_url}/planet/{guid}'
        response = self._http_handler.get(url)
        return response

    def post_planet(self, guid: str, planet_event: PlanetEvent) -> dict:
        """
        Create or update a planet with a given GUID.

        Args:
            guid (str): The planet GUID.
            planet_event (PlanetEvent): The event to be sent to create/update the planet.

        Returns:
            dict: The JSON response from the server.
        """
        settings = get_app_config()
        api_base_url = settings.XRVOYAGE_API_BASE_URL.removesuffix('/')
        url = f'{api_base_url}/planet/{guid}'
        response = self._http_handler.post(url, json=planet_event.dict())
        return response

    def delete_planet(self, guid: str) -> dict:
        """
        Delete a planet by its GUID.

        Args:
            guid (str): The planet GUID.

        Returns:
            dict: The JSON response from the server.
        """
        settings = get_app_config()
        api_base_url = settings.XRVOYAGE_API_BASE_URL.removesuffix('/')
        url = f'{api_base_url}/planet/{guid}'
        response = self._http_handler.delete(url)
        return response
