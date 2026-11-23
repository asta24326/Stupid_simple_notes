from datetime import datetime

from app.models.note import Note
from app.repositories.notes_interface import NotesRepositoryInterface

# UnitOfWork: the interface the fake implements
from app.unit_of_work_interface import UnitOfWorkInterface


class FakeNotesRepository(NotesRepositoryInterface):
    """In-memory repository for tests: same contract as the real one, but with no database"""

    def __init__(self) -> None:
        """Start with an empty store and ids from 1, like a fresh table"""
        self._notes: list[Note] = []
        self._next_id = 1

    def list_notes(self, limit: int, offset: int) -> list[Note]:
        """Return all notes, newest first (a copy, so tests cannot corrupt the store). list() - creates a new list"""
        newest_first = list(reversed(self._notes))
        return newest_first[offset : offset + limit]

    def get_note(self, note_id: int) -> Note:
        """Return one stored note; None if there is no such note"""
        for note in self._notes:
            if note.id == note_id:
                return note
        return None

    def create_note(self, text: str) -> Note:
        """Store a Note and hand out the id and timestamp, as real db would"""
        new_note = Note(id=self._next_id, text=text, created_at=datetime.now())
        self._next_id += 1
        self._notes.append(new_note)
        return new_note

    def update_note(self, note_id: int, text: str) -> Note | None:
        """Change the text of a stored note; None if there is no such note"""
        for note in self._notes:
            if note.id == note_id:
                note.text = text
                return note
        return None

    def delete_note(self, note_id: int) -> bool:
        """Remove stored note; False if note wasn't found"""
        for note in self._notes:
            if note.id == note_id:
                self._notes.remove(note)
                return True

        return False


class FakeUnitOfWork(UnitOfWorkInterface):
    """Counts commits and rollbacks, so tests can check them without a database."""

    def __init__(self) -> None:
        """Start with nothing commited and nothing rolled back"""
        self.commits = 0
        self.rollbacks = 0

    def commit(self) -> None:
        """Remember that the block was committed"""
        self.commits += 1

    def rollback(self) -> None:
        """Remember that the block was rolled back"""
        self.rollbacks += 1
