# Design: add the platform foundation

## Context

The repo root is empty apart from `legacy/` and `openspec/` (see proposal.md, Why). The stack is
fixed by `plan-rollcall-rewrite/design.md`: FastAPI with Jinja2 and htmx, PostgreSQL, Docker
Compose, and no frontend build step. That plan left several choices to the builder: package
layout, migration tool, CSS approach and test tooling. This design makes them. v1 lessons that
apply here: pin runtimes, use versioned migrations instead of `CREATE TABLE IF NOT EXISTS`, and
never send database errors to the browser (`plan-rollcall-rewrite/v1-lessons.md` §4–5).

## Goals / Non-Goals

**Goals:**
- Choices later changes can follow without rethinking: where code goes, how a page is added, how a
  migration is added, how a test gets a database.
- Correct under many simultaneous requests from the start: a connection pool, more than one worker
  process, and migrations that lock.

**Non-Goals:**
- Production hardening beyond what is needed to run on one host. That belongs in `add-operations`.
- Any abstraction for features not yet specified, such as a repository layer, a service layer or
  an ORM.

## Decisions

### Layout
```
rollcall/            Python package
  main.py            create_app(): app factory, lifespan (pool + migrations), middleware
  config.py          Settings, read and checked once from the environment
  db.py              connection pool, transaction helper
  migrate.py         migration runner
  web.py             templates, error pages, security headers
  health.py          /health
  pages/start.py     temporary start page (removed when the dashboard exists)
  migrations/        0001_<name>.sql, 0002_<name>.sql, ...
  templates/         base.html, macros.html, error.html, start.html
  static/            app.css, app.js, vendor/htmx-<version>.min.js, vendor/pico-<version>.min.css
tests/
compose.yaml         production-shaped stack (app + db)
compose.test.yaml    throwaway test database
scripts/test.sh      start test db, run ruff + pytest
```
Each later capability adds its own module (for example `rollcall/customers.py`), with its routes
and SQL together, plus its templates. The package is split by feature, not by layer.

### Database access: psycopg 3 with plain SQL, no ORM
Queries are written in SQL with psycopg 3 and its `ConnectionPool`. Request handlers are ordinary
(synchronous) functions, and FastAPI runs them on its thread pool. The alternatives were
SQLAlchemy, and async psycopg. Version checks, `SELECT ... FOR UPDATE` and advisory locks are
clearest in plain SQL. At shop scale, synchronous code with a pool is simpler to test and debug
than async. Pool size is a setting (default 10 per process).

### Migrations: numbered SQL files and a small runner
The runner takes `pg_advisory_lock` (one fixed key), creates `schema_migrations(version int primary
key, name text, applied_at timestamptz)` if it is missing, then applies each pending
`NNNN_name.sql` in its own transaction and inserts the matching row in the same transaction. If the
database has a version the code does not, the runner refuses to start. Migrations only move
forward; to undo a change, write a new migration. The alternative was Alembic, whose autogenerate
needs an ORM and which brings its own configuration tree. Thirty lines of runner are easier to
understand and test. This change adds no business tables, so there is no `0001` migration; the
runner is tested with migration folders created inside the tests.

### Processes and concurrency
Uvicorn runs with `WEB_CONCURRENCY` worker processes (default 2). Every worker runs the migration
runner at startup, and the advisory lock makes that safe. Each worker has its own pool. All later
writes use explicit transactions through `db.transaction()`.

### Configuration
`config.py` reads `os.environ` into a frozen dataclass at startup. There is no settings library.
| Variable | Required | Rule |
|---|---|---|
| `DATABASE_URL` | yes | `postgresql://` URL |
| `SECRET_KEY` | yes | ≥ 32 characters; used by `add-accounts` for sessions |
| `SHOP_TIMEZONE` | yes | valid IANA name (`zoneinfo`), used for "this week" and displayed times; the shop's is `America/Chicago` (set in `.env.example`) |
| `DATA_DIR` | no, `/data` | must be writable; holds PDFs later |
| `LOG_LEVEL` | no, `INFO` | standard level name |
| `DB_POOL_SIZE` | no, `10` | 1–50 |
| `APP_PORT` | no, `8080` | port published by Compose on the host |

Compose builds `DATABASE_URL` from `POSTGRES_PASSWORD` in `.env`. `.env.example` is committed, and
`.env` stays git-ignored. Error messages name the variable but never echo its value.

### Times
Every timestamp is stored as `timestamptz` in UTC. Times are converted to `SHOP_TIMEZONE` only when
shown, using one Jinja filter.

### Page frame, CSS and htmx
- `base.html` holds the header ("Rollcall"), `<nav>` built from a list of `(label, url)` pairs that
  each capability registers, `<div id="messages">`, and `<main>`. `macros.html` holds the shared
  form field, button and table macros, so every form looks the same.
- CSS is **Pico CSS v2** (owner decision, 2026-11-24) plus a small `app.css`. Pages are written
  as plain semantic HTML (`<nav>`, `<form>`, `<label>`, `<table>`, `<article>`, `<button>`), which
  Pico styles without classes. Invalid fields use `aria-invalid="true"`, which Pico shows in red.
  Colours and spacing are adjusted through Pico's CSS variables at the top of `app.css`.
  `app.css` holds only what is specific to Rollcall: status badges (in shop, out, too long),
  dashboard tiles and the PDF-beside-form layout. It is mobile-first, with no web fonts (system
  font stack). Alternatives were hand-written CSS only (every form and table styled by hand, where
  v1 lost time on polish) and Bootstrap (heavy, class-heavy markup, most of it unused).
- htmx 2.0.x and Pico 2.x are copied into `static/vendor/` under file names that include their
  versions. Their versions, source URLs and SHA-256 hashes are recorded in
  `static/vendor/VENDORED.txt`, and a test checks each file against them.
- `app.js` holds the htmx error handler. On a 4xx or 5xx htmx response it swaps the response's
  error fragment into `#messages` instead of dropping it. That is htmx 2's default behavior, which
  would otherwise make a failed save look like nothing happened.
- Security headers on every response:
  - `Content-Security-Policy: default-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'`
  - `X-Content-Type-Options: nosniff`
  - `Referrer-Policy: same-origin`

  htmx's own inline indicator styles are turned off (`htmx.config.includeIndicatorStyles = false`),
  so the policy needs no `'unsafe-inline'`.

### Errors and logging
Handlers for 404 and for unhandled exceptions render `error.html`, or an error fragment for htmx
requests, identified by the `HX-Request` header. An unhandled error gets a 6-character reference
code. It is logged with the stack trace and the request path. Logs are written as plain text lines
to stdout, which Docker collects.

### Health check
`GET /health` borrows a pool connection with a 2-second timeout and runs `SELECT 1`. If that works
it returns `200 ok`; if anything fails it returns `503 database unavailable`. The compose health
check calls it with Python's `urllib`, so the image needs no curl. The database container uses
`pg_isready`.

### Docker
- Image: `python:3.13-slim` pinned to a patch version, with dependencies installed by
  `uv sync --frozen --no-dev` from `uv.lock`. It runs as a non-root user and exposes port 8000.
- `postgres:18` pinned to a minor version, with a named volume `db-data` mounted at
  `/var/lib/postgresql`, the mount point PostgreSQL 18 images expect. The named volume `app-data`
  is mounted at `/data`.
- The app depends on the database being healthy, and also retries its first connection for up to
  60 seconds.
- The app is published on all of the host's network addresses at port `APP_PORT` (default
  `8080`), so it opens both as `http://localhost:8080` on the host and as
  `http://<host-ip>:8080` from any PC on the shop network (owner decision, 2026-11-24). HTTPS in
  front comes with `add-operations`; the host firewall must allow the port.

### Tests
pytest with FastAPI's `TestClient` (httpx). `compose.test.yaml` runs PostgreSQL on `tmpfs` at
`127.0.0.1:55432`. A session fixture creates a uniquely named database, runs the real migrations
and drops it at the end. Tests that need special migrations use their own temporary database.
`scripts/test.sh` starts the test database if needed, then runs `ruff check`, `ruff format --check`
and `pytest`. Tests always use real PostgreSQL, never SQLite, because locking behavior is part of
what they check.

## Risks / Trade-offs

- [The pinned PostgreSQL 18 volume layout differs from 17] → mount at `/var/lib/postgresql` as its
  image expects. The persistence check in tasks recreates containers and confirms the data is still
  there.
- [htmx 2 drops error responses by default] → handle this in `app.js`, with a test that the error
  fragment and the `#messages` target are both present. The browser check in "What to try" confirms
  it.
- [Strict CSP breaks inline scripts or styles added later] → this is deliberate. Later changes put
  JavaScript in `static/` files, and a test asserts the header on every page.
- [Synchronous handlers block a thread during slow queries] → the thread pool has 40 threads by
  default, with 2 workers. The integration check runs 50 parallel requests.
- [Plain HTTP on the shop network, and no sign-in until `add-accounts`] → acceptable, because no
  real data exists before go-live; sign-in arrives in the next change and HTTPS in
  `add-operations`.
- [Windows/Linux host firewalls block the port by default] → the "What to try" list includes
  opening it from a second PC; the install guide in `add-operations` covers firewall rules.

## Migration Plan

Nothing to migrate, since this is the first code. Rollback means removing the new root files; the
`legacy/` code is unaffected.
