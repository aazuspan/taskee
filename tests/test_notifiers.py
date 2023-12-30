import configparser
from unittest.mock import patch

import pytest

from taskee.notifiers import Pushbullet
from taskee.taskee import Taskee


def test_native_notifier(mock_taskee, mock_running_task, mock_native_notifier):
    """Test that the Native notifier attempts to notify."""
    mock_running_task.update(state="FAILED", error_message="whoops")

    with patch("ee.data.listOperations") as listOperations:
        listOperations.return_value = [mock_running_task.model_dump()]
        mock_taskee.update()

    mock_taskee.dispatch()

    assert mock_native_notifier.application_name == "taskee"
    assert mock_native_notifier.title == "Task Failed"
    expected_msg = "'mock_running_task' failed after 10 minutes with error 'whoops'"
    assert expected_msg in mock_native_notifier.message
    mock_native_notifier.send.assert_called_once()


def test_pushbullet_notifier(mock_taskee, mock_running_task, mock_pushbullet_notifier):
    """Test that Pushbullet attempts to notify."""
    mock_running_task.update(state="FAILED", error_message="uh oh")

    with patch("ee.data.listOperations") as listOperations:
        listOperations.return_value = [mock_running_task.model_dump()]
        mock_taskee.update()

    mock_taskee.dispatch()

    mock_pushbullet_notifier.push_note.assert_called_once()
    title, msg = mock_pushbullet_notifier.push_note.call_args[0]
    assert title == "Task Failed"
    assert "'mock_running_task' failed after 10 minutes with error 'uh oh'" in msg


def test_pushbullet_uninstalled():
    """An ImportError should be raised if the pushbullet package is not installed."""
    with patch("ee.data.listOperations") as listOperations, patch.dict(
        "sys.modules", {"pushbullet": None}
    ):
        listOperations.return_value = []
        with pytest.raises(ImportError, match="pip install pushbullet.py"):
            Taskee(notifiers=["pushbullet"])


def test_initialize_pushbullet_with_key():
    """Test that Pushbullet is initialized with a key."""
    assert Pushbullet()


@pytest.mark.no_config()
def test_initialize_pushbullet_without_key(mock_config_path):
    """Test that Pushbullet prompts and stores a new key when none is found."""
    fake_key = "new_fake_key_12345"

    with patch("taskee.notifiers.pushbullet.Prompt.ask") as ask:
        # Provide a new key to the prompt
        ask.return_value = fake_key
        Pushbullet()
        ask.assert_called_once()

    config = configparser.ConfigParser()
    config.read(mock_config_path)
    assert config["Pushbullet"]["api_key"] == fake_key
