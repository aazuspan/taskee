from __future__ import annotations

import datetime
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import humanize  # type: ignore

if TYPE_CHECKING:
    from taskee.tasks import Task  # pragma: no cover


class Event(ABC):
    title = "Generic Event"

    def __init__(self) -> None:
        self.time = datetime.datetime.now()

    @property
    @abstractmethod
    def message(self) -> str:
        raise NotImplementedError  # pragma: no cover


class TaskEvent(Event, ABC):
    """A Task Event is a type of event originating from an Earth Engine task."""

    def __init__(self, task: Task):
        self.task = task
        super().__init__()


class Error(Event):
    """An Error event occurs when taskee crashes."""

    title = "Oops!"
    message = "Something went wrong and taskee needs to be restarted."


class Failed(TaskEvent):
    """A Failed event occurs when a task fails to complete."""

    title = "Task Failed"

    @property
    def message(self) -> str:
        error = self.task.error_message
        elapsed = humanize.naturaldelta(self.task.time_elapsed)
        return (
            f"Task '{self.task.description}' failed with error '{error}' "
            f"after {elapsed}."
        )


class Completed(TaskEvent):
    """A Completed event occurs when a task completes successfully."""

    title = "Task Completed"

    @property
    def message(self) -> str:
        elapsed = humanize.naturaldelta(self.task.time_elapsed)
        return (
            f"Task '{self.task.description}' completed successfully! "
            f"It ran for {elapsed}."
        )


class Created(TaskEvent):
    """A Created event occurs when a new task is created."""

    title = "Task Created"

    @property
    def message(self) -> str:
        return f"Task '{self.task.description}' was created."


class Attempted(TaskEvent):
    """An Attempted event occurs when an attempt fails and a new attempt beings."""

    title = "Attempt Failed"

    @property
    def message(self) -> str:
        n = self.task._status["attempt"]
        return f"Task '{self.task.description}' attempt {n - 1} failed."


class Cancelled(TaskEvent):
    """A Cancelled event occurs when a task is cancelled by the user."""

    title = "Task Cancelled"

    @property
    def message(self) -> str:
        return f"Task '{self.task.description}' was cancelled."


class Started(TaskEvent):
    """A Started event occurs when a ready task begins running."""

    title = "Task Started"

    @property
    def message(self) -> str:
        return f"Task '{self.task.description}' has started processing."


EVENT_TYPES = {
    "error": Error,
    "failed": Failed,
    "completed": Completed,
    "created": Created,
    "attempted": Attempted,
    "cancelled": Cancelled,
    "started": Started,
}


def get_event(name: str) -> type[Event]:
    """Get an event by name."""
    return EVENT_TYPES[name.lower()]  # type: ignore
