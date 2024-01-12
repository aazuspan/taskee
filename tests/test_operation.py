from .mock_operation import MockOperation


def test_operation_with_unknown_type_and_state():
    """Operations with unrecognized states and types should fall back to UNKNOWN."""
    op = MockOperation(state="MYSTERY_STATE", type="UNEXPECTED_NEW_TYPE")

    assert op.metadata.state == "UNKNOWN"
    assert op.metadata.type == "UNKNOWN"
