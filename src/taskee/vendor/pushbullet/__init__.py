"""A minimal vendored replacement for the archived ``pushbullet.py`` package.

Only the note-pushing functionality used by taskee is included. See ``pushbullet.py``
in this package for details and upstream attribution.
"""

from __future__ import annotations

from . import errors
from .errors import InvalidKeyError, PushbulletError, PushError
from .pushbullet import Pushbullet

__all__ = [
    "Pushbullet",
    "PushbulletError",
    "InvalidKeyError",
    "PushError",
    "errors",
]
