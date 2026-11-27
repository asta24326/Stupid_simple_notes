# Architecture

Layered backend: **handler → service → repository interface → DB repository → PostgreSQL**.
Each layer knows only about the layer below it, never the other way round.

```
Client
  │  HTTP
  ▼
Handler (FastAPI routes, schemas, error mapping, middleware)
  │  calls
  ▼
Service (business rules, transaction boundary)
  │  depends on the interface, not on Postgres
  ▼
NotesRepository (abstract interface)
  ▲  implemented by
  │
DbNotesRepository (SQL, psycopg)  ──►  PostgreSQL
```

Service depends on the **interface** (Dependency Inversion), so tests can plug in
`FakeNotesRepository` and run without a database.

## Layers

### Handler (transport layer)
- **Files:** `backend/app/handlers/notes.py`
- **Does:** receives the HTTP request, gets already validated data, calls the service, returns status code and body.
- **Must not:** contain business rules, SQL, or decide transaction boundaries.
- **Rule of thumb:** a route function is a few lines: call the service, return the result.

### Schemas (DTO = Data Transfer Object)
- **Files:** `backend/app/handlers/schemas.py`
- **Does:** describes the shape of data at the API border: types, `min_length`, `max_length`, `ge`/`le`.
- **Must not:** know anything about the database.

### Error mapping
- **Files:** `backend/app/handlers/errors.py`
- **Does:** translates domain errors into HTTP responses (`NoteNotFoundError` → 404, empty/too long text → 400, validation → 422, unexpected → 500), keeps one response format `{"detail": ...}`, logs client errors as WARNING and unexpected errors as ERROR with a traceback.
- **Must not:** invent new business rules.

### Middleware
- **Files:** request id middleware in `backend/app/`
- **Does:** cross-cutting work for every request: creates `request_id` (stored in a `ContextVar`), logs the request, returns the id to the client.
- **Must not:** know about specific endpoints.

### Service (business layer)
- **Files:** `backend/app/services/notes.py`
- **Does:**
  - business rules (text is not empty, note must exist, batch size, duplicates);
  - raises domain errors (`NoteNotFoundError`, validation errors);
  - owns the **transaction boundary** with `with self._unit_of_work:`;
  - logs business events (`Note created id=...`) without user data.
- **Must not:** know about HTTP (status codes, `Request`) or SQL.

### Repository interface
- **Files:** `backend/app/repositories/notes_interface.py`
- **Does:** the contract: which storage operations exist and what they return.
- **Returns facts, not decisions:** `None`, `bool`, list of ids.
- **Must not:** contain implementation.

### DB repository (data access layer)
- **Files:** `backend/app/repositories/db/notes.py`
- **Does:** SQL with psycopg, mapping rows to `Note`, soft delete filter `deleted_at IS NULL`, batch operations in one query (`id = ANY(%s)`).
- **Must not:** raise domain errors, call `commit`, or know about HTTP.

### Unit of Work
- **Does:** one transaction per business operation: `commit` on success, `rollback` if an exception leaves the `with` block.
- **Must not:** know the business meaning of the operation.

### Domain
- **Does:** entities (`Note`) and domain errors (`NoteNotFoundError`, ...): the shared language of all layers.
- **Must not:** import FastAPI or psycopg.

### Config
- **Files:** `Settings` (reads `.env`)
- **Does:** all settings in one place.
- **Must not:** be replaced by scattered `os.environ` calls.

### Infrastructure
- **Files:** `backend/app/migrate.py`, `db/migrations/*.sql`, logging config, `Makefile`, `.github/workflows/`
- **Does:** database schema (versioned SQL migrations, table `schema_migrations`), running, checks, CI.

## Where each decision lives

| Decision | Layer |
|---|---|
| Shape and limits of input data | Schema |
| "Note does not exist is an error" | Service |
| Which ids were really deleted | DB repository (fact) |
| "Not all ids deleted, so roll back everything" | Service (raises inside `with`) |
| Commit / rollback | Unit of Work |
| 404 / 400 / 422 / 500 | Error mapping |
| SQL text | DB repository |

## Error flow

```
DbNotesRepository   returns None / list of ids      (facts)
Service             raises NoteNotFoundError        (decision)
Error mapping       turns it into HTTP 404          (translation)
```

Each level speaks its own language: SQL results, domain errors, HTTP statuses.

## Transaction flow (batch delete)

1. Service normalizes ids: `sorted(set(note_ids))`.
2. Inside `with unit_of_work`, repository runs one `UPDATE ... WHERE id = ANY(%s) ... RETURNING id`.
3. Service compares requested ids with returned ids (set difference).
4. If something is missing, service raises `NoteNotFoundError` inside the block, so the unit of work rolls back (all or nothing).
5. Otherwise the block ends, `commit` runs, then the service logs the event.

## Testing by layer

| Layer | How it is tested |
|---|---|
| Service | unit tests with `FakeNotesRepository` and `FakeUnitOfWork` (no database) |
| Handler | `TestClient` with a service built on fakes |
| Logging, middleware | `caplog`, `TestClient` |
| Migration runner | `tmp_path` + `monkeypatch` |
| DB repository (SQL) | not covered yet (follow-up: tests against a real database) |

## Not implemented yet

Authentication and authorization, mappers between entities and DTOs, cache, background jobs (e.g. purge of soft-deleted notes), external gateways, messaging, rate limiting, metrics and tracing, connection pool.