# Notes App

A small notes app built from scratch: a plain PHP API, a Postgres database and a single-page UI, all running in Docker Compose behind Nginx.

![Notes App screenshot](docs/screenshot.png)

## Features

- List notes, newest first
- Create a note (up to 1000 characters)
- JSON API with a unified error format

## Architecture

```
Browser ──▶ Nginx (port 80) ──▶ PHP-FPM (port 9000) ──▶ PostgreSQL (port 5432)
              │
              └── serves the static UI from frontend/
```

| Service | Role |
|---|---|
| `nginx` | serves `frontend/` and forwards `/api/*` to PHP-FPM |
| `php` | runs `backend/index.php`: routing, validation, SQL via PDO prepared statements |
| `db` | PostgreSQL 16, data stored in the `pgdata` volume |


## Run locally

Requirements: Docker with Docker Compose.

```bash
git clone https://github.com/asta24326/Stupid_simple_notes
cd https://github.com/asta24326/Stupid_simple_notes
cp .env.example .env
docker compose up -d --build --wait
```

Open http://localhost/ in the browser.

To stop the app:

```bash
docker compose down        # stop, keep the data
docker compose down -v     # stop and delete the database data
```

## API

Base URL: `http://localhost/api`. Requests and responses use JSON.

### `GET /api/notes`

Returns all notes, newest first.

```bash
curl http://localhost/api/notes
```

```json
[
  {"id": 2, "text": "Call mom", "created_at": "2026-10-23 20:38:22.913657"},
  {"id": 1, "text": "Buy milk", "created_at": "2026-10-23 20:38:09.288726"}
]
```

### `POST /api/notes`

Creates a note. Body: `{"text": "..."}`, a non-empty string of at most 1000 characters.

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"text":"Buy milk"}' http://localhost/api/notes
```

Response `201 Created`:

```json
{"id": 3, "text": "Buy milk", "created_at": "2026-10-23 20:40:01.123456"}
```

### Errors

All errors have the same format:

```json
{"error": "message"}
```

| Status | When |
|---|---|
| `400 Bad Request` | invalid JSON, `text` is missing, not a string, empty or longer than 1000 characters |
| `404 Not Found` | unknown path |
| `405 Method Not Allowed` | method other than `GET` and `POST` (the `Allow` header lists the allowed ones) |
| `500 Internal Server Error` | unexpected error, details are only written to the server log |