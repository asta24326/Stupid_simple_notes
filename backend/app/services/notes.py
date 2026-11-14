from app.errors import EmptyTextError, TextTooLongError, NoteNotFoundError
from app.models.note import Note
from app.repositories.notes import NotesRepository

MAX_TEXT_LENGTH = 10000

class NoteService:
    """Business rules for Notes
        Validates the Note text, delegates storage to a Repository and reports
        problems with domain errors. Knows nothing about HTTP and SQL"""

    def __init__(self, repository: NotesRepository) -> None:
        """Take the storage from outside, so it can be mocked"""
        self._repository = repository

    def list_notes(self) -> list[Note]:
        """Show all notes, newest first"""
        return self._repository.list_notes()
    
    def get_note(self, note_id: int) -> Note:
        """Show one note; NoteNotFoundError if it is missing."""
        note = self._repository.get_note(note_id)
        if note is None:
            raise NoteNotFoundError(f"Note {note_id} not found")
        return note
    
    def create_note(self, text: str) -> Note:
        """Add a note after checking its text"""
        self._validate_text(text)
        return self._repository.create_note(text)
    
    def update_note(self, note_id: int, text: str) -> Note:
        """Change the text of an existing note; NoteNotFoundError if it doesn't exist"""
        self._validate_text(text)
        updated_note = self._repository.update_note(note_id, text)
        if updated_note is None:
            raise NoteNotFoundError(f'Note {note_id} not found')
        return updated_note
    
    def delete_note(self, note_id: int) -> None:
        """Remove a note; NoteNotFoundError if it is missing"""
        was_deleted = self._repository.delete_note(note_id)
        if not was_deleted:
            raise NoteNotFoundError(f'Note {note_id} not found')
        
    def _validate_text(self, text: str) -> None:
        """Text rules shared by create and update: not empty, max_chars 10000 chars"""
        if text == '':
            raise EmptyTextError("Note text must not be empty")
        
        if len(text) > MAX_TEXT_LENGTH:
            raise TextTooLongError(f'Note text must be at most {MAX_TEXT_LENGTH} characters')

    
        