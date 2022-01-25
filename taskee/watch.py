import datetime
import time
from typing import List, Type

import ee
import humanize
import rich
from rich import box
from rich.panel import Panel
from rich.status import Status

from taskee import events, states, terminal, utils
from taskee.notifiers.notifier import Notifier, get_notifiers
from taskee.tasks import TaskManager
from taskee.terminal.logger import logger
from taskee.terminal.tables import _create_event_table, _create_task_table


class Watcher:
    def __init__(self, notifiers: List[Notifier], manager: TaskManager):
        """

        Parameters
        ----------
        notifiers : List[Notifier]
            Notifier objects for handling notifications.
        manager : TaskManager
            The manager to handle tasks.
        """
        self.notifiers = notifiers
        self.manager = manager

    def watch(
        self,
        watch_for=(events.Failed, events.Completed, events.Error),
        interval_minutes: int = 15,
    ):
        """
        Parameters
        ----------
        watch_for : List[Union[str, taskee.events.Event]]
            A list of events to watch for, passed by name or class. Events not on this
            list will be ignored.
        interval_minutes: int, default 15
            Number of minutes to wait between updates. Updates that are too
            frequent may lead to rate limits from Earth Engine or Pushbullet.
        """
        last_checked = time.time()
        interval_seconds = interval_minutes * 60.0

        watch_for = events.get_events(watch_for)

        logger.debug("Starting task watcher...")
        logger.debug(f"Watching for: {[event.__name__ for event in watch_for]}")
        logger.debug(f"Update interval: {interval_minutes} min.")

        while True:
            try:
                elapsed = time.time() - last_checked

                if elapsed < interval_seconds:
                    wait_time = datetime.timedelta(seconds=interval_seconds - elapsed)
                    next_check = datetime.datetime.now() + wait_time
                    with Status(
                        f"[yellow]Next update[/]: {humanize.naturaltime(next_check)} [yellow]({next_check.astimezone():%H:%M:%S})[/]",
                        spinner="bouncingBar",
                    ):
                        time.sleep(wait_time.seconds)

                self.update(watch_for)
                last_checked = time.time()

            except Exception as e:
                self.notify_event(events.Error(), watch_for)
                raise e

            except KeyboardInterrupt:
                logger.info("[red italic]Shutting down...")
                break

    def update(self, watch_for):
        self.manager.update(ee.data.getTaskList())

        changed_tasks = []
        for task in self.manager.tasks.values():
            event = task.event

            if event is None:
                continue

            self.notify_event(event, watch_for)

            if isinstance(event, tuple(watch_for)):
                changed_tasks.append(task)

        s = "s" if len(changed_tasks) != 1 else ""
        logger.info(f"[yellow]{len(changed_tasks)} new event{s} found.")

        if len(changed_tasks) > 0:
            events = [task.event for task in changed_tasks]
            rich.print(_create_event_table(events, title="Earth Engine Events"))

    def notify_event(self, event, watch_for):
        """Send a notification for an event if it is being watch for."""
        if isinstance(event, tuple(watch_for)):
            for notifier in self.notifiers:
                notifier.send(event.title, event.message)


def initialize(notifiers: List[Type[Notifier]], logging_level: str = "INFO") -> Watcher:
    """Initialize the system and return a new task watcher. If a
    Pushbullet API key hasn't previously been stored, this will
    request and store one for future use."""
    logger.setLevel(logging_level.upper())

    logger.debug("Initializing Earth Engine...")
    utils.initialize_earthengine()

    logger.debug("Initializing Task Manager...")
    manager = TaskManager(ee.data.getTaskList())

    selected_notifiers = get_notifiers(notifiers)
    activated_notifiers = [notifier() for notifier in selected_notifiers]

    logger.debug(f"Notifiers: {[notifier.__name__ for notifier in selected_notifiers]}")

    total_tasks = len(manager.tasks)
    active_tasks = len(
        [task for task in manager.tasks.values() if task.state in states.ACTIVE]
    )
    verb = "is" if active_tasks == 1 else "are"
    task_prompt = f"[bold yellow]Tasks[/]: {total_tasks} tasks found. {active_tasks} {verb} [green]active[/].\n"
    notifier_prompt = f"[bold cyan]Notifiers[/]: {len(activated_notifiers)} active notifier{'s' if len(activated_notifiers) != 1 else ''} [green]({', '.join([notif.__name__ for notif in selected_notifiers])})[/]."
    prompt = task_prompt + notifier_prompt

    header = Panel(
        prompt,
        title="[bold green]taskee[/]",
        padding=1,
        box=box.DOUBLE,
        width=terminal.settings.TERMINAL_WIDTH,
    )
    rich.print(header)
    rich.print(
        _create_task_table(
            list(manager.tasks.values()), max_tasks=16, title="Earth Engine Tasks"
        )
    )

    return Watcher(notifiers=activated_notifiers, manager=manager)
