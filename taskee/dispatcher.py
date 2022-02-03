from typing import Tuple

from taskee.notifiers.notifier import get_notifiers


class Dispatcher:
    def __init__(self, notifiers: Tuple[str, ...]):
        selected_notifiers = get_notifiers(notifiers)
        self.notifiers = [notifier() for notifier in selected_notifiers]

    def notify(self, title: str, message: str) -> None:
        """Send notifications to all registered notifiers."""
        for notifier in self.notifiers:
            notifier.send(title, message)
