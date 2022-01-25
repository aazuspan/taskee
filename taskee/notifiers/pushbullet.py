import configparser

from taskee.notifiers.notifier import Notifier
from taskee.terminal.logger import logger
from taskee.utils import config_path


class Pushbullet(Notifier):
    def __init__(self):
        logger.debug("Initializing Pushbullet...")
        self.pb = initialize_pushbullet()

    # TODO: Check `push` status code and decide what to do with errors (resend later? Crash? Just log?)
    def send(self, title, message):
        push = self.pb.push_note(title, message)


def initialize_pushbullet() -> "pushbullet.Pushbullet":
    """Initialize the Pushbullet API and return a Pushbullet object."""
    try:
        import pushbullet
    except ImportError:
        raise ImportError(
            "The `pushbullet` package must be installed to use the Pushbullet notifier. Run `pip install pushbullet.py` to install."
        )

    api_key = _get_stored_pushbullet_key(config_path)

    store_key = False
    pb = None
    while pb is None:
        try:
            pb = pushbullet.Pushbullet(api_key)
        except pushbullet.errors.InvalidKeyError:
            logger.error("Invalid Pushbullet API key...")
            api_key = _request_pushbullet_key()
            store_key = True

    if store_key:
        _store_pushbullet_key(api_key, config_path)

    return pb


def _get_stored_pushbullet_key(path: str) -> str:
    """Get the stored Pushbullet API key from a config file, if it exists. If the file,
    section, or key don't exist, return None.

    Parameters
    ----------
    path : str
        The path to the config file.
    """
    config = configparser.ConfigParser()
    config.read(path)

    try:
        return config["Pushbullet"]["api_key"]
    except KeyError:
        return None


def _request_pushbullet_key() -> str:
    """Request a Pushbullet API key from the user."""
    apikey = input("Enter Pushbullet API key to continue:")
    return apikey


def _store_pushbullet_key(key: str, path: str) -> None:
    """Store the Pushbullet API key in the config file. If the config file does not exist,
    it will be created.

    Parameters
    ----------
    key : str
        The Pushbullet API key to store.
    path : str
        The path to the config file.
    """
    config = configparser.ConfigParser()
    config.read(path)

    try:
        config["Pushbullet"]["api_key"] = key
    # If Pushbullet section doesn't exist, create it
    except KeyError:
        config["Pushbullet"] = {"api_key": key}

    with open(path, "w") as dst:
        logger.info(f"Storing Pushbullet API key for future use at {path}.")
        config.write(dst)
