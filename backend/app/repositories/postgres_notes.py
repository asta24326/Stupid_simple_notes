import psycopg

from app.models.note import Note
from app.repositories.notes import NotesRepository

class PostgresNotesRepository(NotesRepository):
    """Stores notes in PostgreSQL: SQL only, no business rules"""

    def __init__(self, connection: psycopg.Connection) -> None:
        """Take an open connection from outside(dependency injection)"""
        self._connection = connection

    def list_notes(self) -> list[Note]:
        """Read all notes from the table, newest first"""
        cursor = self._connection.cursor()
        try:
            cursor.execute("SELECT id, text, created_at FROM notes ORDER BY id DESC")
            rows = cursor.fetchall()
        finally:
            cursor.close()

        notes = []
        for row in rows:
            notes.append(self.raw_to_note(row))
        return notes
    
    def create_note(self, text: str) -> Note:
        raise NotImplementedError
    
    def update_note(self, note_id: int, text:str) -> Note | None:
        raise NotImplementedError
    
    def delete_note(self, note_id: id) -> bool:
        raise NotImplementedError
    
    def raw_to_note(self, row: tuple) -> Note:
        """Turn one table row (id, text, created_at) into a domain model Note"""
        return Note(id=row[0], text=row[1], created_at=[2])

        