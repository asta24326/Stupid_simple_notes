# pytest: test framework; parametrize runs one test function once per listed input
import pytest

# resolve_request_id: the function under test
from app.request_context import SAFE_REQUEST_ID_PATTERN, resolve_request_id


@pytest.mark.parametrize("header_value", ["abc-123", "ABC_def", "x" * 64])
def test_safe_header_value_is_kept(header_value: str) -> None:
    assert resolve_request_id(header_value) == header_value


# Syntax hints:
# 1) @pytest.mark.parametrize("name", [values]): run the test once per value;
# each value is passed in the parameter called "name"
# 2) "x" * 64: a string repeated 64 times (the length limit of a safe id)


@pytest.mark.parametrize("header_value", [None, "", "id\nfake log line", "hello world", "x" * 65, "абв"])
def test_unsafe_header_value_is_replaced(header_value: str | None) -> None:
    request_id = resolve_request_id(header_value)

    assert request_id != header_value
    assert len(request_id) == 8
    assert SAFE_REQUEST_ID_PATTERN.fullmatch(request_id) is not None
