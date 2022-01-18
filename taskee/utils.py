import logging
import os

from rich.logging import RichHandler

logging.basicConfig(level=logging.DEBUG, handlers=[RichHandler()])
logger = logging.getLogger("rich")

config_path = os.path.expanduser("~/.config/taskee.ini")
