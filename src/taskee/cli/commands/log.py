from __future__ import annotations

import datetime
import logging
import time

from rich.logging import RichHandler
from rich.status import Status

from taskee.cli.styles import get_style
from taskee.operation import FINISHED_OPERATION_STATES
from taskee.taskee import Taskee

logging.basicConfig(
    format="%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[RichHandler(show_level=True, show_path=False, markup=True)],
)

logger = logging.getLogger("taskee")


def start(
    t: Taskee,
    interval_minutes: float = 5.0,
) -> None:
    """Run an indefinite logger. This handles scheduling of Earth Engine updates and
    logs events as they occur.
    """
    logger.setLevel("INFO")

    last_checked = 0.0
    interval_seconds = interval_minutes * 60.0

    while True:
        now = time.time()
        elapsed = now - last_checked

        if elapsed > interval_seconds:
            with Status("[yellow]Updating tasks...", spinner="bouncingBar"):
                new_events = t.update()
                t.dispatch()

                last_checked = now

            for event in new_events:
                message = event.message
                state = event.task.metadata.state if hasattr(event, "task") else None
                if state in FINISHED_OPERATION_STATES:
                    message += f" [dim]({len(t.active_tasks)} tasks remaining)[/]"

                muted_style = "[dim]" if event.__class__ not in t.watch_for else ""
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
                f"({len(t.active_tasks)} active tasks)"
            )

            with Status(next_update_msg, spinner="bouncingBar"):
                time.sleep(delta.total_seconds())
