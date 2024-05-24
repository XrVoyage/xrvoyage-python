from .data_handler import DataHandler
from .job_handler import JobHandler
from .wss_handler import WssHandler
from .xrevents_handler import XREventsHandler
from .auth import get_token_strategy


class XrApiClient:
    def __init__(self):
        token_strategy = get_token_strategy()
        self.data = DataHandler(token_strategy)
        self.job = JobHandler(token_strategy)
        self.wss = WssHandler(token_strategy)
        self.events = XREventsHandler(token_strategy)
