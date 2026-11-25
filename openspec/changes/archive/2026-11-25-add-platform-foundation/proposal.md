# Proposal: add the platform foundation

## Why

Every later Rollcall change (accounts, customers and tire sets, PDF pre-fill, dashboard) needs the
same base: a server that starts with one command, a database whose structure changes safely over
time, a shared page frame, and a test setup that runs against real PostgreSQL. Building it first,
on its own, means each later change only adds its own behavior. It is first in the build order in
`plan-rollcall-rewrite/design.md`.

## What Changes

- A Docker Compose stack with two containers, the app and PostgreSQL, started with one command. The
  data lives on persistent volumes.
- Settings read from the environment, with a `.env.example`. The app refuses to start, with a clear
  message, when a required setting is missing or invalid.
- Versioned database migrations applied automatically and exactly once at startup, even when
  several app processes start together.
- A health check that reports whether the app can reach its database.
- The page frame every later page uses: header, navigation and a message area. There is also a
  temporary start page, so the frame can be seen before any real page exists.
- Plain CSS and a vendored copy of htmx, both served by the app itself, so nothing is loaded from
  the internet.
- Friendly error pages that never show internal details, with a reference number that matches the
  server log.
- A test setup that runs against a throwaway PostgreSQL, plus linting.

## Capabilities

### New Capabilities

- `platform`: how Rollcall starts, is configured, upgrades its database, reports health, frames
  its pages, serves its assets and handles errors.

### Modified Capabilities

None.

## Out of scope

- Sign-in, staff accounts and any access control. That is `add-accounts`, next. Until then
  anyone on the shop network can open the start page; there is no data to protect yet.
- Customers, tire sets, history, PDFs and dashboard numbers. This change creates no business
  tables.
- HTTPS, the shop-trusted certificate, choosing the host machine, start after reboot, backups and
  the install guide. Those are all `add-operations`.
- Continuous integration (CI) and automatic dependency updates.
- The spec rules for two users saving the same record and for history do not apply here, because
  this change edits no records.

## Impact

- New at the repo root: `rollcall/` (Python package), `tests/`, `pyproject.toml` + `uv.lock`,
  `Dockerfile`, `compose.yaml`, `compose.test.yaml`, `.env.example`, `scripts/`.
- New dependencies: FastAPI, Uvicorn, Jinja2, psycopg 3 with its connection pool; for development,
  pytest, httpx and ruff. Pinned images: Python 3.13 and PostgreSQL 18.
- `legacy/` is untouched.
