import logging

from rich.logging import RichHandler

logging.basicConfig(
    format="%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[RichHandler(show_level=True, show_path=False, markup=True)],
)

logger = logging.getLogger("taskee")
