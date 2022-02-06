from abc import ABC, abstractmethod
from typing import Mapping, Set, Tuple, Type

from taskee.utils import _get_subclasses, _list_subclasses


class Notifier(ABC):
    @abstractmethod
    def send(self, title: str, message: str) -> None:
        pass


def list_notifiers() -> Mapping[str, Type[Notifier]]:
    """List all Notifier subclasses. Return as a dictionary mapping the subclass name to the
    class.

    Returns
    -------
    Dict[str, Type[Notifier]]
        A dictionary mapping the Notifier name to the class.
    """
    return _list_subclasses(Notifier)


def get_notifiers(names: Tuple[str, ...]) -> Set[Type[Notifier]]:
    """Retrieve a set of subclasses of Notifier.

    Parameters
    ----------
    names : Tuple[str, ...]
        A list of names of Notifiers to retrieve.

    Returns
    -------
    Set[Type[Notifier]]
        A set of Notifiers.
    """
    return _get_subclasses(names, Notifier)
