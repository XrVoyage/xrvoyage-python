from functools import lru_cache

from decouple import config


class BaseSettings:
    XRVOYAGE_WEBSOCKETS_BASE_URL: str = 'wss://ws.xr.voyage'
    XRVOYAGE_API_BASE_URL: str = 'https://apiv2.xr.voyage'


# class CredentialsSettings(pydantic.BaseModel):
#     XRVOYAGE_ACCESS_KEY_ID: str | None = config('XRVOYAGE_ACCESS_KEY_ID', None)
#     XRVOYAGE_SECRET_ACCESS_KEY: str | None = config('XRVOYAGE_SECRET_ACCESS_KEY', None)
#     XRVOYAGE_SESSION_TOKEN: str | None = config('XRVOYAGE_SESSION_TOKEN', None)


class Settings(
    BaseSettings
):
    def __init__(self):
        super().__init__()
        self.XRVOYAGE_ACCESS_KEY_ID: str | None = config('XRVOYAGE_ACCESS_KEY_ID', None)
        self.XRVOYAGE_SECRET_ACCESS_KEY: str | None = config('XRVOYAGE_SECRET_ACCESS_KEY', None)
        self.XRVOYAGE_SESSION_TOKEN: str | None = config('XRVOYAGE_SESSION_TOKEN', None)


@lru_cache()
def get_app_config():
    """
    Returns a Settings Class
    """
    return Settings()
