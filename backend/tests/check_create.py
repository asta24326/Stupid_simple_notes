import psycopg

from app.config import Settings
from app.repositories.postgres_notes import PostgresNotesRepository

settings = Settings()

def open_connection() -> psycopg.Connection:
    return psycopg.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        dbname=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password,
    )

connection = open_connection()
repository = PostgresNotesRepository(connection)

created_note = repository.create_note("created by check_create")
print("created:", created_note)
print("type of created_at:", type(created_note.created_at))
connection.close()

second_connection = open_connection()

second_repository = PostgresNotesRepository(second_connection)

texts = [note.text for note in second_repository.list_notes()]
print("visible from a new connection:", "created by check_create" in texts)
second_connection.close()