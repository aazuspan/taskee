from __future__ import annotations

from .native import Native
from .notifier import Notifier
from .pushbullet import Pushbullet

NOTIFIER_TYPES = {
    "native": Native,
    "pushbullet": Pushbullet,
}


def get_notifier(name: str) -> type[Notifier]:
    """Get a notifier by name."""
    return NOTIFIER_TYPES[name.lower()]


__all__ = ["Native", "Pushbullet", "NOTIFIER_TYPES"]
