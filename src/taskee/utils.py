from __future__ import annotations

import datetime
import difflib
import os

config_path = os.path.expanduser("~/.config/taskee.ini")


def _get_case_insensitive_close_matches(
    word: str, possibilities: list[str], n: int = 3, cutoff: float = 0.6
) -> list[str]:
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
    List[str] : The best (no more than n) matches among the possibilities are returned
        in a list, sorted by similarity score, most similar first.
    """
    lower_matches = difflib.get_close_matches(
        word.lower(), [p.lower() for p in possibilities], n, cutoff
    )
    return [p for p in possibilities if p.lower() in lower_matches]


def _millis_to_datetime(
    millis: str, tz: datetime.timezone | None = None
) -> datetime.datetime:
    """Convert a timestamp in milliseconds (e.g. from Earth Engine) to a datetime
    object."""
    return datetime.datetime.fromtimestamp(int(millis) / 1000.0, tz=tz)


def _datetime_to_millis(dt: datetime.datetime) -> int:
    """Convert a datetime to a timestamp in milliseconds"""
    return int(dt.timestamp() * 1000)
