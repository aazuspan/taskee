import datetime
import time
from typing import List

from rich.status import Status

from taskee import events
from taskee.cli.logger import logger
from taskee.cli.styles import get_style
from taskee.taskee import Taskee


def start(
    t: Taskee,
    watch_for: List[str] = ["error", "completed", "failed"],
    interval_minutes: int = 5,
) -> None:
    """Run an indefinite logger. This handles scheduling of Earth Engine updates and
    logs events as they occur.
    """
    logger.setLevel("INFO")

    last_checked = time.time()
    interval_seconds = interval_minutes * 60.0

    watch_for = events.get_events(watch_for)

    while True:
        elapsed = time.time() - last_checked

        if elapsed > interval_seconds:
            with Status(f"[yellow]Updating tasks...", spinner="bouncingBar"):
                new_events = t._update(watch_for)
                last_checked = time.time()
            
            if len(new_events) > 1:
                new_events = sorted(new_events, key=lambda event: event.time)

            for event in new_events:
                muted_style = "[dim]" if event.__class__ not in watch_for else ""
                style = get_style(event.__class__)
                logger.info(
                    f"[{style.color}]{style.emoji} {event.__class__.__name__}[/]: {muted_style}{event.message}"
                )

        else:
            delta = datetime.timedelta(seconds=interval_seconds - elapsed)
            next_update = datetime.datetime.now() + delta

            with Status(
                f"[yellow]Next update at {next_update:%H:%M:%S}...",
                spinner="bouncingBar",
            ):
                time.sleep(delta.total_seconds())
