"""Versioned database migrations.

Migrations are SQL files named NNNN_name.sql in rollcall/migrations. At startup every pending file
runs in number order, each in its own transaction together with its row in schema_migrations, so a
failing file leaves nothing behind. A PostgreSQL advisory lock makes app processes that start
together take turns: the first applies the migrations, the others then find nothing to do.
Migrations only move forward; to undo one, write a new one.
"""

import re
from dataclasses import dataclass
from pathlib import Path

import psycopg

MIGRATIONS_DIR = Path(__file__).parent / "migrations"
FILE_NAME = re.compile(r"^(?P<version>\d{4})_(?P<name>[a-z0-9_]+)\.sql$")
LOCK_KEY = 0x526F6C6C  # "Roll": the advisory lock that serializes migration runs

CREATE_RECORD_TABLE = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version    integer PRIMARY KEY,
    name       text NOT NULL,
    applied_at timestamptz NOT NULL DEFAULT now()
)
"""


class MigrationError(Exception):
    """A migration file is invalid or failed, or the database is newer than the code."""


@dataclass(frozen=True)
class Migration:
    version: int
    name: str
    path: Path

    @property
    def label(self) -> str:
        return f"{self.version:04d}_{self.name}"


def find_migrations(folder: Path) -> list[Migration]:
    """Every migration in the folder, in number order. Non-SQL files are ignored."""
    found: dict[int, Migration] = {}
    for path in sorted(folder.glob("*.sql")):
        match = FILE_NAME.match(path.name)
        if match is None:
            raise MigrationError(
                f"Migration file {path.name} is badly named: use NNNN_name.sql, "
                "for example 0001_create_customers.sql"
            )
        version = int(match["version"])
        if version in found:
            raise MigrationError(
                f"Two migration files share number {version:04d}: "
                f"{found[version].path.name} and {path.name}"
            )
        found[version] = Migration(version, match["name"], path)
    return [found[version] for version in sorted(found)]


def apply_migrations(conn: psycopg.Connection, folder: Path = MIGRATIONS_DIR) -> list[int]:
    """Apply pending migrations and return their numbers. `conn` must be in autocommit mode."""
    migrations = find_migrations(folder)  # reject bad files before touching the database

    conn.execute("SELECT pg_advisory_lock(%s)", (LOCK_KEY,))
    try:
        conn.execute(CREATE_RECORD_TABLE)
        applied = {v for (v,) in conn.execute("SELECT version FROM schema_migrations")}

        unknown = applied - {m.version for m in migrations}
        if unknown:
            numbers = ", ".join(f"{v:04d}" for v in sorted(unknown))
            raise MigrationError(
                f"The database belongs to a newer version of Rollcall: it has migration(s) "
                f"{numbers} that this code does not know. Run the newer version instead."
            )

        newly_applied = []
        for migration in migrations:
            if migration.version in applied:
                continue
            try:
                with conn.transaction():
                    conn.execute(migration.path.read_text())
                    conn.execute(
                        "INSERT INTO schema_migrations (version, name) VALUES (%s, %s)",
                        (migration.version, migration.name),
                    )
            except psycopg.Error as error:
                raise MigrationError(f"Migration {migration.label} failed: {error}") from error
            newly_applied.append(migration.version)
        return newly_applied
    finally:
        conn.execute("SELECT pg_advisory_unlock(%s)", (LOCK_KEY,))
