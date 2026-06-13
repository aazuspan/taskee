from __future__ import annotations

from enum import Enum

from .native import Native
from .pushbullet import Pushbullet


class NotifierEnum(Enum):
    NATIVE = Native
    PUSHBULLET = Pushbullet


__all__ = ["Native", "Pushbullet", "NotifierEnum"]
