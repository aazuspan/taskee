from __future__ import annotations

import humanize  # type: ignore
import rich
from rich import box
from rich.table import Table

from taskee.cli.styles import get_style
from taskee.operation import ACTIVE_OPERATION_STATES, Operation


def tasks(tasks: tuple[Operation, ...], max_tasks: int) -> None:
    table = create_task_table(tasks, max_tasks)
    rich.print(table)


def create_task_table(tasks: tuple[Operation, ...], max_tasks: int) -> Table:
    """Create and print a table of tasks."""
    t = Table(
        title="[bold bright_green]Earth Engine Tasks",
        box=box.SIMPLE_HEAD,
        header_style="bright_green",
        expand=True,
    )

    t.add_column("State", justify="right")
    t.add_column("Description", justify="left")
    t.add_column("Created", justify="right")
    t.add_column("Runtime", justify="right")
    t.add_column("EECUs", justify="right")

    for task in tasks[:max_tasks]:
        state = task.metadata.state.value
        eecus = task.metadata.batchEecuUsageSeconds

        state_style = get_style(state)
        dim_style = "[dim]" if state not in ACTIVE_OPERATION_STATES else ""
        time_since_creation = humanize.naturaltime(task.time_since_creation)
        runtime = humanize.naturaldelta(task.runtime) if task.runtime else "-"
        eecus_str = "-" if not eecus else f"{eecus:,.0f}"

        t.add_row(
            f"[{state_style.color}]{state}[/] {state_style.emoji}",
            f"{dim_style}{task.metadata.description}",
            f"{dim_style}{time_since_creation}",
            f"{dim_style}{runtime}",
            f"{dim_style}{eecus_str}",
        )

    if len(tasks) > max_tasks:
        t.caption = "..."

    return t
