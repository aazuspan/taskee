import datetime

from taskee.utils import (
    _datetime_to_millis,
    _millis_to_datetime,
)


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
