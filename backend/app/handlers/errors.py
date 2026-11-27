# Request: the incoming request, passed to every exception handler
# logging: standard librarty, used to record the unexpected error with its traceback
import logging

from fastapi import FastAPI, Request

# FastAPI: the exception raised when request data fails validations (wrong type, limit out of range)
from fastapi.exceptions import RequestValidationError

# JSONResponse: builds an HTTP response with a JSON body and a chosen status code
from fastapi.responses import JSONResponse

from app.errors import EmptyTextError, NoteNotFoundError, TextTooLongError

logger: logging.Logger = logging.getLogger(__name__)


def error_response(status_code: int, message: str) -> JSONResponse:
    """Build an error body in FastAPI standard: {"detail": "..."}."""
    return JSONResponse(status_code=status_code, content={"detail": message})


def handle_bad_text(request: Request, error: Exception) -> JSONResponse:
    """The text of a note is not acceptable: 400."""
    logger.warning("Rejected note text: %s", error)
    return error_response(400, str(error))


def handle_not_found(request: Request, error: Exception) -> JSONResponse:
    """The requested note does not exist: 404."""
    logger.warning("Note not found: %s", error)
    return error_response(404, str(error))


def handle_validation_error(request: Request, error: Exception) -> JSONResponse:
    """FastAPI rejected the request data (wrong type, limit/offset out of range): 422."""
    # The signature must accept Exception (what add_exception_handler expects);
    # isinstance narrows the type, so error.errors() is allowed
    if isinstance(error, RequestValidationError):
        # Log only where (loc) and what (type) is wrong; never "input", it holds the user's data
        problems = [(item["loc"], item["type"]) for item in error.errors()]
        logger.warning("Invalid request data: %s", problems)
    return error_response(422, "Invalid request data")


def handle_unexpected_error(request: Request, error: Exception) -> JSONResponse:
    """Anyhting we did not plan for: log it once with the traceback, answer 500 without details for the client."""
    logger.error("Unhandled error", exc_info=error)
    return error_response(500, "Internal server error")
    # syntax hint:
    # logger.error(template, arg, exc_info=...): write an ERROR record
    # "%s" in the template is filled with the argument after it (lazy: only if the record is emitted)
    # exc_info=error: attach the traceback of this exception object to the record (works outside except too)


def register_error_handlers(app: FastAPI) -> None:
    """Tell the application which exception becomes which response."""
    app.add_exception_handler(EmptyTextError, handle_bad_text)
    app.add_exception_handler(TextTooLongError, handle_bad_text)
    app.add_exception_handler(NoteNotFoundError, handle_not_found)
    app.add_exception_handler(RequestValidationError, handle_validation_error)
    app.add_exception_handler(Exception, handle_unexpected_error)
