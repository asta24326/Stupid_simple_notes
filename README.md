# Notes App
 
A small notes service built from scratch: a layered **FastAPI** backend on top of **PostgreSQL**, with request tracing and structured logging.
 
Source: https://github.com/asta24326/Stupid_simple_notes
 
## Features
 
- List notes, newest first, with pagination (`limit`, `offset`)
- Read, create, update and delete a note
- Text rules: not empty, at most 10000 characters
- One error format for every failure
- Request id on every request (`X-Request-Id`), visible in the response and in every log line
- Logging to stdout, level set by an environment variable
- Unit tests for the service, the HTTP layer, the middleware and the logging setup
## Architecture
 
```
Client ──▶ FastAPI app ──▶ handler ──▶ service ──▶ repository ──▶ PostgreSQL
              │
              └── middleware: request id, one log line per request
```
 
| Layer | Role |
|---|---|
| `handlers` | HTTP only: routes, status codes, mapping domain errors to responses |
| `services` | business rules: text validation, log events. Knows nothing about HTTP or SQL |
| `repositories` | storage behind an interface; the real one talks to PostgreSQL |
| `unit of work` | transaction boundary (`repositories/db/unit_of_work.py`): commit on success, rollback on error |
 
Each layer depends on the next one only through an interface, so the tests replace the database with in-memory fakes.
 
```
backend/
  app/
    handlers/          routes, error handlers, middleware
    services/          NotesService (business rules)
    repositories/      repository interface and PostgreSQL implementation
    models/            Note
    errors.py          domain errors (empty text, text too long, note not found)
    unit_of_work_interface.py  interface of the transaction boundary
    config.py          settings from environment variables
    logging_config.py  logging setup (dictConfig) and the request id filter
    request_context.py request id storage (ContextVar) and validation
    main.py            application assembly
  tests/
```
 
## Run locally
 
Requirements: Python 3.14, Docker with Docker Compose, `make`.
 
```bash
git clone https://github.com/asta24326/Stupid_simple_notes
cd Stupid_simple_notes
cp .env.example .env
make setup   # first time only: create backend/.venv, install packages, enable git hooks
make db      # start PostgreSQL in Docker
make migrate # create the tables
make run     # start the API with auto-reload
```
 
The API listens on http://localhost:8000. Interactive documentation (Swagger UI) is at http://localhost:8000/docs.
 
All settings live in `.env`; `.env.example` lists every variable with a comment.
 
Other commands:
 
```bash
make test    # run the tests
make fix     # auto-format and fix lint errors
make check   # lint, format check and tests (run before every commit)
```

## Database migrations

The schema is versioned: every change is a numbered SQL file in `db/migrations/`, and one command applies the files that are not applied yet.

```bash
make db        # start PostgreSQL
make migrate   # apply new migrations
```

The runner (`backend/app/migrate.py`) remembers what it has applied in the table `schema_migrations`. A second run does nothing (`Nothing to apply`). Each migration runs in one transaction together with its record in that table, so a failed migration leaves the database unchanged and stops the run.

### Add a migration

1. Create the next file in `db/migrations/`: a four-digit number, an underscore and a short description, for example `0002_add_title_to_notes.sql`.
2. Write the SQL change in it, one topic per file.
3. Run `make migrate` and check the result.
4. Commit the file together with the code that needs it.

Rules:

- Never edit a migration that has been applied anywhere; fix mistakes with a new migration.
- There are no rollback files: changes only go forward.
- The baseline `0001_create_notes.sql` uses `IF NOT EXISTS`, so it also works on a database created before migrations existed.
- CI runs `make migrate` before the tests that need the database.

 
## API
 
Base URL: `http://localhost:8000/api`. Requests and responses use JSON.
 
| Method | Path | Success | Description |
|---|---|---|---|
| `GET` | `/api/notes` | `200` | list notes, newest first |
| `GET` | `/api/notes/{id}` | `200` | one note |
| `POST` | `/api/notes` | `201` | create a note |
| `PUT` | `/api/notes/{id}` | `200` | replace the text of a note |
| `DELETE` | `/api/notes/{id}` | `204` | delete a note, no response body |
 
A note looks like this:
 
```json
{"id": 1, "text": "Buy milk", "created_at": "2026-11-26T19:40:01.123456"}
```
 
### `GET /api/notes`
 
Query parameters:
 
| Parameter | Rules | Default |
|---|---|---|
| `limit` | integer from 1 to 100 | 50 |
| `offset` | integer, 0 or more | 0 |
 
```bash
curl "http://localhost:8000/api/notes?limit=2&offset=1"
```
 
### `POST /api/notes` and `PUT /api/notes/{id}`
 
Body: `{"text": "..."}`, a non-empty string of at most 10000 characters.
 
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"text":"Buy milk"}' http://localhost:8000/api/notes
```
 
### Errors
 
Every error has the same format:
 
```json
{"detail": "message"}
```
 
| Status | When |
|---|---|
| `400 Bad Request` | text is empty or longer than 10000 characters |
| `404 Not Found` | no note with this id |
| `422 Unprocessable Entity` | wrong type (for example a number instead of a string) or `limit`/`offset` out of range; FastAPI checks this before our code runs. The response is always `{"detail": "Invalid request data"}`; which field was wrong is only written to the log |
| `500 Internal Server Error` | unexpected error; the response has no details, they are only written to the log |
 
## Logging
 
Logs go to **stdout**, the place where Docker and hosting platforms collect them. One line looks like this:
 
```
2026-11-26 19:40:01,123 INFO [request_id:ab12cd34] app.handlers.middleware: POST /api/notes -> 201 (3.2 ms)
```
 
### Request id
 
Every request gets an id that appears in the response header `X-Request-Id` and in every log line written while the request is handled.
 
- If the client sends `X-Request-Id` and it matches `[A-Za-z0-9_-]{1,64}`, the service keeps it.
- Otherwise it generates a new 8-character id. Anything else (spaces, line breaks, non-ASCII characters, more than 64 characters) is rejected, so a client cannot forge log lines.
To see everything that happened during one request:
 
```bash
curl -i -H "X-Request-Id: demo-1" http://localhost:8000/api/notes
make run | grep demo-1
```
 
### Levels
 
| Level | What is written |
|---|---|
| `INFO` | one line per request (method, path, status, duration) and business events: `Note created id=1`, `Note updated id=1`, `Note deleted id=1` |
| `WARNING` | mistakes of the client: rejected text (400), note not found (404), invalid request data (422: field and error type, never the value) |
| `ERROR` | unexpected exception, written once, with the traceback |
 
Note text and other user data are never written to the log.
 
### Configuration
 
| Variable | Values | Default |
|---|---|---|
| `LOG_LEVEL` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` | `INFO` |
 
Setup lives in `backend/app/logging_config.py`. It is called once at startup and is safe to call again: it replaces the handlers instead of adding new ones.
 
## Tests
 
```bash
make test
```
 
The tests do not need a database: the service and the HTTP layer run on in-memory fakes. They cover:
 
- the service rules, commits and rollbacks of the unit of work
- every HTTP status of the API
- request id handling in the middleware, including unsafe header values
- logging: one `ERROR` with traceback for an unexpected failure, `WARNING` (not `ERROR`) for client mistakes, no note text in the log, request id filter, repeated logging setup
## Known limitations
 
- Time stamps in logs use local time; switching logs and the database to UTC is planned.
- Leftovers of the old PHP version (`backend/*.php`, `frontend/`, `nginx/`, the `php` and `nginx` services in `docker-compose.yml`) are still in the repository and are not used by the FastAPI backend. Use `make db`, not a plain `docker compose up`.
 