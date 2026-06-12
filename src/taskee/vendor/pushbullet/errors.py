"""Exceptions for the vendored Pushbullet client."""

from __future__ import annotations


class PushbulletError(Exception):
    """Base class for all Pushbullet errors."""


class InvalidKeyError(PushbulletError):
    """Raised when the Pushbullet API rejects the provided access token."""


class PushError(PushbulletError):
    """Raised when a push fails to send."""
