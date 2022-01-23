from typing import Dict, List

from taskee import events, states
import datetime
from taskee.utils import _millis_to_datetime

class Task:
    """Wrapper class around a persistent Earth Engine task."""

    def __init__(self, obj: Dict):
        self._status = obj
        self.id = obj["id"]
        self.description = obj["description"]
        self.time_created = _millis_to_datetime(obj["creation_timestamp_ms"])
        self.event = events.Created(self)

    def __str__(self) -> str:
        return f"<{self.id}>: {self.description} [{self.state}]"

    @property
    def state(self) -> str:
        """Get the last state of the task."""
        return self._status["state"]

    @property
    def last_update(self) -> datetime.datetime:
        return _millis_to_datetime(self._status["update_timestamp_ms"])

    @property
    def time_elapsed(self) -> datetime.datetime:
        """Return the time elapsed between the task creation and the last update."""
        return self.last_update - self.time_created

    def update(self, new_status: Dict) -> None:
        """Update the status of the task and record any changed attributes as events."""
        self.event = self._parse_event(new_status)
        self._status = new_status

    def _parse_event(self, new_status: Dict) -> events.Event:
        """Take the updated status dictionary and identify if an Event occured."""
        event = None

        old_state = self._status["state"]
        new_state = new_status["state"]

        try:
            old_attempt, new_attempt = self._status["attempt"], new_status["attempt"]
        # During some states, tasks will not have an attempt value
        except KeyError:
            old_attempt, new_attempt = 0

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

    def __init__(self, tasks: Dict):
        self.tasks = {}
        self.update(tasks)

    def update(self, task_list: List[Dict]) -> None:
        """Update all tasks. Existing tasks will be updated and new tasks will be added to the manager."""
        current_tasks = self.tasks.keys()

        for task in task_list:
            task_id = task["id"]

            # Store new tasks
            if task_id not in current_tasks:
                new_task = Task(task)
                self.tasks[task_id] = new_task

            # Update existing tasks
            else:
                self.tasks[task_id].update(task)
