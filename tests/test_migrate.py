"""Database upgrades (spec: Versioned database migrations).

Each test writes its own migration files into a temporary folder and runs them against a fresh
empty database, so the real migrations in rollcall/migrations are not involved here.
"""

import threading

import psycopg
import pytest

from rollcall.migrate import MigrationError, apply_migrations

CREATE_LOG = (
    "CREATE TABLE log (id serial PRIMARY KEY, n int NOT NULL);\nINSERT INTO log (n) VALUES (1);"
)


def write(folder, files: dict[str, str]):
    for name, body in files.items():
        (folder / name).write_text(body)
    return folder


@pytest.fixture
def folder(tmp_path):
    path = tmp_path / "migrations"
    path.mkdir()
    return path


@pytest.fixture
def conn(empty_database_url):
    with psycopg.connect(empty_database_url, autocommit=True) as connection:
        yield connection


def rows(conn, query):
    return conn.execute(query).fetchall()


def table_exists(conn, name):
    return conn.execute("SELECT to_regclass(%s) IS NOT NULL", (name,)).fetchone()[0]


# --- applying ------------------------------------------------------------------------------


def test_empty_folder_applies_nothing_but_creates_the_record_table(conn, folder):
    assert apply_migrations(conn, folder) == []
    assert table_exists(conn, "schema_migrations")


def test_pending_migrations_apply_in_number_order(conn, folder):
    write(
        folder,
        {
            "0010_ten.sql": "INSERT INTO log (n) VALUES (10);",
            "0002_two.sql": "INSERT INTO log (n) VALUES (2);",
            "0001_create_log.sql": CREATE_LOG,
        },
    )
    assert apply_migrations(conn, folder) == [1, 2, 10]
    assert [n for (n,) in rows(conn, "SELECT n FROM log ORDER BY id")] == [1, 2, 10]


def test_applied_migrations_are_recorded_with_name_and_time(conn, folder):
    write(folder, {"0001_create_log.sql": CREATE_LOG})
    apply_migrations(conn, folder)
    [(version, name, applied_at)] = rows(
        conn, "SELECT version, name, applied_at FROM schema_migrations"
    )
    assert (version, name) == (1, "create_log")
    assert applied_at is not None


def test_already_applied_migrations_are_skipped(conn, folder):
    write(
        folder,
        {"0001_create_log.sql": CREATE_LOG, "0002_two.sql": "INSERT INTO log VALUES (DEFAULT, 2);"},
    )
    assert apply_migrations(conn, folder) == [1, 2]
    assert apply_migrations(conn, folder) == []
    write(folder, {"0003_three.sql": "INSERT INTO log VALUES (DEFAULT, 3);"})
    assert apply_migrations(conn, folder) == [3]
    assert [n for (n,) in rows(conn, "SELECT n FROM log ORDER BY id")] == [1, 2, 3]


def test_files_that_are_not_sql_are_ignored(conn, folder):
    write(folder, {"README.md": "notes", "0001_create_log.sql": CREATE_LOG})
    assert apply_migrations(conn, folder) == [1]


# --- failures ------------------------------------------------------------------------------


def test_failing_migration_leaves_nothing_behind_and_names_its_number(conn, folder):
    write(
        folder,
        {
            "0001_create_log.sql": CREATE_LOG,
            "0002_broken.sql": (
                "CREATE TABLE half_done (x int);\nINSERT INTO log (n) VALUES (2);\nSELECT 1 / 0;"
            ),
            "0003_after.sql": "INSERT INTO log (n) VALUES (3);",
        },
    )
    with pytest.raises(MigrationError) as caught:
        apply_migrations(conn, folder)

    assert "0002" in str(caught.value)
    assert not table_exists(conn, "half_done")
    assert [n for (n,) in rows(conn, "SELECT n FROM log")] == [1]
    assert [v for (v,) in rows(conn, "SELECT version FROM schema_migrations")] == [1]


def test_after_a_failure_the_fixed_migration_applies(conn, folder):
    write(folder, {"0001_create_log.sql": CREATE_LOG, "0002_broken.sql": "SELECT 1 / 0;"})
    with pytest.raises(MigrationError):
        apply_migrations(conn, folder)
    write(folder, {"0002_broken.sql": "INSERT INTO log (n) VALUES (2);"})
    assert apply_migrations(conn, folder) == [2]


def test_database_newer_than_the_code_is_refused(conn, folder, tmp_path):
    write(folder, {"0001_create_log.sql": CREATE_LOG, "0002_two.sql": "SELECT 1;"})
    apply_migrations(conn, folder)

    older_code = tmp_path / "older"
    older_code.mkdir()
    write(older_code, {"0001_create_log.sql": CREATE_LOG})
    with pytest.raises(MigrationError) as caught:
        apply_migrations(conn, older_code)
    assert "newer version of Rollcall" in str(caught.value)


@pytest.mark.parametrize(
    "bad_name",
    ["1_init.sql", "0001init.sql", "0001_Init.sql", "0001_init-table.sql", "00001_init.sql"],
)
def test_badly_named_migration_files_are_rejected(conn, folder, bad_name):
    write(folder, {bad_name: "SELECT 1;"})
    with pytest.raises(MigrationError) as caught:
        apply_migrations(conn, folder)
    assert bad_name in str(caught.value)


def test_two_files_with_the_same_number_are_rejected(conn, folder):
    write(folder, {"0001_a.sql": "SELECT 1;", "0001_b.sql": "SELECT 1;"})
    with pytest.raises(MigrationError) as caught:
        apply_migrations(conn, folder)
    assert "0001" in str(caught.value)
    assert not table_exists(conn, "a")


# --- several app processes starting together -----------------------------------------------


def test_two_runners_at_once_apply_each_migration_exactly_once(empty_database_url, folder):
    write(
        folder,
        {
            # IF NOT EXISTS so that a second run would show up as a second row, not an error.
            "0001_slow.sql": (
                "CREATE TABLE IF NOT EXISTS runs (n int);\n"
                "SELECT pg_sleep(0.5);\n"
                "INSERT INTO runs VALUES (1);"
            ),
        },
    )
    start_together = threading.Barrier(2)
    results, errors = [], []

    def runner():
        try:
            with psycopg.connect(empty_database_url, autocommit=True) as connection:
                start_together.wait()
                results.append(apply_migrations(connection, folder))
        except Exception as error:  # reported below
            errors.append(error)

    threads = [threading.Thread(target=runner) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)

    assert errors == []
    assert sorted(results) == [[], [1]]
    with psycopg.connect(empty_database_url) as check:
        assert check.execute("SELECT count(*) FROM runs").fetchone()[0] == 1
        assert check.execute("SELECT count(*) FROM schema_migrations").fetchone()[0] == 1
