import notifypy
import os

from taskee.notifiers.notifier import Notifier


class Native(Notifier):
    def send(self, title, message):
        notification = notifypy.Notify()
        notification.application_name = "taskee"
        notification.icon = "taskee\\notifiers\\taskee.png"
        notification.title = title
        notification.message = message
        notification.send()
