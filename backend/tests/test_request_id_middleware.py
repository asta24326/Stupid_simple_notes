# pytest: test framework
# Standard library: logging levels (logging.INFO)
import logging

import pytest

# FastAPI: the application class; TestClient: calls the app in the same process, no real server
from fastapi import FastAPI
from fastapi.testclient import TestClient

# BaseHTTPMiddleware: Starlette wrapper that turns our async function into middleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.handlers.errors import register_error_handlers
from app.handlers.middleware import REQUEST_ID_HEADER, request_id_middleware


def build_test_app() -> FastAPI:
    """A small application with the same error handlers and middleware as the real one."""

    test_app = FastAPI()
    register_error_handlers(test_app)
    test_app.add_middleware(BaseHTTPMiddleware, dispatch=request_id_middleware)

    @test_app.get("/middleware_test")
    def middleware_test() -> dict[str, str]:
        return {"status": "ok"}

    # Route that simulates an unexpected bug inside a handler
    @test_app.get("/failing_route")
    def failing_route() -> dict[str, str]:
        raise RuntimeError("secret internal detail")

    return test_app


@pytest.fixture
def client() -> TestClient:
    # No yield: there is nothing to clean up after the test
    return TestClient(build_test_app())


def test_response_has_generated_request_id(client: TestClient) -> None:
    response = client.get("/middleware_test")

    assert response.status_code == 200
    assert len(response.headers[REQUEST_ID_HEADER]) == 8


def test_response_keeps_request_id_from_header(client: TestClient) -> None:
    response = client.get("/middleware_test", headers={REQUEST_ID_HEADER: "probe-1"})

    assert response.headers[REQUEST_ID_HEADER] == "probe-1"


def test_unsafe_request_id_is_replaced(client: TestClient) -> None:
    response = client.get("/middleware_test", headers={REQUEST_ID_HEADER: "bad value"})

    assert response.headers[REQUEST_ID_HEADER] != "bad value"


def test_unexpected_error_returns_500_and_logs_once(client: TestClient, caplog: pytest.LogCaptureFixture) -> None:
    # Capture records of level INFO and above while the block runs
    with caplog.at_level(logging.INFO):
        response = client.get("/failing_route")

    assert response.status_code == 500
    assert "x-request-id" in response.headers
    assert "secret internal detail" not in response.text

    error_records = [record for record in caplog.records if record.levelno >= logging.ERROR]

    assert len(error_records) == 1
    assert error_records[0].name == "app.handlers.errors"
    assert error_records[0].exc_info is not None
    assert "secret internal detail" in caplog.text
