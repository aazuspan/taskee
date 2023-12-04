from unittest.mock import patch

import pytest
from click.testing import CliRunner

from taskee.cli.cli import taskee


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.mark.parametrize("mode", ["log", "dashboard"])
@pytest.mark.parametrize("watch_for", [[], ["completed"], ["all"]])
@pytest.mark.parametrize(
    "notifiers",
    [["native"], ["pushbullet"], ["all"]],
    ids=["native", "pushbullet", "all"],
)
def test_start_command(mode, notifiers, watch_for, runner, mock_task_list):
    with patch("ee.data.getTaskList") as getTaskList:
        getTaskList.return_value = [task._status for task in mock_task_list]

        # Start will run indefinitely, so we'll kill it after the first iteration
        with patch("time.sleep", side_effect=KeyboardInterrupt):
            args = [mode] + watch_for + ["--notifier", *notifiers]
            result = runner.invoke(taskee, ["start"] + args)

    assert result.exit_code == 0, result.output


def test_tasks_command(runner, mock_task_list):
    with patch("ee.data.getTaskList") as getTaskList:
        getTaskList.return_value = [task._status for task in mock_task_list]
        result = runner.invoke(taskee, ["tasks"])

    assert result.exit_code == 0
    assert "mock_ready_task" in result.output
    getTaskList.assert_called_once_with()


def test_tasks_command_with_key(
    runner, tmpdir, mock_task_list, mock_service_account_credentials
):
    key_file = tmpdir / "key.json"
    key_file.write_text("mock_key_file", "utf-8")

    with patch("ee.data.getTaskList") as getTaskList:
        getTaskList.return_value = [task._status for task in mock_task_list]
        result = runner.invoke(taskee, ["tasks", "--private-key", key_file])

    assert result.exit_code == 0
    assert "mock_ready_task" in result.output
    mock_service_account_credentials.assert_called_once_with(
        email=None, key_file=key_file
    )

    getTaskList.assert_called_once()


@pytest.mark.parametrize("notifiers", [["native"], ["pushbullet"], ["all"]])
def test_test_command(
    notifiers, runner, mock_native_notifier, mock_pushbullet_notifier
):
    result = runner.invoke(taskee, ["test", "--notifier"] + notifiers)

    assert result.exit_code == 0

    if "native" in notifiers or "all" in notifiers:
        mock_native_notifier.send.assert_called_once()
    if "pushbullet" in notifiers or "all" in notifiers:
        mock_pushbullet_notifier.push_note.assert_called_once()
