from __future__ import annotations

import rich_click as click  # type: ignore
from rich.status import Status

from taskee.cli.commands import dashboard, log, tasks, test
from taskee.events import EVENT_TYPES, Error
from taskee.notifiers import NOTIFIER_TYPES
from taskee.taskee import Taskee

click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.USE_MARKDOWN = True

modes = {"log": log.start, "dashboard": dashboard.start}


@click.group()
@click.version_option()
def taskee() -> None:
    """
    Monitor Earth Engine tasks and send notifications when they change states.  
    \
    
    **Examples**

    ```bash
    $ taskee test
    $ taskee tasks
    $ taskee start log
    $ taskee start dashboard failed completed -n pushbullet -i 0.5
    ```
    """
    return


@taskee.command(name="start", short_help="Start running the notification system.")
@click.argument("mode", nargs=1, type=click.Choice(choices=modes.keys()))
@click.argument(
    "watch_for",
    nargs=-1,
    type=click.Choice(choices=list(EVENT_TYPES.keys()) + ["all"], case_sensitive=False),
)
@click.option(
    "notifiers",
    "-n",
    "--notifier",
    default=("native",),
    multiple=True,
    type=click.Choice(list(NOTIFIER_TYPES.keys()) + ["all"], case_sensitive=False),
    help="One or more notifiers to run (or all).",
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
    watch_for: tuple[str, ...],
    notifiers: tuple[str, ...],
    interval_mins: float,
) -> None:
    """
    Start running the notification system. Select a mode
    and one or more event types to watch for (or all).
    \
    
    **Examples**

    ```bash
    $ taskee start dashboard failed completed -n pushbullet -i 5
    $ taskee start log all
    ```
    """
    if "all" in notifiers:
        notifiers = tuple(NOTIFIER_TYPES.keys())
    if "all" in watch_for:
        watch_for = tuple(EVENT_TYPES.keys())
    elif len(watch_for) == 0:
        watch_for = ("completed", "failed", "error")

    mode_func = modes[mode]
    t = Taskee(notifiers=notifiers)

    try:
        mode_func(t, watch_for=watch_for, interval_minutes=interval_mins)
    except Exception as e:
        if "error" in [event.lower() for event in watch_for]:
            event = Error()
            t.dispatcher.notify(event.title, event.message)
        raise e
    except KeyboardInterrupt:
        return


@taskee.command(name="tasks")
def tasks_command() -> None:
    """Display a table of current Earth Engine tasks."""
    with Status("Retrieving tasks from Earth Engine...", spinner="bouncingBar"):
        t = Taskee(notifiers=tuple())
        tasks.tasks(t)


@taskee.command(name="test", short_help="Send test notifications.")
@click.option(
    "notifiers",
    "-n",
    "--notifier",
    default=("native",),
    multiple=True,
    type=click.Choice(list(NOTIFIER_TYPES.keys()) + ["all"], case_sensitive=False),
    help="One or more notifiers to test (or all).",
)
def test_command(notifiers: tuple[str, ...]) -> None:
    """
    Send test notifications to selected notifiers (default native).
    \
    
    **Examples**

    ```bash
    $ taskee test -n all
    ```
    """
    if "all" in notifiers:
        notifiers = tuple(NOTIFIER_TYPES.keys())

    test.test(notifiers)


if __name__ == "__main__":
    taskee()
