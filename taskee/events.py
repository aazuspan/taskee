import datetime
from abc import ABC, abstractmethod
from typing import Dict, List, Set, Type, Union

import humanize

from taskee import utils


class Event(ABC):
    title = "Generic Event"

    def __init__(self):
        self.time = datetime.datetime.now(tz=datetime.timezone.utc)

    @property
    @abstractmethod
    def message(self):
        pass


class TaskEvent(Event, ABC):
    """A Task Event is a type of event originating from an Earth Engine task."""

    def __init__(self, task):
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
    def message(self):
        error = self.task.error_message
        elapsed = humanize.naturaldelta(self.task.time_elapsed)
        return f"Task '{self.task.description}' failed with error '{error}' after {elapsed}."


class Completed(TaskEvent):
    """A Completed event occurs when a task completes successfully."""

    title = "Task Completed"

    @property
    def message(self):
        elapsed = humanize.naturaldelta(self.task.time_elapsed)
        return f"Task '{self.task.description}' completed successfully! It ran for {elapsed}."


class Created(TaskEvent):
    """A Created event occurs when a new task is created."""

    title = "Task Created"

    @property
    def message(self):
        return f"Task '{self.task.description}' was created."


class Attempted(TaskEvent):
    """An Attempted event occurs when an attempt fails and a new attempt beings."""

    title = "Attempt Failed"

    @property
    def message(self):
        n = self.task._status["attempt"]
        return f"Task '{self.task.description}' attempt {n - 1} failed."


class Cancelled(TaskEvent):
    """A Cancelled event occurs when a task is cancelled by the user."""

    title = "Task Cancelled"

    @property
    def message(self):
        return f"Task '{self.task.description}' was cancelled."


class Started(TaskEvent):
    """A Started event occurs when a ready task begins running."""

    title = "Task Started"

    @property
    def message(self):
        return f"Task '{self.task.description}' has started processing."


def list_events() -> Dict[str, Type["Event"]]:
    """List all Event subclasses. Return as a dictionary mapping the subclass name to the
    class.

    Returns
    -------
    Dict[str, Type[Event]]
        A dictionary mapping the Event name to the class.
    """
    return utils._list_subclasses(Event)


def get_events(names: List[Union[str, Type[Event]]]) -> Set[Type[Event]]:
    """Retrieve a set of subclasses of Event.

    Parameters
    ----------
    names : List[Union[str, Type[Event]]]
        A list of names or classes of Events to retrieve.

    Returns
    -------
    Set[Type[Any]]
        A set of Events.
    """
    return utils._get_subclasses(names, Event)
