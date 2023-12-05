from __future__ import annotations

import datetime
import os

config_path = os.path.expanduser("~/.config/taskee.ini")


def _millis_to_datetime(
    millis: str, tz: datetime.timezone | None = None
) -> datetime.datetime:
    """Convert a timestamp in milliseconds (e.g. from Earth Engine) to a datetime
    object."""
    return datetime.datetime.fromtimestamp(int(millis) / 1000.0, tz=tz)


def _datetime_to_millis(dt: datetime.datetime) -> int:
    """Convert a datetime to a timestamp in milliseconds"""
    return int(dt.timestamp() * 1000)
