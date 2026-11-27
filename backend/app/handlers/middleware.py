# Awaitable, Callable: type hints for call_next (takes a Request, returns an awaitable Response)
# logging: standard library, used to write one log line per request
import logging

# time: standard library; perf_counter() is a precise clock for measuring durations
import time
from collections.abc import Awaitable, Callable

# Token: the "receipt" returned by request_id_var.set(), used to undo it
from contextvars import Token

# Request, Response: Starlette classes re-exported by FastAPI (framework)
from fastapi import Request, Response

# handle_unexpected_error: logs the error once and builds the 500 response
from app.handlers.errors import handle_unexpected_error

# request_id_var: per-request storage; resolve_request_id: header value or our own id
from app.request_context import request_id_var, resolve_request_id

logger = logging.getLogger(__name__)
REQUEST_ID_HEADER = "X-Request-Id"


async def process_request(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Run the request, turn an unexpected error into a 500 response and log one line about it."""
    started_at: float = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception as error:
        response = handle_unexpected_error(request, error)
    duration_ms: float = (time.perf_counter() - started_at) * 1000
    logger.info("%s %s -> %s (%.1f ms)", request.method, request.url.path, response.status_code, duration_ms)
    return response


# Syntax hints:
# 1) call_next - Callable[[Request], Awaitable[Response]]: takes a Request, returns an awaitable Response
# 2) perf_counter(): precise monotonic clock in seconds; (now - started_at) = elapsed time; * 1000 = milliseconds
# 3) "%s" = any value as text, "%.1f" = float with 1 digit after the dot; arguments are filled in order, lazily
# 4) request.method = "GET"/"POST"..., request.url.path = path without the query string, response.status_code = int
# 5) logger.info("%s %s -> %s (%.1f ms)", request.method, request.url.path,
# response.status_code, duration_ms) - hand the response back to request_id_middleware


async def request_id_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Give every request an id, keep it while the request lives, return it in the response header."""
    request_id: str = resolve_request_id(request.headers.get(REQUEST_ID_HEADER))
    token: Token[str] = request_id_var.set(request_id)
    try:
        response: Response = await process_request(request, call_next)
    finally:
        request_id_var.reset(token)
    response.headers[REQUEST_ID_HEADER] = request_id
    return response


# Syntax hints for request_id_middleware:
# 1) @app.middleware("http") - decorator: registers the function as middleware for every HTTP request
# 2) async def / await - coroutine function; await pauses it until the awaited call finishes
# 4) request.headers.get(name) - header value or None; name is case-insensitive
# 5) request_id_var.set(value) - stores the id for the current request, returns a Token (receipt for undoing the set)
# 6) await call_next(request) - passes the request inward (router, handler, service) and waits for the response
# 7) except Exception as error: catch any "normal" error (not task cancellation)
# and bind the exception object to the name "error"
# 8) handle_unexpected_error(request, error): logs the error once and returns a ready 500 response,
# so `response` always has a value after try/except
# 9) request_id_var.reset(token) - restores the value that was stored before our set()
# 10) response.headers[name] = ... - adds or overwrites a header on the outgoing response
