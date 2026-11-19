#!/usr/bin/env bash
set -e
# -e = stop at first error

cd "$(dirname "$0")/../backend"
# (dirname "$0"): current dir where script is
# move to /backend dir regardless where script is

python3 -m ruff check .
python3 -m ruff format --check .
python3 -m pytest -q