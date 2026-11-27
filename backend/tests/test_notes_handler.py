# pytest: test runner; fixture marks a function that prepares objects for tests
import logging

import pytest
from fastapi import FastAPI

# TestClient: calls the app without a real server
from fastapi.testclient import TestClient

# register_error_handlers: maps domain errors to HTTP responses (the code under test)
from app.handlers.errors import register_error_handlers

# get_notes_service: the empty provider the handlers ask for; router: the /api/notes routes
from app.handlers.notes import get_notes_service, router

# MAX_BATCH_SIZE: the id limit of one batch request, used to build a too long list
from app.handlers.schemas import MAX_BATCH_SIZE

# NotesService: the business rules layer, built here on a fake repository
from app.services.notes import NotesService

# FakeNotesRepository: notes in a list, no database
from tests.fakes import FakeNotesRepository, FakeUnitOfWork


@pytest.fixture
def client() -> TestClient:
    """Build the app the way main.py does, but on a fake repository."""
    app = FastAPI()
    register_error_handlers(app)

    service = NotesService(FakeNotesRepository(), FakeUnitOfWork())
    app.dependency_overrides[get_notes_service] = lambda: service
    app.include_router(router)

    return TestClient(app, raise_server_exceptions=False)


@pytest.mark.parametrize(
    ("method", "url", "json_body", "expected_status"),
    [
        ("POST", "/api/notes", {"text": ""}, 400),
        ("POST", "/api/notes", {"text": "a" * 10001}, 400),
        ("POST", "/api/notes", {"text": 5}, 422),
        ("GET", "/api/notes/99", None, 404),
        ("GET", "/api/notes?limit=0", None, 422),
        ("PUT", "/api/notes/99", {"text": "new"}, 404),
        ("DELETE", "/api/notes/99", None, 404),
        ("POST", "/api/notes/batch-delete", {"ids": [99]}, 404),
        ("POST", "/api/notes/batch-delete", {"ids": []}, 422),
    ],
)
def test_client_errors_are_logged_as_warning(client, caplog, method, url, json_body, expected_status):
    """Mistakes of the client give 400/404 and a WARNING, never an ERROR."""
    with caplog.at_level(logging.INFO):
        response = client.request(method, url, json=json_body)

    assert response.status_code == expected_status

    handler_records = [record for record in caplog.records if record.name == "app.handlers.errors"]
    assert len(handler_records) == 1
    assert handler_records[0].levelno == logging.WARNING

    # Nothing at ERROR level or above: the client's mistake is not a server failure
    assert not [record for record in caplog.records if record.levelno >= logging.ERROR]


@pytest.mark.parametrize(
    "json_body",
    [
        {"ids": []},  # empty list
        {"ids": [0]},  # zero is not a positive id
        {"ids": [-1]},  # negative id
        {"ids": "abc"},  # a string instead of a list
        {"ids": [1, "abc"]},  # one bad item among good ones
        {"ids": list(range(1, MAX_BATCH_SIZE + 2))},  # one id more than the limit
        {},  # field "ids" is missing
    ],
)
def test_batch_delete_rejects_invalid_body(client, json_body):
    """Every body that breaks the schema gets 422 with our single error format."""
    response = client.post("/api/notes/batch-delete", json=json_body)

    assert response.status_code == 422
    assert response.json() == {"detail": "Invalid request data"}


def test_create_returns_201_and_the_note(client):
    response = client.post("/api/notes", json={"text": "Buy milk"})

    assert response.status_code == 201
    assert response.json()["text"] == "Buy milk"


def test_create_with_empty_text_returns_400(client):
    """The empty string is refused with 400 and a readable reason."""
    response = client.post("/api/notes", json={"text": ""})

    assert response.status_code == 400
    assert response.json()["detail"] == "Note text must not be empty"


def test_create_with_10001_characters_returns_400(client):
    """One character over the contract limit of 10000 is refused."""
    response = client.post("/api/notes", json={"text": "a" * 10001})

    assert response.status_code == 400


def test_create_with_wrong_type_returns_422(client):
    """A number instead of a string is stopped by FastAPI before our code runs."""
    response = client.post("/api/notes", json={"text": 5})

    assert response.status_code == 422
    assert response.json() == {"detail": "Invalid request data"}


def test_get_returns_the_note(client):
    """An existing note can be read by its id."""
    created = client.post("/api/notes", json={"text": "find me"}).json()

    response = client.get(f"/api/notes/{created['id']}")

    assert response.status_code == 200
    assert response.json()["text"] == "find me"


def test_get_missing_note_returns_404(client):
    """An id that does not exist gives 404 and the domain error message."""
    response = client.get("/api/notes/99")

    assert response.status_code == 404
    assert response.json()["detail"] == "Note 99 not found"


def test_update_changes_the_text(client):
    """PUT replaces the text and keeps the same id."""
    created = client.post("/api/notes", json={"text": "old"}).json()

    response = client.put(f"/api/notes/{created['id']}", json={"text": "new"})

    assert response.status_code == 200
    assert response.json()["text"] == "new"
    assert response.json()["id"] == created["id"]


def test_delete_returns_204_and_the_note_is_gone(client):
    """DELETE answers 204 without a body, and the note can no longer be read."""
    created = client.post("/api/notes", json={"text": "to delete"}).json()

    delete_response = client.delete(f"/api/notes/{created['id']}")
    read_response = client.get(f"/api/notes/{created['id']}")

    assert delete_response.status_code == 204
    assert read_response.status_code == 404


def test_batch_delete_returns_204_and_the_notes_are_gone(client):
    """Batch delete answers 204 without a body, and only the requested notes disappear."""
    first_note = client.post("/api/notes", json={"text": "first"}).json()
    second_note = client.post("/api/notes", json={"text": "second"}).json()
    third_note = client.post("/api/notes", json={"text": "third"}).json()

    response = client.post(
        "/api/notes/batch-delete",
        json={"ids": [first_note["id"], second_note["id"]]},
    )
    list_response = client.get("/api/notes")

    assert response.status_code == 204
    assert [note["id"] for note in list_response.json()] == [third_note["id"]]


def test_batch_delete_with_a_missing_id_returns_404(client):
    """One unknown id fails the whole request and the message names it."""
    existing_note = client.post("/api/notes", json={"text": "exists"}).json()

    response = client.post(
        "/api/notes/batch-delete",
        json={"ids": [existing_note["id"], 99]},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Notes not found: [99]"


def test_list_returns_the_requested_page(client):
    """Limit and offset in the address cut a page out of the newest-first list."""
    for number in range(5):
        client.post("/api/notes", json={"text": f"note {number}"})

    response = client.get("/api/notes", params={"limit": 2, "offset": 1})

    assert response.status_code == 200
    assert [note["text"] for note in response.json()] == ["note 3", "note 2"]


def test_list_without_parameters_returns_the_notes(client):
    """The old call without parameters still works"""
    client.post("/api/notes", json={"text": "first"})

    response = client.get("/api/notes")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_list_with_limit_zero_returns_422(client):
    response = client.get("/api/notes", params={"limit": 0})

    assert response.status_code == 422


def test_list_with_limit_above_the_maximum_returns_422(client):
    response = client.get("/api/notes", params={"limit": 101})

    assert response.status_code == 422


def test_list_with_negative_offset_return_422(client):
    response = client.get("/api/notes", params={"offset": -1})

    assert response.status_code == 422


def test_validation_error_does_not_log_user_input(client, caplog):
    """The rejected value is echoed by FastAPI's error data, but must not reach the log."""
    with caplog.at_level(logging.INFO):
        # A list instead of a string: 422, and the list holds a recognizable marker
        response = client.post("/api/notes", json={"text": ["private note text"]})

    assert response.status_code == 422
    assert "private note text" not in response.text
    assert "private note text" not in caplog.text
