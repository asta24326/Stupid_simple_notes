.PHONY: setup fix check test run

# Put the venv's bin folder first in PATH for every command that make runs
export PATH := $(CURDIR)/backend/.venv/bin:$(PATH)

setup:
	python3 -m venv backend/.venv
	python3 -m pip install -r backend/requirements-dev.txt

fix:
	./scripts/fix.sh

check:
	./scripts/check.sh

test:
	cd backend && python3 -m pytest -q

run:
	cd backend && python3 -m uvicorn app.main:app --reload