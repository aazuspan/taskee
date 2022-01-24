from abc import ABC, abstractmethod
from typing import Dict, List, Set, Type, Union

import humanize

from taskee import colors, utils


class Event(ABC):
    title = "Generic Event"

    @property
    @abstractmethod
    def message(self):
        pass


class TaskEvent(Event, ABC):
    """A Task Event is a type of event originating from an Earth Engine task."""

    def __init__(self, task):
        self.task = task


class Error(Event):
    """An Error event occurs when taskee crashes."""

    title = "Oops!"
    message = "Something went wrong and taskee needs to be restarted."
    _color = colors.COLOR_ERROR


class Failed(TaskEvent):
    """A Failed event occurs when a task fails to complete."""

    title = "Task Failed"
    _color = colors.COLOR_ERROR

    @property
    def message(self):
        error = self.task.error_message
        elapsed = humanize.naturaldelta(self.task.time_elapsed)
        return f"Task '{self.task.description}' failed with error '{error}' after {elapsed}."


class Completed(TaskEvent):
    """A Completed event occurs when a task completes successfully."""

    title = "Task Completed"
    _color = colors.COLOR_SUCCESS

    @property
    def message(self):
        elapsed = humanize.naturaldelta(self.task.time_elapsed)
        return f"Task '{self.task.description}' completed successfully! It ran for {elapsed}."


class Created(TaskEvent):
    """A Created event occurs when a new task is created."""

    title = "Task Created"
    _color = colors.COLOR_INFO

    @property
    def message(self):
        return f"Task '{self.task.description}' was created."


class Attempted(TaskEvent):
    """An Attempted event occurs when an attempt fails and a new attempt beings."""

    title = "Attempt Failed"
    _color = colors.COLOR_ERROR

    @property
    def message(self):
        n = self.task.status["attempt"]
        return f"Task '{self.task.description}' attempt {n - 1} failed."


class Cancelled(TaskEvent):
    """A Cancelled event occurs when a task is cancelled by the user."""

    title = "Task Cancelled"
    _color = colors.COLOR_ERROR

    @property
    def message(self):
        return f"Task '{self.task.description}' was cancelled."


class Started(TaskEvent):
    """A Started event occurs when a ready task begins running."""

    title = "Task Started"
    _color = colors.COLOR_INFO

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
