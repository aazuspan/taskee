import datetime
import time
from typing import List, Type

import ee

from taskee import events
from taskee.notifiers.notifier import Notifier, get_notifiers
from taskee.tasks import TaskManager
from taskee.utils import (_create_task_table, console, initialize_earthengine,
                          logger)


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
        self, watch_for=(events.Failed, events.Completed), interval_minutes: int = 15
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

                if elapsed > interval_seconds:
                    self.update(watch_for)
                    last_checked = time.time()

                else:
                    wait_time = datetime.timedelta(seconds=interval_seconds - elapsed)

                    if wait_time.seconds > 0:
                        next_check = datetime.datetime.now() + wait_time
                        logger.info(f"Next update: {next_check.astimezone():%H:%M:%S}")
                        time.sleep(wait_time.seconds)

            except Exception as e:
                for notifier in self.notifiers:
                    notifier.send(
                        title="Oops",
                        message="Something went wrong and taskee needs to be restarted.",
                    )
                raise e
            except KeyboardInterrupt:
                logger.info("Shutting down...")
                break

    def update(self, watch_for):
        logger.debug("Updating tasks...")
        self.manager.update(ee.data.getTaskList())

        changed_tasks = []
        for task in self.manager.tasks.values():
            event = task.event

            if event is None:
                continue

            event_message = ": ".join([event.title, event.message])

            if isinstance(event, tuple(watch_for)):
                changed_tasks.append(task)

                logger.info(event_message)

                for notifier in self.notifiers:
                    notifier.send(event.title, event.message)

            else:
                logger.debug(f"Event found, but ignored: {event_message}")

        if not changed_tasks:
            logger.info("No events to report.")

        else:
            console.print(_create_task_table(changed_tasks, title="Updated Tasks"))


def initialize(notifiers: List[Type[Notifier]], logging_level: str = "INFO") -> Watcher:
    """Initialize the system and return a new task watcher. If a
    Pushbullet API key hasn't previously been stored, this will
    request and store one for future use."""
    logger.setLevel(logging_level.upper())

    logger.debug("Initializing Earth Engine...")
    initialize_earthengine()

    logger.debug("Initializing Task Manager...")
    manager = TaskManager(ee.data.getTaskList())

    selected_notifiers = get_notifiers(notifiers)
    activated_notifiers = [notifier() for notifier in selected_notifiers]

    logger.debug(f"Notifiers: {[notifier.__name__ for notifier in selected_notifiers]}")

    total_tasks = len(manager.tasks)
    active_tasks = len(
        [
            task
            for task in manager.tasks.values()
            if task.state in ("RUNNING", "STARTED")
        ]
    )
    logger.info(f"{total_tasks} tasks found. {active_tasks} are active.")
    console.print(
        _create_task_table(list(manager.tasks.values()), max_tasks=16, title="Tasks")
    )

    return Watcher(notifiers=activated_notifiers, manager=manager)
