from unittest.mock import patch

from taskee import events

from .mock_operation import MockOperation


def test_taskee_registers_init_tasks(mock_taskee):
    """Taskee should store all tasks found during initialization."""
    # Tasks are defined by the `mock_task_list`
    assert len(mock_taskee.tasks) == 3
    assert len(mock_taskee.active_tasks) == 2
    assert len(mock_taskee.event_queue) == 0


def test_taskee_stores_event_queue(mock_taskee, mock_pending_task, mock_running_task):
    """Taskee should store events in a queue until dispatched."""
    mock_pending_task.update(state="SUCCEEDED")
    mock_running_task.update(state="FAILED")

    with patch("ee.data.listOperations") as listOperations:
        listOperations.return_value = [
            mock_pending_task.model_dump(),
            mock_running_task.model_dump(),
        ]
        mock_taskee.update()

    assert len(mock_taskee.event_queue) == 2
    mock_taskee.dispatch()

    assert len(mock_taskee.event_queue) == 0


def test_taskee_sorts_tasks(mock_taskee):
    """Test that tasks are sorted by activity, then creation time."""
    new_active_task = MockOperation(
        state="PENDING", description="mock_new_active_task", time_since_creation_ms=0
    )
    old_active_task = MockOperation(
        state="RUNNING",
        description="mock_old_active_task",
        time_since_creation_ms=1_000_000,
    )
    new_inactive_task = MockOperation(
        state="FAILED", description="mock_new_task", time_since_creation_ms=0
    )
    old_inactive_task = MockOperation(
        state="SUCCEEDED", description="mock_old_task", time_since_creation_ms=1_000_000
    )

    # Note that these are not in the correct sorted order
    tasks = [old_inactive_task, new_active_task, new_inactive_task, old_active_task]

    with patch("ee.data.listOperations") as listOperations:
        listOperations.return_value = [t.model_dump() for t in tasks]
        mock_taskee.update()

    assert mock_taskee.tasks == (
        new_active_task,
        old_active_task,
        new_inactive_task,
        old_inactive_task,
    )


def test_taskee_ignores_unchanged_tasks(mock_taskee, mock_task_list):
    """Taskee should not register events for unchanged tasks."""
    assert len(mock_taskee.tasks) == 3

    with patch("ee.data.listOperations") as listOperations:
        listOperations.return_value = [task.model_dump() for task in mock_task_list]
        mock_taskee.update()

    assert len(mock_taskee.tasks) == 3
    assert len(mock_taskee.event_queue) == 0


def test_taskee_only_notifies_watched_tasks(
    mock_taskee, mock_pending_task, mock_running_task, mock_native_notifier
):
    """Taskee should only notify for tasks that are being watched."""
    mock_taskee.watch_for = [events.FailedEvent, events.CreatedEvent]
    mock_pending_task.update(state="SUCCEEDED")
    mock_running_task.update(state="FAILED")
    new_task = MockOperation(state="PENDING", description="mock_new_task")

    with patch("ee.data.listOperations") as listOperations:
        listOperations.return_value = [
            mock_pending_task.model_dump(),
            mock_running_task.model_dump(),
            new_task.model_dump(),
        ]
        mock_taskee.update()

    # All events should register
    assert len(mock_taskee.event_queue) == 3
    mock_taskee.dispatch()

    # Only the watched-for events should notify
    assert mock_native_notifier.send.call_count == 2


def test_taskee_reports_remaining(
    mock_taskee, mock_pending_task, mock_running_task, mock_native_notifier
):
    """A completed event should report the number of remaining tasks."""
    mock_taskee.watch_for = [events.CompletedEvent]
    mock_pending_task.update(state="SUCCEEDED")

    with patch("ee.data.listOperations") as listOperations:
        listOperations.return_value = [
            mock_pending_task.model_dump(),
            mock_running_task.model_dump(),
        ]
        mock_taskee.update()

    mock_taskee.dispatch()

    expected_msg = "(1 tasks remaining)"
    assert expected_msg in mock_native_notifier.message
