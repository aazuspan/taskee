from typing import List, Type, Union

from taskee.notifiers.notifier import Notifier, get_notifiers


class Dispatcher:
    def __init__(self, notifiers: List[Union[str, Type[Notifier]]]):
        selected_notifiers = get_notifiers(notifiers)
        self.notifiers = [notifier() for notifier in selected_notifiers]

    def notify(self, title: str, message: str):
        """Send notifications to all registered notifiers."""
        for notifier in self.notifiers:
            notifier.send(title, message)
