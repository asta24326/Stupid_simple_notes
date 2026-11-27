from abc import ABC, abstractmethod

from app.models.note import Note


class NotesRepositoryInterface(ABC):
    """Is interface
    Storage contract for Notes
    The service layer depends on this interface only,
    so the real database can be replaced by fake
    one in tests. Implementation contains no business
    logic, it only store and load notes."""

    @abstractmethod
    def list_notes(self, limit: int, offset: int) -> list[Note]:
        """Return all Notes, newest first, skip offset and return at most 'limit' amount."""

    @abstractmethod
    def get_note(self, note_id: int) -> Note | None:
        """Return one note by note_id; None if doesn't exist."""

    @abstractmethod
    def create_note(self, text: str) -> Note:
        """Store a new Note and return it with
        generated id and timestamp."""

    @abstractmethod
    def update_note(self, note_id: int, text: str) -> Note | None:
        """Replace note's text and return it or return None if note
        doesn't exist."""

    @abstractmethod
    def delete_note(self, note_id: int) -> bool:
        """Delete a note. Return True if it existed, False otherwise."""

    @abstractmethod
    def delete_notes(self, note_ids: list[int]) -> list[int]:
        """Soft delete several notes with one command.
        Return the ids that were really deleted: ids that do not exist
        or already deleted are not in the result."""
