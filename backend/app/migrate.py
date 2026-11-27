# Standard library: path as objects instead of plain strings
# sys: a function that raises SystemExit for you
import sys
from pathlib import Path

# psycopg: the PostgreSQL driver, the same one the application uses
import psycopg

# Settings: the same database settings the application reads from .env
from app.config import Settings

# Folder with the numbered .sql files, in the repository root next to db/init.sql
# __file__ is this file; parents[2] goes two folders up from backend/app, to the repository root
MIGRATIONS_DIRECTORY = Path(__file__).resolve().parents[2] / "db" / "migrations"
# root / "db" / "migrations" - is gluing together
# Path(__file__).resolve().parents[0] = .../Notes_taker/backend/app (directory, where this file is)
# Path(__file__).resolve().parents[1] = .../Notes_taker/backend
# Path(__file__).resolve().parents[2] = .../Notes_taker


def find_migration_files() -> list[Path]:
    """Return all .sql files of the migrations folder, sorted by file name."""
    return sorted(MIGRATIONS_DIRECTORY.glob("*.sql"))


# syntax hint:
# .glob("*.sql") - returns all the files in the directory, which name ends with .sql


def connect_to_database() -> psycopg.Connection:
    """Open a connection with the same settings as the application."""
    settings = Settings()
    return psycopg.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        dbname=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password,
    )


def create_versions_table(connection: psycopg.Connection) -> None:
    """Create the table that remembers applied migrations, if it does not exist yet."""
    with connection.cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
            """
        )
    connection.commit()


def check_applied_versions(connection: psycopg.Connection) -> set[str]:
    """Return the names of the migrations already recorded in the database."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT version FROM schema_migrations")
        rows = cursor.fetchall()
    # Even a SELECT opens a transaction; end it so the next step starts clean
    connection.commit()
    return {row[0] for row in rows}


def collect_pending_files(migration_files: list[Path], applied_versions: set[str]) -> list[Path]:
    """Keep only the files whose version is not recorded yet, in the original order."""
    return [migration_file for migration_file in migration_files if migration_file.stem not in applied_versions]


def apply_migration(connection: psycopg.Connection, migration_file: Path) -> None:
    """Run one migration file and record its version, in one transaction."""
    migration_sql = migration_file.read_text(encoding="utf-8")
    try:
        with connection.cursor() as cursor:
            cursor.execute(migration_sql)
            cursor.execute(
                "INSERT INTO schema_migrations (version) VALUES (%s)",
                (migration_file.stem,),
            )
    except Exception:
        # Undo everything from this migration, the version is not recorded either
        connection.rollback()
        raise
    connection.commit()


# Syntax hint:
# Path.stem: the file name WITHOUT the extension (a property, so no parentheses)
#   Path(".../0001_create_notes.sql").stem   -> "0001_create_notes"
#   Path(".../0001_create_notes.sql").name   -> "0001_create_notes.sql"  (with extension)
#   Path(".../0001_create_notes.sql").suffix -> ".sql"                   (only the extension)
# We use it as the migration version stored in schema_migrations


def run_migrations() -> int:
    """Apply all pending migrations in order; return the exit code."""
    connection = connect_to_database()
    try:
        create_versions_table(connection)
        applied_versions = check_applied_versions(connection)
        pending_files = collect_pending_files(find_migration_files(), applied_versions)

        if not pending_files:
            print("Nothing to apply")
            return 0

        for migration_file in pending_files:
            apply_migration(connection, migration_file)
            print(f"Applied {migration_file.stem}")
        return 0
    except Exception as error:
        print(f"Migration failed: {error}")
        return 1
    finally:
        connection.close()


if __name__ == "__main__":
    sys.exit(run_migrations())
