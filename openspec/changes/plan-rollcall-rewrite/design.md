# Design: plan the Rollcall rewrite

## Context

`legacy/` contains v1: React + HeroUI frontend, FastAPI + PostgreSQL backend, a pypdf-based
Protractor parser, an Electron client and about 40 planning documents. Its tests pass, and its
data-integrity code is careful, but only about 3,000 lines of application code exist and the
central workflow was never built. v1 only ever held synthetic data, so there is nothing to migrate.

Useful v1 knowledge to re-adopt deliberately (summarized in Phase 0, step 3):

- Protractor PDF layout and quirks: `legacy/backend/app/document_parser.py` and its tests
  (`legacy/PROTRACTOR_INVOICE_PDF_HANDOFF.md` is an unrelated bulk-export side project).
- Tire size formats: metric `225/55R17` ↔ `2255517`; flotation `35x12.50R20` ↔ `35125020`.
- Accessories (lug nuts, center caps, centering rings) as unknown/yes/no, never defaulting to no.
- Content-addressed PDF archive with atomic writes; version-checked saves:
  `legacy/backend/app/document_store.py`.
- Coordinated database + PDF backup with checksums: `legacy/backend/backup_rollcall.py`.

## Goals / Non-Goals

**Goals**

- CRUD for customers and their tire sets, with tire size, tread depth and related details.
- PDF upload pre-fills the form; original shown beside it; staff review and save.
- User accounts with admin user management; every change attributed and kept in history.
- Dashboard: sets in shop, sets in shop too long, and a few other useful stats.
- Many simultaneous users without lost or silently overwritten changes.
- Docker-hosted server; any browser on the shop LAN is the client.

**Non-Goals**

Automatic inventory changes from PDFs; storage-period billing and renewals; payments and
scheduling (Protractor owns these); OCR; Electron; React or any frontend build step; remote access;
migrating v1 data.

**Anti-goals** (failure even if it technically works)

- Growing back into many pages. Target set: sign-in, dashboard, tire list/search, tire set
  form/detail (with PDF review), customer view, admin settings.
- PDF reading turning into a rules engine. It only suggests form values.
- Silent overwrites between users, or history that can be lost or edited.

## Decisions

| Topic | Decision | Source |
|---|---|---|
| Rewrite | Ground up; v1 is reference only, kept in `legacy/` | Owner |
| Documentation | OpenSpec only | Owner |
| Server | Docker Compose: app container + PostgreSQL (+ HTTPS proxy) | Owner (Docker); assistant (layout) |
| Frontend | Server-rendered HTML (FastAPI + Jinja2) + htmx; plain CSS/JS | Owner chose option 1 |
| Concurrency | Must handle many users at once; version-checked saves | Owner; assistant (mechanism) |
| Accounts | Yes, for attribution and history | Owner |
| First admin | First account on a fresh install | Owner |
| Admin powers | Promote to admin; user-management settings | Owner |
| Account creation | Admin creates accounts with a temporary password; no self-signup after first admin | Assistant proposal, not objected to |
| Deactivation | Deactivated users can't sign in, their history stays; last admin can't be removed | Assistant proposal, not objected to |
| PDF | Pre-fill the form; staff review and save | Owner |
| Customer from PDF | Form suggests existing customers with similar names; staff pick or create new; never auto-merge | Assistant call |
| Sample PDFs | Real samples kept in git-ignored `samples/private/`; committed tests use synthetic PDFs | Assistant call |
| Root record | The **customer** is the root. Staff create a customer (e.g. Bob) and log the tires he stores under him | Owner |
| Returning tires | Tire sets stay under the customer permanently. Staff toggle a set **checked in** when it arrives and **checked out** when it leaves; it can return any number of times | Owner |
| Stays | Each check-in/check-out pair is kept as a stay in the set's history | Assistant (follows from owner decision) |
| Customers don't sign in | Customers are records only; only staff have sign-in accounts. "Customer" and "staff account" are the terms used in specs to avoid two kinds of "user" | Assistant proposal, confirm in Phase 2 |
| Record unit | A stored item is a set of tires, tread depth per wheel position | Assistant proposal, confirm in Phase 2 |
| "Too long" | One shop-wide threshold, measured from the current stay's check-in | Assistant proposal, confirm in Phase 2 |
| Go-live | Staff start using the app only after every change is built | Owner |
| Branch | Work on `rewrite`; merge when the rewrite replaces v1 | Assistant call |

### Stack approaches considered

1. **FastAPI server-rendered HTML + htmx — chosen.** Least JavaScript; logic in one place; reuses
   Python PDF knowledge.
2. FastAPI JSON API + plain-JS frontend. Every form, list and error built twice.
3. Node.js throughout. One language, but weaker layout-preserving PDF text extraction.

React was considered and rejected: the app is lists, forms and server round-trips, so React adds a
build step, a JSON API and client state without paying for itself. PostgreSQL is chosen over SQLite
for many concurrent writers.

## Planning roadmap

### Phase 0 — Set up (done in this change)

1. `rewrite` branch; v1 moved to `legacy/`.
2. `openspec init`; project constraints in `openspec/config.yaml`.
3. Write `openspec/changes/plan-rollcall-rewrite/v1-lessons.md`: the reference summary listed under
   Context, plus what went wrong in v1, so later work never needs to re-read the 40 v1 documents.

### Phase 1 — Confirm the capability map

The eight capabilities in proposal.md. Confirm with the owner, merge or split if needed.

### Phase 2 — Settle product questions (one bundled review)

With recommendations, covering at least the Open Questions below plus:

- Exact tire set fields and units (tread depth in 32nds of an inch).
- What "remove" means: set leaves the shop; record and history stay (recommended).
- Dashboard stats beyond count and too-long; the threshold value.
- Search fields (customer, size, RO, vehicle…).
- Vehicles as their own records or as text on the set.
- Which PDF fields to pre-fill.

### Phase 3 — Spec and build, one change at a time

Decided 2026-11-23 by the owner: write one change, build it, then write the next. Phases 1 and 2
come first because they fix the decisions every change depends on; after that, each change is
specified with the real code of the earlier changes in hand.

Order:

1. `add-platform-foundation`
2. `add-accounts`
3. `add-customers-and-tire-inventory` (audit history folded in if small, else `add-audit-history`)
4. `add-pdf-prefill`
5. `add-dashboard`
6. `add-operations`

Cycle for each change:

1. **Spec:** write proposal, specs, design and tasks; check against the archived specs of earlier
   changes and the Review focus list; `openspec validate <name>` passes; owner reviews.
2. **Build:** implement its tasks test-first; verify in a running Docker stack (several browser
   sessions at once where relevant).
3. **Sign-off:** owner follows the change's "What to try" list.
4. **Archive:** `openspec archive <name>`, which merges its specs into `openspec/specs/`. Only
   then does the next change start.

Because staff only start after everything is built, HTTPS, backups and the host choice stay in
`add-operations`. Before go-live, `add-operations` must be finished and the full stack rehearsed.
This planning change is archived with `--skip-specs` after the last change is archived.

## Open Questions

None blocking. Both earlier questions are answered (see Decisions):

- Tire sets return: they stay under the customer and are toggled checked in / checked out; stays
  are kept. "In shop" counts sets currently checked in; "too long" uses the current stay.
- Go-live is after all changes are built, so HTTPS, backups and the host choice stay in
  `add-operations`, last in the build order.

## Risks / Trade-offs

- **Docker on the Windows office PC** (Docker Desktop/WSL2) is less dependable at restarting after
  reboot than a Linux host. Mitigation: decide the host early; test reboot recovery.
- **HTTPS on a LAN** needs a certificate the shop's browsers trust. Mitigation: an HTTPS proxy
  container with a shop-local certificate; covered in `platform` or `operations`.
- **PDF reading is layout-dependent.** Mitigation: it only suggests values; staff always review.
- **No-build frontend** means no component framework. Mitigation: Jinja2 template macros for
  repeated parts (fields, tables, buttons).

## Left to the builder

Python package layout; template organization; CSS approach (plain or a minimal classless
stylesheet); migration tool (Alembic or numbered SQL); password hashing (argon2 recommended);
session storage; PDF viewer in the review screen (browser built-in or pdf.js); test tooling,
linting and CI.
