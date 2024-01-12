import re
from enum import Enum

import pytest

from taskee.utils import SuggestionEnumMeta, fallback_enum


def test_suggestion_enum():
    """Test that SuggestionEnumMeta raises with suggestions."""

    class TestEnum(Enum, metaclass=SuggestionEnumMeta):
        A = 1
        B = 2
        C = 3

    msg = "TestEnum 'CC' not in ['A', 'B', 'C']. Did you mean 'C'?"
    with pytest.raises(KeyError, match=re.escape(msg)):
        TestEnum["CC"]


def test_fallback_enum():
    @fallback_enum(fallback="UNKNOWN")
    class TestStrEnum(str, Enum):
        A = "A"
        B = "B"
        C = "C"

    assert TestStrEnum("D") == "UNKNOWN"

    with pytest.raises(TypeError, match="value must match the enum type"):

        @fallback_enum(fallback=1)
        class TestStrEnum(str, Enum):
            A = "A"
            B = "B"
            C = "C"
