from ..handlers.auth import TokenStrategy


class JobHandler:
    def __init__(self, token_strategy: TokenStrategy):
        """
        Job Handler Constructor

        Args:
            token_strategy (TokenStrategy): The strategy to get the auth token
        """
        self._token_strategy = token_strategy
