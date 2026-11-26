# Itearator: type hint for functions that use `yield` (generators)
# psycopg: PostgreSQL driver, used to open one connection per request
# FastAPI: Web framework; creates the application object
# Settings: Reads database parameters from the env
# get_notes_service(): empty provider handlers asks for; router: the group of /api/notes routes
# DbNotesRepository: the layer that runs SQL (receives the connection)
# NotesService: the business rules layer (receives the repository)

# Awaitable, Callable: type hints for call_next (a function that takes a Request and returns an awaitable Response)
from collections.abc import Iterator

# Token: the "receipt" returned by request_id_var.set(),
# used to return value in requesr_id_var back to it's value before change
import psycopg

# Request, Response: Starlette classes re-exported by FastAPI (framework)
from fastapi import FastAPI

from app.config import Settings
from app.handlers.errors import register_error_handlers

# request_id_middleware: gives every request an id and catches unexpected errors
from app.handlers.middleware import request_id_middleware
from app.handlers.notes import get_notes_service, router

# configure_logging(): sets up the root logger (level, format, stdout) once at startup
from app.logging_config import configure_logging
from app.repositories.db.notes import DbNotesRepository

# DbUnitOfWork: commit and rollback of the same connection the repository works on
from app.repositories.db.unit_of_work import DbUnitOfWork

# request_id_var: per-request storage; resolve_request_id: header value or our own id
from app.services.notes import NotesService

settings = Settings()
configure_logging(settings.log_level)


def provide_notes_service() -> Iterator[NotesService]:
    """Open a connection for one request, build the layers on it, close it afterwards"""
    connection = psycopg.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        dbname=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password,
    )
    try:
        repository = DbNotesRepository(connection)
        unit_of_work = DbUnitOfWork(connection)
        yield NotesService(repository, unit_of_work)
    finally:
        connection.close()


# Creating app object
app = FastAPI()


# Set custom error handlers
register_error_handlers(app)

# Same as @app.middleware("http") above a function: a decorator is just a function we can call by hand
app.middleware("http")(request_id_middleware)

# Everytime a handler asks for is get_notes_service, FastAPI calls provide_notes_service instead
# dependency_overrides - means we replace call of get_notes_service with provide_notes_service
app.dependency_overrides[get_notes_service] = provide_notes_service

# Attach the /api/notes routes from handlers/notes.py to the application
app.include_router(router)
