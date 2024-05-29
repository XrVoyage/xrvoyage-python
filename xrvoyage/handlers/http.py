import requests
from pydantic import BaseModel
import logzero

class ApiError(Exception):
    def __init__(self, status_code, body):
        self.status_code = status_code
        self.body = body
        super().__init__(f"API Error {status_code}: {body}")

class HttpHandler:
    def __init__(self, token_strategy):
        """
        HTTP Handler Constructor

        Args:
            token_strategy (TokenStrategy): The strategy to get the auth token
        """
        self._token_strategy = token_strategy

    def _request(self, method: str, url: str, **kwargs) -> dict:
        """
        Send an HTTP request with the specified method.

        Args:
            method (str): The HTTP method (GET, POST, PUT, DELETE).
            url (str): The URL to send the request to.

        Returns:
            dict: The JSON response from the server.

        Raises:
            ApiError: If the response status code is not 2xx.
        """
        token = self._token_strategy.get_token()
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'Bearer {token}'
        kwargs['headers'] = headers

        if 'json' in kwargs and isinstance(kwargs['json'], BaseModel):
            payload = kwargs['json'].dict(by_alias=True, exclude_none=True)
            logzero.logger.debug(f"Request Payload: {payload}")
            kwargs['json'] = payload

        response = requests.request(method, url, **kwargs)
        if not response.ok:
            raise ApiError(status_code=response.status_code, body=response.text)
        return response.json()

    def post(self, url: str, json: BaseModel) -> dict:
        """
        Send a POST request to a specified URL with JSON payload.

        Args:
            url (str): The URL to send the POST request to.
            json (BaseModel): The JSON payload to send.

        Returns:
            dict: The JSON response from the server.
        """
        return self._request('POST', url, json=json)

    def put(self, url: str, json: BaseModel) -> dict:
        """
        Send a PUT request to a specified URL with JSON payload.

        Args:
            url (str): The URL to send the PUT request to.
            json (BaseModel): The JSON payload to send.

        Returns:
            dict: The JSON response from the server.
        """
        return self._request('PUT', url, json=json)

    def get(self, url: str, params: dict = None) -> dict:
        """
        Send a GET request to a specified URL.

        Args:
            url (str): The URL to send the GET request to.
            params (dict, optional): The query parameters to send.

        Returns:
            dict: The JSON response from the server.
        """
        return self._request('GET', url, params=params)

    def delete(self, url: str) -> dict:
        """
        Send a DELETE request to a specified URL.

        Args:
            url (str): The URL to send the DELETE request to.

        Returns:
            dict: The JSON response from the server.
        """
        return self._request('DELETE', url)
