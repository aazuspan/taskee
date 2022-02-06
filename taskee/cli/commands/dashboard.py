import time
from collections import deque
from typing import TYPE_CHECKING, Deque, Optional, Tuple

import humanize  # type: ignore
from rich import box
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress_bar import ProgressBar
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


class Dashboard:
    def __init__(
        self,
        t: Taskee,
        watch_for: Tuple[str, ...] = ("error", "completed", "failed"),
        interval_minutes: float = 5.0,
    ):
        self.event_log: Deque["Event"] = deque(maxlen=MAX_ROWS)
        self.last_checked = time.time()

        self.t = t
        self.watch_events = events.get_events(watch_for)
        self.interval_seconds = interval_minutes * 60.0

        self.layout = self.create_layout()
        self.window = Panel(
            self.layout,
            title="[bold white]taskee",
            border_style="bright_black",
            height=36,
        )

        # Initialize the dashboard before we start Live so we don't render a preview layout
        self.update_display()

    @property
    def elapsed(self) -> float:
        """Return the time elapsed since the last event update"""
        return time.time() - self.last_checked

    @property
    def time_remaining(self) -> float:
        """Return the time remaining until the next event update"""
        return self.interval_seconds - self.elapsed

    def run(self) -> None:
        """Run the dashboard indefinitely."""
        with Live(self.window):
            while True:
                if self.elapsed > self.interval_seconds:
                    self.update_events()

                self.update_display()
                time.sleep(REFRESH_SECONDS)

    def update_events(self) -> None:
        """Update Earth Engine tasks and store new events."""
        self.t._update(self.watch_events)

        new_events = self.t.manager.events
        for event in new_events:
            self.event_log.appendleft(event)

        self.last_checked = time.time()

    def update_display(self) -> None:
        """Update the dasboard display."""
        self.layout["header"].update(self.create_header())
        self.layout["progress"].update(self.create_progress())

        task_table, event_table = self.create_tables()
        self.layout["tasks"].update(task_table)
        self.layout["events"].update(event_table)
        self.layout["tasks"].size = task_table.row_count + TABLE_HEADER_HEIGHT
        self.layout["events"].size = event_table.row_count + TABLE_HEADER_HEIGHT

    def create_layout(self) -> Layout:
        """Create the dashboard Layout"""
        layout = Layout()

        layout.split(
            Layout(name="header", size=1),
            Layout(name="progress", size=2),
            Layout(name="events", minimum_size=4),
            Layout(name="tasks", minimum_size=4),
        )

        layout["progress"].update(self.create_progress())
        layout["header"].update(self.create_header())

        return layout

    def create_header(self) -> Table:
        """Create the dashboard Header showing the update time and controls."""
        grid = Table.grid(expand=True)
        grid.add_column(justify="left")
        grid.add_column(justify="right")
        grid.add_row(
            "[italic]Next update in"
            f" {humanize.naturaldelta(self.time_remaining)}...[/]",
            Text("Press CTRL + C to exit...", style="dim"),
        )

        return grid

    def create_progress(self) -> ProgressBar:
        return ProgressBar(
            total=self.interval_seconds,
            completed=self.interval_seconds - self.time_remaining,
            complete_style="bright_yellow",
        )

    def create_tables(self) -> Tuple[Table, Table]:
        n_tasks = MAX_ROWS - min(max(len(self.event_log), 1), MAX_ROWS // 2)
        n_events = MAX_ROWS - n_tasks

        task_table = self.create_task_table(n_tasks)
        event_table = self.create_event_table(n_events)

        return task_table, event_table

    def create_task_table(self, max_tasks: Optional[int] = None) -> Table:
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

        for task in self.t.manager.tasks[:max_tasks]:
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

    def create_event_table(self, max_events: Optional[int] = None) -> Table:
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

        for event in tuple(self.event_log)[:max_events]:
            event_time = humanize.naturaltime(event.time)
            event_style = get_style(event.__class__)
            event_name = event.__class__.__name__
            muted_style = "[dim]" if event.__class__ not in self.watch_events else ""
            t.add_row(
                f"[{event_style.color}]{event_name}[/] {event_style.emoji}",
                f"{muted_style}{event.message}",
                event_time,
            )
        if len(self.event_log) == 0:
            t.add_row("", Text("No events yet..."), "", style="dim italic bright_black")

        return t


def start(
    t: Taskee,
    watch_for: Tuple[str, ...] = ("error", "completed", "failed"),
    interval_minutes: float = 5.0,
) -> None:
    """Run an indefinite dashboard. This handles scheduling of Earth Engine updates and
    runs a live-updating dashboard of tasks and events as they occur.
    """
    dashboard = Dashboard(t, watch_for, interval_minutes)
    dashboard.run()
