import configparser
from typing import TYPE_CHECKING, Union

from requests.exceptions import ConnectionError
from rich.prompt import Prompt

from taskee.notifiers.notifier import Notifier
from taskee.utils import config_path

if TYPE_CHECKING:
    import pushbullet  # type: ignore


class Pushbullet(Notifier):
    def __init__(self) -> None:
        self.pb = initialize_pushbullet()

    def send(self, title: str, message: str) -> None:
        push = self.pb.push_note(title, message)


def initialize_pushbullet() -> "pushbullet.Pushbullet":
    """Initialize the Pushbullet API and return a Pushbullet object."""
    try:
        import pushbullet
    except ImportError:
        raise ImportError(
            "The `pushbullet` package must be installed to use the Pushbullet notifier."
            " Run `pip install pushbullet.py` to install."
        )

    api_key = _get_stored_pushbullet_key(config_path)

    store_key = False
    pb: Union[str, None] = None
    while pb is None:
        try:
            pb = pushbullet.Pushbullet(api_key)
        except pushbullet.errors.InvalidKeyError:
            api_key = _request_pushbullet_key()
            store_key = True
        except ConnectionError:
            raise ConnectionError(
                "Failed to connect to Pushbullet! Please make sure you are connected to"
                " internet and try again."
            )

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
        return ""


def _request_pushbullet_key() -> str:
    """Request a Pushbullet API key from the user."""
    apikey = Prompt.ask("Enter your [yellow bold]Pushbullet[/] API key to continue")
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
        config.write(dst)
