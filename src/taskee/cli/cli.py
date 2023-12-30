from __future__ import annotations

import ee
import rich_click as click  # type: ignore
from rich.status import Status

from taskee.cli.commands import dashboard, log, tasks, test
from taskee.events import ErrorEvent, EventEnum
from taskee.notifiers import NotifierEnum
from taskee.taskee import Taskee

click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.USE_MARKDOWN = True

modes = {"log": log.start, "dashboard": dashboard.start}

PRIVATE_KEY_OPTION = click.option(
    "private_key",
    "-k",
    "--private-key",
    default=None,
    type=click.Path(exists=True, dir_okay=False),
    help="Optional path to private key file for Earth Engine authentication.",
)

NOTIFIERS_OPTION = click.option(
    "notifiers",
    "-n",
    "--notifier",
    default=("native",),
    multiple=True,
    type=click.Choice(
        list(NotifierEnum.__members__.keys()) + ["all"], case_sensitive=False
    ),
    help="The notifier to run (or all).",
)

INTERVAL_OPTION = click.option(
    "interval_mins",
    "-i",
    "--interval-mins",
    default=5.0,
    help="Minutes between queries to Earth Engine for task updates.",
)

WATCH_FOR_ARG = click.argument(
    "watch_for",
    nargs=-1,
    type=click.Choice(
        choices=list(EventEnum.__members__.keys()) + ["all"], case_sensitive=False
    ),
)


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
@WATCH_FOR_ARG
@NOTIFIERS_OPTION
@INTERVAL_OPTION
@PRIVATE_KEY_OPTION
def start_command(
    mode: str,
    watch_for: tuple[str, ...],
    notifiers: tuple[str, ...],
    interval_mins: float,
    private_key: str | None,
) -> None:
    """
    Start running the notification system. Select a mode
    and one or more event types to watch for (or all).
    \
    
    **Examples**

    ```bash
    $ taskee start dashboard failed completed -n pushbullet -i 5
    $ taskee start log all
    $ taskee start log --private-key .private-key.json
    ```
    """
    if "all" in notifiers:
        notifiers = tuple(NotifierEnum.__members__.keys())
    if "all" in watch_for:
        watch_for = tuple(EventEnum.__members__.keys())
    elif len(watch_for) == 0:
        watch_for = ("completed", "failed", "error")

    if private_key:
        credentials = ee.ServiceAccountCredentials(email=None, key_file=private_key)
    else:
        credentials = "persistent"

    mode_func = modes[mode]
    t = Taskee(notifiers=notifiers, watch_for=watch_for, credentials=credentials)

    try:
        mode_func(t, interval_minutes=interval_mins)
    except Exception as e:
        if "error" in [event.lower() for event in watch_for]:
            t.event_queue.append(ErrorEvent())
            t.dispatch()
        raise e
    except KeyboardInterrupt:
        return


@taskee.command(name="tasks")
@click.option("max_tasks", "-m", "--max-tasks", default=30, help="Max tasks displayed.")
@PRIVATE_KEY_OPTION
def tasks_command(max_tasks: int, private_key: str | None) -> None:
    """Display a table of current Earth Engine tasks."""
    if private_key:
        credentials = ee.ServiceAccountCredentials(email=None, key_file=private_key)
    else:
        credentials = "persistent"

    with Status("Retrieving tasks from Earth Engine...", spinner="bouncingBar"):
        t = Taskee(notifiers=tuple(), credentials=credentials)
        tasks.tasks(t.tasks, max_tasks=max_tasks)


@taskee.command(name="test", short_help="Send test notifications.")
@NOTIFIERS_OPTION
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
        notifiers = tuple(NotifierEnum.__members__.keys())

    notifier_instances = tuple(NotifierEnum[notifier].value() for notifier in notifiers)
    test.test(notifier_instances)


if __name__ == "__main__":
    taskee()
