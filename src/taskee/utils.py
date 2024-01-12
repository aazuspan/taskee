import difflib
import os
from enum import Enum, EnumMeta
from typing import Any

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


# def fallback_enum(name: str="UNKNOWN", fallback: Any="UNKNOWN") -> Enum:
#     """An enum decorator that falls back to a default value for invalid members.
    
#     Parameters
#     ----------
#     name : str
#         The name of the fallback member.
#     fallback : Any
#         The value of the fallback member. The type of this value should match the enum
#         type.
#     """

#     def _fallback_enum(enumeration: Enum) -> Enum:
#         print(enumeration)
#         @classmethod
#         def _get_fallback_member(cls: Enum, _: Any) -> Enum:
#             member_cls = type(fallback)
#             member = member_cls.__new__(cls, fallback)
#             member._name_ = name
#             member._value_ = fallback

#             return member

#         if not isinstance(fallback, enumeration._member_type_):
#             raise TypeError(
#                 "Fallback value must match the enum type. "
#                 f"Expected {enumeration._member_type_} but got {type(fallback)}."
#             )
#         enumeration._missing_ = _get_fallback_member
#         return enumeration

#     return _fallback_enum
        
def fallback_enum(fallback: Any, name: str="UNKNOWN") -> Enum:
    """An enum decorator that falls back to a default value for invalid members.
    
    Parameters
    ----------
    fallback : Any
        The value of the fallback member. The type of this value must match the enum
        type.
    name : str
        The name of the fallback member.
    """
    def _fallback_enum(enumeration: Enum) -> Enum:
        @classmethod
        def _get_fallback_member(cls: Enum, _: Any) -> Enum:
            member_cls = type(fallback)
            member = member_cls.__new__(cls, fallback)
            member._name_ = name
            member._value_ = fallback

            return member

        if not isinstance(fallback, enumeration._member_type_):
            raise TypeError(
                "Fallback value must match the enum type. "
                f"Expected {enumeration._member_type_} but got {type(fallback)}."
            )
        enumeration._missing_ = _get_fallback_member
        return enumeration

    return _fallback_enum