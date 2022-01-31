from typing import Type, Union

from taskee import events, states

COLOR_SUCCESS = "green"
COLOR_ERROR = "red"
COLOR_INFO = "cyan"
COLOR_WARNING = "yellow"


class Style:
    def __init__(self, color, emoji=""):
        self.color = color
        self.emoji = emoji


_event_styles = {
    events.Error: Style(color=COLOR_ERROR, emoji=":exclamation:"),
    events.Failed: Style(color=COLOR_ERROR, emoji=":fire:"),
    events.Completed: Style(color=COLOR_SUCCESS, emoji=":evergreen_tree:"),
    events.Created: Style(color=COLOR_INFO, emoji=":seedling:"),
    events.Started: Style(color=COLOR_INFO, emoji=":herb:"),
    events.Attempted: Style(color=COLOR_WARNING, emoji=":fallen_leaf:"),
    events.Cancelled: Style(color=COLOR_ERROR, emoji=":axe:"),
}


_state_styles = {
    states.CANCEL_REQUESTED: Style(color=COLOR_ERROR, emoji=":triangular_flag:"),
    states.CANCELLED: Style(color=COLOR_ERROR, emoji=":prohibited:"),
    states.COMPLETED: Style(color=COLOR_SUCCESS, emoji=":white_heavy_check_mark:"),
    states.FAILED: Style(color=COLOR_ERROR, emoji=":x:"),
    states.READY: Style(color=COLOR_INFO, emoji=":hourglass:"),
    states.RUNNING: Style(color=COLOR_INFO, emoji=":wrench:"),
}

styles = {**_event_styles, **_state_styles}


def get_style(obj: Union[str, Type["Event"]]) -> Style:
    """Retrieve the Style for a given object or class, such as an Event class or a state string."""
    try:
        return styles[obj]
    except KeyError:
        raise KeyError(f"'{obj}' does not have a registered style.")


if __name__ == "__main__":
    import rich
    from rich.panel import Panel

    event_prompts = []
    for event, style in _event_styles.items():
        event_prompts.append(f"[{style.color}]{event.__name__}[/] {style.emoji}")
    rich.print(Panel("\n".join(event_prompts), title="Event Types", expand=False))

    state_prompts = []
    for state, style in _state_styles.items():
        state_prompts.append(f"[{style.color}]{state}[/] {style.emoji}")
    rich.print(Panel("\n".join(state_prompts), title="Task States", expand=False))
