# Standard library: logging levels (logging.INFO)
import logging

import pytest

from app.errors import EmptyTextError, NoteNotFoundError, TextTooLongError
from app.services.notes import MAX_TEXT_LENGTH, NotesService
from tests.fakes import FakeNotesRepository, FakeUnitOfWork


def make_service() -> NotesService:
    """Build a service on a fresh repository and a fake transaction boundary."""
    return NotesService(FakeNotesRepository(), FakeUnitOfWork())


def test_create_note_returns_note_with_text():
    """A valid text gives back a stored note with that text and the first id"""
    service = make_service()

    created_note = service.create_note("Buy milk")

    assert created_note.text == "Buy milk"
    assert created_note.id == 1


def test_create_note_rejects_empty_text():
    service = make_service()

    # We create context manager object, and make it wait for EmptyTextError.
    # If no, pytest raises "Failed" error with message "DID NOT RAISE <class 'EmptyTextError'>
    with pytest.raises(EmptyTextError):
        service.create_note("")
    # Same look:
    # try:
    #    service.create_note("")
    # except EmptyTextError:
    #    return
    # assert False, "EmptyTextError was not raised"
    # (manually failing and throwing up AssertionError with message "EmptyTextError was not raised")


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


def test_create_note_commits_once():
    """A successful write is one committed transaction."""
    unit_of_work = FakeUnitOfWork()
    service = NotesService(FakeNotesRepository(), unit_of_work)

    service.create_note("saved")

    assert unit_of_work.commits == 1
    assert unit_of_work.rollbacks == 0


def test_invalid_text_does_not_open_a_transaction():
    """Text is checked before the block, so a rejected note touches no transaction."""
    unit_of_work = FakeUnitOfWork()
    service = NotesService(FakeNotesRepository(), unit_of_work)

    with pytest.raises(EmptyTextError):
        service.create_note("")

    assert unit_of_work.commits == 0
    assert unit_of_work.rollbacks == 0


def test_update_of_a_missing_note_rolls_back():
    """NoteNotFoundError raised inside the block ends with rollback."""
    unit_of_work = FakeUnitOfWork()
    service = NotesService(FakeNotesRepository(), unit_of_work)

    with pytest.raises(NoteNotFoundError):
        service.update_note(99, "new")

    assert unit_of_work.commits == 0
    assert unit_of_work.rollbacks == 1


def test_delete_of_a_missing_note_rolls_back():
    """The same for delete."""
    unit_of_work = FakeUnitOfWork()
    service = NotesService(FakeNotesRepository(), unit_of_work)

    with pytest.raises(NoteNotFoundError):
        service.delete_note(99)

    assert unit_of_work.rollbacks == 1


def test_list_notes_returns_the_requested_page():
    """limit and offset cut one page out of the newest-first list."""
    service = make_service()
    for number in range(5):
        service.create_note(f"note {number}")

    page = service.list_notes(limit=2, offset=1)

    assert [note.text for note in page] == ["note 3", "note 2"]


def test_list_notes_offset_beyond_the_end_gives_an_empty_page():
    """Asking for a page past the last note is not an error."""
    service = make_service()
    service.create_note("only one")

    assert service.list_notes(limit=10, offset=5) == []


def test_list_notes_without_arguments_uses_the_default_page():
    """The old call without arguments still returns the notes."""
    service = make_service()
    service.create_note("first")

    assert len(service.list_notes()) == 1


def test_create_note_logs_event_without_note_text(caplog: pytest.LogCaptureFixture) -> None:
    """Creating a note logs its id, and the private notes text never reaches the log"""
    service = make_service()

    # Capture records of level INFO and above while the block runs
    with caplog.at_level(logging.INFO):
        created_note = service.create_note("private note text")

    service_records = [record for record in caplog.records if record.name == "app.services.notes"]

    assert len(service_records) == 1
    assert service_records[0].levelno == logging.INFO
    assert service_records[0].getMessage() == f"Note created id={created_note.id}"
    assert "private note text" not in caplog.text


def test_delete_notes_removes_all_requested_notes():
    """Deleting several existing notes removes exactly them in one committed transaction."""
    # We need our own unit of work object to read its counters after the call
    unit_of_work = FakeUnitOfWork()
    service = NotesService(FakeNotesRepository(), unit_of_work)
    first_note = service.create_note("first")
    second_note = service.create_note("second")
    third_note = service.create_note("third")
    # create_note also commits, so remember the counters before the call under test
    commits_before = unit_of_work.commits
    rollbacks_before = unit_of_work.rollbacks

    service.delete_notes([first_note.id, second_note.id])

    # Only the third note is left
    assert [note.id for note in service.list_notes()] == [third_note.id]
    # One new commit and no new rollback
    assert unit_of_work.commits == commits_before + 1
    assert unit_of_work.rollbacks == rollbacks_before


def test_delete_notes_with_a_missing_id_rolls_back_and_names_it():
    """If any id is missing, the whole batch fails: one rollback, no commit."""
    unit_of_work = FakeUnitOfWork()
    service = NotesService(FakeNotesRepository(), unit_of_work)
    existing_note = service.create_note("exists")
    commits_before = unit_of_work.commits

    # "as error_info" keeps the caught exception inside an ExceptionInfo object
    with pytest.raises(NoteNotFoundError) as error_info:
        service.delete_notes([existing_note.id, 99])

    # error_info.value is the exception object; str() gives its message
    assert str(error_info.value) == "Notes not found: [99]"
    assert unit_of_work.commits == commits_before
    assert unit_of_work.rollbacks == 1


def test_delete_notes_ignores_repeated_ids():
    """The same id twice is not an error: the note is deleted once."""
    unit_of_work = FakeUnitOfWork()
    service = NotesService(FakeNotesRepository(), unit_of_work)
    created_note = service.create_note("to delete")
    commits_before = unit_of_work.commits

    service.delete_notes([created_note.id, created_note.id])

    assert service.list_notes() == []
    assert unit_of_work.commits == commits_before + 1
    assert unit_of_work.rollbacks == 0


def test_delete_notes_logs_event_without_note_text(caplog: pytest.LogCaptureFixture) -> None:
    """Batch delete logs the deleted ids once, and the note texts never reach the log."""
    service = make_service()
    first_note = service.create_note("private first")
    second_note = service.create_note("private second")

    # Start capturing only now, so the log lines of create_note are not counted
    with caplog.at_level(logging.INFO):
        service.delete_notes([second_note.id, first_note.id])

    service_records = [record for record in caplog.records if record.name == "app.services.notes"]

    assert len(service_records) == 1
    assert service_records[0].levelno == logging.INFO
    # ids are logged sorted, whatever order the caller used
    assert service_records[0].getMessage() == f"Notes deleted ids={[first_note.id, second_note.id]}"
    assert "private" not in caplog.text
