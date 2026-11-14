import pytest

from app.errors import EmptyTextError, TextTooLongError, NoteNotFoundError
from app.services.notes import MAX_TEXT_LENGTH, NoteService
from tests.fakes import FakeNotesRepository

def make_service() -> NoteService:
    """Build a service on a fresh repository, so every test starts clean"""
    return NoteService(FakeNotesRepository())

def test_create_note_returns_note_with_text():
    """A valid text gives back a stored note with that text and the first id"""
    service = make_service()

    created_note = service.create_note("Buy milk")

    assert created_note.text == "Buy milk"
    assert created_note.id == 1


def test_create_note_rejects_empty_text():
    service = make_service()

    # We create context manager object, and make it wait for EmptyTextError. If no, pytest raises "Failed" error with message "DID NOT RAISE <class 'EmptyTextError'>
    with pytest.raises(EmptyTextError):
        service.create_note('')
    # Same look:
    # try:
    #    service.create_note("")
    # except EmptyTextError:
    #    return
    # assert False, "EmptyTextError was not raised" (manually failing and throwing up AssertionError with message "EmptyTextError was not raised")

def test_create_note_accepts_whitespace_only_text():
    service = make_service()

    created_note = service.create_note("     ")

    assert created_note.text == "     "

def test_create_note_accepts_text_of_max_length():
    """Exactly MAX_TEXT_LENGTH characters is the longest text that is still allowed."""
    service = make_service()

    created_note = service.create_note("a" * MAX_TEXT_LENGTH)

    assert len(created_note.text) == MAX_TEXT_LENGTH

def test_create_note_rejects_text_longer_than_max_length():
    """One character over the limit must be refused."""
    service = make_service()

    with pytest.raises(TextTooLongError):
        service.create_note("a" * (MAX_TEXT_LENGTH + 1))

def test_list_notes_returns_newest_first():
    """The list must start with the most recently created note."""
    service = make_service()
    service.create_note("first")
    service.create_note("second")

    notes = service.list_notes()

    assert [note.text for note in notes] == ["second", "first"]

def test_get_note_returns_the_note():
    """An existing note can be fetched by its id."""
    service = make_service()
    created_note = service.create_note("find me")

    found_note = service.get_note(created_note.id)

    assert found_note.text == "find me"

def test_get_note_raises_when_note_is_missing():
    """Asking for an id that does not exist is a NoteNotFoundError."""
    service = make_service()

    with pytest.raises(NoteNotFoundError):
        service.get_note(99)

def test_update_note_changes_text():
    """Updating an existing note replaces its text and keeps its id."""
    service = make_service()
    created_note = service.create_note("old")

    updated_note = service.update_note(created_note.id, "new")

    assert updated_note.text == "new"
    assert updated_note.id == created_note.id

def test_update_note_raises_when_note_is_missing():
    """Updating an id that does not exist is a NoteNotFoundError."""
    service = make_service()

    with pytest.raises(NoteNotFoundError):
        service.update_note(99, "new")

def test_update_note_rejects_empty_text():
    """The same text rules apply to updates as to creation."""
    service = make_service()
    created_note = service.create_note("old")

    with pytest.raises(EmptyTextError):
        service.update_note(created_note.id, "")

def test_delete_note_removes_it_from_the_list():
    """After deleting, the note is no longer listed."""
    service = make_service()
    created_note = service.create_note("to delete")

    service.delete_note(created_note.id)

    assert service.list_notes() == []

def test_delete_note_raises_when_note_is_missing():
    """Deleting an id that does not exist is a NoteNotFoundError."""
    service = make_service()

    with pytest.raises(NoteNotFoundError):
        service.delete_note(99)






