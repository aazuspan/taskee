import datetime
import difflib
import os
from inspect import isabstract
from typing import Any, Dict, List, Set, Type, Union

import ee
from requests.structures import CaseInsensitiveDict

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


def _all_subclasses(cls):
    """Recursively find all subclasses of a given class."""
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in _all_subclasses(c)]
    )


def _list_subclasses(superclass: Type[Any]) -> Dict[str, Type[Any]]:
    """List all non-abstract subclasses of a given superclass. Return as a dictionary mapping the
    subclass name to the class. This is recursive, so sub-subclasses will also be returned.

    Parameters
    ----------
    superclass : Type[Any]
        The superclass to list subclasses of.

    Returns
    -------
    Dict[str, Type[Any]]
        A dictionary mapping the subclass name to the class.
    """
    return CaseInsensitiveDict(
        {
            cls.__name__: cls
            for cls in _all_subclasses(superclass)
            if not isabstract(cls)
        }
    )


def _get_subclasses(
    names: List[Union[str, Type[Any]]], superclass: Type[Any]
) -> Set[Type[Any]]:
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


def _millis_to_datetime(millis: str) -> datetime.datetime:
    """Convert a timestamp in UTC milliseconds (e.g. from Earth Engine) to a datetime object."""
    return datetime.datetime.fromtimestamp(
        int(millis) / 1000.0, tz=datetime.timezone.utc
    )


def _datetime_to_millis(dt: datetime.datetime) -> int:
    """Convert a UTC datetime to a timestamp in milliseconds"""
    return int(dt.timestamp() * 1000)


def _shorten_string(s: str, max_len: int = 10):
    """Shorten a string by abbreviating it at max_len and adding an ellipse if it was shortened."""
    if len(s) > max_len:
        return s[:max_len] + "..."
    return s
