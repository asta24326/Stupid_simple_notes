# pytest: test runner; fixture marks a function that prepares objects for tests
import pytest
from fastapi import FastAPI

# TestClient: calls the app wihtout a real server
from fastapi.testclient import TestClient

# register_error_handlers: maps domain errors to HTTP responses (the code under test)
from app.handlers.errors import register_error_handlers

# get_notes_service: the empty provider the handlers ask for; router: the /api/notes routes
from app.handlers.notes import get_notes_service, router

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


def test_list_returns_the_requested_page(client):
    """Limit and offset in the address cut a page out of the newest-first list."""
    for number in range(5):
        client.post("/api/notes", json={"text": f"note {number}"})

    response = client.get("/api/notes", params={"limit": 2, "offset": 1})

    assert response.status_code == 200
    assert [note["text"] for note in response.json()] == ["note 3", "note 2"]


def test_list_without_parameters_returns_the_notes(client):
    """The old call wothout parameters still works"""
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
