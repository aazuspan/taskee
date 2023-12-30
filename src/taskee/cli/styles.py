from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

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
