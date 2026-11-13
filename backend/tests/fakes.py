from datetime import datetime
from app.models.note import Note
from app.repositories.notes import NotesRepository

class FakeNotesRepository(NotesRepository):
    """In-memory repository for tests: same contract as the real one, but with no database"""

    def __init__(self) -> None:
        """Start with an empty store and ids from 1, like a fresh table"""
        self._notes: list[Note] = []
        self._next_id = 1

    def list_notes(self) -> list[Note]:
        """Return all notes, newest first (a copy, so tests cannot corrupt the store). list() - creates a new list"""
        return list(reversed(self._notes))
    
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


