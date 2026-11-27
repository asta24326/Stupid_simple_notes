# ============================================================
# Notes App: developer commands
#
# Usage: make <command>
#
# First time on a new machine (or after a fresh clone):
#   1. make setup    create backend/.venv, install packages, enable git hooks
#
# Every working session:
#   1. make db       start the PostgreSQL container
#   2. make run      start the API on http://127.0.0.1:8000 (Ctrl+C to stop)
#
# Before committing:
#   make fix         fix what ruff can fix and format the code
#   make lint        fast check (ruff only), the pre-commit hook runs it
#
# Before pushing:
#   make test        run the tests only
#   make check       full check: lint, format check, tests
#                    (the pre-push hook and CI run the same scripts/check.sh)
#
# Notes:
#   - No manual venv activation needed: make puts backend/.venv/bin first in PATH.
#   - Commands inside a target must start with a Tab character, not spaces.
#   - Skip the hooks in an emergency: git commit --no-verify / git push --no-verify
# ============================================================

# Targets are commands, not files: always run them
.PHONY: setup db run fix lint test check migrate

# Put the project venv first in PATH for every command that make runs,
# so python3 is the venv's python3 and no manual activation is needed
export PATH := $(CURDIR)/backend/.venv/bin:$(PATH)

# One-time preparation: venv, packages, git hooks
setup:
	python3 -m venv backend/.venv
	python3 -m pip install -r backend/requirements-dev.txt
	git config core.hooksPath .githooks

# Start the PostgreSQL container
db:
	docker compose up -d --wait db

# Apply the database migrations that are not applied yet (the database must be running: make db)
migrate:
	cd backend && python3 -m app.migrate

# Run the API with auto-reload on http://127.0.0.1:8000
run:
	cd backend && python3 -m uvicorn app.main:app --reload

# Fix what ruff can fix and format the code
fix:
	./scripts/fix.sh

# Fast check without tests (used by the pre-commit hook)
lint:
	cd backend && python3 -m ruff check . && python3 -m ruff format --check .

# Run the tests only
test:
	cd backend && python3 -m pytest -q

# Full check: lint, format check and tests (pre-push hook and CI)
check:
	./scripts/check.sh