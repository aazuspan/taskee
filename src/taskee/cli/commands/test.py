from __future__ import annotations

from taskee.cli.commands import log
from taskee.notifiers.notifier import Notifier


def test(notifiers: tuple[Notifier, ...]) -> None:
    log.logger.setLevel("INFO")

    for notifier in notifiers:
        notifier.send(
            title="Notification Test",
            message="If you receive this notification, taskee is working!",
        )

        log.logger.info(f"Notification sent to {notifier.__class__.__name__}!")
