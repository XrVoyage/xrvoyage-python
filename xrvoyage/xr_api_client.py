import asyncio
import signal
import sys
from xrvoyage.entities.data_webhook import DataWebhookHandler
from xrvoyage.entities.job import JobHandler
from xrvoyage.entities.webhooks_xrweb import Webhooks_XRWebHandler
from xrvoyage.entities.data import DataHandler
from xrvoyage.entities.panel import PanelHandler
from xrvoyage.entities.plugin import PluginHandler
from xrvoyage.entities.ship import ShipHandler
from xrvoyage.entities.planet import PlanetHandler  # Import the PlanetHandler
from xrvoyage.handlers.wss import WssHandler
from xrvoyage.handlers.decorators import DecoratorsHandlers
from xrvoyage.handlers.auth import get_token_strategy
from xrvoyage.common.static import get_version

class XrApiClient:
    def __init__(self, ship_guid: str):
        self.version = get_version()
        self.ship_guid = ship_guid
        self.token_strategy = get_token_strategy()
        self.data_webhook = DataWebhookHandler(self.token_strategy)
        self.webhooks_xrweb = Webhooks_XRWebHandler(self.token_strategy)
        self.project_guid = "A3689E3BAA2B40389099DC91BCE30DF8" #NeuxFactionPeterSolarSystem
        self.decorators = DecoratorsHandlers(self.webhooks_xrweb, self.project_guid)
        
        # Initialize the new handlers
        self.panel_handler = PanelHandler(self.token_strategy)
        self.plugin_handler = PluginHandler(self.token_strategy)
        self.data_handler = DataHandler(self.token_strategy)
        self.ship_handler = ShipHandler(self.token_strategy)
        self.planet_handler = PlanetHandler(self.token_strategy)  # Add PlanetHandler

        self._shutdown = False

        self.total = 0 # persistence test

    def add_five(self): # persistence test
        self.total += 5
        return f"Current Total: {self.total}"          

    async def connect(self):
        self.wss = WssHandler(self.token_strategy, self.decorators)
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
