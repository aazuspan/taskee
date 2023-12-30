import re
from enum import Enum

import pytest

from taskee.utils import SuggestionEnumMeta


def test_suggestion_enum():
    """Test that SuggestionEnumMeta raises with suggestions."""

    class TestEnum(Enum, metaclass=SuggestionEnumMeta):
        """A test enum."""

        A = 1
        B = 2
        C = 3

    msg = "TestEnum 'CC' not in ['A', 'B', 'C']. Did you mean 'C'?"
    with pytest.raises(KeyError, match=re.escape(msg)):
        TestEnum["CC"]
