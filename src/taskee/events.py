from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

import humanize  # type: ignore

from taskee.utils import SuggestionEnumMeta

if TYPE_CHECKING:
    from taskee.operation import Operation  # pragma: no cover


@dataclass(repr=False)
class _Event(ABC):
    title = "Generic Event"

    @property
    @abstractmethod
    def message(self) -> str:
        raise NotImplementedError  # pragma: no cover

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.message}>"


@dataclass(repr=False)
class _TaskEvent(_Event, ABC):
    """A Task Event is a type of event originating from an Earth Engine task."""

    task: Operation


class ErrorEvent(_Event):
    """An Error event occurs when taskee crashes."""

    title = "Oops!"
    message = "Something went wrong and taskee needs to be restarted."


class FailedEvent(_TaskEvent):
    """A Failed event occurs when a task fails to complete."""

    title = "Task Failed"

    @property
    def message(self) -> str:
        error = self.task.error.message if self.task.error else "Unknown"
        elapsed = humanize.naturaldelta(self.task.time_elapsed)
        return (
            f"Task '{self.task.metadata.description}' failed after {elapsed} "
            f"with error '{error}'."
        )


class CompletedEvent(_TaskEvent):
    """A Completed event occurs when a task completes successfully."""

    title = "Task Completed"

    @property
    def message(self) -> str:
        elapsed = humanize.naturaldelta(self.task.time_elapsed)
        eecus = self.task.metadata.batchEecuUsageSeconds
        return (
            f"Task '{self.task.metadata.description}' completed successfully! "
            f"It ran for {elapsed} and used {eecus:.2f} EECU-seconds."
        )


class CreatedEvent(_TaskEvent):
    """A Created event occurs when a new task is created."""

    title = "Task Created"

    @property
    def message(self) -> str:
        return f"Task '{self.task.metadata.description}' was created."


class AttemptedEvent(_TaskEvent):
    """An Attempted event occurs when an attempt fails and a new attempt begins."""

    title = "Attempt Failed"

    @property
    def message(self) -> str:
        n = self.task.metadata.attempt
        return f"Task '{self.task.metadata.description}' attempt {n - 1} failed."


class CancelledEvent(_TaskEvent):
    """A Cancelled event occurs when a task is cancelled by the user."""

    title = "Task Cancelled"

    @property
    def message(self) -> str:
        return f"Task '{self.task.metadata.description}' was cancelled."


class StartedEvent(_TaskEvent):
    """A Started event occurs when a pending task begins running."""

    title = "Task Started"

    @property
    def message(self) -> str:
        return f"Task '{self.task.metadata.description}' has started processing."


class EventEnum(Enum, metaclass=SuggestionEnumMeta):
    ERROR = ErrorEvent
    FAILED = FailedEvent
    COMPLETED = CompletedEvent
    CREATED = CreatedEvent
    ATTEMPTED = AttemptedEvent
    CANCELLED = CancelledEvent
    STARTED = StartedEvent
