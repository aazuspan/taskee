import configparser
from unittest.mock import patch

import pytest

from taskee.events import Failed
from taskee.notifiers import Pushbullet
from taskee.taskee import Taskee


@pytest.fixture()
def mock_config_path(tmpdir):
    """Mock the config path where credentials are stored."""
    config_path = tmpdir / "config.ini"
    with patch("taskee.notifiers.pushbullet.config_path", config_path):
        yield config_path


def test_native_notifier(mock_task_list, mock_native_notifier):
    """Test that the Native notifier attempts to notify."""
    with patch("ee.data.getTaskList") as getTaskList:
        notification = mock_native_notifier

        getTaskList.return_value = [task._status for task in mock_task_list]
        initialized_taskee = Taskee(notifiers=["native"])

        mock_task_list[0].update(new_state="FAILED", error_message="whoops")
        getTaskList.return_value = [task._status for task in mock_task_list]
        initialized_taskee._update(watch_for=[Failed])

        assert notification.application_name == "taskee"
        assert notification.title == "Task Failed"
        assert "'mock_ready_task' failed with error 'whoops'" in notification.message
        notification.send.assert_called_once()


def test_pushbullet_notifier(mock_task_list, mock_pushbullet_notifier):
    """Test that Pushbullet attempts to notify."""
    with patch("ee.data.getTaskList") as getTaskList:
        getTaskList.return_value = [task._status for task in mock_task_list]
        initialized_taskee = Taskee(notifiers=["pushbullet"])

        mock_task_list[0].update(new_state="FAILED", error_message="whoops")
        getTaskList.return_value = [task._status for task in mock_task_list]
        initialized_taskee._update(watch_for=[Failed])

        mock_pushbullet_notifier.push_note.assert_called_once()
        call_args = mock_pushbullet_notifier.push_note.call_args[0]
        assert call_args[0] == "Task Failed"
        assert "'mock_ready_task' failed with error 'whoops'" in call_args[1]


def test_pushbullet_uninstalled():
    """An ImportError should be raised if the pushbullet package is not installed."""
    with patch("ee.data.getTaskList") as getTaskList, patch.dict(
        "sys.modules", {"pushbullet": None}
    ):
        getTaskList.return_value = []
        with pytest.raises(ImportError, match="pip install pushbullet.py"):
            Taskee(notifiers=["pushbullet"])


def test_initialize_pushbullet_with_key(mock_config_path):
    """Test that Pushbullet is initialized with a key."""
    fake_key = "fake_key_12345"

    config = configparser.ConfigParser()
    config["Pushbullet"] = {"api_key": fake_key}
    with open(mock_config_path, "w") as f:
        config.write(f)

    assert Pushbullet()


def test_initialize_pushbullet_without_key(tmp_path, mock_config_path):
    """Test that Pushbullet prompts and stores a new key when none is found."""
    fake_key = "new_fake_key_12345"

    with patch("taskee.notifiers.pushbullet.Prompt.ask") as ask:
        ask.return_value = fake_key
        Pushbullet()
        ask.assert_called_once()

    config = configparser.ConfigParser()
    config.read(mock_config_path)
    assert config["Pushbullet"]["api_key"] == fake_key
