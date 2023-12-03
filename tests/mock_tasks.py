from __future__ import annotations

import random
import string
from datetime import datetime

from taskee import states
from taskee.tasks import Task
from taskee.utils import _datetime_to_millis


class MockTask(Task):
    def __init__(
        self,
        state: str,
        *,
        description: str = "mock_task",
        id: str = None,
        task_type: str = "EXPORT_IMAGE",
        update_timestamp_ms: int = None,
        time_since_creation_ms=600_000,
        started_after_ms: int = 60_000,
        error_message: str = "error message",
    ):
        """Initialize a mock task by passing in specific parameters. These will be used
        to build a status dictionary matching those created by Earth Engine.

        Parameters
        ----------
        state : int
            The current state of the task.
        description : str, default mock_task
            The name of the task.
        id : str, optional
            A unique task ID. If none is provided, a random ID will be generated.
        task_type : str, default EXPORT_IMAGE
            The type of task, as defined by Earth Engine.
        update_timestamp_ms : int, optional
            The timestamp in UTC milliseconds of the last task update. If none is
            provided, the current time will be used.
        time_since_creation_ms : int, default 600000
            The amount of time, in milliseconds, since the task was created. Defaults to
            10 minutes.
        started_after_ms : int, default 60000
            The delay between the creation time and the starting time. Defaults to 1
            minute.
        error_message : str, default "error message"
            The error message to assign to Failed and Cancelled tasks. The argument will
            be ignored for other task types.

        Returns
        -------
        MockTask
            A Task that is comparable with one created by Earth Engine.
        """
        if state not in states.ALL:
            raise AttributeError(f"Invalid state: {state}. Choice from {states.ALL}.")

        now_ms = _datetime_to_millis(datetime.now())
        update_timestamp_ms = update_timestamp_ms if update_timestamp_ms else now_ms
        creation_timestamp_ms = now_ms - time_since_creation_ms
        start_timestamp_ms = creation_timestamp_ms + started_after_ms

        task_dict = _build_task_dict(
            id=id if id else self.random_id(),
            state=state,
            description=description,
            task_type=task_type,
            updated_time=update_timestamp_ms,
            created_time=creation_timestamp_ms,
            started_time=start_timestamp_ms,
            error_message=error_message,
        )

        super().__init__(task_dict)

    @staticmethod
    def random_id(length=24):
        """Create a random alphanumeric ID that is roughly consistent with an Earth
        Engine task ID."""
        chars = string.ascii_uppercase + string.digits
        return "".join([random.choice(chars) for i in range(length)])

    def update(
        self,
        new_state: str = None,
        *,
        retry: bool = False,
        time_delta: int = 0,
        error_message: str = None,
    ):
        """Update the task with the new attributes.

        As much as possible, new attributes are validated to ensure they could occur in
        normal usage.
        """
        last_state = self._status["state"]

        if last_state in ["FAILED", "CANCELLED", "COMPLETED"]:
            raise ValueError("Tasks that have finished cannot be updated.")

        new_status = self._status.copy()

        update_attrs = {}

        if new_state:
            if new_state not in [
                states.RUNNING,
                states.CANCELLED,
                states.COMPLETED,
                states.FAILED,
            ]:
                raise ValueError("Invalid new state.")
            if new_state == states.RUNNING and last_state != states.READY:
                raise ValueError("Only READY tasks can change to RUNNING.")
            update_attrs["state"] = new_state
        if retry is True:
            if last_state != states.RUNNING or new_state not in [None, states.RUNNING]:
                raise ValueError("Only running tasks can be retried.")
            update_attrs["attempt"] = self._status["attempt"] + 1
        if time_delta:
            if time_delta < 0:
                raise ValueError("Time deltas must be positive.")
            new_update_time = self._status["update_timestamp_ms"] + time_delta
            update_attrs["update_timestamp_ms"] = new_update_time
        if error_message:
            if new_state != states.FAILED:
                raise ValueError("Only failed tasks can have an error message.")
            update_attrs["error_message"] = error_message

        new_status.update(update_attrs)

        super().update(new_status)


def _build_task_dict(
    *,
    id: str,
    state: str,
    description: str,
    task_type: str,
    updated_time: int,
    created_time: int,
    started_time: int,
    error_message: str,
) -> dict:
    """Build an Earth Engine-compatible status dictionary from parameters."""
    # These parameters are common to all task types
    base_obj = {
        "state": state,
        "description": description,
        "creation_timestamp_ms": created_time,
        "update_timestamp_ms": updated_time,
        "start_timestamp_ms": started_time,
        "task_type": task_type,
        "id": id,
        "name": f"projects/earthengine-legacy/operations/{id}",
    }

    if state == states.COMPLETED:
        base_obj["destination_uris"] = ["https://drive.google.com/"]
    elif state in [states.FAILED, states.CANCELLED]:
        base_obj["error_message"] = error_message
    elif state == states.READY:
        base_obj["start_timestamp_ms"] = 0

    if state in [
        states.COMPLETED,
        states.FAILED,
        states.CANCELLED,
        states.RUNNING,
        states.CANCEL_REQUESTED,
    ]:
        base_obj["attempt"] = 1

    return base_obj
