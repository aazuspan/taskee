"""A minimal Pushbullet API client.

This is a trimmed-down, vendored replacement for the archived ``pushbullet.py``
package (https://github.com/rbrcsk/pushbullet.py). It keeps only the note-pushing
functionality that taskee uses and drops the file-upload support that pulled in the
``python-magic``/libmagic dependency, which caused installation issues on some
platforms.

Adapted from ``pushbullet.py`` (MIT License, Copyright (c) 2014 Richard Borcsik).
See ``LICENSE`` in this directory for the full license text.
"""

from __future__ import annotations

import json

import requests

from .errors import InvalidKeyError, PushError


class Pushbullet:
    """A client for sending note pushes through the Pushbullet API."""

    ME_URL = "https://api.pushbullet.com/v2/users/me"
    PUSH_URL = "https://api.pushbullet.com/v2/pushes"

    def __init__(self, api_key: str = "") -> None:
        self.api_key = api_key

        self._session = requests.Session()
        self._session.auth = (self.api_key, "")
        self._session.headers.update({"Content-Type": "application/json"})

        # Verify the key up front so callers can react to bad credentials, matching
        # the behavior of the original package's constructor.
        self._verify_key()

    def _verify_key(self) -> None:
        """Confirm the API key is valid by fetching the current user."""
        resp = self._session.get(self.ME_URL)
        if resp.status_code in (401, 403):
            raise InvalidKeyError(resp.text)
        resp.raise_for_status()

    def push_note(self, title: str, body: str) -> dict:
        """Send a note push to every device on the account and return the response.

        Parameters
        ----------
        title : str
            The title of the note.
        body : str
            The body of the note.
        """
        data = {"type": "note", "title": title, "body": body}
        resp = self._session.post(self.PUSH_URL, data=json.dumps(data))
        if resp.status_code in (401, 403):
            raise InvalidKeyError(resp.text)
        if resp.status_code != requests.codes.ok:
            raise PushError(resp.text)
        return resp.json()
