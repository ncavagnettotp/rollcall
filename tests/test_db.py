"""Connection pool and transactions (spec: One-command start, database slow to start)."""

import time

import pytest

from rollcall.db import DatabaseUnavailable, create_pool, transaction

UNREACHABLE = "postgresql://rollcall:hunter2-secret@127.0.0.1:1/rollcall"


def test_pool_connects_and_answers(database_url):
    with create_pool(database_url, size=2) as pool, pool.connection() as conn:
        assert conn.execute("SELECT 1").fetchone() == (1,)


def test_unreachable_database_gives_up_after_the_wait_with_a_clear_error():
    started = time.monotonic()
    with pytest.raises(DatabaseUnavailable) as caught:
        create_pool(UNREACHABLE, size=2, wait_seconds=1)
    elapsed = time.monotonic() - started

    assert 1 <= elapsed < 10
    message = str(caught.value)
    assert "database" in message.lower()
    assert "1 second" in message
    assert "hunter2-secret" not in message


def test_transaction_commits_on_success(database_url):
    with create_pool(database_url, size=2) as pool:
        with pool.connection() as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS tx_ok (n int)")
            conn.execute("TRUNCATE tx_ok")
        with transaction(pool) as conn:
            conn.execute("INSERT INTO tx_ok VALUES (1)")
            conn.execute("INSERT INTO tx_ok VALUES (2)")
        with pool.connection() as conn:
            assert conn.execute("SELECT count(*) FROM tx_ok").fetchone() == (2,)


def test_transaction_rolls_back_everything_on_error(database_url):
    with create_pool(database_url, size=2) as pool:
        with pool.connection() as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS tx_fail (n int)")
            conn.execute("TRUNCATE tx_fail")
        with pytest.raises(RuntimeError), transaction(pool) as conn:
            conn.execute("INSERT INTO tx_fail VALUES (1)")
            raise RuntimeError("something went wrong halfway")
        with pool.connection() as conn:
            assert conn.execute("SELECT count(*) FROM tx_fail").fetchone() == (0,)
