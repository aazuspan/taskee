import datetime

from taskee import events, states, tasks
from taskee.utils import _datetime_to_millis
from tests.mock_tasks import MockTask


def test_task_failed_event():
    """Test that a Failed event is created when any active task switches states to FAILED"""
    for state in states.ACTIVE:
        task = MockTask(state)
        task.update(task.get_next_status("FAILED"))
        assert isinstance(task.event, events.Failed)


def test_task_completed_event():
    """Test that a Completed event is created when any active task switches states to COMPLETED"""
    for state in states.ACTIVE:
        task = MockTask(state)
        task.update(task.get_next_status("COMPLETED"))
        assert isinstance(task.event, events.Completed)


def test_task_created_event():
    """Test that a Created event is created when any task is initialized"""
    for state in states.ALL:
        task = MockTask(state)
        assert isinstance(task.event, events.Created)


def test_task_attempted_event():
    """Test that an Attempted event is created when a running task is retried"""
    task = MockTask("RUNNING")
    task.update(task.get_next_status(retry=True))
    assert isinstance(task.event, events.Attempted)


def test_task_cancelled_event():
    """Test that a Cancelled event is created when any active task switches states to CANCELLED"""
    for state in states.ACTIVE:
        task = MockTask(state)
        task.update(task.get_next_status("CANCELLED"))
        assert isinstance(task.event, events.Cancelled)


def test_task_started_event():
    """Test that a Started event is created when a task switches states from READY to RUNNING"""
    task = MockTask("READY")
    task.update(task.get_next_status("RUNNING"))
    assert isinstance(task.event, events.Started)


def test_time_elapsed():
    """Test that time elapsed between creation and update is correctly calculated."""
    task = MockTask("RUNNING", time_since_creation_ms=10_000)
    assert task.time_elapsed.seconds * 1_000 == 10_000


def test_time_updated():
    """Test that a task's time_updated is correctly retrieved"""
    dt = datetime.datetime(year=1970, month=1, day=1)
    ms = _datetime_to_millis(dt)
    task = MockTask("READY", update_timestamp_ms=ms)
    assert task.time_updated == dt


def test_error_message():
    """Test that a task's error message is correctly retrieved."""
    err = "This is an error message."
    task = MockTask("FAILED", error_message=err)
    assert task.error_message == err


def test_state():
    """Test that a task's state is correctly retrieved."""
    task = MockTask("CANCEL_REQUESTED")
    assert task.state == states.CANCEL_REQUESTED


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
