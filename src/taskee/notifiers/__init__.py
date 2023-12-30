from __future__ import annotations

from enum import Enum

from taskee.utils import SuggestionEnumMeta

from .native import Native
from .pushbullet import Pushbullet


class NotifierEnum(Enum, metaclass=SuggestionEnumMeta):
    NATIVE = Native
    PUSHBULLET = Pushbullet


__all__ = ["Native", "Pushbullet", "NotifierEnum"]
