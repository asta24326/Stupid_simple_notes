# Standard library: paths as objects
from pathlib import Path

# Our code: the module itself (to replace its folder constant in a test) and the functions under test
import app.migrate as migrate_module
from app.migrate import collect_pending_files, find_migration_files


def test_pending_files_skip_applied_versions() -> None:
    """Files whose version is already recorded are not run again"""
    migration_files = [Path("0001_first.sql"), Path("0002_second.sql"), Path("0003_third.sql")]
    applied_versions = {"0001_first", "0002_second"}

    pending_files = collect_pending_files(migration_files, applied_versions)

    assert pending_files == [Path("0003_third.sql")]


def test_pending_files_is_empty_when_everything_is_applied() -> None:
    """Second run: nothing to do (idempotency)"""
    migration_files = [Path("0001_first.sql")]

    assert collect_pending_files(migration_files, {"0001_first"}) == []


def test_pending_files_keep_the_original_order() -> None:
    """A gap in the middle does not change the order of the rest"""
    migration_files = [Path("0001_first.sql"), Path("0002_second.sql"), Path("0003_third.sql")]

    pending_files = collect_pending_files(migration_files, {"0002_second"})

    assert pending_files == [Path("0001_first.sql"), Path("0003_third.sql")]


def test_find_migration_files_returns_only_sql_files_sorted(tmp_path, monkeypatch) -> None:
    """Only .sql files are found, in the order of their numbers"""
    (tmp_path / "0002_second.sql").write_text("SELECT 2;", encoding="utf-8")
    (tmp_path / "0001_first.sql").write_text("SELECT 1;", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("not a migration", encoding="utf-8")
    # For this test the runner looks into the temporary folder instead of db/migrations
    monkeypatch.setattr(migrate_module, "MIGRATIONS_DIRECTORY", tmp_path)

    file_names = [migration_file.name for migration_file in find_migration_files()]

    assert file_names == ["0001_first.sql", "0002_second.sql"]
