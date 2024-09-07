import os
from functools import lru_cache
from decouple import config
import logzero

class BaseSettings:
    XRVOYAGE_WEBSOCKETS_BASE_URL: str = 'wss://ws.xr.voyage'
    XRVOYAGE_API_BASE_URL: str = 'https://apiv2.xr.voyage'

    def __init__(self):
        self.XRVOYAGE_API_BASE_URL = self.XRVOYAGE_API_BASE_URL.rstrip('/')

class Settings(BaseSettings):
    def __init__(self):
        super().__init__()
        self.XRVOYAGE_ACCESS_KEY_ID: str | None = config('XRVOYAGE_ACCESS_KEY_ID', None)
        self.XRVOYAGE_SECRET_ACCESS_KEY: str | None = config('XRVOYAGE_SECRET_ACCESS_KEY', None)
        self.XRVOYAGE_SESSION_TOKEN: str | None = config('XRVOYAGE_SESSION_TOKEN', None)
        self.LOGLEVEL: str = config('LOGLEVEL', 'DEBUG').upper()
        logzero.loglevel(getattr(logzero.logging, self.LOGLEVEL, logzero.logging.DEBUG))

        self.XRVOYAGE_CURRENT_PLUGIN: str | None = config('XRVOYAGE_CURRENT_PLUGIN', None)
        self.XRVOYAGE_CURRENT_SHIP: str | None = config('XRVOYAGE_CURRENT_SHIP', None)      

@lru_cache()
def get_app_config():
    """
    Returns a Settings Class
    """
    return Settings()
