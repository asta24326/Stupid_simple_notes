from datetime import datetime

from app.handlers.schemas import NoteResponse
from app.models.note import Note

note = Note(id=1, text="Buy milk", created_at=datetime(2026, 11, 15, 12, 0))

response = NoteResponse.model_validate(note)

print(response)
print(response.model_dump_json())

