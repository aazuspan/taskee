from __future__ import annotations

import humanize  # type: ignore
import rich
from rich import box
from rich.table import Table

from taskee import states
from taskee.cli.styles import get_style
from taskee.taskee import Taskee
from taskee.tasks import Task


def tasks(t: Taskee, max_tasks: int) -> None:
    tasks = t.manager.tasks
    rich.print(create_task_table(tuple(tasks), max_tasks))


def create_task_table(tasks: tuple[Task, ...], max_tasks: int) -> Table:
    """Create a table of tasks."""
    t = Table(
        title="[bold bright_green]Tasks",
        box=box.SIMPLE_HEAD,
        header_style="bright_green",
        expand=True,
    )

    t.add_column("State", justify="right")
    t.add_column("Description", justify="left")
    t.add_column("Created", justify="right")
    t.add_column("Elapsed", justify="right")

    for task in tasks[:max_tasks]:
        state_style = get_style(task.state)
        dim_style = "[dim]" if task.state not in states.ACTIVE else ""
        time_created = humanize.naturaltime(task.time_created)
        time_elapsed = humanize.naturaldelta(task.time_elapsed)

        t.add_row(
            f"[{state_style.color}]{task.state}[/] {state_style.emoji}",
            f"{dim_style}{task.description}",
            f"{dim_style}{time_created}",
            f"{dim_style}{time_elapsed}",
        )

    if len(tasks) > max_tasks:
        t.caption = "..."

    return t
