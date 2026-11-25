# Tasks: add the platform foundation

Spec: `specs/platform/spec.md`. Design: `design.md`. Each behavior is test-first: write the test,
see it fail, implement, see it pass.

## 1. Project and test tooling

- [x] 1.1 Create `pyproject.toml` (Python 3.13; FastAPI, Uvicorn, Jinja2, psycopg[binary] +
  psycopg-pool; dev: pytest, httpx, ruff) and `uv.lock` with `uv lock`; add the `rollcall/` and
  `tests/` packages; extend `.gitignore` for `.ruff_cache/`. Verify: `uv sync` succeeds and
  `uv run python -c "import rollcall"` exits 0.
- [x] 1.2 Add `compose.test.yaml` (PostgreSQL 18 on tmpfs, `127.0.0.1:55432`), `tests/conftest.py`
  with a session fixture that creates and drops a uniquely named database, and `scripts/test.sh`
  (starts the test db if needed, then `ruff check`, `ruff format --check`, `pytest`). Verify:
  `scripts/test.sh` passes with one smoke test that runs `SELECT 1` in the fixture database.

## 2. Configuration

- [x] 2.1 Write `tests/test_config.py`: missing `DATABASE_URL` → error naming it; `SECRET_KEY` of
  31 chars → error "too short" without the value in the message; `SHOP_TIMEZONE=Mars/Base` → error
  naming the setting; defaults for `DATA_DIR`, `LOG_LEVEL`, `DB_POOL_SIZE`; `DB_POOL_SIZE=0`
  rejected. Verify: the tests fail (no module).
- [x] 2.2 Implement `rollcall/config.py` (`Settings` frozen dataclass, `load_settings(env)`
  raising `ConfigError`) and commit `.env.example` with every variable and a comment each
  (`SHOP_TIMEZONE=America/Chicago`).
  Verify: `tests/test_config.py` passes.

## 3. Database and migrations

- [x] 3.1 Write `tests/test_migrate.py` using temporary migration folders: pending migrations apply
  in number order and are recorded with `applied_at`; already-applied ones are skipped; a failing
  migration leaves no tables or rows behind, is not recorded, and raises an error naming its
  number; two threads running the runner together apply a migration once (assert one row and the
  migration's insert ran once); a recorded version missing from the folder raises the "newer
  version of Rollcall" error; a file name that doesn't match `NNNN_name.sql` is rejected. Verify:
  the tests fail.
- [x] 3.2 Implement `rollcall/db.py` (pool creation with first-connection retry for up to 60 s;
  `transaction()` context manager) and `rollcall/migrate.py` (`apply_migrations(conn, folder)`,
  advisory lock per design). Verify: `tests/test_migrate.py` passes, plus a test that the retry gives
  up with a clear error after the configured time (use a short timeout in the test).

## 4. Page frame, assets and security headers

- [x] 4.1 Vendor htmx 2.0.x (`htmx-<version>.min.js`) and Pico CSS 2.x (`pico-<version>.min.css`)
  into `rollcall/static/vendor/` from their official releases, recording each version, source URL
  and SHA-256 in `VENDORED.txt`. Write `tests/test_assets.py`: each file's SHA-256 matches
  `VENDORED.txt`; `/static/app.css`, `/static/app.js` and both vendored files return 200 with
  correct content types. Verify: the checksum
  test passes, and the route tests fail until 4.3.
- [x] 4.2 Write `tests/test_frame.py`: `GET /` returns 200, links the vendored Pico stylesheet, contains the "Rollcall" header, the
  `<nav>`, `id="messages"` and the "Rollcall is running" line; every `src`/`href` in the page is a
  relative or same-origin URL; every nav link returns 200; the response carries the CSP,
  `X-Content-Type-Options` and `Referrer-Policy` headers from design.md; the page sets
  `includeIndicatorStyles` to false. Verify: the tests fail.
- [x] 4.3 Implement `rollcall/main.py` (`create_app()`, lifespan checking `DATA_DIR` is writable, opening the pool and running
  migrations), `rollcall/web.py` (templates, nav registry, header middleware, shop-time filter),
  `templates/base.html`, `macros.html` (field, button, table), `start.html`,
  `rollcall/pages/start.py`, `static/app.css` (Pico variable overrides plus status badge styles; system fonts) and
  `static/app.js`. Verify: `tests/test_frame.py` and `tests/test_assets.py` pass.

## 5. Errors and health

- [ ] 5.1 Write `tests/test_errors.py`: an unknown path returns 404 with the "Page not found" page in
  the frame and a link to `/`; a test-only route that raises returns 500 with a reference code
  matching `E-[A-Z0-9]{6}`, and no traceback, file path or exception text in the body; the captured
  log has the same code and the traceback; the same failing route with `HX-Request: true` returns
  an error fragment, not a full page, containing the code. Write `tests/test_health.py`: 200 `ok`
  with the database up; 503 `database unavailable` with the pool pointed at a closed port, with
  nothing else in the body; returns to 200 once the database is reachable again. Verify: the tests
  fail.
- [ ] 5.2 Implement the error handlers and `error.html` in `rollcall/web.py`, the htmx error handler
  in `static/app.js` (4xx/5xx responses swapped into `#messages`), and `rollcall/health.py`.
  Verify: `tests/test_errors.py` and `tests/test_health.py` pass.

## 6. Docker stack

- [ ] 6.1 Write `Dockerfile` (pinned `python:3.13-slim` patch version, uv, `uv sync --frozen
  --no-dev`, non-root user, `uvicorn rollcall.main:create_app --factory`, `WEB_CONCURRENCY`
  default 2) and `compose.yaml` (`postgres:18` pinned minor with `pg_isready` health check and
  `db-data` at `/var/lib/postgresql`; app with health check via `/health`, `app-data` at `/data`,
  `depends_on` db healthy, published on `${APP_PORT:-8080}` on all host addresses). Verify: `docker compose up -d --build`
  shows both containers healthy within 60 s; `curl -s localhost:8080/health` and
  `curl -s <host-LAN-ip>:8080/health` both print `ok`.
- [ ] 6.2 Persistence and recovery check: add a throwaway migration in a scratch branch of the
  working copy (not committed), start the stack, then `docker compose down && docker compose up -d`.
  Confirm `schema_migrations` still has the row and the app log shows no migration applied on the
  second start. Then stop `db`: `/health` → 503. Start `db`: `/health` → 200 with no app restart.
  Verify: record the commands and outputs in the task's commit message. Remove the throwaway
  migration and reset the volume (`docker compose down -v`).
- [ ] 6.3 Concurrency check: with the stack up, send 50 parallel requests to `/` and `/health`
  (`seq 50 | xargs -P50 -I{} curl -s -o /dev/null -w "%{http_code}\n" localhost:8080/`). Verify: all
  return 200 and the app log has no errors.

## 7. What to try (shop owner, in a browser)

- [ ] 7.1 Owner sign-off:
  1. Run `cp .env.example .env`, fill in the two passwords, then run
     `docker compose up -d`.
  2. Open http://localhost:8080. You should see the Rollcall header and "Rollcall is running".
  3. From another PC or phone on the shop network, open http://<this PC's IP>:8080. Same page.
  4. Open http://localhost:8080/health. It should say `ok`.
  5. Open http://localhost:8080/nothing-here. You should see a friendly "Page not found" with a
     link back.
  6. Make the browser window phone-narrow. Nothing should scroll sideways.
  7. Run `docker compose stop db` and reload `/health`. It should say `database unavailable`. Run
     `docker compose start db` and reload. It should say `ok` again.
  8. Run `docker compose down`, then `docker compose up -d`. The start page loads again.

## Workflow follow-up

- After owner sign-off: `openspec archive add-platform-foundation`, verify `openspec/specs/platform/spec.md`
  exists, then tick 5.1 in `plan-rollcall-rewrite/tasks.md`.
