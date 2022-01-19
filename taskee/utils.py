import configparser
import difflib
import logging
import os
from typing import List

import ee
import pushbullet
from rich.logging import RichHandler

logging.basicConfig(handlers=[RichHandler()])

logger = logging.getLogger("taskee")
logger.setLevel(logging.DEBUG)

config_path = os.path.expanduser("~/.config/taskee.ini")


def initialize_earthengine() -> None:
    """Initialize the Earth Engine API."""
    try:
        ee.Initialize()
    except ee.EEException:
        ee.Authenticate()
        ee.Initialize()


def initialize_pushbullet() -> pushbullet.Pushbullet:
    """Initialize the Pushbullet API and return a Pushbullet object."""
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


def _get_case_insensitive_close_matches(
    word: str, possibilities: List[str], n: int = 3, cutoff: float = 0.6
) -> List[str]:
    """A case-insensitive wrapper around difflib.get_close_matches.
    Parameters
    ----------
    word : str
        A string for which close matches are desired.
    possibilites : List[str]
        A list of strings against which to match word.
    n : int, default 3
        The maximum number of close matches to return. n must be > 0.
    cutoff : float, default 0.6
        Possibilities that don't score at least that similar to word are ignored.

    Returns
    -------
    List[str] : The best (no more than n) matches among the possibilities are returned in
        a list, sorted by similarity score, most similar first.
    """
    lower_matches = difflib.get_close_matches(
        word.lower(), [p.lower() for p in possibilities], n, cutoff
    )
    return [p for p in possibilities if p.lower() in lower_matches]
