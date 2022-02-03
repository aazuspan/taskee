import os

import notifypy  # type: ignore

from taskee.notifiers.notifier import Notifier


class Native(Notifier):
    def send(self, title: str, message: str) -> None:
        notification = notifypy.Notify()
        notification.application_name = "taskee"
        notification.icon = os.path.join("taskee", "notifiers", "taskee.png")
        notification.title = title
        notification.message = message
        notification.send()
