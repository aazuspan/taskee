"""Tests for the vendored minimal Pushbullet client."""

import json
from unittest.mock import MagicMock, patch

import pytest
import requests

from taskee.vendor.pushbullet import InvalidKeyError, Pushbullet, PushError


def _response(status_code, json_data=None, text=""):
    """Build a mock ``requests`` response."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.text = text
    resp.json.return_value = json_data
    return resp


@pytest.fixture
def mock_session():
    """Patch ``requests.Session`` and return the mock session instance.

    The session defaults to a valid key (``GET /users/me`` returns 200) so that the
    ``Pushbullet`` constructor succeeds unless a test overrides it.
    """
    with patch("taskee.vendor.pushbullet.pushbullet.requests.Session") as Session:
        session = Session.return_value
        session.get.return_value = _response(200)
        yield session


def test_constructor_sets_auth_and_verifies_key(mock_session):
    """The constructor should authenticate with the key and verify it."""
    pb = Pushbullet("my_key")

    assert pb.api_key == "my_key"
    assert mock_session.auth == ("my_key", "")
    mock_session.get.assert_called_once_with(Pushbullet.ME_URL)


@pytest.mark.parametrize("status_code", [401, 403])
def test_constructor_rejects_invalid_key(mock_session, status_code):
    """An unauthorized response while verifying the key raises InvalidKeyError."""
    mock_session.get.return_value = _response(status_code, text="invalid")

    with pytest.raises(InvalidKeyError, match="invalid"):
        Pushbullet("bad_key")


def test_constructor_raises_for_other_errors(mock_session):
    """A non-auth error response while verifying the key propagates."""
    resp = _response(500)
    resp.raise_for_status.side_effect = requests.HTTPError("boom")
    mock_session.get.return_value = resp

    with pytest.raises(requests.HTTPError, match="boom"):
        Pushbullet("my_key")


def test_push_note_sends_payload_and_returns_response(mock_session):
    """push_note posts a note payload and returns the parsed JSON response."""
    mock_session.post.return_value = _response(200, json_data={"iden": "abc"})

    pb = Pushbullet("my_key")
    result = pb.push_note("Title", "Body")

    assert result == {"iden": "abc"}
    (url,) = mock_session.post.call_args.args
    assert url == Pushbullet.PUSH_URL
    payload = json.loads(mock_session.post.call_args.kwargs["data"])
    assert payload == {"type": "note", "title": "Title", "body": "Body"}


@pytest.mark.parametrize("status_code", [401, 403])
def test_push_note_rejects_invalid_key(mock_session, status_code):
    """An unauthorized response when pushing raises InvalidKeyError."""
    pb = Pushbullet("my_key")
    mock_session.post.return_value = _response(status_code, text="nope")

    with pytest.raises(InvalidKeyError, match="nope"):
        pb.push_note("Title", "Body")


def test_push_note_raises_on_failure(mock_session):
    """A non-200, non-auth response when pushing raises PushError."""
    pb = Pushbullet("my_key")
    mock_session.post.return_value = _response(500, text="server error")

    with pytest.raises(PushError, match="server error"):
        pb.push_note("Title", "Body")
