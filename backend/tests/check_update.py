import psycopg

from app.config import Settings
from app.repositories.postgres_notes import PostgresNotesRepository

settings = Settings()

connection = psycopg.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        dbname=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password,
)

repository = PostgresNotesRepository(connection)

created_note = repository.create_note("before update")
print("created:", created_note.id, created_note.text)

updated_note = repository.update_note(created_note.id, "after update")
print("updated:", updated_note.id, updated_note.text)

missing_note = repository.update_note(99999, "nothing")
print("missing:", missing_note)

connection.close()