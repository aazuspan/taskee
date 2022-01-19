import configparser
import datetime
import os
import time

import ee
import pushbullet

from taskee import events
from taskee.tasks import TaskManager
from taskee.utils import initialize_earthengine, initialize_pushbullet, logger


class Watcher:
    def __init__(self, pb: pushbullet.Pushbullet, manager: TaskManager):
        """

        Parameters
        ----------
        pb : pushbullet.Pushbullet
            An initialized Pushbullet object for handling notifications.
        manager : TaskManager
            The manager to handle tasks.
        """
        self.pb = pb
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
                self.pb.push_note(
                    "Oops!",
                    "Something went wrong and taskee crashed. You'll have to restart now.",
                )
                raise e

    def update(self, watch_for):
        logger.debug("Updating tasks...")
        self.manager.update(ee.data.getTaskList())

        event_found = False
        for task in self.manager.tasks.values():
            event = task.event

            if event is None:
                continue

            event_message = ": ".join([event.title, event.message])

            if isinstance(event, tuple(watch_for)):
                event_found = True
                
                logger.info(event_message)
                # TODO: Check `push` status code and decide what to do with errors (resend later? Crash? Just log?)
                push = self.pb.push_note(event.title, event.message)
            
            else:
                logger.debug(f"Event found, but ignored: {event_message}")

        if not event_found:
            logger.info("No events to report.")


def initialize() -> Watcher:
    """Initialize the system and return a new task watcher. If a
    Pushbullet API key hasn't previously been stored, this will
    request and store one for future use."""
    logger.debug("Initializing Earth Engine...")
    initialize_earthengine()

    logger.debug("Initializing Pushbullet...")
    pb = initialize_pushbullet()

    logger.debug("Initializing Task Manager...")
    manager = TaskManager(ee.data.getTaskList())

    total_tasks = len(manager.tasks)
    active_tasks = len(
        [
            task
            for task in manager.tasks.values()
            if task.state in ("RUNNING", "STARTED")
        ]
    )
    logger.info(f"{total_tasks} tasks found. {active_tasks} are active.")

    return Watcher(pb, manager)
