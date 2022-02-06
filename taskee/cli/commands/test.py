from typing import Tuple

from taskee.cli.commands import log


def test(notifiers: Tuple[str, ...]) -> None:
    from taskee.dispatcher import Dispatcher

    log.logger.setLevel("INFO")
    dispatcher = Dispatcher(notifiers)

    dispatcher.notify(
        title="Notification Test",
        message="If you receive this notification, taskee is working!",
    )
    log.logger.info("Notification sent!")
