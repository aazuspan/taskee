from abc import ABC, abstractmethod
from typing import Dict, List, Set, Type, Union

from requests.structures import CaseInsensitiveDict

from taskee.events import Event
from taskee.utils import _get_case_insensitive_close_matches


class Notifier(ABC):
    @abstractmethod
    def send(self, title, message):
        pass


def list_notifiers() -> Dict[str, Type["Event"]]:
    """Return a case-insensitive dictionary of all available Notifier classes."""
    return CaseInsensitiveDict({cls.__name__: cls for cls in Notifier.__subclasses__()})


def get_notifiers(names: List[Union[str, Type[Notifier]]]) -> Set[Type[Notifier]]:
    """Take a list of notifiers by name or class and return a list of the corresponding classes."""
    # Allow single values to be passed
    names = [names] if not isinstance(names, (list, tuple)) else names

    if "all" in [name.lower() for name in names if isinstance(name, str)]:
        return set(list_notifiers().values())

    options = list_notifiers()
    keys = list(options.keys())

    selected = []

    for name in names:
        if isinstance(name, str):
            try:
                selected.append(options[name])
            except KeyError:
                close_matches = _get_case_insensitive_close_matches(name, keys, n=3)
                hint = (
                    " Close matches: {}.".format(close_matches) if close_matches else ""
                )

                raise AttributeError(
                    '"{}" is not a supported notifier. Choose from {}.{}'.format(
                        name, keys, hint
                    )
                )
        else:
            try:
                if issubclass(name, Notifier):
                    selected.append(name)
            except TypeError:
                raise AttributeError(
                    f"Notifiers must be strings or subclasses of Notifier, not {type(name)}."
                )

    return set(selected)
