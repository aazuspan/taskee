from taskee.notifiers.notifier import Notifier


class Native(Notifier):
    def __init__(self):
        try:
            import notifypy

            self.notifypy = notifypy
        except ImportError:
            raise ImportError("")

    def send(self, title, message):
        notification = self.notifypy.Notify()
        notification.application_name = "taskee"
        notification.title = title
        notification.message = message
        notification.send()
