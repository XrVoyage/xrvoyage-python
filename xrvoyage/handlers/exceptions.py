class InvalidCredentialsError(Exception):
    """
        Exception for thrown for invalid credentials.
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
        Exception for thrown for invalid credentials.
    """

    def __init__(self, msg: str):
        """
         Constructor.

         Args:
             msg (str): The exception message
        """
        super().__init__(msg)
