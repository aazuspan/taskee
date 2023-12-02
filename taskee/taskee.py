from typing import Set, Tuple, Type, Union

import ee  # type: ignore
from google.oauth2.credentials import Credentials as OAuthCredentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials

from taskee import events, states, utils
from taskee.dispatcher import Dispatcher
from taskee.tasks import TaskManager

Credentials = Union[OAuthCredentials, ServiceAccountCredentials, str]

class Taskee:
    """The Taskee object is the primary interface to the taskee library. It connects the task manager, which
    tracks tasks and events, to the dispatcher, which distributes notifications. The Taskee object is the
    only direct point of contact with Earth Engine."""

    def __init__(self, notifiers: Tuple[str, ...] = ("native",), credentials: Credentials="persistent"):

        """
        Parameters
        ----------
        notifiers : Tuple[str, ...]
            Notifier names for handling notifications.
        credentials : Credentials
            Credentials for initializing Earth Engine, e.g. from ee.ServiceAccountCredentials. If not provided,
            the default persistent credentials will be used.
        """
        ee.Initialize(credentials=credentials)
        self.manager = TaskManager(ee.data.getTaskList())
        self.dispatcher = Dispatcher(notifiers)

    def _update(self, watch_for: Set[Type[events.Event]]) -> Tuple[events.Event, ...]:
        """Update tasks and return any events that occured. Dispatch notifications for events of interest."""
        self.manager.update(ee.data.getTaskList())

        new_events = self.manager.events
        active_tasks = self.manager.active_tasks

        for event in new_events:
            if not isinstance(event, tuple(watch_for)):
                continue

            message = event.message
            if (
                isinstance(event, events.TaskEvent)
                and event.task.state in states.FINISHED
            ):
                message += f" ({len(active_tasks)} tasks remaining)"

            self.dispatcher.notify(event.title, message)

        return new_events
