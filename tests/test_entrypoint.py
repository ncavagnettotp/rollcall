"""The container's start command, python -m rollcall (spec: One-command start, Configuration
from the environment, Versioned database migrations).

Every one-time check runs before any worker process starts, so a problem ends the process with
status 1 and a clear message instead of workers restarting in a loop.
"""

import psycopg
import pytest

import rollcall.__main__ as entry


@pytest.fixture
def started(monkeypatch):
    """Replaces uvicorn.run: records how it was called instead of serving."""
    calls = []
    monkeypatch.setattr(entry.uvicorn, "run", lambda *args, **kwargs: calls.append((args, kwargs)))
    return calls


@pytest.fixture
def env(database_url, tmp_path):
    return {
        "DATABASE_URL": database_url,
        "SECRET_KEY": "k" * 40,
        "SHOP_TIMEZONE": "America/Chicago",
        "DATA_DIR": str(tmp_path / "data"),
    }


def test_bad_settings_exit_with_1_before_any_worker_starts(started, capsys):
    assert entry.main({"SECRET_KEY": "short"}) == 1
    assert started == []
    error = capsys.readouterr().err
    assert "DATABASE_URL is required" in error
    assert "SECRET_KEY is too short" in error


def test_unwritable_data_folder_exits_with_1(started, env, tmp_path, capsys):
    blocker = tmp_path / "a-file"
    blocker.write_text("not a folder")
    env["DATA_DIR"] = str(blocker / "data")
    assert entry.main(env) == 1
    assert started == []
    assert "DATA_DIR" in capsys.readouterr().err


def test_unreachable_database_exits_with_1_after_the_wait(started, env, monkeypatch, capsys):
    monkeypatch.setattr(entry, "DATABASE_WAIT_SECONDS", 1)
    env["DATABASE_URL"] = "postgresql://rollcall:pw-not-shown@127.0.0.1:1/rollcall"
    assert entry.main(env) == 1
    assert started == []
    error = capsys.readouterr().err
    assert "database did not answer" in error
    assert "pw-not-shown" not in error


@pytest.mark.parametrize("workers", ["0", "17", "two"])
def test_bad_worker_count_exits_with_1(started, env, workers, capsys):
    env["WEB_CONCURRENCY"] = workers
    assert entry.main(env) == 1
    assert started == []
    assert "WEB_CONCURRENCY" in capsys.readouterr().err


def test_good_start_applies_migrations_then_starts_the_workers(env, monkeypatch):
    seen = {}

    def fake_run(app, **options):
        with psycopg.connect(env["DATABASE_URL"]) as conn:
            seen["migrations_table"] = conn.execute(
                "SELECT to_regclass('schema_migrations')"
            ).fetchone()[0]
        seen["app"], seen["options"] = app, options

    monkeypatch.setattr(entry.uvicorn, "run", fake_run)
    env["WEB_CONCURRENCY"] = "3"

    assert entry.main(env) == 0
    assert seen["migrations_table"] is not None  # upgraded before any worker started
    assert seen["app"] == "rollcall.main:create_app"
    assert seen["options"]["factory"] is True
    assert seen["options"]["host"] == "0.0.0.0"
    assert seen["options"]["port"] == 8000
    assert seen["options"]["workers"] == 3
    assert seen["options"]["server_header"] is False


def test_worker_count_defaults_to_2(env, started):
    assert entry.main(env) == 0
    [(_, options)] = started
    assert options["workers"] == 2


def test_data_folder_check_is_safe_when_workers_start_together(tmp_path):
    """Every worker checks the data folder at the same moment; none may trip over another."""
    import threading

    from rollcall.main import ensure_data_dir

    folder = tmp_path / "data"
    folder.mkdir()
    start_together = threading.Barrier(16)
    errors = []

    def worker():
        start_together.wait()
        for _ in range(50):
            try:
                ensure_data_dir(folder)
            except Exception as error:  # collected and reported below
                errors.append(error)

    threads = [threading.Thread(target=worker) for _ in range(16)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert errors == []
    assert list(folder.iterdir()) == []  # no leftover check files
