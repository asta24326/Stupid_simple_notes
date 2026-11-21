from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.handlers.schemas import NoteIn, NoteOut
from app.services.notes import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, NotesService

router = APIRouter(prefix="/api/notes")


def get_notes_service() -> NotesService:
    """Dependency Provider of the service; main.py replaces it with the real one."""
    raise NotImplementedError


# Type alias: is a simple assignment, we put type and description into variable
NotesServiceDependency = Annotated[NotesService, Depends(get_notes_service)]


@router.get("", response_model=list[NoteOut])
def list_notes(
    service: NotesServiceDependency,
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    """Show one page of notes, newest first."""
    # syntax: "before calling this function, call the provider and place it to the service var"
    # syntax: ge = greater or equal, le = less or equal
    # so that's how we limit out input data from browser

    notes = service.list_notes(limit, offset)
    return notes


@router.get("/{note_id}", response_model=NoteOut)
def get_note(note_id: int, service: NotesServiceDependency):
    """Show one note; 404 if doens't exist."""
    note = service.get_note(note_id)
    return note


@router.post("", response_model=NoteOut, status_code=201)
def create_note(body: NoteIn, service: NotesServiceDependency):
    """Create a note from the request body"""
    note = service.create_note(body.text)
    return note


@router.put("/{note_id}", response_model=NoteOut)
def update_note(note_id: int, body: NoteIn, service: NotesServiceDependency):
    """Replace the text of a note; 404 if doens't exist."""
    note = service.update_note(note_id, body.text)
    return note


@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: int, service: NotesServiceDependency):
    """Delete a note; 404 if doesn't exist"""
    service.delete_note(note_id)
