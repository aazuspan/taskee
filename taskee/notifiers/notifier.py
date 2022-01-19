from abc import ABC, abstractmethod
from typing import Dict, List, Set, Type, Union

from taskee.utils import _list_subclasses, _get_subclasses


class Notifier(ABC):
    @abstractmethod
    def send(self, title, message):
        pass


def list_notifiers() -> Dict[str, Type[Notifier]]:
    """List all Notifier subclasses. Return as a dictionary mapping the subclass name to the 
    class.
    
    Returns
    -------
    Dict[str, Type[Notifier]]
        A dictionary mapping the Notifier name to the class.
    """
    return _list_subclasses(Notifier)


def get_notifiers(names: List[Union[str, Type[Notifier]]]) -> Set[Type[Notifier]]:
    """Retrieve a set of subclasses of Notifier.

    Parameters
    ----------
    names : List[Union[str, Type[Notifier]]]
        A list of names or classes of Notifiers to retrieve.

    Returns
    -------
    Set[Type[Notifier]]
        A set of Notifiers.
    """
    return _get_subclasses(names, Notifier)