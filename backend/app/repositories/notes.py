from abc import ABC, abstractmethod
from app.models.note import Note

class NotesRepository(ABC):
    """ Storage contract for Notes
        The service layer depends on this interface only,
        so the real database can be replaced by fake
        one in tests. Implementation contains no business
        logic, it only store and load notes """

    @abstractmethod
    def list_notes(self) -> list[Note]:
        """ Return all Notes, newest first """

    @abstractmethod
    def create_note(self, text: str) -> Note:
        """ Store a new Note and return it with
            generated id and timestamp """

    @abstractmethod
    def update_note(self, note_id: int, text: str) -> Note | None:
        """ Replace note's text and return it or return None if note
            doesn't exist """

    @abstractmethod
    def delete_note(self, note_id: int) -> bool:
        """Delete a note. Return True if it existed, False otherwise."""





