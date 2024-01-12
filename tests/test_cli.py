from time import sleep
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from taskee.cli.cli import taskee

from .mock_operation import MockOperation

# Parameterize over the --notifier options
PARAMETRIZE_NOTIFIER = pytest.mark.parametrize(
    "notifier",
    ["native", "pushbullet", "all"],
)

PARAMETRIZE_WATCH_FOR = pytest.mark.parametrize(
    "watch_for",
    [[], ["completed"], ["created", "failed"], ["all"]],
    ids=["watch_none", "watch_one", "watch_two", "watch_all"],
)


@pytest.fixture()
def cli():
    return CliRunner(echo_stdin=True)


@pytest.fixture()
def _keyboardinterrupt_on_sleep():
    """Patch `time.sleep` to raise KeyboardInterrupt, killing long-running commands."""
    with patch("time.sleep", side_effect=KeyboardInterrupt):
        yield


@pytest.fixture()
def _runtimeerror_on_sleep():
    """Patch `time.sleep` to raise RuntimeError, killing long-running commands."""
    with patch("time.sleep", side_effect=RuntimeError):
        yield


@PARAMETRIZE_WATCH_FOR
@PARAMETRIZE_NOTIFIER
def test_start_log_command(
    notifier, watch_for, cli, mock_pending_task, mock_running_task
):
    """The `start log` command should run and log events.

    This test is pretty complicated since the CLI runs an indefinite loop, and in order
    to get an output we need to allow it to run for a few iterations and then interrupt
    it after events have triggered. This is based on timing and may be fragile under
    some circumstances. If it turns out to be unreliable, we may need to rework this.
    """
    # Sleep time must be long enough for the CLI to register an update, but not so long
    # that it slows down tests. 0.1 - 0.01 seconds seems to work well.
    SLEEP_TIME = 0.01
    # The update interval must be less than the sleep time to ensure we get an update.
    UPDATE_INTERVAL = (SLEEP_TIME / 60) * 0.1

    update_count = 0

    def update_or_interrupt(*_):
        """
        On the first pass, update tasks to trigger an event.
        On the second pass, trigger a KeyboardInterrupt to stop execution.
        """
        nonlocal update_count
        if update_count > 0:
            raise KeyboardInterrupt

        mock_pending_task.update(state="RUNNING")
        mock_running_task.update(state="SUCCEEDED")
        listOperations.return_value = [
            mock_pending_task.model_dump(),
            mock_running_task.model_dump(),
        ]
        update_count += 1
        sleep(SLEEP_TIME)

    with patch("ee.data.listOperations") as listOperations, patch(
        "taskee.cli.commands.log.time.sleep", side_effect=update_or_interrupt
    ), patch("taskee.cli.commands.log.logger.info") as info:
        args = ["--interval-mins", UPDATE_INTERVAL, "--notifier", notifier]
        result = cli.invoke(taskee, ["start", "log", *watch_for, *args])

    calls = info.call_args_list
    assert len(calls) == 2, result.output

    assert "'mock_pending_task' has started processing" in calls[0][0][0]
    # Only completed tasks should show the remaining count
    assert "tasks remaining" not in calls[0][0][0]

    # Unwatched tasks should be dimmed
    if "all" not in watch_for and "start" not in watch_for:
        assert "[dim]" in calls[0][0][0]
    else:
        assert "[dim]" not in calls[0][0][0]

    assert "'mock_running_task' completed successfully" in calls[1][0][0]
    assert "1 tasks remaining" in calls[1][0][0]

    # The CLI catches the keyboard interrupt, so we should a zero exit code
    assert result.exit_code == 0, result.output


@PARAMETRIZE_WATCH_FOR
@PARAMETRIZE_NOTIFIER
def test_start_dashboard_command(
    notifier, watch_for, cli, mock_pending_task, mock_running_task
):
    """The `start dashboard` command should run and log events.

    This test is pretty complicated since the CLI runs an indefinite loop, and in order
    to get an output we need to allow it to run for a few iterations and then interrupt
    it after events have triggered. This is based on timing and may be fragile under
    some circumstances. If it turns out to be unreliable, we may need to rework this.
    """
    # Sleep time must be long enough for the CLI to register an update, but not so long
    # that it slows down tests. 0.1 - 0.01 seconds seems to work well.
    SLEEP_TIME = 0.01
    # The update interval must be less than the sleep time to ensure we get an update.
    UPDATE_INTERVAL = (SLEEP_TIME / 60) * 0.1

    update_count = 0

    def update_or_interrupt(*_):
        """
        On the first pass, update tasks to trigger an event.
        On the second pass, trigger a KeyboardInterrupt to stop execution.
        """
        nonlocal update_count
        if update_count > 0:
            raise KeyboardInterrupt

        mock_pending_task.update(state="RUNNING")
        mock_running_task.update(state="SUCCEEDED")
        listOperations.return_value = [
            mock_pending_task.model_dump(),
            mock_running_task.model_dump(),
        ]
        update_count += 1
        sleep(SLEEP_TIME)

    with patch("ee.data.listOperations") as listOperations, patch(
        "taskee.cli.commands.log.time.sleep", side_effect=update_or_interrupt
    ):
        args = ["--interval-mins", UPDATE_INTERVAL, "--notifier", notifier]
        result = cli.invoke(taskee, ["start", "dashboard", *watch_for, *args])

    assert result.exit_code == 0, result.output

    # UI Elements
    assert "Next update in" in result.output
    assert "Press CTRL + C to exit" in result.output

    # Events
    assert "'mock_pending_task' has started" in result.output
    assert "'mock_running_task' completed" in result.output
    assert "now" in result.output

    # Tasks
    assert "RUNNING" in result.output
    assert "SUCCEEDED" in result.output


@pytest.mark.parametrize("mode", ["log", "dashboard"])
@pytest.mark.usefixtures("_keyboardinterrupt_on_sleep")
def test_start_command_with_key(
    mode,
    cli,
    tmpdir,
    mock_task_list,
    mock_service_account_credentials,
):
    """The `start` command should accept and use service credentials."""
    key_file = tmpdir / "key.json"
    key_file.write_text("mock_key_file", "utf-8")

    with patch("ee.data.listOperations") as listOperations:
        listOperations.return_value = [task.model_dump() for task in mock_task_list]

        args = [mode, "--private-key", key_file]
        result = cli.invoke(taskee, ["start"] + args)

    assert result.exit_code == 0, result.output
    mock_service_account_credentials.assert_called_once_with(
        email=None, key_file=key_file
    )


@pytest.mark.parametrize("mode", ["log", "dashboard"])
@pytest.mark.usefixtures("_runtimeerror_on_sleep")
def test_start_command_handles_crash(mode, cli, mock_native_notifier):
    """The `start` command should send an error notification on crash."""
    with patch("ee.data.listOperations") as listOperations:
        listOperations.return_value = []
        result = cli.invoke(taskee, ["start", mode, "--notifier", "all"])

    assert result.exit_code == 1, result.output
    mock_native_notifier.send.assert_called_once()
    assert mock_native_notifier.title == "Oops!"
    assert "taskee needs to be restarted" in mock_native_notifier.message


def test_tasks_command(cli, mock_task_list):
    """The `tasks` command should list tasks."""
    with patch("ee.data.listOperations") as listOperations:
        listOperations.return_value = [task.model_dump() for task in mock_task_list]
        result = cli.invoke(taskee, ["tasks"])

    assert result.exit_code == 0, result.output
    assert "Earth Engine Tasks" in result.output
    assert "PENDING" in result.output
    assert "mock_pending_task" in result.output
    assert "mock_running_task" in result.output
    assert "mock_succeeded_task" in result.output
    assert "10 minutes ago" in result.output
    assert "42" in result.output


def test_tasks_command_with_key(
    cli, tmpdir, mock_task_list, mock_service_account_credentials
):
    """The `tasks` command should accept and use service credentials."""
    key_file = tmpdir / "key.json"
    key_file.write_text("mock_key_file", "utf-8")

    with patch("ee.data.listOperations") as listOperations:
        listOperations.return_value = [task.model_dump() for task in mock_task_list]
        result = cli.invoke(taskee, ["tasks", "--private-key", key_file])

    assert result.exit_code == 0
    assert "mock_pending_task" in result.output
    mock_service_account_credentials.assert_called_once_with(
        email=None, key_file=key_file
    )


def test_tasks_truncates(cli, mock_task_list):
    """The `task` command should hide tasks beyond `--max-tasks`."""
    with patch("ee.data.listOperations") as listOperations:
        listOperations.return_value = [task.model_dump() for task in mock_task_list]
        result = cli.invoke(taskee, ["tasks", "--max-tasks", 2])

    assert result.exit_code == 0, result.output
    assert "mock_pending_task" in result.output
    assert "mock_running_task" in result.output
    assert "..." in result.output
    assert "mock_succeeded_task" not in result.output

def test_tasks_unknown_state(cli):
    """The `task` command should handle unknown task states."""
    unexpected_op = MockOperation(description="unexpected_task", state="Ddf!sD?sdfl")

    with patch("ee.data.listOperations") as listOperations:
        listOperations.return_value = [unexpected_op.model_dump()]
        result = cli.invoke(taskee, ["tasks"])

    assert result.exit_code == 0, result.output
    assert "unexpected_task" in result.output
    assert "UNKNOWN" in result.output


@PARAMETRIZE_NOTIFIER
def test_test_command(notifier, cli, mock_native_notifier, mock_pushbullet_notifier):
    """The `test` command should send notifications."""
    result = cli.invoke(taskee, ["test", "--notifier", notifier])

    assert result.exit_code == 0

    if notifier == "native" or notifier == "all":
        mock_native_notifier.send.assert_called_once()
    if notifier == "pushbullet" or notifier == "all":
        mock_pushbullet_notifier.push_note.assert_called_once()
