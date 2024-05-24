from typing import Callable, Dict
import asyncio
import json
import websockets
import logzero
from logzero import logger

from ..models.events import XRWebhookEventBatch
from .auth import TokenStrategy
from ..config.config import get_app_config
from .exceptions import WssConnectionError

EventCallback = Callable[[XRWebhookEventBatch], None]
event_handlers: Dict[str, EventCallback] = {}

def eventIngress(event_type: str):
    """
    Decorator to register a callback for a specific event type.
    """
    logger.debug(f'Registering event handler for event type: {event_type}')
    def decorator(func: EventCallback):
        event_handlers[event_type] = func
        return func
    return decorator

class WssHandler:
    def __init__(self, token_strategy: TokenStrategy) -> None:
        """
        Websockets Handler Constructor

        Args:
            token_strategy (TokenStrategy): The strategy to get the API token.
        """
        logger.debug('Initializing WssHandler')
        self._token_strategy = token_strategy
        self._task = None
        self._websocket = None

    async def _listen_async(self, guid: str) -> None:
        settings = get_app_config()
        token = self._token_strategy.get_token()
        ws_url = f"{settings.XRVOYAGE_WEBSOCKETS_BASE_URL}/v2/ship/{guid}/?token={token}"

        logger.info(f'Connecting to websockets server: {ws_url}')
        try:
            async with websockets.connect(ws_url) as websocket:
                self._websocket = websocket
                logger.info(f'Listening for websocket updates for ship: {guid}')
                while True:
                    result = await websocket.recv()
                    logger.info(f'Received event: {result}')
                    event_dict = json.loads(result)
                    event_type = event_dict.get("type")
                    if event_type in event_handlers:
                        parsed_event = XRWebhookEventBatch(**event_dict)
                        logger.debug(f'Triggering event handler for event type: {event_type}')
                        event_handlers[event_type](parsed_event)
                    else:
                        logger.warning(f"No handler registered for event type: {event_type}")
        except Exception as e:
            logger.error(f'Error in websocket connection: {e}')
            raise WssConnectionError(str(e))

    def connect(self, ship_guid: str) -> None:
        """
        Connects to the Websockets server and listens for ship events.

        Args:
            ship_guid (str): The guid for the ship whose events we want to listen to.

        Returns:
            None: Returns nothing. Events are passed to the callback.

        Raises:
            xrvoyage.handlers.exceptions.InvalidCredentialsError: Invalid credentials.
        """
        logger.debug(f'Attempting to connect to websocket for ship: {ship_guid}')
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._listen_async(ship_guid))

    async def destroy(self) -> None:
        """
        Closes the websocket connection if it exists.
        """
        logger.debug('Destroying websocket connection')
        if self._websocket:
            await self._websocket.close()
            logger.info('Websocket connection closed.')

# Ensure eventIngress is included in the module's export
__all__ = ['WssHandler', 'eventIngress']
