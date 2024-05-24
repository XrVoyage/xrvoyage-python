from .auth import TokenStrategy


class DataHandler:
    def __init__(self, token_strategy: TokenStrategy):
        """
        Data Handler Constructor

        Args:
            token_strategy (TokenStrategy): The strategy to get the auth token
        """
        self._token_strategy = token_strategy
