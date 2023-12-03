from unittest.mock import patch

import pytest

from taskee.taskee import Taskee

from .mock_tasks import MockTask


@pytest.fixture(autouse=True)
def _mock_ee_initialize():
    """Mock the ee_initialize function."""
    with patch("ee.Initialize"):
        yield


@pytest.fixture()
def mock_task_list():
    return [
        MockTask(state="READY", description="mock_ready_task"),
        MockTask(state="RUNNING", description="mock_running_task"),
        MockTask(state="COMPLETED", description="mock_completed_task"),
        MockTask(state="CANCEL_REQUESTED", description="mock_cancel_requested_task"),
        MockTask(state="CANCELLED", description="mock_cancelled_task"),
        MockTask(state="FAILED", description="mock_failed_task"),
    ]


@pytest.fixture()
def initialized_taskee(mock_task_list) -> Taskee:
    """A Taskee instance initialized with mock tasks."""
    with patch("ee.data.getTaskList") as getTaskList:
        getTaskList.return_value = [task._status for task in mock_task_list]
        return Taskee(notifiers=[])
