from __future__ import annotations

from taskee.notifiers import get_notifier


class Dispatcher:
    def __init__(self, notifiers: tuple[str, ...]):
        self.notifiers = [get_notifier(name)() for name in notifiers]

    def notify(self, title: str, message: str) -> None:
        """Send notifications to all registered notifiers."""
        for notifier in self.notifiers:
            notifier.send(title, message)
