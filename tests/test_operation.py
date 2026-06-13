from unittest.mock import patch

from taskee.operation import Operation, list_operations

from .mock_operation import MockOperation


def test_operation_with_unknown_type_and_state():
    """Operations with unrecognized states and types should fall back to UNKNOWN."""
    op = MockOperation(state="MYSTERY_STATE", type="UNEXPECTED_NEW_TYPE")

    assert op.metadata.state == "UNKNOWN"
    assert op.metadata.type == "UNKNOWN"


def test_list_operations_wraps_raw_operations():
    """list_operations should return Operation models for each raw operation."""
    raw = [
        MockOperation(state="RUNNING").model_dump(),
        MockOperation(state="SUCCEEDED").model_dump(),
    ]
    with patch("ee.data.listOperations", return_value=raw) as list_ops:
        operations = list_operations()

    list_ops.assert_called_once()
    assert isinstance(operations, tuple)
    assert all(isinstance(op, Operation) for op in operations)
    assert [op.metadata.state for op in operations] == ["RUNNING", "SUCCEEDED"]
