import difflib
import os
from enum import EnumMeta
from typing import Any, Callable

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


def fallback_enum(fallback: Any, name: str = "UNKNOWN") -> Callable:
    """An enum decorator that falls back to a default value for invalid members.

    Parameters
    ----------
    fallback : Any
        The value of the fallback member. The type of this value must match the enum
        type.
    name : str
        The name of the fallback member.
    """

    def _fallback_enum(enumeration: Any) -> Any:
        enum_type = getattr(enumeration, "_member_type_", type(None))
        if not isinstance(fallback, enum_type):
            raise TypeError(
                "Fallback value must match the enum type. "
                f"Expected {enum_type} but got {type(fallback)}."
            )

        def _get_fallback_member(cls: Any, _: Any) -> Any:
            member_cls = type(fallback)
            member: Any = member_cls.__new__(cls, fallback)
            member._name_ = name
            member._value_ = fallback

            return member

        enumeration._missing_ = classmethod(_get_fallback_member)
        return enumeration

    return _fallback_enum
