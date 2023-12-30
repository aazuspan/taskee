from __future__ import annotations

import time
from collections import deque
from typing import TYPE_CHECKING

import humanize  # type: ignore
from rich import box
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress_bar import ProgressBar
from rich.table import Table
from rich.text import Text

from taskee.cli.commands.tasks import create_task_table
from taskee.cli.styles import STYLES
from taskee.taskee import Taskee

if TYPE_CHECKING:
    from taskee.events import _Event


class _Dashboard:
    REFRESH_SECONDS = 1
    MAX_ROWS = 20
    TABLE_HEADER_HEIGHT = 6

    def __init__(
        self,
        t: Taskee,
        interval_minutes: float = 5.0,
    ):
        self.event_log: deque[_Event] = deque(maxlen=self.MAX_ROWS)
        self.last_checked = 0.0

        self.t = t
        self.interval_seconds = interval_minutes * 60.0

        self.layout = self._create_layout()
        self.window = Panel(
            self.layout,
            title="[bold white]taskee",
            border_style="bright_black",
            height=36,
        )

        # Initialize dashboard before starting Live so we don't render a preview layout
        self._update_display()

    @property
    def _elapsed(self) -> float:
        """Return the time elapsed since the last event update"""
        return time.time() - self.last_checked

    @property
    def _time_remaining(self) -> float:
        """Return the time remaining until the next event update"""
        return self.interval_seconds - self._elapsed

    def _run(self) -> None:
        """Run the dashboard indefinitely."""
        with Live(self.window):
            while True:
                if self._elapsed > self.interval_seconds:
                    self._update_events()

                self._update_display()
                time.sleep(self.REFRESH_SECONDS)

    def _update_events(self) -> None:
        """Update Earth Engine tasks and store new events."""
        new_events = self.t.update()
        self.t.dispatch()

        for event in new_events:
            self.event_log.appendleft(event)

        self.last_checked = time.time()

    def _update_display(self) -> None:
        """Update the dasboard display."""
        self.layout["header"].update(self._create_header())
        self.layout["progress"].update(self._create_progress())

        task_table, event_table = self._create_tables()
        self.layout["tasks"].update(task_table)
        self.layout["events"].update(event_table)
        self.layout["tasks"].size = task_table.row_count + self.TABLE_HEADER_HEIGHT
        self.layout["events"].size = event_table.row_count + self.TABLE_HEADER_HEIGHT

    def _create_layout(self) -> Layout:
        """Create the dashboard Layout"""
        layout = Layout()

        layout.split(
            Layout(name="header", size=1),
            Layout(name="progress", size=2),
            Layout(name="events", minimum_size=4),
            Layout(name="tasks", minimum_size=4),
        )

        layout["progress"].update(self._create_progress())
        layout["header"].update(self._create_header())

        return layout

    def _create_header(self) -> Table:
        """Create the dashboard Header showing the update time and controls."""
        grid = Table.grid(expand=True)
        grid.add_column(justify="left")
        grid.add_column(justify="right")
        grid.add_row(
            "[italic]Next update in"
            f" {humanize.naturaldelta(self._time_remaining)}...[/]",
            Text("Press CTRL + C to exit...", style="dim"),
        )

        return grid

    def _create_progress(self) -> ProgressBar:
        return ProgressBar(
            total=self.interval_seconds,
            completed=self.interval_seconds - self._time_remaining,
            complete_style="bright_yellow",
        )

    def _create_tables(self) -> tuple[Table, Table]:
        n_tasks = self.MAX_ROWS - min(max(len(self.event_log), 1), self.MAX_ROWS // 2)
        n_events = self.MAX_ROWS - n_tasks

        task_table = create_task_table(self.t.tasks, n_tasks)
        event_table = self._create_event_table(n_events)

        return task_table, event_table

    def _create_event_table(self, max_events: int | None = None) -> Table:
        """Create a table of events."""
        t = Table(
            title="[bold bright_blue]Events",
            box=box.SIMPLE_HEAD,
            header_style="bright_blue",
            expand=True,
        )

        t.add_column("Event", justify="right")
        t.add_column("Message", justify="left")
        t.add_column("Time", justify="right")

        now = time.time()

        for event in tuple(self.event_log)[:max_events]:
            event_time = humanize.naturaltime(now)
            event_style = STYLES[event.__class__]
            event_name = event.__class__.__name__.replace("Event", "")
            muted_style = "[dim]" if event.__class__ not in self.t.watch_for else ""
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
    interval_minutes: float = 5.0,
) -> None:
    """Run an indefinite dashboard. This handles scheduling of Earth Engine updates and
    runs a live-updating dashboard of tasks and events as they occur.
    """
    dashboard = _Dashboard(t, interval_minutes)
    dashboard._run()
