import datetime
import logging
import time
from typing import Tuple

from rich.logging import RichHandler
from rich.status import Status

from taskee import events
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
    watch_for: Tuple[str, ...] = ("error", "completed", "failed"),
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

        if elapsed > interval_seconds:
            with Status(f"[yellow]Updating tasks...", spinner="bouncingBar"):
                new_events = t._update(watch_events)
                last_checked = time.time()

            if len(new_events) > 1:
                new_events = tuple(sorted(new_events, key=lambda event: event.time))

            for event in new_events:
                muted_style = "[dim]" if event.__class__ not in watch_events else ""
                style = get_style(event.__class__)
                logger.info(
                    f"[{style.color}]{style.emoji} {event.__class__.__name__}[/]:"
                    f" {muted_style}{event.message}"
                )

        else:
            delta = datetime.timedelta(seconds=interval_seconds - elapsed)
            next_update = datetime.datetime.now() + delta

            with Status(
                f"[yellow]Next update at {next_update:%H:%M:%S}...",
                spinner="bouncingBar",
            ):
                time.sleep(delta.total_seconds())
