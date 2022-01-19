from abc import ABC, abstractmethod
from typing import Dict, List, Set, Type, Union

from requests.structures import CaseInsensitiveDict

from taskee.states import CANCELLED, COMPLETED, FAILED, READY, RUNNING
from taskee.utils import _get_case_insensitive_close_matches


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
    """Return a case-insensitive dictionary of all available Event classes."""
    return CaseInsensitiveDict({cls.__name__: cls for cls in Event.__subclasses__()})


def get_events(names: List[Union[str, Type[Event]]]) -> Set[Type[Event]]:
    """Take a list of events by name or class and return a list of the corresponding classes."""
    if names == "all":
        return set(list_events().values())

    # Allow single values to be passed
    names = [names] if not isinstance(names, (list, tuple)) else names
    options = list_events()
    keys = list(options.keys())

    selected = []

    for name in names:
        if isinstance(name, str):
            try:
                selected.append(options[name])
            except KeyError:
                close_matches = _get_case_insensitive_close_matches(name, keys, n=3)
                hint = (
                    " Close matches: {}.".format(close_matches) if close_matches else ""
                )

                raise AttributeError(
                    '"{}" is not a supported event type. Choose from {}.{}'.format(
                        name, keys, hint
                    )
                )
        else:
            try:
                if issubclass(name, Event):
                    selected.append(name)
            except TypeError:
                raise AttributeError(
                    f"Events must be strings or subclasses of Event, not {type(name)}."
                )

    return set(selected)


def parse_event(
    task, old_state: str, new_state: str, old_attempts: int = 0, new_attempts: int = 0
) -> Event:
    """Take details from a Task and return a corresponding Event object."""
    event = None

    if old_state != new_state:
        if new_state == RUNNING:
            event = Started(task)
        elif new_state == CANCELLED:
            event = Cancelled(task)
        elif new_state == FAILED:
            event = Failed(task)
        elif new_state == COMPLETED:
            event = Completed(task)

    if old_attempts != new_attempts:
        event = Attempted(task)

    return event
