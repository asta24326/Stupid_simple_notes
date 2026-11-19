# Itearator: type hint for functions that use `yield` (generators)
# psycopg: PostgreSQL driver, used to open one connection per request
# FastAPI: Web framework; creates the application object
# Settings: Reads database parameters from the env
# get_notes_service(): empty provider handlers asks for; router: the group of /api/notes routes
# DbNotesRepository: the layer that runs SQL (receives the connection)
# NotesService: the business rules layer (receives the repository)

from collections.abc import Iterator

import psycopg
from fastapi import FastAPI

from app.config import Settings
from app.handlers.errors import register_error_handlers
from app.handlers.notes import get_notes_service, router
from app.repositories.db.notes import DbNotesRepository
from app.services.notes import NotesService

settings = Settings()


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
        yield NotesService(repository)
    finally:
        connection.close()


app = FastAPI()
register_error_handlers(app)

# Everytime a handler asks for get_notes_service, FastAPI calls provide_notes_service instead
# dependency_overrides - means we replace call of get_notes_service with provide_notes_service
app.dependency_overrides[get_notes_service] = provide_notes_service

# Attach the /api/notes routes from handlers/notes.py to the application
app.include_router(router)
