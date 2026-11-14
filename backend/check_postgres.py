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

for note in repository.list_notes():
    print(note.id, note.text[:20], note.created_at)

connection.close()