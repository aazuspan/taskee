import datetime

import pytest

from taskee import events, states, tasks
from taskee.utils import _datetime_to_millis

from .mock_tasks import MockTask


@pytest.mark.parametrize("state", states.ACTIVE)
def test_task_failed_event(state):
    """A Failed event should trigger when an active task switches to FAILED."""
    task = MockTask(state)
    task.update("FAILED")
    assert isinstance(task.event, events.Failed)


@pytest.mark.parametrize("state", states.ACTIVE)
def test_task_completed_event(state):
    """A Completed event should trigger when an active task switches to COMPLETED."""
    task = MockTask(state)
    task.update("COMPLETED")
    assert isinstance(task.event, events.Completed)


@pytest.mark.parametrize("state", states.ALL)
def test_task_created_event(state):
    """A Created event should trigger when a task is initialized."""
    task = MockTask(state)
    assert isinstance(task.event, events.Created)


def test_task_attempted_event():
    """An Attempted event should trigger when a task is retried."""
    task = MockTask("RUNNING")
    task.update(retry=True)
    assert isinstance(task.event, events.Attempted)


@pytest.mark.parametrize("state", states.ACTIVE)
def test_task_cancelled_event(state):
    """A Cancelled event should trigger when an active task switches to CANCELLED."""
    task = MockTask(state)
    task.update("CANCELLED")
    assert isinstance(task.event, events.Cancelled)


def test_task_started_event():
    """A Started event should trigger when a task switches from READY to RUNNING."""
    task = MockTask("READY")
    task.update("RUNNING")
    assert isinstance(task.event, events.Started)


def test_time_elapsed():
    """A task's time_elapsed should be the difference between creation and update."""
    task = MockTask("RUNNING", time_since_creation_ms=10_000)
    assert task.time_elapsed.seconds * 1_000 == 10_000


def test_time_updated():
    """A task's time_updated should be the time of its last update."""
    dt = datetime.datetime(year=1999, month=1, day=1)
    ms = _datetime_to_millis(dt)
    task = MockTask("READY", update_timestamp_ms=ms)
    assert task.time_updated == dt


def test_error_message():
    """A failed task should store its error message."""
    err = "This is an error message."
    task = MockTask("FAILED", error_message=err)
    assert task.error_message == err

    task = MockTask("RUNNING")
    assert task.error_message == ""


def test_state():
    """Test that a task's state is correctly retrieved."""
    task = MockTask("CANCEL_REQUESTED")
    assert task.state == states.CANCEL_REQUESTED


def test_task_str():
    """Test that a task's string representation is correct."""
    task = MockTask(id="1234", state="RUNNING", description="test_task")
    assert str(task) == "<1234>: test_task [RUNNING]"


def test_task_sorting():
    """Tasks are auto-sorted by the task manager, with active tasks first and then by
    creation time. Test that tasks are sorted as expected.
    """
    t = [
        MockTask(
            "COMPLETED", description="old inactive", time_since_creation_ms=5
        )._status,
        MockTask(
            "RUNNING", description="older active", time_since_creation_ms=20
        )._status,
        MockTask(
            "FAILED", description="new inactive", time_since_creation_ms=0
        )._status,
        MockTask(
            "READY", description="newer active", time_since_creation_ms=15
        )._status,
        MockTask(
            "CANCEL_REQUESTED",
            description="very old inactive",
            time_since_creation_ms=100,
        )._status,
    ]
    tm = tasks.TaskManager(t)
    correct_order = [
        "newer active",
        "older active",
        "new inactive",
        "old inactive",
        "very old inactive",
    ]
    actual_order = [task.description for task in tm.tasks]
    assert actual_order == correct_order
