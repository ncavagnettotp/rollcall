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
| Customers don't sign in | Customers are records only; only staff have sign-in accounts. "Customer" and "staff account" are the terms used in specs to avoid two kinds of "user" | Owner (Q8) |
| Customer fields | First name, last name, one or more phones, email, notes; no address | Owner (Q8) |
| Record unit | A **tire set**: 1–8 tires (usually 4) stored together for one customer; one size or two (staggered front/rear); each tire has a position (LF, RF, LR, RR, Extra) | Owner (Q1) |
| Tread depth | Recorded per tire on **every check-in**, in 32nds of an inch (whole numbers 0–20), kept on the stay; the set shows the latest readings; blank allowed; never from the PDF | Owner (Q2) |
| Set fields | Size(s); brand and model; on wheels or tires only, with wheel description; season; lug nuts, center caps, centering rings, TPMS sensors, each unknown/yes/no; notes. Per tire: position, **DOT date code** (4 digits, week + year, optional) | Owner (Q3) |
| Stay fields | Check-in date, RO number, storage location, tread depths, check-out date, attached PDF if any | Owner (Q2, Q3, Q9) |
| Not stored | Condition grades, photos, storage pricing | Owner (Q3) |
| Remove | Nothing is deleted. A set can be archived only while checked out; a customer only when none of their sets are checked in; both hidden from search and restorable; history kept | Owner (Q4) |
| Roles | Every staff account does all inventory work; admins also manage staff accounts and shop settings | Owner (Q5) |
| Dashboard | Sets checked in now; sets in too long; checked in this week; checked out this week; customers with a set in the shop. Each links to the matching search | Owner (Q6) |
| "Too long" | Current stay older than one shop-wide threshold, default **6 months**, changeable by admins | Owner (Q6) |
| PDF for a returning customer | The form suggests the existing customer; staff can check one of their checked-out sets in from the PDF instead of creating a new set. Every value the new PDF provides **replaces** the stored value in the form, with no per-field choice; fields the PDF could not read keep their stored value (a blank never wipes data). Staff still review the form and save, as for any PDF; previous values stay in history. The new PDF is attached to the new stay; earlier PDFs stay with earlier stays | Owner (Q7); blank-keeps-stored is the assistant's call |
| PDF fills | Customer name, phone, email; vehicle, VIN, plate; RO and invoice numbers; invoice date as check-in date; size(s) and brand from storage notes; accessories. Never tread depth, DOT codes or location | Owner (Q7) |
| Vehicles | Text on the set (year make model, optional VIN and plate); no vehicle records | Owner (Q9) |
| Storage location | On; optional free text on each stay; current location shown while checked in | Owner (Q9) |
| Search | One box: customer name, phone, tire size (digits only), brand, vehicle, VIN, plate, RO, location. Filters: in shop, out, too long, archived. Archived hidden by default | Owner (Q10) |
| Mockups | Pages are designed as the app's own templates in a `/mockups` gallery with invented data, before the features behind them are built. A UI design discovery phase comes first: two or three distinct designs of one sample page, adjusted until the owner is happy; only then are the other pages mocked up in that design | Owner (2026-11-25) |
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
2. `add-ui-components` (added 2026-11-25 by the owner: mockups first)
3. `add-accounts`
4. `add-customers-and-tire-inventory` (audit history folded in if small, else `add-audit-history`)
5. `add-pdf-prefill`
6. `add-dashboard`
7. `add-operations`

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

## Product questions (Phase 2)

**Answered by the owner on 2026-11-24; the answers are in Decisions.** All ten were accepted.
Q3 added a DOT date code per tire. Q7 added that a new PDF replaces the stored details outright
(no per-field choice). The recommendations
below are kept as the reasoning. Evidence from the five real invoices in `samples/private/`
(checked 2026-11-24): none contains tread depths; all contain `Bill To`, a vehicle `Description`,
VIN, license plate, `Invoice #`, `Work Order #`, and a storage section with the accessories line
and a free-text tire description.

**Q1. What is one stored item?**
Recommendation: a **tire set**, meaning the tires one customer stores together. It is usually 4
tires, but it can have 1 to 8 (a spare, or a set with a spare), and one size or two (staggered
front/rear). Each tire has a position (LF, RF, LR, RR, or Extra).
Changes: the `tire-inventory` data model. The form starts with four tire rows and has "add tire".

**Q2. When is tread depth recorded?**
Recommendation: on **each check-in**, per tire, in 32nds of an inch (whole numbers 0–20). Tires
wear between stays, so each stay keeps its own readings. The set shows the latest ones, and the
history shows how they changed. The PDFs never contain tread depth, so staff always type it.
Changes: tread depth belongs to the stay, not the set. The check-in step asks for readings;
leaving them blank is allowed.

**Q3. Tire set fields.**
Recommendation:
- Per set: size (front, and rear if staggered); brand and model; on wheels or tires only, with a
  wheel description; season (summer, winter, all-season); lug nuts, center caps and centering
  rings, each unknown/yes/no; TPMS sensors, unknown/yes/no; notes.
- Per stay: check-in date, RO number, storage location (Q9), tread depths (Q2), check-out date.

Left out unless asked for: DOT date codes, condition grades, photos, storage pricing.
Changes: the form, the search and what the PDF can fill.

**Q4. What does "remove" mean?**
Recommendation: nothing is ever deleted.
- **Archive a set**, for example after it is sold or disposed of. This is allowed only while the
  set is checked out. The set is hidden from search, listed under "Archived" on the customer, and
  can be restored.
- **Archive a customer.** This is allowed only when none of their sets are checked in. It hides
  the customer and their sets, and can be undone.
- A record created by mistake is archived too.

History always stays.
Changes: there is no delete button anywhere. Archive and restore appear in history.

**Q5. Who can do what?**
Recommendation: every staff account can do all inventory work: add and edit records, check in and
out, archive and restore, upload PDFs. Admins can also manage staff accounts and change shop
settings (the Q6 threshold).
Changes: there are only two roles, and only admin settings are restricted.

**Q6. Dashboard stats and "too long".**
Recommendation:
- Sets checked in now.
- Sets in too long.
- Checked in this week and checked out this week.
- Customers with at least one set in the shop.

"Too long" means the current stay is older than one shop-wide threshold. The default is **6
months**, which matches "6 month maximum" on the invoices, and admins can change it. Each stat
links to the matching search.
Changes: `dashboard` counting rules, plus one setting in admin settings.

**Q7. Uploading a PDF for a returning customer.**
Recommendation: after upload, the form suggests existing customers with similar names (already
decided). If the chosen customer has checked-out sets, staff can **check one of them in** from the
PDF instead of creating a new set. The RO number and date fill the new stay.
Fields the PDF fills:
- customer: name, phone, email
- vehicle: description, VIN, plate
- RO number and invoice number
- invoice date, as the check-in date
- size(s) and brand, read from the storage notes
- accessories

It never fills tread depth or storage location.
Changes: `pdf-prefill` leads to either "new set" or "check in an existing set".

**Q8. Customer fields and terms.**
Recommendation:
- Fields: first name, last name, one or more phone numbers, email and notes. Address is not
  stored, because Protractor has it.
- Customers never sign in. Specs say "customer" for the person storing tires and "staff account"
  for people who sign in.

Changes: the customer form and the duplicate suggestions (name and phone).

**Q9. Vehicles, and storage location.**
Recommendation:
- **Vehicle:** stored as text on the set (year make model, plus optional VIN and plate), not as
  separate vehicle records.
- **Storage location:** on, as optional free text on each stay (for example "Rack B3"). While the
  set is checked in, its current location is shown.

Changes: there is no vehicle table or page. Location appears on the check-in step and in search.

**Q10. Search fields.**
Recommendation: one box matching customer name, phone, tire size (by digits, so `225/55R17` and
`2255517` both match), brand, vehicle, VIN, plate, RO number and location. Filters are: in shop,
out, too long and archived. The default shows customers that are not archived.
Changes: the `tire-inventory` search and the database indexes.

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

Python package layout; CSS approach (plain or a minimal classless
stylesheet); migration tool (Alembic or numbered SQL); password hashing (argon2 recommended);
session storage; PDF viewer in the review screen (browser built-in or pdf.js); test tooling,
linting and CI.
