import logging
import os

from rich.logging import RichHandler

logging.basicConfig(handlers=[RichHandler()])

logger = logging.getLogger("taskee")
logger.setLevel(logging.DEBUG)

config_path = os.path.expanduser("~/.config/taskee.ini")
