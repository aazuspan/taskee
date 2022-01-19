from typing import Tuple

import click

from taskee import watch


@click.command(
    help="Run the taskee task watcher. EVENTS is one or more event types to watch for from the list ['created', 'started', 'attempted', 'cancelled', 'completed', 'failed', 'all']. By default, 'completed' and 'failed' are used."
)
@click.argument("events", nargs=-1)
@click.option(
    "notifiers",
    "-n",
    "--notifier",
    multiple=True,
    help="A notifier engine to send notifications from the list ['native', 'pushbullet', 'all']. By default, native notifications are used.",
)
@click.option(
    "interval_minutes",
    "-i",
    "--interval_mins",
    default=15.0,
    help="Interval in minutes between updates.",
)
def main(events: Tuple[str], notifiers: Tuple[str], interval_minutes: float) -> None:
    events = ("completed", "failed") if not events else events
    notifiers = "native" if not notifiers else notifiers

    watcher = watch.initialize(notifiers=notifiers)
    watcher.watch(watch_for=events, interval_minutes=interval_minutes)


if __name__ == "__main__":
    main()
