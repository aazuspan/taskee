from typing import List, Type, Union

import ee

from taskee import events, utils
from taskee.dispatcher import Dispatcher
from taskee.notifiers.notifier import Notifier
from taskee.tasks import TaskManager


class Taskee:
    """The Taskee object schedules and handles task updates."""

    def __init__(self, notifiers: List[Union[str, Type[Notifier]]] = ["native"]):
        """
        Parameters
        ----------
        notifiers : List[Union[str, Type[Notifier]]]
            Notifier objects for handling notifications, by name or class.
        """
        utils.initialize_earthengine()
        self.manager = TaskManager(ee.data.getTaskList())
        self.dispatcher = Dispatcher(notifiers)

    def _update(self, watch_for: List[Type[events.Event]]) -> List[events.Event]:
        """Update tasks and return any events that occured. Dispatch notifications for events of interest."""
        self.manager.update(ee.data.getTaskList())

        new_events = []
        for task in self.manager.tasks.values():
            event = task.event

            if event is not None:
                new_events.append(event)

            if isinstance(event, tuple(watch_for)):
                self.dispatcher.notify(event.title, event.message)

        return new_events
