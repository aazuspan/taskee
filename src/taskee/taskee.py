from __future__ import annotations

from collections import deque
from datetime import datetime
from typing import Union

import ee
import humanize
from google.oauth2.credentials import Credentials as OAuthCredentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials

from taskee import events
from taskee.notifiers import NotifierEnum
from taskee.operation import FINISHED_OPERATION_STATES, Operation

Credentials = Union[OAuthCredentials, ServiceAccountCredentials, str]


class Taskee:
    """The Taskee task manager.

    The task manager tracks tasks, retrieves events, and dispatches notifications.
    """

    def __init__(
        self,
        notifiers: tuple[()] | tuple[str, ...] = ("native",),
        watch_for: tuple[()] | tuple[str, ...] = ("completed", "failed", "error"),
        credentials: Credentials = "persistent",
    ):
        """
        Parameters
        ----------
        notifiers : Tuple[str, ...]
            Notifier names for handling notifications.
        watch_for : Tuple[str, ...]
            Names of event types to dispatch notifications for.
        credentials : Credentials
            Credentials for initializing Earth Engine, e.g. from
            ee.ServiceAccountCredentials. If not provided, the default persistent
            credentials will be used.
        """
        ee.Initialize(credentials=credentials)
        self.notifiers = [NotifierEnum[name.upper()].value() for name in notifiers]
        self.watch_for = [events.EventEnum[name.upper()].value for name in watch_for]
        self.tasks: tuple[Operation, ...] = tuple()
        self.event_queue: deque[events._Event] = deque()
        self.last_update = datetime.fromtimestamp(0)
        self._get_events()

    @property
    def active_tasks(self) -> tuple[Operation, ...]:
        """Return all active tasks."""
        return tuple(filter(lambda task: not task.done, self.tasks))

    def __repr__(self) -> str:
        time_since_update = datetime.now() - self.last_update

        return (
            f"{super().__repr__()}\n"
            f"\tLast update: {humanize.naturaldelta(time_since_update)} ago\n"
            f"\tTasks: {len(self.tasks)} ({len(self.active_tasks)} active)\n"
            f"\tNotifiers: {[notif.__class__.__name__ for notif in self.notifiers]}\n"
            f"\tWatching: {[event.__name__ for event in self.watch_for]}"
        )

    def update(self) -> tuple[events._Event, ...]:
        """Update tasks and add any events to the queue."""
        new_events = self._get_events()

        for event in new_events:
            message = event.message
            state = event.task.metadata.state if hasattr(event, "task") else None

            if state in FINISHED_OPERATION_STATES:
                message += f" ({len(self.active_tasks)} tasks remaining)"

            self.event_queue.append(event)

        return new_events

    def dispatch(self) -> None:
        """Dispatch all events in the event queue to notifiers."""
        while self.event_queue:
            event = self.event_queue.popleft()
            if not isinstance(event, tuple(self.watch_for)):
                continue

            for notifier in self.notifiers:
                notifier.send(event.title, event.message)

    def _get_events(self) -> tuple[events._Event, ...]:
        """Update all tasks and return any events that occured since the last update."""
        ops = tuple(Operation(**op) for op in ee.data.listOperations())
        events = []

        for op in ops:
            prev_op = self.tasks[self.tasks.index(op)] if op in self.tasks else None

            if event := op.get_event(prev=prev_op):
                events.append(event)

        self.tasks = tuple(sorted(ops))
        self.last_update = datetime.now()

        return tuple(events)
