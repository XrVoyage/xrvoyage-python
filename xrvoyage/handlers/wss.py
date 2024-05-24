from typing import Callable
import asyncio
import json

import websockets
import logzero

from ..models.events import XRWebhookEventBatch
from ..auth import TokenStrategy
from ..config.config import get_app_config
from ..exceptions import WssConnectionError

EventCallback = Callable[[XRWebhookEventBatch], None]


class WssHandler:
    def __init__(self, token_strategy: TokenStrategy) -> None:
        """
        Websockets Handler Constructor

        Args:
            token_strategy (TokenStrategy): The strategy to get the API token.
        """
        self._token_strategy = token_strategy

    async def _listen_async(self, guid: str, cb: EventCallback) -> None:
        settings = get_app_config()
        token = self._token_strategy.get_token()
        ws_url = f"{settings.XRVOYAGE_WEBSOCKETS_BASE_URL}/v2/ship/{guid}/?token={token}"

        logzero.logger.info(f'Connecting to websockets server...')
        try:
            async with websockets.connect(ws_url) as websocket:
                logzero.logger.info(f'Listening for websocket updates for ship: {guid}...')
                while True:
                    result = await websocket.recv()
                    logzero.logger.info(f'Received event: {result}')
                    event_dict = json.loads(result)
                    parsed_event = XRWebhookEventBatch(**event_dict)
                    cb(parsed_event)
        except Exception as e:
            raise WssConnectionError(str(e))

    def connect(self, ship_guid: str, callback: EventCallback) -> None:
        """
        Connects to the Websockets server and listens for ship events.

        Args:
            ship_guid (str): The guid for the ship whose events we want to listen to.
            callback (EventCallback): The callback function to be called when an event is received.

        Returns:
            None: Returns nothing. Events are passed to the callback.

        Raises:
            xrvoyage.handlers.exceptions.InvalidCredentialsError: Invalid credentials.
            xrvoyage.handlers.exceptions.WssConnectionError: Connection to websockets server.
        """
        coro = self._listen_async(ship_guid, callback)

        try:
            # Check if an event loop is already running
            loop = asyncio.get_running_loop()
            task = loop.create_task(coro)
            asyncio.gather(task)
        except RuntimeError:
            # No event loop is running, start a new one
            asyncio.run(coro)
