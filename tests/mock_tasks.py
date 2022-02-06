import datetime
import random
import string
from typing import Dict

from taskee import events, states
from taskee.tasks import Task
from taskee.utils import _datetime_to_millis, _millis_to_datetime


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
        """Initialize a mock task by passing in specific parameters. These will be used to
        build a status dictionary matching those created by Earth Engine.

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
            The timestamp in UTC milliseconds of the last task update. If none is provided,
            the current time will be used.
        time_since_creation_ms : int, default 600000
            The amount of time, in milliseconds, since the task was created. Defaults to
            10 minutes.
        started_after_ms : int, default 60000
            The delay between the creation time and the starting time. Defaults to 1 minute.
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

        self.id = self.random_id() if id is None else id
        self.description = description
        self.event = events.Created(self)

        update_timestamp_ms = (
            _datetime_to_millis(datetime.datetime.now())
            if update_timestamp_ms is None
            else update_timestamp_ms
        )
        creation_timestamp_ms = (
            _datetime_to_millis(datetime.datetime.now()) - time_since_creation_ms
        )
        start_timestamp_ms = creation_timestamp_ms + started_after_ms

        self.time_created = _millis_to_datetime(creation_timestamp_ms)

        self._status = self.build_status(
            state,
            task_type,
            updated_time=update_timestamp_ms,
            created_time=creation_timestamp_ms,
            started_time=start_timestamp_ms,
            error_message=error_message,
        )

    @staticmethod
    def random_id(length=24):
        """Create a random alphanumeric ID that is roughly consistent with an Earth Engine task ID."""
        chars = string.ascii_uppercase + string.digits
        return "".join([random.choice(chars) for i in range(length)])

    def build_status(
        self,
        state: str,
        task_type: str,
        updated_time: int,
        created_time: int,
        started_time: int,
        error_message: str,
    ) -> Dict:
        """Build an Earth Engine-compatible status dictionary from initialized parameters."""
        # These parameters are common to all task types
        base_obj = {
            "state": state,
            "description": self.description,
            "creation_timestamp_ms": created_time,
            "update_timestamp_ms": updated_time,
            "start_timestamp_ms": started_time,
            "task_type": task_type,
            "id": self.id,
            "name": f"projects/earthengine-legacy/operations/{self.id}",
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

    def get_next_status(
        self, new_state: str = None, retry: bool = False, time_delta: int = 0
    ):
        """Build the next status dictionary based on requested changes to the task's attributes.
        As much as possible, new attributes are validated to ensure they could occur in normal usage.
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

        new_status.update(update_attrs)

        return new_status
