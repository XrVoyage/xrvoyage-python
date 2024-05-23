# xrvoyage/__init__.py
try:
    from ._version import version as __version__
except ImportError:
    __version__ = "0.0.0"

def print_version():
    print(__version__)