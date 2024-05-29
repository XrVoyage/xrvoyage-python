# handlers/static.py
try:
    from .._version import version as __version__
except ImportError:
    __version__ = "0.0.0"

def get_version():
    return __version__

def print_version():
    print(__version__)