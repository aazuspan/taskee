from abc import ABC, abstractmethod
from typing import Dict, List, Set, Type, Union

from taskee.utils import _get_subclasses, _list_subclasses


class Event(ABC):
    title = "Generic Event"

    def __init__(self, task):
        self.task = task

    @property
    @abstractmethod
    def message(self):
        pass


class Failed(Event):
    """A Failed event occurs when a task fails to complete."""

    title = "Task Failed"

    @property
    def message(self):
        error = self.task.status["error_message"]
        return f"Task '{self.task.description}' failed with error '{error}'"


class Completed(Event):
    """A Completed event occurs when a task completes successfully."""

    title = "Task Completed"

    @property
    def message(self):
        return f"Task '{self.task.description}' completed successfully!"


class Created(Event):
    """A Created event occurs when a new task is created."""

    title = "Task Created"

    @property
    def message(self):
        return f"Task '{self.task.description}' was created."


class Attempted(Event):
    """An Attempted event occurs when an attempt fails and a new attempt beings."""

    title = "Attempt Failed"

    @property
    def message(self):
        n = self.task.status["attempt"]
        return f"Task '{self.task.description}' attempt {n - 1} failed."


class Cancelled(Event):
    """A Cancelled event occurs when a task is cancelled by the user."""

    title = "Task Cancelled"

    @property
    def message(self):
        return f"Task '{self.task.description}' was cancelled."


class Started(Event):
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
    return _list_subclasses(Event)


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
    return _get_subclasses(names, Event)
