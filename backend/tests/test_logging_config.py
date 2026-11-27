# Standard library: logging.makeLogRecord builds a LogRecord without any logger
import logging

# Standard library: type of a fixture that yields once (Iterator[None] = "gives control, returns nothing")
from collections.abc import Iterator

# pytest: fixtures and the usefixtures marker
import pytest

# Our code: the filter under test
# Our code: the function under test
from app.logging_config import RequestIdFilter

# Our code: the storage the filter reads the id from
from app.request_context import request_id_var


def test_filter_uses_dash_when_no_request_id_set() -> None:
    """Outside of a request the filter puts the default "-" into the record."""

    # Empty dict = no extra attributes; we get a plain record, like a logger would create
    record = logging.makeLogRecord({})

    request_id_filter = RequestIdFilter()
    # filter() returns True when the record must be kept, and adds record.request_id
    keep_record = request_id_filter.filter(record)

    assert keep_record is True
    assert record.request_id == "-"


def test_filter_uses_request_id_from_context() -> None:
    """Inside a request the filter copies the stored id into the record."""
    record = logging.makeLogRecord({})

    # set() returns a Token, reset() needs it to restore the previous value
    token = request_id_var.set("abc123")
    try:
        RequestIdFilter().filter(record)
    finally:
        # Always restore, so the id does not leak into other tests
        request_id_var.reset(token)

    assert record.request_id == "abc123"


@pytest.fixture
def restore_root_logger() -> Iterator[None]:
    """Remember the root logger state, run the test, put the state back"""
    root_logger = logging.getLogger()
    # [:] makes a copy of the list; the original list will be changed by dictConfig
    saved_handlers = root_logger.handlers[:]
    saved_level = root_logger.level

    # Everything before yield is setup, everything after it is cleanup
    yield

    # Slice assignment replaces the contents of the same list object
    root_logger.handlers[:] = saved_handlers
    root_logger.setLevel(saved_level)
