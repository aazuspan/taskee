import datetime

import pytest

from taskee.utils import (
    _datetime_to_millis,
    _get_subclasses,
    _list_subclasses,
    _millis_to_datetime,
)


class MockClass:
    pass


class MockSubclassOne(MockClass):
    pass


class MockSubclassTwo(MockClass):
    pass


def test_list_subclasses():
    subclasses = _list_subclasses(MockClass)
    assert "MockSubclassOne" in subclasses.keys()
    assert MockSubclassOne in subclasses.values()


def test_get_subclasses_from_strings():
    """Test that we can get subclasses using their string names, case-insensitive."""
    subclasses = _get_subclasses(["MockSubclassOne", "mocksubclasstwo"], MockClass)
    assert subclasses == {MockSubclassOne, MockSubclassTwo}


def test_get_all_subclasses():
    """Test that we can get all subclasses using keyword 'all'."""
    subclasses = _get_subclasses(["all"], MockClass)
    assert subclasses == {MockSubclassOne, MockSubclassTwo}


def test_get_subclasses_gives_close_match():
    """Test that _get_subclasses raises an AttributeError and gives a correct close match when an invalid input is given."""
    with pytest.raises(AttributeError, match="MockSubclassOne"):
        _get_subclasses(["mocksubclasson"], MockClass)


def test_datetime_to_millis():
    """Test that a datetime in UTC is correctly converted to Unix milliseconds"""
    dt = datetime.datetime(year=2020, month=4, day=14, tzinfo=datetime.timezone.utc)
    millis = _datetime_to_millis(dt)
    assert millis == 1586822400000


def test_millis_to_datetime():
    millis = 1586822400000
    dt = _millis_to_datetime(millis, tz=datetime.timezone.utc)
    assert dt == datetime.datetime(
        year=2020, month=4, day=14, tzinfo=datetime.timezone.utc
    )
