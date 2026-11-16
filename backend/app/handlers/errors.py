# Request: the incoming request, passed to every exception handler
from fastapi import FastAPI, Request

# JSONResponse: builds an HTTP response with a JSON body and a chosen status code
from fastapi.responses import JSONResponse

from app.errors import EmptyTextError, NoteNotFoundError, TextTooLongError


def error_response(status_code: int, message: str) -> JSONResponse:
    """Build an error body in FastAPI standard: {"detail": "..."}."""
    return JSONResponse(status_code=status_code, content={"detail": message})


def handle_bad_text(request: Request, error: Exception) -> JSONResponse:
    """The text of a note is not acceptable: 400."""
    return error_response(400, str(error))


def handle_not_found(request: Request, error: Exception) -> JSONResponse:
    """The requested note does not exist: 404."""
    return error_response(404, str(error))


def handle_unexpected_error(request: Request, error: Exception) -> JSONResponse:
    """Anyhting we did not plan for: 500 wohtoit details for the client."""
    return error_response(500, "Internal server error")


def register_error_handlers(app: FastAPI) -> None:
    """Tell the application which exception becomes which response."""
    app.add_exception_handler(EmptyTextError, handle_bad_text)
    app.add_exception_handler(TextTooLongError, handle_bad_text)
    app.add_exception_handler(NoteNotFoundError, handle_not_found)
    app.add_exception_handler(Exception, handle_unexpected_error)
