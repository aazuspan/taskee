import datetime
from typing import Tuple

import ee  # type: ignore
import humanize  # type: ignore
import rich
from rich import box
from rich.status import Status
from rich.table import Table

from taskee import states
from taskee.cli.styles import get_style
from taskee.tasks import Task
from taskee.utils import initialize_earthengine


def tasks() -> None:
    with Status("Retrieving tasks from Earth Engine...", spinner="bouncingBar"):
        initialize_earthengine()
        tasks = [Task(task) for task in ee.data.getTaskList()]

        rich.print(create_task_table(tuple(tasks)))


def create_task_table(tasks: Tuple[Task, ...]) -> Table:
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

    for task in tasks:
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

    return t
