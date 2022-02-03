import datetime
import time
from typing import TYPE_CHECKING, List, Optional, Set, Tuple, Type

import humanize  # type: ignore
from rich import box
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import ProgressBar
from rich.table import Table
from rich.text import Text

from taskee import events, states
from taskee.cli.styles import get_style
from taskee.taskee import Taskee

REFRESH_SECONDS = 1
MAX_ROWS = 20
TABLE_HEADER_HEIGHT = 6
BOX_STYLE = box.SIMPLE_HEAD

if TYPE_CHECKING:
    from taskee.events import Event
    from taskee.tasks import Task


def start(
    t: Taskee,
    watch_for: Tuple[str, ...] = ("error", "completed", "failed"),
    interval_minutes: float = 5.0,
) -> None:
    """Run an indefinite dashboard. This handles scheduling of Earth Engine updates and
    runs a live-updating dashboard of tasks and events as they occur.
    """
    last_checked = time.time()
    interval_seconds = interval_minutes * 60.0

    watch_events = events.get_events(watch_for)
    event_log: List["Event"] = []
    layout = create_layout()
    window = Panel(
        layout, title="[bold white]taskee", border_style="bright_black", height=36
    )

    tasks = tuple(t.manager.tasks.values())
    new_events = t.manager.events
    # Initialize the dashboard before we start Live so we don't render a preview layout
    update_dashboard(
        tasks=tasks,
        events=new_events,
        layout=layout,
        time_remaining=interval_seconds,
        total_time=interval_seconds,
        watch_for=watch_events,
    )

    with Live(window):
        while True:
            elapsed = time.time() - last_checked

            if elapsed > interval_seconds:
                t._update(watch_events)
                last_checked = time.time()

            # TODO: Set a max number and events to keep. Probably use deque
            tasks = tuple(t.manager.tasks.values())

            if elapsed > interval_seconds:
                new_events = t.manager.events

                for event in new_events:
                    event_log.insert(0, event)

            update_dashboard(
                tasks=tasks,
                events=tuple(event_log),
                layout=layout,
                time_remaining=interval_seconds - elapsed,
                total_time=interval_seconds,
                watch_for=watch_events,
            )

            time.sleep(REFRESH_SECONDS)


def update_dashboard(
    tasks: Tuple["Task", ...],
    events: Tuple["Event", ...],
    layout: Layout,
    time_remaining: float,
    total_time: float,
    watch_for: Set[Type["Event"]],
) -> None:
    layout["header"].update(create_header(time_remaining=time_remaining))
    layout["progress"].update(create_progress_bar(time_remaining, total_time))
    task_table, event_table = create_tables(tasks, events, watch_for)
    layout["tasks"].update(task_table)
    layout["events"].update(event_table)
    layout["tasks"].size = task_table.row_count + TABLE_HEADER_HEIGHT
    layout["events"].size = event_table.row_count + TABLE_HEADER_HEIGHT


def create_layout() -> Layout:
    layout = Layout()

    layout.split(
        Layout(name="header", size=1),
        Layout(name="progress", size=2),
        Layout(name="events", minimum_size=4),
        Layout(name="tasks", minimum_size=4),
    )

    layout["progress"].update(create_progress_bar(0, 0))
    layout["header"].update(create_header(0))

    return layout


def create_header(time_remaining: float) -> Table:
    grid = Table.grid(expand=True)
    grid.add_column(justify="left")
    grid.add_column(justify="right")
    grid.add_row(
        f"[italic]Next update in {humanize.naturaldelta(time_remaining)}...[/]",
        Text("Press CTRL + C to exit...", style="dim"),
    )

    return grid


def create_progress_bar(time_remaining: float, total_time: float) -> ProgressBar:
    return ProgressBar(
        total=total_time,
        completed=total_time - time_remaining,
        complete_style="bright_yellow",
    )


def create_tables(
    tasks: Tuple["Task", ...],
    events: Tuple["Event", ...],
    watch_for: Set[Type["Event"]],
) -> Tuple[Table, Table]:
    n_tasks = MAX_ROWS - min(max(len(events), 1), MAX_ROWS // 2)
    n_events = MAX_ROWS - n_tasks

    task_table = create_task_table(tasks, n_tasks)
    event_table = create_event_table(events, watch_for, n_events)

    return task_table, event_table


def create_task_table(
    tasks: Tuple["Task", ...], max_tasks: Optional[int] = None
) -> Table:
    """Create a table of tasks."""
    t = Table(
        title="[bold bright_green]Tasks",
        box=BOX_STYLE,
        header_style="bright_green",
        expand=True,
    )

    t.add_column("State", justify="right")
    t.add_column("Description", justify="left")
    t.add_column("Created", justify="right")
    t.add_column("Elapsed", justify="right")

    table_tasks = tasks[:max_tasks]
    for task in table_tasks:
        state_style = get_style(task.state)
        dim_style = "[dim]" if task.state not in states.ACTIVE else ""
        time_created = humanize.naturaltime(
            task.time_created, when=datetime.datetime.now(tz=datetime.timezone.utc)
        )
        time_elapsed = humanize.naturaldelta(task.time_elapsed)

        t.add_row(
            f"[{state_style.color}]{task.state}[/] {state_style.emoji}",
            f"{dim_style}{task.description}",
            f"{dim_style}{time_created}",
            f"{dim_style}{time_elapsed}",
        )

    return t


def create_event_table(
    events: Tuple["Event", ...],
    watch_for: Set[Type["Event"]],
    max_events: Optional[int] = None,
) -> Table:
    """Create a table of events."""
    t = Table(
        title="[bold bright_blue]Events",
        box=BOX_STYLE,
        header_style="bright_blue",
        expand=True,
    )

    t.add_column("Event", justify="right")
    t.add_column("Message", justify="left")
    t.add_column("Time", justify="right")

    table_events = events[:max_events]
    for event in table_events:
        event_time = humanize.naturaltime(
            event.time, when=datetime.datetime.now(tz=datetime.timezone.utc)
        )
        event_style = get_style(event.__class__)
        event_name = event.__class__.__name__
        muted_style = "[dim]" if event.__class__ not in watch_for else ""
        t.add_row(
            f"[{event_style.color}]{event_name}[/] {event_style.emoji}",
            f"{muted_style}{event.message}",
            event_time,
        )
    if len(table_events) == 0:
        t.add_row("", Text("No events yet..."), "", style="dim italic bright_black")

    return t
