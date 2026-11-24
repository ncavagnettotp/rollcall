# v1 lessons

What the rewrite should know from v1 (`legacy/`) without re-reading its 40+ documents. Paths are
relative to `legacy/`. v1's parser was tested against eight real Protractor PDFs; those files are
**not in the repo** (git-ignored), so real samples must be supplied again into `samples/private/`.

## 1. Protractor PDF layout

Source: `backend/app/document_parser.py`, `backend/tests/test_documents.py`, `docs/stage-2-design.md`.

- **Text extraction:** pypdf `page.extract_text(extraction_mode='layout')`, pages joined. Layout
  mode keeps label and value on the same line, which the field patterns rely on.
- **Document type:** the first non-empty line is `Invoice`, `Authorization` or `Work Order`.
- **Header labels:**

  | Label in PDF | Meaning |
  |---|---|
  | `Bill To <name>` | Customer name, often `Last, First` |
  | `Description <year make model>` | Vehicle |
  | `VIN <17 chars>` | VIN (may be missing) |
  | `Invoice # <n>` | Invoice number (differs from RO) |
  | `Work Order # <n>` | RO / work order number, the shop's transaction ID |
  | phone numbers, emails | Customer contact, only in the header before the `Inspection`/`Service` heading |

- **Dates:** only labeled dates count: `Invoice Date`, `Authorization Date`, `Work Order Date`, in
  `m/d/yyyy`. Every page footer carries an **export timestamp** (`10/30/2026 9:01 PM Invoice #123456
  Page 1 of 2`) and some PDFs show an `Appointment` date. Neither is the document date.
- **Storage section:** heading variants `Seasonal Tire Storage`, `Tire & Wheel Storage`,
  `Wheel Storage`; then boilerplate `Store customers wheels/tires. 6 month maximum.`; then an
  accessories line: `Lugs Y / N Center caps Y / N Center rings Y / N Notes__<description>`.
  - Untouched template `Y / N` means **unknown**; a single `Y` or `N` means the advisor chose.
  - The description after `Notes__` is free text typed by the advisor, e.g.
    `285/45R22 Michelin on Asanti wheels`. Staggered sets list two sizes
    (`Pirelli 275/35R21 and 315/30R21`).
  - The section can **span a page break**; the footer line interrupts it.
  - It ends at the next service heading (`TPMS Sensor`, `Mount, Install`, `Alignment Inspection`,
    `Total Parts`…) or at legal text (`Customer acknowledges…`).
- **Charge line:** `Storage $99.99` (one period) or multiples such as `$199.98`.
- **Rejected/limited input:** encrypted PDFs are rejected; scanned PDFs with no text are kept but
  nothing can be read (no OCR).

**For the rewrite:** the PDF only pre-fills the form, so a missed field is a blank box, not a wrong
inventory change. Keep extraction to the header labels, the labeled date and the storage section.
v1 also matched sample-specific phrases (`discard summers`, `dispose continentals`,
`NEEDS TIRES REPLACED`): that overfits to eight files; do not copy it.

## 2. Tire sizes

Source: `ROLLCALL_HANDOFF.md` (tire-size table), `backend/app/inventory.py` (search).

| Type | Typed by staff | Compact | Display |
|---|---|---|---|
| Metric | `225/55R17`, `225 55 17` | `2255517` | `225/55R17` |
| Flotation | `35x12.50R20` | `35125020` | `35x12.50R20` |

Store sizes as text, keep the type, and compare searches on digits only so any typing finds the set.
A set can have two sizes (staggered front/rear).

## 3. Accessories

Source: `backend/app/documents.py` (validation), `backend/app/document_parser.py`.

Lug nuts, center caps and centering rings are each **unknown / yes / no**. Never turn an unknown
into "no"; the PDF template is often left untouched.

## 4. Patterns worth keeping

| Pattern | Where in v1 | What it does |
|---|---|---|
| Content-addressed PDF archive | `backend/app/document_store.py` `persist` | File named by SHA-256; written to a temp file, `fsync`, then `os.replace`; a PostgreSQL advisory lock on the hash stops two simultaneous uploads of the same file from racing; an exact repeat returns the existing record |
| Version-checked saves | `document_store.py` `save_review` | `SELECT … FOR UPDATE`, compare version, reject with 409 and a "changed in another session, reload" message |
| Original vs corrected values | `document_store.py` schema | Extracted values never change; corrections and superseded versions are stored separately |
| Bounded upload | `backend/app/documents.py` `upload` | Streams the body and stops at 10 MiB; 1–50 pages; caps extracted text size |
| Safe errors | `backend/app/main.py`, `inventory.py` | Database errors become short generic messages; no stack traces or SQL to the browser |
| Coordinated backup | `backend/backup_rollcall.py` | `pg_dump` from an exported snapshot, then copies only the PDFs that snapshot references; checksums in a manifest; builds in a staging folder and renames when complete; restores into a **new** database and verifies the PDF references |

## 5. What went wrong

- **Scope kept moving.** A 7-stage roadmap (`MASTER_PLAN.md`), then a 31-step planning checklist
  (`ROLLCALL_HANDOFF.md`), then a desktop/LAN plan (`docs/rollcall/desktop-lan-design-plan.md`).
  Core rules changed several times: universal confirmation → automatic apply → ask on a third set
  (`docs/rollcall/CHAT_CONTINUATION.md`).
- **Documents outgrew code.** About 3,000 lines of app code against 14 MB of docs; five documents
  each claimed authority and opened with "superseded by" banners. `README.md` said no inventory
  existed while `backend/app/inventory.py` did.
- **Polish before function.** Many mockup variants under `docs/rollcall/` and about 50 one-off
  browser scripts in `work/` checking tab geometry and animation, while PDFs never updated inventory.
- **Rules not enforced in code.** The parser still fell back to today's date
  (`document_parser.py`), which the agreed rules forbade.
- **Fragile setup.** Windows-only instructions; frontend tests broke under a newer Node (built-in
  `localStorage`) because the runtime version wasn't pinned. Schema created with
  `CREATE TABLE IF NOT EXISTS` (no versioned migrations); the history table's key
  `(customer, date, description)` silently merges identical same-day entries
  (`backend/app/inventory.py`).
- **No access control.** The inventory write endpoint had no sign-in check
  (`backend/app/inventory.py` `update_accessory`).

**For the rewrite:** one source of truth (OpenSpec); function before polish; every rule lands as a
test; pinned runtimes in Docker; versioned migrations; every write requires a signed-in staff account.
