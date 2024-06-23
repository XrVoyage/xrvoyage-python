from typing import Callable, Dict, List, Union
import asyncio
import json
import websockets
import logzero
from logzero import logger

from ..models.events import XRWebhookEventBatch
from .auth import TokenStrategy
from ..common.config import get_app_config
from ..common.exceptions import WssConnectionError
from .decorators import DecoratorsHandlers

class WssHandler:
    def __init__(self, token_strategy: TokenStrategy, decorators: DecoratorsHandlers) -> None:
        """
        Websockets Handler Constructor

        Args:
            token_strategy (TokenStrategy): The strategy to get the API token.
            decorators (DecoratorsHandlers): Instance of DecoratorsHandlers to access event handlers.
        """
        logger.debug('Initializing WssHandler')
        self._token_strategy = token_strategy
        self._task = None
        self._websocket = None
        self._connected_event = asyncio.Event()
        self._decorators = decorators      

    async def _listen_async(self, guid: str) -> None:
        settings = get_app_config()
        token = self._token_strategy.get_token()
        ws_url = f"{settings.XRVOYAGE_WEBSOCKETS_BASE_URL}/v2/ship/{guid}/?token={token}"

        try:
            async with websockets.connect(ws_url) as websocket:
                self._websocket = websocket
                self._connected_event.set()  # Set the event after connection is established
                logger.info(f'Listening for websocket updates for ship: {guid}')
                while True:
                    result = await websocket.recv()
                    logger.info(f'Received event: {result}')
                    event_dict = json.loads(result)
                    self._handle_event(event_dict)
        except websockets.exceptions.ConnectionClosedOK:
            logger.info('Websocket connection closed normally.')
        except Exception as e:
            logger.error(f'Error in websocket connection: {e}')
            raise WssConnectionError(str(e))

    def _handle_event(self, event_dict: dict) -> None:
        """
        Handle the received event, determining if it's a batch or single event.

        Args:
            event_dict (dict): The event dictionary received from the websocket.
        """
        for key, value in event_dict.items():
            if key.startswith("xr."):
                if isinstance(value, list):
                    for event_data in value:
                        self._trigger_event_handler(event_data)
                else:
                    self._trigger_event_handler(value)

    def _trigger_event_handler(self, event_data: dict) -> None:
        """
        Trigger the registered event handler for the event type.

        Args:
            event_data (dict): The event data containing the event type and other details.
        """
        event_type = event_data.get("type")
        if event_type in self._decorators.event_handlers:
            try:
                logger.info(f'eventIngress sent to registered handler: {event_type}')
                handler = self._decorators.event_handlers[event_type]
                logger.debug(f"Handler for {event_type}: {handler}")
                if asyncio.iscoroutinefunction(handler):
                    logger.debug(f"{event_type} handler is a coroutine, scheduling with asyncio.ensure_future")
                    asyncio.ensure_future(handler(event_data))
                else:
                    logger.debug(f"{event_type} handler is not a coroutine, calling directly")
                    handler(event_data)
            except Exception as e:
                logger.error(f"Error handling event {event_type}: {e}")
        else:
            logger.debug(f"eventIngress skipping not handled: {event_type}")

    async def connect(self, ship_guid: str) -> None:
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
            self._connected_event.clear()  # Clear the event before starting the task
            self._task = asyncio.create_task(self._listen_async(ship_guid))
            await self._connected_event.wait()  # Wait for the connection to be established

    async def destroy(self) -> None:
        """
        Closes the websocket connection if it exists.
        """
        logger.debug('Destroying websocket connection')
        if self._websocket:
            await self._websocket.close()
            logger.info('Websocket connection closed.')

# Ensure eventIngress is included in the module's export
__all__ = ['WssHandler', 'DecoratorsHandlers']
