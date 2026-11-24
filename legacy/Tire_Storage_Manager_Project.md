# Tire Pros — Tire & Wheel Storage Management System

Original concept reference. November 10 clarification supersedes its physical-check-in-date wording below: posted Invoice Date starts the storage timer. See MASTER_PLAN.md for current rules. Invoice 215777 is confirmed Retrieve Only even without a storage service package.

## Project objective
A locally hosted, easy-to-use storage management application driven by completed Protractor invoice PDFs. Employees upload a digital invoice, review an inferred storage action, and confirm it. The system tracks tire sets, storage periods, due dates, and history with minimal manual entry.

## Technology and hosting
- Frontend: React with Tailwind CSS.
- Backend: Python FastAPI.
- Database: PostgreSQL, persistent and shared across employees.
- PDF ingestion: embedded-text extraction from digitally generated Protractor PDFs (e.g., PyMuPDF). **No OCR or scanned invoice support.** Unreadable PDFs require review.
- Existing Windows office PC as host, accessed through browsers on the shop LAN only; no cloud, remote access, or port forwarding.
- Background service, automatic recovery, reserved local IP managed by IT, restricted firewall, and separate-location backups of both database and original PDFs.
- Individual staff logins for accountability; all employees may upload, edit, and search.

## Storage business rules
- Standard storage rate: **$99.99 per six calendar months**.
- Period begins on actual physical check-in date, not automatically on invoice date unless verified reliable.
- Due date is six calendar months after check-in (handle month-end dates correctly).
- Expired sets stay in storage and display as overdue with days overdue; no automatic renewal or charging.
- Protractor handles payments; app tracks storage periods and charges appearing on invoices, not unpaid balances.
- One customer may have multiple vehicles and sets; one set may have multiple historical storage periods.
- Completed periods and edits remain in permanent history.
- Due Soon threshold: **proposed default 30 days**, to confirm.
- Historical record import is required.

## VIN-based matching
- Match vehicles by full VIN, and maintain separately identified tire/wheel sets with known statuses (in storage, on vehicle, retrieved, unknown).
- Seasonal swap invoices **rarely describe installed tires** and include only one storage description: the set going into storage.
- New tire/wheel purchase invoices usually include complete descriptions and sizes. Use verified purchase invoices and set history to infer the outgoing and incoming sets.
- Automatically fill missing storage descriptions from confirmed history; show inferred information on review screen.
- Do not silently guess when multiple sets match, VIN is conflicting, or history is insufficient. Flag for employee selection.
- Detect duplicate invoices and prevent duplicate transactions.
- Confirm Swap updates both sets atomically and preserves invoice/event history.

## Storage event types
1. **Initial Storage:** A set first enters storage.
2. **Swap:** One set leaves storage and another enters.
3. **Retrieval:** A set leaves without replacement; simple Retrieve Only action.
4. **Renewal:** New six-month period for an already stored set, based on confirmed renewal; no automatic renewal.
5. **Edit:** Employee changes a record while retaining original values, employee identity, and timestamp in audit history.

## User interface
- Simple dashboard with four clickable categories: **In Storage**, **Due Soon**, **Overdue**, **Needs Attention**.
- Permanent universal search across active and historical records by customer, full/partial VIN, tire size (normalized punctuation), tire brand/model, and custom item description. **Wheel size is not a search field.**
- Record details show customer/contact information, vehicle/VIN, set descriptions, storage and due dates, status, original PDF, accessories, notes, and history.
- Swap review: heading “Tire Swap Detected”; vehicle information left and customer name right; side-by-side “Coming out of storage” and “Going into storage”; checkboxes for **lug nuts** and **center caps** associated with the set entering storage; prominent legible notes/customer requests; **Confirm Swap** and **Edit** actions.
- Edit reuses data extracted from the uploaded invoice and offers Correct Swap, Create New Set, or No Swap/Retrieve Only rather than a blank form.
- Important notes carry forward while historical versions remain intact.
- Rare **Other Storage / No VIN** is a discreet expandable option, not a separate dashboard category. Supports custom descriptions (e.g., ATV winter tracks), unique storage ID, notes, and **custom six-month rate**; prior custom rate may be suggested on renewal. VIN not mandatory for this option.
- No notifications, popups, automated alerts, physical storage locator, or remote access required.

## PDF upload and review
1. Upload finished Protractor PDF.
2. Extract embedded text: invoice/RO number, date, customer/contact, VIN, year/make/model, tire/wheel descriptions and sizes, storage line/charge, and actual check-in date when available.
3. Link and archive original PDF.
4. Match VIN and known sets; infer likely Initial Storage, Swap, Retrieval, or Renewal.
5. Autofill from verified history, but flag uncertainty, missing check-in dates, and conflicting evidence.
6. Advisor reviews and confirms or edits; commit records and event history transactionally.

## Data model (conceptual)
- Customers, Vehicles, TireSets, StoragePeriods, StorageEvents, Invoices, Accessories, Notes, Users, AuditLog.
- Use stable IDs for each set, invoice uniqueness constraints, transaction integrity, and optimistic concurrency protection.
- Store extracted invoice fields and provenance (invoice versus confirmed history versus inference).
- Preserve original invoices and historical data through restarts and backups.

## Iterative development plan — build, test, verify, then advance
1. **Foundation:** React + Tailwind, FastAPI, PostgreSQL, basic four-card dashboard; test frontend/backend/database connectivity on Windows.
2. **PDF upload:** Digital PDF text extraction and field review; test with real Protractor invoices. No OCR.
3. **Storage records:** Database entities, $99.99 rate, six-month calculations, persistence; test month-end dates and restart recovery.
4. **VIN matching:** Purchase and storage history inference; test missing descriptions, multiple sets, conflicts.
5. **Actions:** Confirm Swap, Edit, Create New Set, Retrieve Only, Renewal, custom storage; test atomic updates, duplicates, audit trail.
6. **Dashboard/search:** Live counts, filters, overdue and due-soon logic, normalized tire-size search, history.
7. **Deployment/reliability:** Staff accounts, historical import, Windows service, concurrent edits, backup and restore tests, LAN access.

**Rule:** Finish and test each milestone before proceeding. Keep versioned checkpoints; do not carry known bugs forward.

## Remaining dependencies
- Real digital Protractor sample PDFs: seasonal swap, aftermarket purchase with stock takeoffs stored, and renewal/exception if available.
- Verify whether invoice date equals actual check-in date.
- Confirm host Windows version/resources, LAN configuration with IT, and separate backup destination.
- Inspect format of existing records for migration.
- Confirm Due Soon threshold (30 days is only a proposed default).

## Preview status
The prior interactive dashboard and swap screen were **illustrative prototypes with fictional data**, not a running or connected production application. The working app must be built and tested in milestones.
