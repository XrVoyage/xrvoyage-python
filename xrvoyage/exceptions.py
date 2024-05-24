class InvalidCredentialsError(Exception):
    """
        Exception thrown for invalid credentials.
    """

    def __init__(self, msg: str):
        """
         Constructor.

         Args:
             msg (str): The exception message
        """
        super().__init__(msg)


class WssConnectionError(Exception):
    """
        Exception thrown for invalid credentials.
    """

    def __init__(self, msg: str):
        """
         Constructor.

         Args:
             msg (str): The exception message
        """
        super().__init__(msg)


class ApiError(Exception):
    """
        Exception thrown due to an api error
    """
    def __init__(self, status_code: int, body: str):
        """
        Constructor.

        Args:
            status_code (int): The server status code.
            body (str): The server message
        """
        msg = f'Status Code: {status_code}, Body: {body}'
        super().__init__(msg)
