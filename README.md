# Tire & Wheel Storage — Stage 2

> Rollcall planning is now tracked in [docs/rollcall/README.md](docs/rollcall/README.md), with current decisions in [ROLLCALL_HANDOFF.md](ROLLCALL_HANDOFF.md). The specification is being prepared for consolidated review. Setup and accepted Stage 2 behavior below describe the existing app, not the future Rollcall workflow. No inventory implementation is implied by the planning documents.

Project navigation: [Master plan](MASTER_PLAN.md), [Project management](PROJECT_MANAGEMENT.md), [Skill register](PROJECT_SKILLS.md), [Verification evidence](VERIFICATION.md).

## Rollcall mockup quick launch

[Open the interactive mockup](docs/rollcall/interaction-preview.html). This standalone preview uses sample data and opens without starting the application services.

Local path on this development PC:

```text
C:\Users\ndcav\Documents\Codex\2026-10-21\referenced-chatgpt-conversation-this-is-an\outputs\tire-wheel-storage\docs\rollcall\interaction-preview.html
```

Browser address:

```text
file:///C:/Users/ndcav/Documents/Codex/2026-10-21/referenced-chatgpt-conversation-this-is-an/outputs/tire-wheel-storage/docs/rollcall/interaction-preview.html
```

UI component library: **HeroUI React/styles 3.2.7**, pinned and integrated across the existing dashboard and document-review controls. Tailwind styles load before HeroUI; the root uses the dark theme. Layout/category colors use project CSS and documented theme tokens. Functional development remains the priority, with broader visual redesign deferred. `npm.cmd run audit:ui` checks actual source/imports for native/custom widget replacements; `npm.cmd run build` runs it automatically before Vite. Runtime behavior and source review are still required alongside that guard.

React + Tailwind CSS (Vite), FastAPI, and PostgreSQL. Compose targets PostgreSQL 17; the native installation tested on this PC is PostgreSQL 18.6. Stage 1 is accepted. Stage 2 adds digital PDF upload, original-document archival, extraction, correction/review saves, and recent-document reopening. The dark dashboard retains truthful em-dash placeholder counts and disabled search. Business storage records, confirmed actions, VIN-history matching, OCR, payments, and staff accounts are later stages. Stage 2 is accepted by the user.

## Stage 2 setup and use

Follow the existing database/backend/frontend setup below. After installing updated backend requirements and before starting the backend, explicitly run this command from `backend`:

```powershell
.\.venv\Scripts\python.exe migrate_documents.py
```

It creates only `storage_documents` if absent; application startup never creates it implicitly. Digital-text extraction uses pypdf; tzdata supplies shop-local America/Chicago dates on Windows. Originals default to `backend/data/documents`; optionally set `DOCUMENT_ARCHIVE_DIR` to an absolute persistent folder in backend configuration. Preserve that location together with the PostgreSQL database. Source checkpoints deliberately exclude documents, extracted customer data, credentials, and database files.

Open the frontend and choose **Upload Invoice**. Select a digital invoice, authorization, or work-order PDF (10 MiB / 50 pages maximum), then **Upload PDF**. Review the proposed fields and warnings, expand Accessories for centering rings/lug nuts/center caps, and use **Save review**. This saves document review only; it cannot execute a swap, retrieval, renewal, or new storage period. Recent documents reopen saved reviews, and View original PDF retrieves the exact archived bytes. Exact-file repeats reopen the same document; different PDFs sharing a work order remain separate originals with a warning.

Original extraction stays immutable. Corrections and superseded review revisions are stored separately. A stale save returns a conflict and keeps local edits until explicit reload. Valid no-text/scanned PDFs remain available for manual review with a warning; there is no OCR. Malformed/encrypted PDFs are rejected. Date fallback and action proposals require review; later event-linking will enforce final-invoice precedence without duplicate storage actions.

The original setup/acceptance sections below describe foundation checks. For the current Stage 2 results and limitations see VERIFICATION.md. This session's manual preview uses frontend port 5174; the default README/Vite setup uses 5173.

This computer is the development PC, not the shop computer. Frontend/backend development servers start manually. Compose explicitly disables database automatic restart. This project has not installed a Windows login/startup task or service. An existing native PostgreSQL 18 Windows service was found running with automatic startup; it was left unchanged because it may serve other applications. Do not stop or reconfigure it as if it were a project-owned Compose container. Shop-computer startup behavior is a future deployment decision.

If you already created the database container using the earlier configuration, run `docker compose up -d --force-recreate db` once from this directory to apply the manual-start policy. This preserves the named database volume. The command starts the database for that session; use `docker compose stop db` when finished.

## Windows prerequisites

Install Python 3.12 or 3.13, Node.js 22 LTS (with npm), and Docker Desktop with Linux containers / WSL2 enabled when using Compose. Run commands in PowerShell from this project directory. Native PostgreSQL is an alternative: create a dedicated database/login, skip Compose, and set the backend DATABASE_URL accordingly. Native PostgreSQL 18.6 has passed the current foundation integration checks; choose one database route rather than starting both on the same port.

## Milestone 1: configuration and PostgreSQL

```powershell
Copy-Item .env.example .env
Copy-Item backend/.env.example backend/.env
Copy-Item frontend/.env.example frontend/.env
docker compose up -d --wait db
docker compose ps
```

Before starting, change the local example password in both root `.env` and `backend/.env` to the same value. Percent-encode special characters in the URL password. Root `.env` configures Compose; backend `.env` configures FastAPI; frontend `.env` configures the dev proxy. Do not commit these files. PostgreSQL credentials are applied on **first initialization** of the volume: editing `.env` later does not change an existing database password.

The named `postgres_data` volume retains data when containers restart or are removed normally. `docker compose down` preserves it. **Do not run `docker compose down -v`: that deletes the database volume.** Port 5432 binds only to localhost. If occupied, change the Compose host port and backend URL together.

## Milestone 2: backend

```powershell
cd backend
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

No activation script or execution-policy change is needed. Keep this terminal running. In a second PowerShell terminal, from the project root:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
Invoke-RestMethod http://127.0.0.1:8000/api/health/db
```

Expected: both return `status: ok`; DB also returns `database: postgresql`. Liveness does not require a database; DB readiness executes real `SELECT 1` with bounded connection/query timeouts and returns HTTP 503 with sanitized text when unavailable. API docs: http://127.0.0.1:8000/docs. No schema is silently created at startup.

## Milestone 3: frontend

In a third terminal, from the project root:

```powershell
cd frontend
npm.cmd install
npm.cmd test
npm.cmd run build
npm.cmd run dev
```

Open http://127.0.0.1:5173. Expect the four cards, placeholder counts, API Online and PostgreSQL Connected. `npm.cmd` avoids PowerShell script-policy problems. The included `pnpm-lock.yaml` records the versions tested here; alternatively use pnpm 11 (`pnpm install --frozen-lockfile`, `pnpm test`, `pnpm run dev`). npm resolves its own transitive dependencies on first install.

The dev server proxies `/api` to FastAPI; no broad CORS permission is required. Backend proxy configuration is server-only. `vite preview` serves static build output but does not provide the API proxy; use `npm.cmd run dev` for this milestone. Production hosting/authentication is outside Step 1; services are intended for local development.

## User-side acceptance checks

1. Confirm the dashboard on desktop and a narrow browser width; four labels and em dashes should be legible.
2. Stop PostgreSQL with `docker compose stop db`, refresh the dashboard, and confirm PostgreSQL Unavailable while API remains Online. Restart with `docker compose up -d --wait db`, refresh, and confirm Connected.
3. Stop FastAPI with Ctrl+C. Refresh and confirm the dashboard error and unavailable statuses. Restart FastAPI, refresh, and confirm recovery.
4. Verify **actual persistence**, from `backend`, while PostgreSQL is running:

```powershell
.\.venv\Scripts\python.exe check_persistence.py write
cd ..
docker compose down
docker compose up -d --wait db
cd backend
.\.venv\Scripts\python.exe check_persistence.py read
$env:TEST_DATABASE_URL = (Get-Content .env | Where-Object { $_ -like 'DATABASE_URL=*' }) -replace '^DATABASE_URL=', ''
.\.venv\Scripts\python.exe -m pytest -q
Remove-Item Env:TEST_DATABASE_URL
```

Expected: write/read each print PASS; the integration test runs instead of skipping. The probe creates one clearly named `foundation_probe` table solely to verify durability. It is not a storage record model. A fresh PostgreSQL instance begins with no business tables or records.

Stop frontend/backend with Ctrl+C and stop the database with `docker compose stop db`. On subsequent runs skip installation/configuration and start the database, backend, and frontend commands above.

## Troubleshooting

If `py` is missing, use your installed Python executable. If Docker is missing or its daemon is stopped, start/install Docker Desktop before Compose. For DB failures, inspect `docker compose logs db`, URL credentials, and port conflicts. For dashboard errors, check the backend terminal and `frontend/.env`; restart Vite after config changes. Never paste passwords into bug reports.

Official references: [Tailwind Vite installation](https://tailwindcss.com/docs/installation/using-vite), [FastAPI testing dependencies](https://fastapi.tiangolo.com/advanced/testing-dependencies/), [PostgreSQL Docker image](https://hub.docker.com/_/postgres).
