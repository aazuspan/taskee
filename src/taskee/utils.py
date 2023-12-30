import difflib
import os
from enum import EnumMeta

CONFIG_PATH = os.path.expanduser("~/.config/taskee.ini")


class SuggestionEnumMeta(EnumMeta):
    """A metaclass that raises with suggested matches and options for failed lookups."""

    def __getitem__(cls, key: str):
        """Get an event by name."""
        try:
            return super().__getitem__(key)
        except KeyError:
            members = list(cls.__members__.keys())

            msg = f"{cls.__name__} '{key}' not in {members}."
            if close_match := difflib.get_close_matches(key.upper(), members, n=1):
                msg += f" Did you mean '{close_match[0]}'?"

            raise KeyError(msg) from None
