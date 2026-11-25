"""Start Rollcall: python -m rollcall (the container's command).

All one-time work happens here, once, before any worker process exists: check the settings and
the data folder, wait for the database, apply migrations. Any problem prints a clear message and
exits with status 1. Only then do the workers start; each one finds no migrations left to apply.
(Starting uvicorn directly with several workers would instead restart failing workers forever.)
"""

import os
import sys
from collections.abc import Mapping

import uvicorn

from rollcall.config import ConfigError, load_settings
from rollcall.db import DatabaseUnavailable, create_pool
from rollcall.main import StartupError, ensure_data_dir
from rollcall.migrate import MigrationError, apply_migrations

DATABASE_WAIT_SECONDS = 60
WORKER_RANGE = range(1, 17)
PORT = 8000  # inside the container; compose.yaml publishes it as APP_PORT


def fail(message: str) -> int:
    print(message, file=sys.stderr)
    return 1


def main(env: Mapping[str, str]) -> int:
    try:
        settings = load_settings(env)
    except ConfigError as error:
        return fail(str(error))

    workers_text = env.get("WEB_CONCURRENCY", "").strip() or "2"
    workers = int(workers_text) if workers_text.isdigit() else 0
    if workers not in WORKER_RANGE:
        return fail(
            f"Rollcall cannot start:\n  - WEB_CONCURRENCY must be a whole number from "
            f"{WORKER_RANGE.start} to {WORKER_RANGE.stop - 1}"
        )

    try:
        ensure_data_dir(settings.data_dir)
        pool = create_pool(settings.database_url, size=1, wait_seconds=DATABASE_WAIT_SECONDS)
        with pool, pool.connection() as conn:
            applied = apply_migrations(conn)
        if applied:
            print("Applied migrations: " + ", ".join(f"{v:04d}" for v in applied), file=sys.stderr)
    except (StartupError, DatabaseUnavailable, MigrationError) as error:
        return fail(f"Rollcall cannot start:\n  - {error}")

    uvicorn.run(
        "rollcall.main:create_app",
        factory=True,
        host="0.0.0.0",
        port=PORT,
        workers=workers,
        server_header=False,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(os.environ))
