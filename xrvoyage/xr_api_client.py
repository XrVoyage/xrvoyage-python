from xrvoyage.entities.data_webhook import DataWebhookHandler
from xrvoyage.entities.job import JobHandler
from xrvoyage.handlers.wss import WssHandler
from xrvoyage.entities.webhooks_xrweb import Webhooks_XRWebHandler
from xrvoyage.handlers.auth import get_token_strategy


class XrApiClient:
    def __init__(self):
        token_strategy = get_token_strategy()
        self.data   = DataWebhookHandler(token_strategy)
        self.job    = JobHandler(token_strategy)
        self.wss    = WssHandler(token_strategy)
        self.events = Webhooks_XRWebHandler(token_strategy)
