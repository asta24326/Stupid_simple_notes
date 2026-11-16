from typing import Annotated

from fastapi import APIRouter, Depends

from app.handlers.schemas import NoteOut
from app.services.notes import NotesService

router = APIRouter(prefix="/api/notes")


def get_notes_service() -> NotesService:
    """Dependency Provider of the service; main.py replaces it with the real one."""
    raise NotImplementedError


# Type alias: is a simple assignment, we put type and description into variable
NotesServiceDependency = Annotated[NotesService, Depends(get_notes_service)]


@router.get("", response_model=list[NoteOut])
def list_notes(service: NotesServiceDependency):
    """Show all notes, newest first."""
    # syntax: "before calling this function, call the provider and place it to the service var"
    notes = service.list_notes()
    return notes
