from taskee import events, states
from tests.mock_tasks import MockTask


def test_task_failed_event():
    """Test that a Failed event is created when any active task switches states to FAILED"""
    for state in states.ACTIVE:
        task = MockTask(state)
        task.set_next_status("FAILED")
        assert isinstance(task.event, events.Failed)


def test_task_completed_event():
    """Test that a Completed event is created when any active task switches states to COMPLETED"""
    for state in states.ACTIVE:
        task = MockTask(state)
        task.set_next_status("COMPLETED")
        assert isinstance(task.event, events.Completed)


def test_task_created_event():
    """Test that a Created event is created when any task is initialized"""
    for state in states.ALL:
        task = MockTask(state)
        assert isinstance(task.event, events.Created)


def test_task_attempted_event():
    """Test that an Attempted event is created when a running task is retried"""
    task = MockTask("RUNNING")
    task.set_next_status(retry=True)
    assert isinstance(task.event, events.Attempted)


def test_task_cancelled_event():
    """Test that a Cancelled event is created when any active task switches states to CANCELLED"""
    for state in states.ACTIVE:
        task = MockTask(state)
        task.set_next_status("CANCELLED")
        assert isinstance(task.event, events.Cancelled)


def test_task_started_event():
    """Test that a Started event is created when a task switches states from READY to RUNNING"""
    task = MockTask("READY")
    task.set_next_status("RUNNING")
    assert isinstance(task.event, events.Started)
