from unittest.mock import patch

from taskee.events import (
    AttemptedEvent,
    CancelledEvent,
    CompletedEvent,
    CreatedEvent,
    FailedEvent,
    StartedEvent,
)

from .mock_operation import MockOperation


def test_failed_event(mock_taskee, mock_pending_task):
    """A Failed event should include the task description in the message."""
    mock_pending_task.update(state="FAILED", error_message="whoops")

    with patch("ee.data.listOperations") as listOperations:
        listOperations.return_value = [mock_pending_task.model_dump()]
        event = mock_taskee.update()[0]

    assert isinstance(event, FailedEvent)

    expected_msg = "'mock_pending_task' failed after a moment with error 'whoops'"
    assert expected_msg in event.message


def test_succeeded_event(mock_taskee, mock_pending_task):
    """A Completed event should include the task description in the message."""
    mock_pending_task.update(state="SUCCEEDED")

    with patch("ee.data.listOperations") as listOperations:
        listOperations.return_value = [mock_pending_task.model_dump()]
        event = mock_taskee.update()[0]

    assert isinstance(event, CompletedEvent)

    expected_msg = "'mock_pending_task' completed successfully"
    assert expected_msg in event.message


def test_created_event(mock_taskee):
    """A Created event should include the task description in the message."""
    new_task = MockOperation(state="PENDING", description="mock_new_task")

    with patch("ee.data.listOperations") as listOperations:
        listOperations.return_value = [new_task.model_dump()]
        event = mock_taskee.update()[0]

    assert isinstance(event, CreatedEvent)

    expected_msg = "'mock_new_task' was created"
    assert expected_msg in event.message


def test_created_and_completed_event(mock_taskee):
    """A new task should only register the latest event."""
    new_task = MockOperation(state="PENDING", description="mock_new_task")
    new_task.update(state="SUCCEEDED")

    with patch("ee.data.listOperations") as listOperations:
        listOperations.return_value = [new_task.model_dump()]
        event = mock_taskee.update()[0]

    assert isinstance(event, CompletedEvent)

    expected_msg = "'mock_new_task' completed successfully"
    assert expected_msg in event.message


def test_attempted_event(mock_taskee, mock_running_task):
    """An Attempted event should include the number of attempts in the message."""
    mock_running_task.update(retry=True)

    with patch("ee.data.listOperations") as listOperations:
        listOperations.return_value = [mock_running_task.model_dump()]
        event = mock_taskee.update()[0]

    assert isinstance(event, AttemptedEvent)

    assert "attempt 1 failed" in event.message


def test_cancelled_event(mock_taskee, mock_running_task):
    """A Cancelled event should include the task description in the message."""
    mock_running_task.update(state="CANCELLED")

    with patch("ee.data.listOperations") as listOperations:
        listOperations.return_value = [mock_running_task.model_dump()]
        event = mock_taskee.update()[0]

    assert isinstance(event, CancelledEvent)

    expected_msg = "'mock_running_task' was cancelled"
    assert expected_msg in event.message


def test_started_event(mock_taskee, mock_pending_task):
    """A Started event should include the task description in the message."""
    mock_pending_task.update(state="RUNNING")

    with patch("ee.data.listOperations") as listOperations:
        listOperations.return_value = [mock_pending_task.model_dump()]
        event = mock_taskee.update()[0]

    assert isinstance(event, StartedEvent)

    expected_msg = "'mock_pending_task' has started processing"
    assert expected_msg in event.message


def test_succeeded_event_with_null_eecus(mock_taskee):
    """Some tasks will succeed and not report EECUs (e.g. asset ingestion)."""
    mock_succeeded_ingestion = MockOperation(
        "SUCCEEDED",
        description="mock_ingestion",
    )

    with patch("ee.data.listOperations") as listOperations:
        listOperations.return_value = [mock_succeeded_ingestion.model_dump()]
        event = mock_taskee.update()[0]

    assert "'mock_ingestion' completed successfully" in event.message
    assert "used 0 EECU-seconds" in event.message
