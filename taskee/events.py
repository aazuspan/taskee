from abc import ABC, abstractmethod

from taskee.states import CANCELLED, COMPLETED, FAILED, READY, RUNNING


class Event(ABC):
    title = "Generic Task"

    def __init__(self, task):
        self.task = task

    @property
    @abstractmethod
    def message(self):
        pass


class Failed(Event):
    title = "Task Failed"

    @property
    def message(self):
        error = self.task.status["error_message"]
        return f"Task '{self.task.description}' failed with error '{error}'"


class Completed(Event):
    title = "Task Completed"

    @property
    def message(self):
        return f"Task '{self.task.description}' completed successfully!"


class New(Event):
    title = "New Task"

    @property
    def message(self):
        return f"Task '{self.task.description}' was created."


class Attempt(Event):
    title = "New Attempt"

    @property
    def message(self):
        n = self.task.status["attempt"]
        return f"Task '{self.task.description}' attempts changed to {n}."


class Cancelled(Event):
    title = "Task Cancelled"

    @property
    def message(self):
        return f"Task '{self.task.description}' was cancelled."


class Started(Event):
    title = "Task Started"

    @property
    def message(self):
        return f"Task '{self.task.description}' has started processing."


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
        event = Attempt(task)

    return event
