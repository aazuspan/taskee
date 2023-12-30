import configparser
from unittest.mock import MagicMock, patch

import pushbullet
import pytest

from taskee.taskee import Taskee

from .mock_operation import MockOperation


@pytest.fixture()
def mock_pending_task():
    return MockOperation(state="PENDING", description="mock_pending_task")


@pytest.fixture()
def mock_running_task():
    return MockOperation(state="RUNNING", description="mock_running_task")


@pytest.fixture()
def mock_succeeded_task():
    return MockOperation(state="SUCCEEDED", description="mock_succeeded_task")


@pytest.fixture()
def mock_task_list(mock_pending_task, mock_running_task, mock_succeeded_task):
    return [
        mock_pending_task,
        mock_running_task,
        mock_succeeded_task,
    ]


@pytest.fixture(autouse=True)
def _mock_ee_initialize():
    """Mock the ee_initialize function."""
    with patch("ee.Initialize"):
        yield


@pytest.fixture()
def mock_service_account_credentials():
    """Mock the ee.ServiceAccountCredentials class."""
    with patch("ee.ServiceAccountCredentials") as ServiceAccountCredentials:
        yield ServiceAccountCredentials


@pytest.fixture()
def mock_taskee(mock_task_list) -> Taskee:
    """A Taskee instance initialized with mock tasks."""
    with patch("ee.data.listOperations") as listOperations:
        listOperations.return_value = [task.model_dump() for task in mock_task_list]
        return Taskee(notifiers=["native", "pushbullet"])


@pytest.fixture(autouse=True)
def mock_native_notifier():
    """Mock the native notifier."""
    with patch("notifypy.Notify") as Notify:
        yield Notify.return_value


@pytest.fixture(autouse=True)
def mock_pushbullet_notifier():
    """Override Pushbullet instantiation to pass unless the API key is empty."""
    mock_pb = MagicMock()

    def initialize_mock_pushbullet(key: str):
        if not key:
            raise pushbullet.errors.InvalidKeyError
        return mock_pb

    with patch("pushbullet.Pushbullet", side_effect=initialize_mock_pushbullet):
        yield mock_pb


@pytest.fixture(autouse=True)
def mock_config_path(tmpdir):
    """Mock the config path where credentials are stored."""
    config_path = tmpdir / "config.ini"
    with patch("taskee.notifiers.pushbullet.CONFIG_PATH", config_path):
        yield config_path


@pytest.fixture(autouse=True)
def _mock_config(mock_config_path, request):
    """Patch in a config file with a fake Pushbullet API key."""
    # Skip this fixture if the test is marked with `no_config`. This will mean there is
    # no config file at the mocked path.
    if "no_config" in request.keywords:
        return

    fake_key = "fake_key_12345"

    config = configparser.ConfigParser()
    config["Pushbullet"] = {"api_key": fake_key}
    with open(mock_config_path, "w") as f:
        config.write(f)
