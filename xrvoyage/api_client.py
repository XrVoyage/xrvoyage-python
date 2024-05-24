from xrvoyage.handlers.data import DataHandler
from xrvoyage.handlers.job import JobHandler
from xrvoyage.handlers.wss import WssHandler
from xrvoyage.handlers.xrevents import XREventsHandler
from xrvoyage.auth import get_token_strategy


class XrApiClient:
    def __init__(self):
        token_strategy = get_token_strategy()
        self.data = DataHandler(token_strategy)
        self.job = JobHandler(token_strategy)
        self.wss = WssHandler(token_strategy)
        self.events = XREventsHandler(token_strategy)
