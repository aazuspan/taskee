from typing import Tuple

import click  # type: ignore

from taskee import events
from taskee.cli.commands import dashboard, log, tasks, test
from taskee.notifiers import notifier
from taskee.taskee import Taskee

version = "0.0.1"
modes = {"log": log.start, "dashboard": dashboard.start}


@click.group()
@click.version_option(version, prog_name="taskee")
def taskee() -> None:
    """Monitor Earth Engine tasks and send notifications when they change states.

    \b
    Examples
        $ taskee test
        $ taskee tasks
        $ taskee start log
        $ taskee start dashboard failed completed -n pushbullet -i 0.5
    """
    return


@taskee.command(name="start")
@click.argument("mode", nargs=1, type=click.Choice(choices=modes.keys()))
@click.argument(
    "watch_for",
    nargs=-1,
    type=click.Choice(
        choices=list(events.list_events().keys()) + ["all"], case_sensitive=False
    ),
)
@click.option(
    "notifiers",
    "-n",
    "--notifier",
    default=("native",),
    multiple=True,
    type=click.Choice(
        list(notifier.list_notifiers().keys()) + ["all"], case_sensitive=False
    ),
    help="One or more notifiers to run.",
)
@click.option(
    "interval_mins",
    "-i",
    "--interval_mins",
    default=5.0,
    help="Minutes between queries to Earth Engine for task updates.",
)
def start_command(
    mode: str,
    watch_for: Tuple[str, ...],
    notifiers: Tuple[str, ...],
    interval_mins: float,
) -> None:
    """Start running the notification system. Select a mode (default native)
    and one or more event types to watch for (or all).

    \b
    Examples
        $ taskee start dashboard failed completed -n pushbullet -i 5
        $ taskee start log all
    """
    if len(watch_for) == 0:
        watch_for = ("completed", "failed", "error")

    mode_func = modes[mode]
    t = Taskee(notifiers=notifiers)

    try:
        mode_func(t, watch_for=watch_for, interval_minutes=interval_mins)
    except Exception as e:
        if "error" in [event.lower() for event in watch_for]:
            event = events.Error()
            t.dispatcher.notify(event.title, event.message)
        raise e
    except KeyboardInterrupt:
        return


@taskee.command(name="tasks")
def tasks_command() -> None:
    """Display a table of current Earth Engine tasks."""
    tasks.tasks()


@taskee.command(name="test", short_help="Send test notifications.")
@click.option(
    "notifiers",
    "-n",
    "--notifier",
    default=("native",),
    multiple=True,
    type=click.Choice(
        list(notifier.list_notifiers().keys()) + ["all"], case_sensitive=False
    ),
    help="One or more notifiers to test.",
)
def test_command(notifiers: Tuple[str, ...]) -> None:
    """
    Send test notifications to selected notifiers (default native).

    \b
    Examples
        $ taskee test -n all
    """
    test.test(notifiers)


if __name__ == "__main__":
    taskee()
