import datetime
from typing import List

import humanize
from rich.table import Table
from rich.text import Text

from taskee import states, terminal


def _create_task_table(
    tasks: List["Task"], max_tasks: int = None, title: str = None
) -> Table:
    """Create a table of tasks."""
    t = Table(
        title=title, row_styles=["", "dim"], width=terminal.settings.TERMINAL_WIDTH
    )

    t.add_column("State", justify="right")
    t.add_column("Description", justify="left")
    t.add_column("Created", justify="right")
    t.add_column("Elapsed", justify="right")

    table_tasks = tasks[:max_tasks]
    for task in table_tasks:
        row_style = states.STATE_COLORS[task.state]
        if task.state == states.CANCELLED:
            row_style += " strike"

        t.add_row(
            task.state,
            task.description,
            humanize.naturaltime(task.time_created, when=datetime.datetime.now(tz=datetime.timezone.utc)),
            humanize.naturaldelta(task.time_elapsed),
            style=row_style,
        )

    return t


def _create_event_table(events: List["Event"], title: str = None) -> Table:
    """Create a table of events."""
    t = Table(
        title=title, row_styles=["", "dim"], width=terminal.settings.TERMINAL_WIDTH
    )

    t.add_column("Event", justify="right")
    t.add_column("Message", justify="left")

    for event in events:
        t.add_row(Text(event.__class__.__name__, style=event._color), event.message)

    return t
