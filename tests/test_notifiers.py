import configparser
from unittest.mock import Mock, patch

import pushbullet
import pytest

from taskee.events import Failed
from taskee.notifiers.pushbullet import initialize_pushbullet
from taskee.taskee import Taskee


def MockPushbullet(key: str):
    """Instantiate a mock Pushbullet object. Only fail if the API key is empty."""
    if not key:
        raise pushbullet.errors.InvalidKeyError

    return Mock()


def test_native_notifier(mock_task_list):
    """Test that the Native notifier attempts to notify."""
    with patch("ee.data.getTaskList") as getTaskList, patch(
        "notifypy.Notify"
    ) as Notify:
        notification = Notify.return_value

        getTaskList.return_value = [task._status for task in mock_task_list]
        initialized_taskee = Taskee(notifiers=["native"])

        mock_task_list[0].update(new_state="FAILED", error_message="whoops")
        getTaskList.return_value = [task._status for task in mock_task_list]
        initialized_taskee._update(watch_for=[Failed])

        assert notification.application_name == "taskee"
        assert notification.title == "Task Failed"
        assert "'mock_ready_task' failed with error 'whoops'" in notification.message
        notification.send.assert_called_once()


def test_pushbullet_notifier(mock_task_list):
    """Test that Pushbullet attempts to notify."""
    with patch("ee.data.getTaskList") as getTaskList, patch(
        "taskee.notifiers.pushbullet.initialize_pushbullet"
    ) as initialize_pushbullet:
        mock_pb = Mock()
        initialize_pushbullet.return_value = mock_pb

        getTaskList.return_value = [task._status for task in mock_task_list]
        initialized_taskee = Taskee(notifiers=["pushbullet"])

        mock_task_list[0].update(new_state="FAILED", error_message="whoops")
        getTaskList.return_value = [task._status for task in mock_task_list]
        initialized_taskee._update(watch_for=[Failed])

        mock_pb.push_note.assert_called_once()
        call_args = mock_pb.push_note.call_args[0]
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


def test_initialize_pushbullet_with_key(tmp_path):
    """Test that Pushbullet is initialized with a key."""
    config_path = tmp_path / "config.ini"
    fake_key = "fake_key_12345"

    config = configparser.ConfigParser()
    config["Pushbullet"] = {"api_key": fake_key}
    with open(config_path, "w") as f:
        config.write(f)

    with patch("taskee.notifiers.pushbullet.config_path", config_path), patch(
        "pushbullet.Pushbullet", side_effect=MockPushbullet
    ):
        assert initialize_pushbullet()


def test_initialize_pushbullet_without_key(tmp_path):
    """Test that Pushbullet prompts and stores a new key when none is found."""
    config_path = tmp_path / "config.ini"
    fake_key = "new_fake_key_12345"

    with patch("taskee.notifiers.pushbullet.config_path", config_path), patch(
        "pushbullet.Pushbullet", side_effect=MockPushbullet
    ), patch("taskee.notifiers.pushbullet.Prompt.ask") as ask:
        ask.return_value = fake_key
        initialize_pushbullet()
        ask.assert_called_once()

    config = configparser.ConfigParser()
    config.read(config_path)
    assert config["Pushbullet"]["api_key"] == fake_key
