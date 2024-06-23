from ..handlers.auth import TokenStrategy
from ..models.data import PutDataRequestDTO  # Import only the existing model
from ..common.config import get_app_config
from ..common.exceptions import ApiError
from ..handlers.http import HttpHandler
from logzero import logger

class DataHandler:
    def __init__(self, token_strategy: TokenStrategy):
        """
        Data Handler Constructor

        Args:
            token_strategy (TokenStrategy): The strategy to get the auth token
        """
        self._http_handler = HttpHandler(token_strategy)

    # async def put_data(self, args: dict, name: str):
    #     payload = {
    #         "data": {
    #             "object": {
    #                 "metadata": {
    #                     "solarsystem_guid": self.xr.project_guid,  # Directly using project_guid
    #                     "solarsystem_name": "shiptype.systemcruiser NeuxPeterFaction",
    #                     "type": "data.type.default"
    #                 }
    #             },
    #             "response": args
    #         },
    #         "name": name
    #     }
        
    #     data_request = PutDataRequestDTO(**payload)
        
    #     try:
    #         response = self.xr.data_handler.put_data(data_request)
    #         logger.info("Data sent successfully: %s", response)
    #     except Exception as e:
    #         logger.error("Error sending data: %s", str(e))


    def put_data(self, data_request: PutDataRequestDTO) -> dict:
        """
        Update data.

        Args:
            data_request (PutDataRequestDTO): The data to be updated.

        Returns:
            dict: The updated data.
        """
        settings = get_app_config()
        api_base_url = settings.XRVOYAGE_API_BASE_URL.removesuffix('/')
        url = f'{api_base_url}/data'
        response = self._http_handler.put(url, json=data_request.dict())
        return response

    def get_data_by_guid(self, guid: str) -> dict:
        """
        Get data by GUID.

        Args:
            guid (str): The data GUID.

        Returns:
            dict: The retrieved data.
        """
        settings = get_app_config()
        api_base_url = settings.XRVOYAGE_API_BASE_URL.removesuffix('/')
        url = f'{api_base_url}/data/{guid}'
        response = self._http_handler.get(url)
        return response

    def post_data(self, guid: str, data_request: PutDataRequestDTO) -> dict:
        """
        Create or update data with a given GUID.

        Args:
            guid (str): The data GUID.
            data_request (PutDataRequestDTO): The data to be created/updated.

        Returns:
            dict: The created/updated data.
        """
        settings = get_app_config()
        api_base_url = settings.XRVOYAGE_API_BASE_URL.removesuffix('/')
        url = f'{api_base_url}/data/{guid}'
        response = self._http_handler.post(url, json=data_request.dict())
        return response

    def delete_data(self, guid: str) -> dict:
        """
        Delete data by GUID.

        Args:
            guid (str): The data GUID.

        Returns:
            dict: The JSON response from the server.
        """
        settings = get_app_config()
        api_base_url = settings.XRVOYAGE_API_BASE_URL.removesuffix('/')
        url = f'{api_base_url}/data/{guid}'
        response = self._http_handler.delete(url)
        return response
