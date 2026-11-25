"""Database connection pool and transactions.

Connections are in autocommit mode, so a plain query runs on its own. Anything that changes more
than one row together goes through transaction(), which commits at the end or rolls everything
back on any error.
"""

from collections.abc import Iterator
from contextlib import contextmanager

import psycopg
from psycopg_pool import ConnectionPool, PoolTimeout

DEFAULT_WAIT_SECONDS = 60


class DatabaseUnavailable(Exception):
    """The database could not be reached in time. The message never contains the URL."""


def create_pool(
    database_url: str, size: int, *, wait_seconds: float = DEFAULT_WAIT_SECONDS
) -> ConnectionPool:
    """Open a pool of up to `size` connections, retrying for up to `wait_seconds` until the
    database answers. Once open, the pool replaces broken connections on its own."""
    pool = ConnectionPool(
        database_url,
        min_size=1,
        max_size=size,
        kwargs={"autocommit": True},
        open=False,
        name="rollcall",
    )
    try:
        pool.open(wait=True, timeout=wait_seconds)
    except PoolTimeout:
        pool.close()
        unit = "second" if wait_seconds == 1 else "seconds"
        raise DatabaseUnavailable(
            f"The database did not answer within {wait_seconds:g} {unit}. "
            "Check that the database container is running and DATABASE_URL is correct."
        ) from None
    return pool


@contextmanager
def transaction(pool: ConnectionPool) -> Iterator[psycopg.Connection]:
    """Borrow a connection and run the block as one transaction."""
    with pool.connection() as conn, conn.transaction():
        yield conn
