from __future__ import annotations

from taskee.cli.commands import log


def test(notifiers: tuple[str, ...]) -> None:
    from taskee.dispatcher import Dispatcher

    log.logger.setLevel("INFO")
    dispatcher = Dispatcher(notifiers)

    dispatcher.notify(
        title="Notification Test",
        message="If you receive this notification, taskee is working!",
    )
    log.logger.info("Notification sent!")
