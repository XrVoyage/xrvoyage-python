# xrvoyage/__init__.py
from .handlers.static import get_version, print_version
from .api_client import XrApiClient

__version__ = get_version()
