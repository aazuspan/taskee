from typing import TYPE_CHECKING, Any, Mapping, Type, Union

from taskee import events, states

COLOR_SUCCESS = "green"
COLOR_ERROR = "red"
COLOR_INFO = "cyan"
COLOR_WARNING = "yellow"

if TYPE_CHECKING:
    from taskee.events import Event


class Style:
    def __init__(self, color: str, emoji: str = ""):
        self.color = color
        self.emoji = emoji


styles: Mapping[Any, Style] = {
    events.Error: Style(color=COLOR_ERROR, emoji=":exclamation:"),
    events.Failed: Style(color=COLOR_ERROR, emoji=":fire:"),
    events.Completed: Style(color=COLOR_SUCCESS, emoji=":evergreen_tree:"),
    events.Created: Style(color=COLOR_INFO, emoji=":seedling:"),
    events.Started: Style(color=COLOR_INFO, emoji=":herb:"),
    events.Attempted: Style(color=COLOR_WARNING, emoji=":fallen_leaf:"),
    events.Cancelled: Style(color=COLOR_ERROR, emoji=":axe:"),
    states.CANCEL_REQUESTED: Style(color=COLOR_ERROR, emoji=":triangular_flag:"),
    states.CANCELLED: Style(color=COLOR_ERROR, emoji=":prohibited:"),
    states.COMPLETED: Style(color=COLOR_SUCCESS, emoji=":white_heavy_check_mark:"),
    states.FAILED: Style(color=COLOR_ERROR, emoji=":x:"),
    states.READY: Style(color=COLOR_INFO, emoji=":hourglass:"),
    states.RUNNING: Style(color=COLOR_INFO, emoji=":wrench:"),
}


def get_style(obj: Union[str, Type["Event"]]) -> Style:
    """Retrieve the Style for a given object or class, such as an Event class or a state string."""
    try:
        return styles[obj]
    except KeyError:
        raise KeyError(f"'{obj}' does not have a registered style.")
