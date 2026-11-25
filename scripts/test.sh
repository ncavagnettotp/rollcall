#!/usr/bin/env bash
# Run Rollcall's checks: start the throwaway test database if needed, then lint and test.
# Extra arguments go to pytest, e.g. scripts/test.sh -k migrate -x
set -euo pipefail
cd "$(dirname "$0")/.."

docker compose -f compose.test.yaml up -d --wait --quiet-pull
uv run ruff check .
uv run ruff format --check .
uv run pytest "$@"
