import datetime
import time
from typing import List

import rich
from rich.live import Live
from rich.tree import Tree

from taskee import events
from taskee.cli.styles import get_style
from taskee.taskee import Taskee

event_map = {}


from rich.panel import Panel
from rich.table import Table

from taskee import states


def build_tree(t, watch_for):
    tasks = list(t.manager.tasks.values())
    active_tree = Tree("[italic]Tasks[/]")
    inactive_tree = Tree("[italic] Tasks[/]")

    for task in tasks:
        if task.state in states.ACTIVE:
            tree = active_tree
        else:
            tree = inactive_tree

        if task.event is not None:
            try:
                event_map[task].append(task.event)
            except KeyError:
                event_map[task] = [task.event]

        try:
            task_events = event_map[task]
        except KeyError:
            task_events = None

        task_style = get_style(task.state)
        task_branch = tree.add(
            f"{task_style.emoji} [bold {task_style.color}]{task.description}[/]"
        )

        if task_events:
            for event in task_events:
                muted_style = "dim" if event.__class__ not in watch_for else ""
                style = get_style(event.__class__)

                task_branch.add(
                    f"[{style.color} {muted_style}]{style.emoji} {event.__class__.__name__} ({event.time:%H:%M:%S})"
                )

    grid = Table.grid()
    grid.add_column()
    grid.add_column()

    active_panel = Panel(active_tree, title="[bold bright_green]Active", style="white")
    inactive_panel = Panel(
        inactive_tree, title="[bold bright_red]Inactive", style="bright_black"
    )

    grid.add_row(active_panel, inactive_panel)

    return grid


def start(
    t: Taskee,
    watch_for: List[str] = ["error", "completed", "failed"],
    interval_minutes: int = 5,
) -> None:
    """Run an indefinite notifier with a tree display. This handles scheduling of Earth Engine updates and
    updates the tree with events as they occur.
    """
    last_checked = time.time()
    interval_seconds = interval_minutes * 60.0

    watch_for = events.get_events(watch_for)

    with Live(build_tree(t, watch_for)) as live:
        while True:
            elapsed = time.time() - last_checked

            if elapsed > interval_seconds:
                t._update(watch_for)
                last_checked = time.time()

                live.update(build_tree(t, watch_for))

            else:
                delta = datetime.timedelta(seconds=interval_seconds - elapsed)
                next_update = datetime.datetime.now() + delta

                rich.print(f"[yellow]Next update at {next_update:%H:%M:%S}...")
                time.sleep(delta.total_seconds())
