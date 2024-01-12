from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Any

from taskee import events
from taskee.operation import OperationState


class Color(Enum):
    SUCCESS = "green"
    ERROR = "red"
    INFO = "cyan"
    WARNING = "yellow"


@dataclass
class Style:
    color: str
    emoji: str


STYLES: Mapping[Any, Style] = {
    # Events
    events.ErrorEvent: Style(color=Color.ERROR.value, emoji="❗"),
    events.FailedEvent: Style(color=Color.ERROR.value, emoji="🔥"),
    events.CompletedEvent: Style(color=Color.SUCCESS.value, emoji="🌲"),
    events.CreatedEvent: Style(color=Color.INFO.value, emoji="🌱"),
    events.StartedEvent: Style(color=Color.INFO.value, emoji="🌿"),
    events.AttemptedEvent: Style(color=Color.WARNING.value, emoji="🍂"),
    events.CancelledEvent: Style(color=Color.ERROR.value, emoji="🪓"),
    # States
    OperationState.CANCELLING: Style(color=Color.ERROR.value, emoji="🚩"),
    OperationState.CANCELLED: Style(color=Color.ERROR.value, emoji="🚫"),
    OperationState.SUCCEEDED: Style(color=Color.SUCCESS.value, emoji="✔️"),
    OperationState.FAILED: Style(color=Color.ERROR.value, emoji="❌"),
    OperationState.PENDING: Style(color=Color.INFO.value, emoji="⏳"),
    OperationState.RUNNING: Style(color=Color.INFO.value, emoji="🔧"),
}


def get_style(obj: Any) -> Style:
    """Get the style for an object."""
    return STYLES.get(obj, Style(color=Color.INFO.value, emoji="❓"))
