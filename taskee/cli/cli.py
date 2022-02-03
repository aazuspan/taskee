import click

from taskee import events
from taskee.cli import dashboard, log, tree
from taskee.cli.tasks import tasks
from taskee.notifiers import notifier
from taskee.taskee import Taskee

# TODO: Add to Bumpversion or add a module-level version file
__version__ = "0.0.1"

modes = {"log": log.start, "dashboard": dashboard.start, "tree": tree.start}


@click.group(help="Monitor Earth Engine tasks and send notifications.")
@click.version_option(__version__, prog_name="taskee")
def main():
    return


@main.command(name="start", help="Start running the notification system.")
@click.argument("mode", nargs=1, type=click.Choice(choices=modes.keys()))
@click.argument(
    "watch_for",
    nargs=-1,
    type=click.Choice(
        choices=list(events.list_events().keys()) + ["all"], case_sensitive=False
    ),
)
@click.option(
    "notifiers",
    "-n",
    "--notifier",
    default=("native",),
    multiple=True,
    type=click.Choice(
        list(notifier.list_notifiers().keys()) + ["all"], case_sensitive=False
    ),
    help="One or more notifiers to run.",
)
@click.option(
    "interval_mins",
    "-i",
    "--interval_mins",
    default=5.0,
    help="Minutes between queries to Earth Engine for task updates.",
)
def start_command(mode, watch_for, notifiers, interval_mins):
    if not watch_for:
        watch_for = ("completed", "failed", "error")

    mode_func = modes[mode]
    t = Taskee(notifiers=notifiers)

    try:
        mode_func(t, watch_for=watch_for, interval_minutes=interval_mins)
    except Exception as e:
        if "error" in [event.lower() for event in watch_for]:
            event = events.Error()
            t.dispatcher.notify(event.title, event.message)
        raise e
    except KeyboardInterrupt:
        return


@main.command(name="tasks", help="Display a table of current Earth Engine tasks.")
def tasks_command():
    tasks()


@main.command(name="test", help="Send a test notification.")
@click.option(
    "notifiers",
    "-n",
    "--notifier",
    default=("native",),
    multiple=True,
    type=click.Choice(notifier.list_notifiers().keys(), case_sensitive=False),
    help="One or more notifiers to test.",
)
def test_command(notifiers):
    from taskee.dispatcher import Dispatcher

    log.logger.setLevel("INFO")
    dispatcher = Dispatcher(notifiers)

    dispatcher.notify(
        title="Notification Test",
        message="If you receive this notification, taskee is working!",
    )
    log.logger.info("Notification sent!")


if __name__ == "__main__":
    main()
