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

created_note = repository.create_note("fetch me")
print("found:", repository.get_note(created_note.id).text)
print("missing:", repository.get_note(999999))

repository.delete_note(created_note.id)
connection.close()