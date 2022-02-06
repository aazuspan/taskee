import datetime
from typing import Dict, List, Tuple, Union

from taskee import events, states
from taskee.utils import _millis_to_datetime


class Task:
    """Wrapper class around a persistent Earth Engine task."""

    def __init__(self, obj: Dict):
        self._status = obj
        self.id = obj["id"]
        self.description = obj["description"]
        self.time_created = _millis_to_datetime(obj["creation_timestamp_ms"])
        self.event: Union[events.Event, None] = events.Created(self)

    def __str__(self) -> str:
        return f"<{self.id}>: {self.description} [{self.state}]"

    @property
    def error_message(self) -> str:
        if self.state == states.FAILED:
            return self._status["error_message"]
        return ""

    @property
    def state(self) -> str:
        """Get the last state of the task."""
        return self._status["state"]

    @property
    def time_updated(self) -> datetime.datetime:
        return _millis_to_datetime(self._status["update_timestamp_ms"])

    @property
    def time_elapsed(self) -> datetime.timedelta:
        """Return the time elapsed between the task creation and the last update."""
        return self.time_updated - self.time_created

    def update(self, new_status: Dict) -> None:
        """Update the status of the task and record any changed attributes as events."""
        self.event = self._parse_event(new_status)
        self._status = new_status

    def _parse_event(self, new_status: Dict) -> Union[None, events.Event]:
        """Take the updated status dictionary and identify if an Event occured."""
        event: Union[None, events.Event] = None

        old_state = self._status["state"]
        new_state = new_status["state"]

        try:
            old_attempt, new_attempt = self._status["attempt"], new_status["attempt"]
        # During some states, tasks will not have an attempt value
        except KeyError:
            old_attempt, new_attempt = 0, 0

        if old_state != new_state:
            if new_state == states.RUNNING:
                event = events.Started(self)
            elif new_state == states.CANCELLED:
                event = events.Cancelled(self)
            elif new_state == states.FAILED:
                event = events.Failed(self)
            elif new_state == states.COMPLETED:
                event = events.Completed(self)

        if old_attempt != new_attempt:
            event = events.Attempted(self)

        return event


class TaskManager:
    """Manager class for handling all Earth Engine tasks."""

    def __init__(self, tasks: List[Dict]):
        self._tasks: Dict = {}
        self.update(tasks)

        # The initial set of tasks should not register Created events.
        # There's a better way to handle this, but for now I'm just manually suppressing those events.
        for task in self._tasks.values():
            task.event = None

    @property
    def events(self) -> Tuple[events.Event, ...]:
        """Retrieve active events from all tasks, sorted by time."""
        task_events = [task.event for task in self.tasks if task.event is not None]
        if len(task_events) > 1:
            task_events = sorted(task_events, key=lambda event: event.time)
        return tuple(task_events)

    @property
    def tasks(self) -> Tuple[Task, ...]:
        return tuple(self._tasks.values())

    def update(self, task_list: List[Dict]) -> None:
        """Update all tasks. Existing tasks will be updated and new tasks will be added to the manager."""
        current_tasks = self._tasks.keys()

        for task in task_list:
            task_id = task["id"]

            # Store new tasks
            if task_id not in current_tasks:
                new_task = Task(task)
                self._tasks[task_id] = new_task

            # Update existing tasks
            else:
                self._tasks[task_id].update(task)

        self._sort_tasks()

    def _sort_tasks(self) -> None:
        """Sort the tasks by placing active tasks first and then sorting by their creation date."""
        self._tasks = {
            k: v
            for k, v in sorted(
                self._tasks.items(),
                key=lambda x: [x[1].state in states.ACTIVE, x[1].time_created],
                reverse=True,
            )
        }
