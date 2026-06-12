from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict

from taskee import events
from taskee.utils import fallback_enum


@fallback_enum("UNKNOWN")
class OperationState(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLING = "CANCELLING"
    CANCELLED = "CANCELLED"


@fallback_enum("UNKNOWN")
class OperationType(StrEnum):
    EXPORT_FEATURES = "EXPORT_FEATURES"
    EXPORT_IMAGE = "EXPORT_IMAGE"
    EXPORT_VIDEO = "EXPORT_VIDEO"
    EXPORT_TILES = "EXPORT_TILES"
    EXPORT_CLASSIFIER = "EXPORT_CLASSIFIER"
    INGEST = "INGEST"
    INGEST_IMAGE = "INGEST_IMAGE"
    INGEST_TABLE = "INGEST_TABLE"


class OperationStage(BaseModel):
    """A stage from a running operation."""

    displayName: str
    totalWorkUnits: float | None = None
    completeWorkUnits: float | None = None
    description: str


class OperationError(BaseModel):
    """An error from a failed operation."""

    code: int
    message: str | None = "Unknown error."


class OperationMetadata(BaseModel):
    """Metadata about an Operation."""

    model_config = ConfigDict(validate_assignment=True)

    state: OperationState
    type: OperationType
    description: str
    createTime: datetime
    updateTime: datetime
    startTime: datetime
    endTime: datetime | None = None
    attempt: int = 1
    progress: float = 0.0
    stages: tuple[OperationStage, ...] | None = None
    scriptUri: str | None = None
    destinationUris: tuple[str, ...] | None = None
    batchEecuUsageSeconds: float | None = 0.0


class Operation(BaseModel):
    """An Operation returned from ee.data.listOperations()."""

    name: str
    metadata: OperationMetadata
    done: bool = False
    error: OperationError | None = None

    model_config = ConfigDict(validate_assignment=True)

    @property
    def time_since_creation(self) -> float:
        """Return the time since the operation was created in seconds."""
        now = datetime.now(tz=UTC)
        return (now - self.metadata.createTime).total_seconds()

    @property
    def runtime(self) -> float:
        """Return the total runtime of the operation in seconds."""
        # Unstarted tasks list their start time as 1970-01-01T00:00:00Z UTC
        if not self.metadata.startTime.timestamp():
            return 0.0

        return (self.metadata.updateTime - self.metadata.startTime).total_seconds()

    def __lt__(self, other: Operation) -> bool:
        """Compare two operations based on their status and creation time.

        With ascending sort, this will put active and recent tasks first, in that order.
        """
        if not isinstance(other, Operation):
            return NotImplemented
        if not self.done and other.done:
            return True
        if self.done and not other.done:
            return False

        return self.metadata.createTime > other.metadata.createTime

    def __eq__(self, other: Any) -> bool:
        """Use the unique operation name to compare equality."""
        if not isinstance(other, Operation):
            return NotImplemented

        return self.name == other.name

    def get_event(self, prev: Operation | None = None) -> events._Event | None:
        """Compare the operation to a previous state and return the appropriate event.

        The previous state can be None in the case of newly created tasks. In this case,
        the most recent event will be guessed, e.g. "Created" if the task is pending
        or "Completed" if the task is already finished.
        """
        if prev is None:
            if self.metadata.state == OperationState.PENDING:
                return events.CreatedEvent(task=self)

            init_state = {
                "metadata": self.metadata.model_copy(
                    update={"state": OperationState.PENDING}
                )
            }
            prev = self.model_copy(update=init_state)

        if prev.metadata.state != self.metadata.state:
            if self.metadata.state == OperationState.RUNNING:
                return events.StartedEvent(task=self)
            if self.metadata.state == OperationState.SUCCEEDED:
                return events.CompletedEvent(task=self)
            if self.metadata.state == OperationState.FAILED:
                return events.FailedEvent(task=self)
            if self.metadata.state == OperationState.CANCELLED:
                return events.CancelledEvent(task=self)

        elif prev.metadata.attempt != self.metadata.attempt:
            return events.AttemptedEvent(task=self)

        return None


ACTIVE_OPERATION_STATES = (
    OperationState.PENDING,
    OperationState.RUNNING,
    OperationState.CANCELLING,
)

FINISHED_OPERATION_STATES = (
    OperationState.CANCELLED,
    OperationState.FAILED,
    OperationState.SUCCEEDED,
)
