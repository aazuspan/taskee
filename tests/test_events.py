from unittest.mock import patch

from taskee.events import (
    Attempted,
    Cancelled,
    Completed,
    Created,
    Error,
    Failed,
    Started,
    get_event,
)

from .mock_tasks import MockTask


def test_failed_event(initialized_taskee, mock_task_list):
    """A Failed event should include the task description in the message."""
    mock_task_list[0].update(new_state="FAILED", error_message="whoops")

    with patch("ee.data.getTaskList") as getTaskList:
        getTaskList.return_value = [task._status for task in mock_task_list]
        initialized_taskee._update(watch_for=[])

    event = initialized_taskee.manager.events[0]
    assert isinstance(event, Failed)

    expected_msg = "'mock_ready_task' failed with error 'whoops'"
    assert expected_msg in event.message


def test_completed_event(initialized_taskee, mock_task_list):
    """A Completed event should include the task description in the message."""
    mock_task_list[0].update(new_state="COMPLETED")

    with patch("ee.data.getTaskList") as getTaskList:
        getTaskList.return_value = [task._status for task in mock_task_list]
        initialized_taskee._update(watch_for=[])

    event = initialized_taskee.manager.events[0]
    assert isinstance(event, Completed)

    expected_msg = "'mock_ready_task' completed successfully"
    assert expected_msg in event.message


def test_created_event(initialized_taskee, mock_task_list):
    """A Created event should include the task description in the message."""
    mock_task_list.append(MockTask(state="READY", description="mock_created_task"))

    with patch("ee.data.getTaskList") as getTaskList:
        getTaskList.return_value = [task._status for task in mock_task_list]
        initialized_taskee._update(watch_for=[])

    event = initialized_taskee.manager.events[0]
    assert isinstance(event, Created)

    expected_msg = "'mock_created_task' was created"
    assert expected_msg in event.message


def test_attempted_event(initialized_taskee, mock_task_list):
    """An Attempted event should include the number of attempts in the message."""
    mock_task_list[1].update(retry=True)

    with patch("ee.data.getTaskList") as getTaskList:
        getTaskList.return_value = [task._status for task in mock_task_list]
        initialized_taskee._update(watch_for=[])

    event = initialized_taskee.manager.events[0]
    assert isinstance(event, Attempted)

    expected_msg = "attempt 1 failed"
    assert expected_msg in event.message


def test_cancelled_event(initialized_taskee, mock_task_list):
    """A Cancelled event should include the task description in the message."""
    mock_task_list[0].update(new_state="CANCELLED")

    with patch("ee.data.getTaskList") as getTaskList:
        getTaskList.return_value = [task._status for task in mock_task_list]
        initialized_taskee._update(watch_for=[])

    event = initialized_taskee.manager.events[0]
    assert isinstance(event, Cancelled)

    expected_msg = "'mock_ready_task' was cancelled"
    assert expected_msg in event.message


def test_started_event(initialized_taskee, mock_task_list):
    """A Started event should include the task description in the message."""
    mock_task_list[0].update(new_state="RUNNING")

    with patch("ee.data.getTaskList") as getTaskList:
        getTaskList.return_value = [task._status for task in mock_task_list]
        initialized_taskee._update(watch_for=[])

    event = initialized_taskee.manager.events[0]
    assert isinstance(event, Started)

    expected_msg = "'mock_ready_task' has started processing"
    assert expected_msg in event.message


def test_get_event():
    """The get_event function should return the correct event type."""
    assert get_event("created") == Created
    assert get_event("failed") == Failed
    assert get_event("completed") == Completed
    assert get_event("attempted") == Attempted
    assert get_event("cancelled") == Cancelled
    assert get_event("started") == Started
    assert get_event("error") == Error
