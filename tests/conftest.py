"""Shared test fixtures.

Every test session creates its own uniquely named PostgreSQL database on the throwaway server
from compose.test.yaml, and drops it at the end. Tests never touch SQLite or the app's real
database. Override the server with TEST_DATABASE_ADMIN_URL.
"""

import os
import uuid
from contextlib import contextmanager

import psycopg
import pytest
from psycopg import sql

ADMIN_URL = os.environ.get(
    "TEST_DATABASE_ADMIN_URL", "postgresql://postgres:postgres@127.0.0.1:55432/postgres"
)


def _url_for(database: str) -> str:
    base, _, _ = ADMIN_URL.rpartition("/")
    return f"{base}/{database}"


@contextmanager
def throwaway_database():
    """Create a uniquely named empty database, yield its URL, then drop it."""
    name = f"rollcall_test_{uuid.uuid4().hex[:12]}"
    try:
        admin = psycopg.connect(ADMIN_URL, autocommit=True, connect_timeout=5)
    except psycopg.OperationalError as error:
        pytest.exit(
            f"Test database server not reachable at {ADMIN_URL!r}. Run scripts/test.sh, or "
            f"start it with: docker compose -f compose.test.yaml up -d --wait\n{error}",
            returncode=2,
        )
    with admin:
        admin.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
        try:
            yield _url_for(name)
        finally:
            admin.execute(
                sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(sql.Identifier(name))
            )


@pytest.fixture(scope="session")
def database_url():
    """One database shared by the whole test session."""
    with throwaway_database() as url:
        yield url


@pytest.fixture
def empty_database_url():
    """A fresh empty database for one test, for tests that need a clean slate."""
    with throwaway_database() as url:
        yield url


@pytest.fixture
def db(database_url):
    with psycopg.connect(database_url, autocommit=True) as conn:
        yield conn
