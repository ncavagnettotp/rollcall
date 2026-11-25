"""The test setup itself: every test run gets its own real PostgreSQL database."""


def test_database_answers(db):
    assert db.execute("SELECT 1").fetchone() == (1,)


def test_database_is_a_throwaway(db, database_url):
    name = db.execute("SELECT current_database()").fetchone()[0]
    assert name.startswith("rollcall_test_")
    assert database_url.endswith("/" + name)


def test_database_is_postgresql_18(db):
    version = db.execute("SHOW server_version_num").fetchone()[0]
    assert version.startswith("18")
