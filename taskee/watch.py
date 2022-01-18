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
        self, watch_for=(events.Failed, events.Completed), interval_seconds: int = 60
    ):
        """
        Parameters
        ----------
        watch_for : List[Union[str, taskee.events.Event]]
            A list of events to watch for, passed by name or class. Events not on this
            list will be ignored.
        interval_seconds: int, default 60
            Number of seconds to wait between updates. Updates that are too
            frequent may lead to rate limits from Earth Engine or Pushbullet.
        """
        last_checked = time.time()

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
        logger.info("Checking tasks!")
        self.manager.update(ee.data.getTaskList())

        for task in self.manager.tasks.values():
            event = task.event

            if event is None:
                continue

            if isinstance(event, watch_for):
                logger.info(": ".join([event.title, event.message]))

                # TODO: Check `push` status code and decide what to do with errors (resend later? Crash? Just log?)
                push = self.pb.push_note(event.title, event.message)


def initialize() -> Watcher:
    """Initialize the system and return a new task watcher. If a
    Pushbullet API key hasn't previously been stored, this will
    request and store one for future use."""
    logger.debug("Initializing Earth Engine...")
    initialize_earthengine()

    logger.debug("Initializing Pushbullet...")
    pb = initialize_pushbullet()

    manager = TaskManager(ee.data.getTaskList())

    return Watcher(pb, manager)


if __name__ == "__main__":
    watch = (
        events.Cancelled,
        events.Attempt,
        events.New,
        events.Started,
        events.Failed,
        events.Completed,
    )

    watcher = initialize()
    watcher.watch(watch_for=watch, interval_seconds=15)
