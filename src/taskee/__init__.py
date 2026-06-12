from importlib.metadata import PackageNotFoundError, version

from .taskee import Taskee

try:
    __version__ = version("taskee")
except PackageNotFoundError:
    __version__ = "unknown"

__all__ = ["Taskee"]
