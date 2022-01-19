import difflib
import logging
import os
from typing import List, Union, Any, Dict, Type, Set
from requests.structures import CaseInsensitiveDict

import ee
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


def _list_subclasses(superclass: Type[Any]) -> Dict[str, Type[Any]]:
    """List all subclasses of a given superclass. Return as a dictionary mapping the 
    subclass name to the class.
    
    Parameters
    ----------
    superclass : Type[Any]
        The superclass to list subclasses of.
    
    Returns
    -------
    Dict[str, Type[Any]]
        A dictionary mapping the subclass name to the class.
    """
    return CaseInsensitiveDict({cls.__name__: cls for cls in superclass.__subclasses__()})


def _get_subclasses(names: List[Union[str, Type[Any]]], superclass: Type[Any]) -> Set[Type[Any]]:
    """Retrieve a set of subclasses of a given superclass.

    Parameters
    ----------
    names : List[Union[str, Type[Any]]]
        A list of names or classes to retrieve from the superclass.
    superclass : Type[Any]
        The superclass to retrieve subclasses of.

    Returns
    -------
    Set[Type[Any]]
        A set of subclasses of the superclass.
    """
    # Allow single values to be passed
    names = [names] if not isinstance(names, (list, tuple)) else names

    options = _list_subclasses(superclass)
    keys = list(options.keys())

    if "all" in [name.lower() for name in names if isinstance(name, str)]:
        return set(options.values())

    selected = []

    for name in names:
        if isinstance(name, str):
            try:
                selected.append(options[name])
            except KeyError:
                close_matches = _get_case_insensitive_close_matches(name, keys, n=3)
                hint = (
                    " Close matches: {}.".format(close_matches) if close_matches else ""
                )

                raise AttributeError(
                    f'"{name}" is not a supported {superclass.__name__} type. Choose from {keys}.{hint}'
                )
        else:
            try:
                if issubclass(name, superclass):
                    selected.append(name)
            except TypeError:
                raise AttributeError(
                    f"Choices must be strings or subclasses of {superclass.__name__}, not {type(name).__name__}."
                )

    return set(selected)