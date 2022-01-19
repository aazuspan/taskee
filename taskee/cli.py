from typing import List

import click

from taskee import watch
from taskee.events import get_events


@click.command()
@click.option(
    "--events",
    "-e",
    default=("completed", "failed"),
    multiple=True,
    help="An event type to watch for. See taskee.events.list_events()",
)
@click.option(
    "--interval",
    "-i",
    default=15,
    help="The interval in minutes to check for new events.",
)
def main(events: List[str], interval: int) -> None:
    watch_for = get_events(events)
    watcher = watch.initialize()
    watcher.watch(watch_for=watch_for, interval_minutes=interval)


if __name__ == "__main__":
    main()
