from __future__ import annotations

import random
import string
from datetime import datetime

from taskee.operation import (
    Operation,
    OperationError,
    OperationMetadata,
    OperationState,
    OperationType,
)

COMPLETED_STATES = (
    OperationState.SUCCEEDED,
    OperationState.FAILED,
    OperationState.CANCELLED,
)


class MockOperation(Operation):
    """A mock Operation that can be created and updated manually."""

    def __init__(
        self,
        state: OperationState,
        *,
        description: str = "mock_task",
        time_since_creation_ms=600_000,
        started_after_ms=60_000,
        update_time_ms=None,
        error_message: str | None = None,
        type: OperationType = OperationType.EXPORT_IMAGE,
    ):
        now_ms = int(datetime.now().timestamp() * 1000)
        creation_time_ms = now_ms - time_since_creation_ms

        meta = OperationMetadata(
            state=state,
            description=description,
            createTime=creation_time_ms,
            startTime=creation_time_ms + started_after_ms,
            updateTime=update_time_ms or now_ms,
            type=type,
        )
        super().__init__(name=_random_name(), metadata=meta)
        self._set_metadata(error_message=error_message)

    def _set_metadata(self, error_message: str = None):
        """Set optional metadata based on current state."""
        if self.metadata.state == OperationState.FAILED:
            self.error = OperationError(code=3, message=error_message)
        elif error_message:
            raise ValueError("Error message provided for non-failed operation")

        elif self.metadata.state == OperationState.CANCELLED:
            self.error = OperationError(code=1, message="Cancelled.")

        elif self.metadata.state == OperationState.PENDING:
            self.metadata.startTime = datetime.utcfromtimestamp(0)

        elif self.metadata.state == OperationState.SUCCEEDED:
            self.metadata.destinationUris = ("https://drive.google.com/",)
            self.metadata.batchEecuUsageSeconds = 42.0
            self.metadata.progress = 1.0

        if self.metadata.state in COMPLETED_STATES:
            self.metadata.endTime = self.metadata.updateTime
            self.done = True

        return self

    def update(
        self,
        state: OperationState = None,
        *,
        retry: bool = False,
        time_delta: int = 0,
        error_message: str = None,
    ) -> Operation:
        """Update to a new state."""
        if self.metadata.state in COMPLETED_STATES:
            raise ValueError("Cannot update a completed operation.")

        if retry:
            self.metadata.attempt += 1

        if time_delta:
            self.metadata.updateTime += time_delta

        if state:
            self.metadata.state = state
            self._set_metadata(error_message=error_message)

        return self


def _random_name() -> str:
    """Return a randomized operation name that resembles a real one."""
    chars = string.ascii_uppercase + string.digits
    op_id = "".join([random.choice(chars) for i in range(24)])
    return f"projects/earthengine-legacy/operations/{op_id}"
