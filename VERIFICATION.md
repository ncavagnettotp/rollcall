# Rollcall planning package — November 11, 2026

Latest visual-foundation batch: shared standalone preview restyled against the supplied dashboard reference, licensed local font bundled, Dashboard comparison added, customer/profile navigation retained. Real headless Edge now runs with reviewed execution permission; desktop and narrow screenshots, font loading, overflow checks at six widths, sidebar label/badge spacing and profile navigation/location interactions pass. See [current planning evidence](docs/rollcall/verification.md) and `output/rollcall-visual/`. Earlier preview-browser limitations below are superseded. User visual approval and production runtime/database checks remain pending.

Draft specification and expandable 31-step checklist saved under [docs/rollcall](docs/rollcall/README.md). Independent document review findings corrected and rechecked. Four approved references preserved/inspected; local links, inline mockup script and simulated interactions checked. Real Edge could not launch in the sandbox; visual/mobile preview verification remains open. No fresh application runtime tests or product/database/deployment changes in this planning batch. See [planning evidence and limits](docs/rollcall/verification.md). Specification user review remains required before implementation planning/product work.

# HeroUI visual refresh — November 11, 2026

Existing screens now follow native HeroUI dark visual styling, not only its controls. Legacy root theme/font/field overrides removed; native Typography, card sections, status Chips, separators, primary actions, and contrasting secondary fields adopted. Spacious category grid and semantic colors retained. **9 frontend tests passed**, mandatory HeroUI audit/build passed, desktop/mobile visual and upload/save/reopen/feedback checks passed. Independent review found no important issues. See [visual verification](docs/verification/2026-11-11-heroui-visual.md). Source checkpoint: checkpoints/heroui-visual-2026-11-11.zip. Backend unchanged; two existing upstream CSS optimizer warnings remain.

---

# HeroUI foundation conversion — November 10, 2026

Existing dashboard/upload/review controls converted to actual HeroUI React/styles3.2.7, pinned with lockfile. Source audit passes and is enforced by npm run build. Final real-component suite: **9 passed**; production build: **passed**,1783 modules; real Edge upload/select/save/reopen, dashboard failure/recovery, and desktop/mobile visible-feedback checks passed. Independent review found no important issues. Full audit, component inventory, fixes and remaining two upstream CSS optimizer warnings: [HeroUI verification](docs/verification/2026-11-10-heroui-audit.md). Source checkpoint: checkpoints/heroui-foundation-2026-11-10.zip. Backend unchanged.

---

# Stage 2 — November 10, 2026

Post-review interaction fix: reproduced successful HTTP 200 saves whose confirmation was above the viewport (top -614px), and archived-item clicks whose loaded review stayed above the viewport (top -1254px). Save success/errors/conflicts now appear beside the Save button; archive/upload opening focuses and scrolls to the review heading. Dashboard includes a direct Review uploaded documents button. Two targeted assertions failed before the fix; all 9 frontend tests/build passed afterward. Real Edge viewport assertions plus the full Stage 2 browser flow passed. No backend/storage-state change was needed. Original checkpoint retained; updated source checkpoint is `checkpoints/stage2-feedback-2026-11-10.zip`.

Working flow: Upload Invoice opens a dedicated dark upload/review view. Digital PDFs are archived on disk; extracted fields, warnings, correction history, and revisions persist in PostgreSQL. Recent documents reopen reviews; original PDFs are served byte-for-byte. Saving a review performs no business-storage action. Stage 1 remains accepted; Stage 2 is accepted by the user.

| Check | Result |
|---|---|
| Frontend Vitest | **9 passed**, 2 files; final coordinator run after accessible-label fix |
| Production Vite build | **Passed**, 31 modules |
| Backend full suite with real isolated PostgreSQL | **23 passed**, 6.39s, one preexisting Starlette/AnyIO warning |
| Actual sample API acceptance | **8/8 PDFs passed**, 15 pages; dates/internal IDs, retrieval exceptions, staggered size evidence, explicit/unknown accessories, replacement note |
| Original PDF retrieval | SHA256/byte equality verified for all eight originals |
| Exact duplicate upload | Same archive ID returned, duplicate flag true; concurrent upload regression uses real SQL and verifies one row/file |
| Authorization + invoice for same work order | Separate originals retained; related-source warning verified with fictional integration fixtures |
| Review correction/history | Original extraction immutable; prior corrected fields/history retained; stale revision **409**; save/reopen verified |
| Invalid/no-text PDFs | Malformed/encrypted/over-50-page rejection; no-text PDF retained with explicit manual-review warning; 10 MiB limit validated |
| Real browser, Edge | Upload/duplicate reopen, original link, three accessories, save/reload/archive reopening; no page errors |
| Mobile 390px | No horizontal overflow; desktop/mobile review screenshots inspected |
| Real database restart durability | Original bytes, extraction, corrected review, and revision survived restart of isolated project-only native PG18.6 cluster |
| Database failure/recovery | Isolated cluster: readiness 503 while API remains live, then readiness 200 after restart |
| Independent review | No important correctness issues remaining; final-invoice precedence ruling reconciled with specification |

Coordinator applied `backend/migrate_documents.py` explicitly to the configured development database. It creates only `storage_documents`; startup does not create schema. Eight supplied samples and one blank verification PDF are archived as development review data. No Customers/Vehicles/TireSets/StoragePeriods/StorageEvents tables or real transactions were introduced. During final parser verification, only this run's own unedited sample seed rows were backed up and refreshed; original PDF files remained intact. Real customer documents and private screenshots are excluded from source checkpoints.

Current artifacts:

- `docs/verification/2026-11-10-stage2-api.json`: credential-free eight-sample API acceptance summary.
- `docs/verification/2026-11-10-stage2-restart.json`: credential-free restart evidence.
- `output/isolated-postgres/run-c363a18f3295/pytest.log`: full isolated backend test log (ignored runtime artifacts).
- `output/stage2-private/review-desktop.png` and `review-mobile.png`: local review screenshots containing sample customer information; excluded from checkpoints.
- `work/verify-stage2.py` and `verify-stage2.cjs`: manual acceptance scripts; API requires 8000, browser expects frontend 5174 and bundled Playwright/Edge.
- `checkpoints/stage2-2026-11-10.zip`: source-only archive and separate SHA256 manifest.

Limits: extraction is conservative and validated against these samples, not a guarantee for every future Protractor layout. Unknown source data requires manual review. Invoice identity and exact-file deduplication are implemented; cross-document business-event reconciliation/final-invoice supersession will be applied when events/periods exist in later stages. No OCR, business record/search/count implementation, login, payment tracking, automatic renewals, or production deployment. Raw parser bounds are practical development limits, not a hardened process sandbox. PostgreSQL's machine-wide service was not restarted or reconfigured; Docker/PG17 runtime remains untested.

Date ruling: an explicit final Invoice Date wins over provisional authorization dates normally, without an extra confirmation question. Conflicting dates at the same priority still warn. A missing usable source date gets a labeled current America/Chicago fallback. tzdata is pinned for this Windows behavior.

---

# Stage 1 continuation — October 30, 2026

The latest Stage 1 dashboard now follows the selected dark design with a two-column desktop grid and translucent green, amber, red, and slate cards. The earlier October 21 appearance/results below are historical.

| Current check | Result |
|---|---|
| Frontend Vitest | **4 passed**, independently rerun by coordinator |
| Production Vite build | **Passed**, 29 modules |
| Backend baseline | **6 passed, 1 skipped** without TEST_DATABASE_URL |
| Backend against configured native PostgreSQL | **7 passed**, real integration enabled |
| Installed database | Native PostgreSQL **18.6**; real SELECT 1 and existing probe marker read succeeded |
| Browser, installed Edge | **Passed** against actual Vite proxy/FastAPI/native PostgreSQL; API Online and PostgreSQL Connected |
| Desktop 1280×1000 and mobile 390×844 | **Passed**; screenshots visually inspected, no horizontal overflow; exactly four cards with two desktop columns |
| Browser failure/recovery | **Passed** with intercepted DB 503 and API request failures, then refresh back to real connected backend; these browser failures were simulated |
| Isolated real PostgreSQL stop/restart | **Passed** on dedicated port 55432; marker survived restart, database readiness 200 → 503 → 200, API liveness remained 200 |
| Backend suite on isolated restarted cluster | **7 passed**, 3.51s |
| Independent source review | No important correctness issues found; browser card-count assertion strengthened and screenshots refreshed after final copy |

The isolated PostgreSQL verifier uses native PG18 binaries, a unique project-only cluster, random SCRAM credentials, and manual lifecycle. It does not modify backend/.env or the installed service. It stopped its cluster on completion and deleted its temporary initialization password file. Full cluster artifacts remain under ignored `output/isolated-postgres/`; the credential-free evidence summary is copied under `docs/verification/`.

The installed `postgresql-x64-18` service was found running with Automatic startup. It may serve other applications and was **not** restarted, disabled, or reconfigured. This is an existing machine condition, distinct from this project's manual frontend/backend startup and Compose `restart: "no"` policy. The actual configured database's restart was not exercised. Docker is unavailable, so Compose runtime/recreation and PG17-specific behavior remain untested; the native PG18 path supplied real connectivity and isolated restart evidence instead.

The existing Starlette/AnyIO deprecation warning remains. Runtime commands stalled or could not access processes/localhost inside the sandbox; approved outside-sandbox runs supplied the successful evidence above.

Useful checks from project root (adapt executables to your Python/Node installation):

```powershell
cd frontend
node node_modules/vitest/vitest.mjs run
node node_modules/vite/bin/vite.js build
cd ../backend
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe verify_isolated_database.py --bin-dir 'C:/Program Files/PostgreSQL/18/bin'
```

The isolated verifier requires a free loopback port 55432 and initialized Python dependencies. The browser acceptance script is `work/verify-dashboard.cjs`; it uses the preexisting bundled Playwright runtime and expects backend 8000/frontend 5174. Screenshots: `output/playwright/stage1-desktop.png` and `stage1-mobile.png`.

**Acceptance:** User explicitly accepted Stage 1 after reviewing the foundation and documented limitations. Stage 2 implementation has not started. Search, invoice upload, category filtering, business records, and real counts remain unimplemented; future controls are disabled and counts stay em dashes. Source checkpoint is recorded in PROJECT_MANAGEMENT.md.

---

# Step 1 verification — October 21, 2026

Design revision: simplified to a sidebar and four pastel-header storage columns, following the user's visual reference. Preserved placeholder counts, empty record areas, refresh behavior, and compact API/database statuses. Reverified: 3 frontend tests passed; production build passed (29 modules); Edge desktop/mobile smoke check passed with no horizontal overflow at 390px. Updated screenshots included. No later workflow or automatic startup was added.

## Scope delivered

React/Tailwind dashboard with Stored, Due Soon, Overdue, Needs Attention; explicitly labeled null placeholder counts; refresh, loading and failure/recovery behavior. FastAPI liveness, PostgreSQL readiness, dashboard endpoints and OpenAPI docs. PostgreSQL 17 Compose service with named persistent volume. Configuration templates, Windows PowerShell commands, automated tests, and an explicit persistence probe. No invoice parsing, OCR, record workflows, or later milestones.

## Results

| Check | Result |
|---|---|
| Backend full suite (`python -m pytest -q`) | **6 passed, 1 skipped**, 3.81 seconds |
| Frontend full suite (`vitest run`) | **3 passed**, 1 test file |
| Production frontend (`vite build`) | **Passed**, 29 modules, 1.09 seconds |
| Browser smoke check (installed Edge through Playwright) | **Passed**: real Vite proxy to running FastAPI, four category headings, API Online, PostgreSQL Unavailable |
| Desktop 1280×800 / mobile 390×844 | **Passed**: screenshots inspected; no mobile horizontal overflow |
| Live PostgreSQL SELECT 1 | **Not run**: no PostgreSQL or Docker executable available |
| PostgreSQL persistence across container recreation | **Not run**: requires Docker/PostgreSQL; commands in README |
| Docker Compose runtime validation | **Not run**: Docker unavailable |
| Fresh-machine installation using stock Windows Python/npm | **User-side check remains**; testing here used bundled Python 3.12 and pnpm |

Backend tests verify liveness, exact dashboard labels/placeholders, missing DB configuration, real refused-connection sanitization, and dependency-controlled success/failure responses. A mocked success does **not** prove live DB connectivity. The optional test requires TEST_DATABASE_URL and actually executes SELECT 1. No SQLite replacement was used.

One warning: Starlette TestClient references the deprecated `anyio.abc.BlockingPortal` alias. Tests pass; this is a dependency warning, not suppressed.

Frontend tests verify successful cards/connectivity, request failure with refresh recovery, and unsuccessful DB HTTP status handling. Screenshots show PostgreSQL Unavailable truthfully because no database was running.

Dependency installation required network approval after sandbox failures. pnpm initially blocked dependency build scripts; explicitly allowed builds are recorded in pnpm-workspace.yaml. The subsequent direct Vitest and Vite build commands passed using installed platform binaries. Python dependencies were installed into a workspace virtual environment, not system Python. requirements-lock.txt captures the tested Python dependency set (Python 3.12/Windows); requirements.txt pins direct dependencies.

## Remaining acceptance

Development-PC correction: Compose now explicitly uses `restart: "no"`. All project startup is manual; no Windows startup task or service is installed. Existing containers must be recreated with the README command to apply the changed policy. This configuration change was inspected in source and the updated ZIP; runtime Docker verification remains unavailable here.

Follow README milestones on the user's Windows machine, verify PostgreSQL Connected, exercise database/backend stop-and-recovery, and run the write → container recreation → read persistence check. Confirm the four category labels and appearance. Approve Step 1 before starting later work.
