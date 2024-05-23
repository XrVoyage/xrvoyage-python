from typing import Callable
import asyncio
import json

import websockets
import logzero

from .models import XRWebhookEventBatch
from . import auth
from .config.config import get_app_config

settings = get_app_config()

EventCallback = Callable[[XRWebhookEventBatch], None]


class XrWssClient:
    def __init__(self) -> None:
        self._token_strategy = auth.get_token_strategy()

    async def _listen_async(self, guid: str, cb: EventCallback) -> None:
        token = self._token_strategy.get_token()
        ws_url = f"{settings.XRVOYAGE_WEBSOCKETS_BASE_URL}/v2/ship/{guid}/?token={token}"

        logzero.logger.info(f'Connecting to websockets server...')
        async with websockets.connect(ws_url) as websocket:
            logzero.logger.info(f'Listening for websocket updates for ship: {guid}...')
            while True:
                result = await websocket.recv()
                logzero.logger.info(f'Received event: {result}')
                event_dict = json.loads(result)
                parsed_event = XRWebhookEventBatch(**event_dict)
                cb(parsed_event)

    def connect(self, ship_guid: str, callback: EventCallback) -> None:
        coro = self._listen_async(ship_guid, callback)
        asyncio.run(coro)
