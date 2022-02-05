from typing import Set, Tuple, Type

import ee  # type: ignore

from taskee import events, utils
from taskee.dispatcher import Dispatcher
from taskee.tasks import TaskManager


class Taskee:
    """The Taskee object is the primary interface to the taskee library. It connects the task manager, which
    tracks tasks and events, to the dispatcher, which distributes notifications. The Taskee object is the
    only direct point of contact with Earth Engine."""

    def __init__(self, notifiers: Tuple[str, ...] = ("native",)):

        """
        Parameters
        ----------
        notifiers : Tuple[str, ...]
            Notifier names for handling notifications.
        """
        utils.initialize_earthengine()
        self.manager = TaskManager(ee.data.getTaskList())
        self.dispatcher = Dispatcher(notifiers)

    def _update(self, watch_for: Set[Type[events.Event]]) -> Tuple[events.Event, ...]:
        """Update tasks and return any events that occured. Dispatch notifications for events of interest."""
        self.manager.update(ee.data.getTaskList())

        new_events = self.manager.events

        for event in new_events:
            if isinstance(event, tuple(watch_for)):
                self.dispatcher.notify(event.title, event.message)

        return new_events
