from __future__ import annotations

import datetime
import logging
import time

from rich.logging import RichHandler
from rich.status import Status

from taskee import events, states
from taskee.cli.styles import get_style
from taskee.taskee import Taskee

logging.basicConfig(
    format="%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[RichHandler(show_level=True, show_path=False, markup=True)],
)

logger = logging.getLogger("taskee")


def start(
    t: Taskee,
    watch_for: tuple[str, ...] = ("error", "completed", "failed"),
    interval_minutes: float = 5.0,
) -> None:
    """Run an indefinite logger. This handles scheduling of Earth Engine updates and
    logs events as they occur.
    """
    logger.setLevel("INFO")

    last_checked = time.time()
    interval_seconds = interval_minutes * 60.0

    watch_events = events.get_events(watch_for)

    while True:
        elapsed = time.time() - last_checked
        active_tasks = t.manager.active_tasks

        if elapsed > interval_seconds:
            with Status("[yellow]Updating tasks...", spinner="bouncingBar"):
                new_events = t._update(watch_events)
                last_checked = time.time()
                remaining_tasks = t.manager.active_tasks

            if len(new_events) > 1:
                new_events = tuple(sorted(new_events, key=lambda event: event.time))

            for event in new_events:
                message = event.message
                if (
                    isinstance(event, events.TaskEvent)
                    and event.task.state in states.FINISHED
                ):
                    message += f" [dim]({len(remaining_tasks)} tasks remaining)[/]"

                muted_style = "[dim]" if event.__class__ not in watch_events else ""
                style = get_style(event.__class__)
                logger.info(
                    f"[{style.color}]{style.emoji} {event.__class__.__name__}[/]:"
                    f" {muted_style}{message}"
                )

        else:
            delta = datetime.timedelta(seconds=interval_seconds - elapsed)
            next_update = datetime.datetime.now() + delta
            next_update_msg = (
                f"[yellow]Next update at {next_update:%H:%M:%S}... "
                f"({len(active_tasks)} active tasks)"
            )

            with Status(next_update_msg, spinner="bouncingBar"):
                time.sleep(delta.total_seconds())
