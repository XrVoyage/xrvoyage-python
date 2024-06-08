# xrvoyage/xr_api_client.py
import asyncio
import signal
import sys
from xrvoyage.entities.data_webhook import DataWebhookHandler
from xrvoyage.entities.job import JobHandler
from xrvoyage.entities.webhooks_xrweb import Webhooks_XRWebHandler
from xrvoyage.handlers.wss import WssHandler
from xrvoyage.handlers.decorators import DecoratorsHandlers
from xrvoyage.handlers.auth import get_token_strategy
from xrvoyage.common.static import get_version

class XrApiClient:
    def __init__(self, ship_guid: str):
        self.version = get_version()
        self.ship_guid = ship_guid
        token_strategy = get_token_strategy()
        self.data_webhook = DataWebhookHandler(token_strategy)
        # self.job = JobHandler(token_strategy)
        self.wss = WssHandler(token_strategy)
        self.webhooks_xrweb = Webhooks_XRWebHandler(token_strategy)
        self.project_guid = "A895570833F0429A98940C079555AE51"
        self.decorators = DecoratorsHandlers(self.webhooks_xrweb, self.project_guid)
        self._shutdown = False

    async def connect(self):
        loop = asyncio.get_event_loop()

        if sys.platform != "win32":
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, self.shutdown)

        await self.wss.connect(self.ship_guid)

        try:
            while not self._shutdown:
                await asyncio.sleep(1)
        finally:
            await self.wss.destroy()

    def shutdown(self):
        self._shutdown = True
