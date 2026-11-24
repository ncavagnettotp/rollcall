# Tire Pros — Storage Manager Master Plan

> Current planning authority (November 11, 2026): [Rollcall handoff](ROLLCALL_HANDOFF.md) and [Rollcall planning index](docs/rollcall/README.md). The handoff's confirmed decisions supersede conflicting rules below, including universal confirmation, date fallback, VIN requirements and the older dark visual direction. Rollcall specification is a draft pending consolidated review; this historical roadmap and evidence remain preserved.

Consolidated October 30, 2026. This is the primary project roadmap for future work.

## 1. Purpose and source documents

Build a simple, locally hosted tire and wheel storage manager driven by digital Protractor invoices, authorizations, and work orders. Employees upload a document, review the proposed storage action, and confirm it. Authorizations/work orders are allowed before payment so employees can prepare ahead of the work. The application tracks sets, storage periods, due dates, source documents, and permanent history with minimal manual entry.

This plan combines:

- [Tire_Storage_Manager_Project.md](Tire_Storage_Manager_Project.md): original concept, business rules, workflows, and seven-stage development sequence.
- [README.md](README.md): existing Step 1 scope, development-PC setup, manual startup instructions, and acceptance procedures.
- [VERIFICATION.md](VERIFICATION.md): historical evidence of what was tested and what remains unverified.
- The dashboard direction selected in this chat: a dark interface with spacious cards and subtle category colors.

The master plan governs the intended product and stage order. README remains the operational setup guide; VERIFICATION remains a dated evidence record. Preserve the original concept as reference. Future changes should update this roadmap and the affected operational or verification documents together.

The README's three setup “milestones” are steps within **Stage 1**, not replacements for the seven product stages below.

## 2. Current position

Update October 30: the selected dashboard is now implemented. Current evidence in VERIFICATION.md records 4 passing frontend tests/build/browser checks, 7 backend tests against native PG18.6, and successful isolated native-cluster persistence/recovery across restart. Stage 1 has been explicitly accepted by the user. The configured Windows service was not restarted; Compose remains untested. The initial baseline table below is retained as historical context.

| Area | Documented position |
|---|---|
| Foundation | React/Tailwind/Vite frontend, FastAPI backend, PostgreSQL 17 configuration, health endpoints, and placeholder dashboard exist. |
| Automated checks | October 21 report records backend: 6 passed, 1 skipped; frontend: 3 passed; frontend build and desktop/mobile browser smoke checks passed. These are historical results, not newly run checks. |
| Live database | Live PostgreSQL connectivity, persistence through recreation, and Docker runtime checks were not completed in that report. Recheck the actual environment before declaring them complete. |
| Step 1 acceptance | Remaining database and recovery checks, plus explicit user acceptance, are outstanding in the available documentation. |
| Visual design | Latest preferred concept is the dark dashboard with translucent green, amber, red, and slate-gray category cards. It has not been implemented in the working app. |
| Later features | PDF ingestion, business records, matching, storage actions, live search/counts, and production deployment remain planned. |

The earlier sidebar/pastel-column appearance described in VERIFICATION is historical. The latest dashboard concept supersedes it as the intended design. Sample records and counts in mockups are fictional and do not prove working functionality.

## 3. Development and deployment boundaries

- Frontend: React with Tailwind CSS and Vite. **HeroUI React and styles 3.2.7 are installed and pinned**, per user direction. Existing dashboard and document-review controls have been converted to real HeroUI components. Use HeroUI controls/layout primitives instead of creating a competing component system; retain domain layout, icons, and theme tokens.
- Backend: Python FastAPI.
- Database: PostgreSQL 17, persistent and shared by employees at deployment.
- PDF ingestion: embedded-text extraction from digitally generated Protractor PDFs; evaluate a library such as PyMuPDF against real samples. No OCR or scanned-invoice support.
- Development happens on this Windows development PC. Start services manually. Keep Compose `restart: "no"`; do not install Windows startup tasks or background services here as part of foundation work.
- Eventual hosting is on the existing shop Windows office PC, accessed in browsers on the shop LAN only. No cloud hosting, remote access, or port forwarding.
- Shop deployment will need background operation, automatic recovery, an IT-managed reserved local IP, restricted firewall access, and backups in a separate location. Choose and validate the exact service arrangement in Stage 7.
- Original PDFs and database records must both survive restarts and be included in backup/restore procedures.

## 4. Business rules

- Standard storage costs **$99.99 per six calendar months**.
- For a new storage period, use explicit **Invoice Date** or **Authorization Date** as its start. For an uninvoiced work order without either, use its explicit work-order date; if no usable document date exists, suggest the current shop-local date (America/Chicago) and identify it as a fallback for advisor review. Preserve date provenance and allow correction. November 11 renewal exception below supersedes the earlier rule applying document dates to every renewal.
- **Early renewal, confirmed November 11:** extend the matched existing period's due date by six calendar months. The extension takes effect at the existing due date, not the date of early payment/invoice. Preserve invoice date separately as transaction evidence. Example: renewal invoice April 9, existing due date April 30 → new due date October 30. No automatic renewal; advisor confirms the extension. If the existing due date is missing/ambiguous, request review rather than starting a new invoice-date timer. Same-day and overdue renewal anchoring remain to be clarified.
- Calculate the due date by adding six calendar months to the selected start date, handling month ends correctly; do not substitute a fixed day count. Do not infer extra duration from a charge or silently use a historical 'stored since', appointment, promised, print/export, or payment timestamp as the document date. Conflicting dates at the same precedence (for example, two different Invoice Dates) require review. A final Invoice Date overriding an earlier Authorization Date is normal precedence and needs no extra confirmation.
- Authorizations and work orders may be uploaded and reviewed before invoicing/payment. Upload alone does not confirm a storage action. **Final invoices supersede authorizations**: link to the same work order/event and replace provisional document details. For new storage, recalculate the timer from final Invoice Date; for early renewal, preserve the existing-due-date anchor. Preserve earlier documents, values, and employee changes in history; do not create another storage transaction or repeat a swap. Require selection if the existing event cannot be matched reliably.
- Product priority confirmed November 10: practical, good-enough tracking for customer and employee accountability. Use a short review of the proposed action, set, date, accessories, and important notes; focus questions on missing or conflicting information that affects the record. Do not require perfect free-text descriptions or repeated confirmation of already settled rules.
- Expired sets remain in storage and display days overdue. No automatic renewal or charging.
- Confirmed pickup example: Invoice 210874 is retrieval without renewal. A storage service package or charge alone does not establish a new period; pickup closes the matched active period and starts no new timer.
- Protractor handles payments. This application records storage periods and invoice storage charges, not unpaid balances.
- Customers can have multiple vehicles and sets. Each set has a stable identity and can have multiple historical periods.
- Track set states separately: in storage, on vehicle, retrieved, or unknown.
- Completed periods, important notes, original values, and edits remain in permanent history.
- Due Soon uses a **proposed 30-day threshold**, pending confirmation.
- Custom storage can use a custom six-month rate; a prior rate may be suggested on renewal but requires confirmation.

## 5. Agreed dashboard direction and remaining screen requirements

Priority after Stage 2 acceptance: function and structure first. The user confirmed the document workflow works and expects the overall appearance to be redesigned later. Treat the current dark design as provisional. Defer cosmetic refinement and broader information-display redesign while building business records and workflows; continue fixing usability problems that obscure feedback or prevent actions.

November 11 user-directed exception completed: restyled the existing dashboard and upload/review screens to HeroUI's native visual language. Native theme, typography, card sections, status chips, separators and secondary field variants replace the remaining legacy skin. Category meanings and existing workflows are preserved. This frontend-only refresh is verified; it does not expand Stage3 functionality.

Component-library decision: use HeroUI (https://heroui.com/en/docs/react/getting-started). User requested immediate conversion as a foundation task; existing controls are now migrated. Preserve upload/review behavior, clear save feedback, keyboard use, and mobile fit. Broad visual redesign remains deferred. Default to the open-source React components; premium templates or services are separate decisions. `npm run audit:ui` checks production JSX/imports, and `npm run build` runs that audit before Vite.

Required UI-library check after every major adjustment: inspect changed UI files and their dependencies to confirm standard controls use HeroUI components. Check buttons, inputs, text areas, selects, checkboxes, cards, dialogs, tables, tabs, alerts, and other library-covered widgets; flag new native/custom replacements rather than silently introducing them. Page layout, domain logic, and theme CSS can remain project-specific. Record the inspected files, HeroUI components used, remaining legacy controls, and any exceptions in the verification report. Do not claim compliance from a package install or passing tests alone. Existing pre-HeroUI controls are migration debt, not proof of compliance; any necessary new replacement requires a documented reason and user agreement before adoption. Run appropriate behavior/build/browser checks alongside this source review.

### Dashboard direction selected in this chat

- Dark charcoal background, readable white/muted-gray text, thin borders, rounded cards, and generous spacing.
- Header: **Tire Pros | Storage Manager**, a short dashboard subtitle, and a small **Upload Invoice** button.
- A persistent, prominent universal search field.
- Four clickable category cards in a **2 × 2 grid** at the reference desktop width:

| Category | Subtle translucent fill |
|---|---|
| In Storage | Green |
| Due Soon | Amber |
| Overdue | Red |
| Needs Attention | Slate gray |

- Keep card labels, counts, and icons legible; status must also be conveyed in text. Exact color/opacity values are implementation details to tune against the selected concept.
- Beneath the categories, show a simple Storage Records list. Each roomy record card includes customer, vehicle, tire size, tire description, due date, status, and an opening affordance.
- Use consistent gaps between records. Show an empty-state message once for an empty result list, not between records.
- Adapt the layout for narrow screens without horizontal overflow.
- Place full record details and invoice review on their own views, keeping the dashboard uncluttered.
- Future user-facing category label is **In Storage**; existing foundation copy uses **Stored** and must be reconciled when implementing the approved appearance.
- Use em dashes for unavailable/unimplemented counts. Real zeroes are valid only when backed by a successful query. Loading, failure, and recovery must be clear.

### Search and details

- Search active and historical records by customer, full/partial VIN, normalized tire size, tire brand/model, and custom description. Wheel size is excluded.
- Make active versus historical scope understandable; do not silently limit universal search to the visible cards.
- Details include customer/contact, full VIN, vehicle, set descriptions, storage/check-in and due dates, status, original PDF, accessories, notes, and history.
- Important notes carry forward while historical versions remain intact.
- Other Storage / No VIN is a discreet expandable option, never a fifth dashboard category. Support custom descriptions, a unique storage ID, notes, and a custom rate without requiring a VIN.
- No notifications, popups, automated alerts, or physical storage locator are required.

### Invoice and swap review

- Heading: **Tire Swap Detected**.
- Vehicle information on the left; customer name on the right.
- Side-by-side **Coming out of storage** and **Going into storage** sections where screen width permits.
- An accessories icon on the storage view opens controls for **centering rings**, **lug nuts**, and **center caps**, associated with the set entering storage. Show which items accompany the set; preserve unknown/yes/no rather than converting an untouched Y/N template into No.
- Prominent legible notes/customer requests, invoice-based storage start date, and **Confirm Swap** / **Edit** actions.
- Label information sourced from the invoice, confirmed history, or inference. Require selection when evidence is ambiguous.
- Edit reuses extracted information and offers Correct Swap, Create New Set, or No Swap / Retrieve Only instead of starting with a blank form.

The dashboard concept has a selected direction. Detail, edit, and swap-review layouts still need their own focused drafts before implementation.

## 6. Invoice processing and matching

1. Upload a digital Protractor invoice, authorization, or work-order PDF; prepayment authorizations are accepted.
2. Extract document type, invoice/RO number, explicit invoice/authorization/work-order date, customer/contact, full VIN, year/make/model, tire/wheel descriptions and sizes, and storage line/charge. Apply the date rule above, with visible provenance for a current-date fallback. Preserve historical dates separately as evidence.
3. Archive and link the original PDF; preserve extracted fields and their provenance.
4. Match the vehicle by full VIN and inspect known sets and confirmed history.
5. Propose Initial Storage, Swap, Retrieval, or Renewal. Flag unreadable text, missing dates, conflicts, and ambiguous matches for review.
6. Employee corrects or confirms the proposal. Only a confirmed action changes business storage state.
7. Save business changes, invoice/event links, and audit history transactionally; prevent duplicate transactions.

Seasonal swap invoices usually describe only the set entering storage. Use verified purchase invoices and confirmed history to help identify both sets. Never silently guess when history is insufficient, multiple sets match, or VIN evidence conflicts.

## 7. Data and integrity requirements

Conceptual entities: Customers, Vehicles, TireSets, StoragePeriods, StorageEvents, Invoices, Accessories, Notes, Users, and AuditLog.

- Stable identifiers for sets, invoices, events, and custom storage items.
- Invoice uniqueness rules and duplicate detection, including retry protection.
- Original invoice files, extracted fields, and provenance retained with links to confirmed events.
- Atomic swaps: both sets and their periods/history update together or neither does.
- Permanent history for Initial Storage, Swap, Retrieval, Renewal, and Edit.
- Edits preserve original values, employee identity, and timestamp.
- Optimistic concurrency protection prevents silent overwrites.
- Staff identity must be attributable before real operational edits are allowed. Stage 7 delivers individual logins; earlier stages use development data until accountability is ready.
- Database migrations and recoverable changes are required as the schema grows.

## 8. Staged delivery roadmap

Finish, test, document, checkpoint, and obtain acceptance for each stage before advancing. A stage is not complete solely because its interface looks finished. Record unresolved defects and do not carry known bugs forward as accepted work.

### Stage 1 — Foundation and acceptance

**Deliverable:** A working local Windows development foundation with truthful connectivity and placeholder dashboard data.

- [ ] Reassess the existing frontend, backend, database configuration, and documented test baseline.
- [ ] Apply the selected dark dashboard shell and four category colors while retaining placeholder counts; keep future controls clearly unavailable until functional.
- [ ] Verify configuration and PostgreSQL startup using the README's Docker route or documented native PostgreSQL alternative.
- [ ] Confirm real API liveness and PostgreSQL readiness, including bounded/sanitized database failure behavior.
- [ ] Verify frontend/backend/database stop-and-recovery behavior.
- [ ] Run the persistence probe: write, stop/recreate the container while preserving its volume, restart, and read successfully. For native PostgreSQL, verify persistence through its restart instead.
- [ ] Verify desktop/narrow-screen appearance, frontend tests/build, backend tests, and the live DB integration test.
- [ ] Update verification evidence, preserve manual startup, create a versioned checkpoint, and obtain Step 1 acceptance.

**Exit evidence:** Real PostgreSQL Connected state; successful recovery and persistence checks; passing applicable checks; accepted foundation appearance. Existing historical results alone do not close this gate.

### Stage 2 — PDF upload and extraction review

November 10 status: implemented, verified, and accepted by the user. Current evidence is in VERIFICATION.md. Stored reviews remain separate from later business storage records/actions.

**Deliverable:** Upload a digital invoice, archive it, and review extracted fields without creating confirmed storage transactions.

- [x] Obtain representative real Protractor invoices and identify their field formats.
- [x] Implement PDF upload, embedded-text extraction, original-file archival, and a simple field-review view.
- [x] Preserve original extracted values and employee corrections separately.
- [x] Identify unreadable/scanned files and incomplete fields explicitly; do not guess or add OCR.
- [x] Establish invoice identity and duplicate-upload handling, including repeat requests.
- [x] Test seasonal swap, purchase, renewal/exception, malformed, and no-text PDFs; confirm archive/review persistence through restart.

**Exit evidence:** Correct extraction on reviewed sample PDFs, accessible original files, clear review states for failures, no unintended storage-state changes.

### Stage 3 — Storage records and period rules

**Deliverable:** Persist customers, vehicles, separately identified sets, storage periods, and supporting history.

- [ ] Add schema migrations and relationships supporting invoices, notes, accessories, and later actions.
- [ ] Implement six-calendar-month due dates from the confirmed document-date/fallback rule above and the $99.99 standard rate.
- [ ] Support multiple vehicles/sets per customer and successive periods per set.
- [ ] Build the focused record-details view with original PDFs and history.
- [ ] Prepare custom/no-VIN records and custom rates in the model; deliver their operational actions in Stage 5.
- [ ] Test month ends, leap years, multiple sets, exact money values, historical periods, and restart persistence.

**Exit evidence:** Correct dates and rates, durable relationships and history, no automatic renewal or payment balance tracking.

### Stage 4 — VIN and set matching

**Deliverable:** Reviewable action proposals based on full VIN, invoice evidence, and confirmed history.

- [ ] Match vehicles using full VIN and maintain distinct set identities/states.
- [ ] Use verified purchase and storage history to propose incoming/outgoing sets.
- [ ] Label invoice-derived, historical, and inferred values.
- [ ] Require employee selection for missing evidence, multiple matches, conflicting VINs, or unknown sets.
- [ ] Test sparse seasonal invoices, purchase takeoffs, multiple sets, missing descriptions, and conflicting history.

**Exit evidence:** Useful proposals on real samples and explicit uncertainty without silent guesses or premature commits.

### Stage 5 — Confirmed actions and audit history

**Deliverable:** Safe employee-confirmed Initial Storage, Swap, Retrieval, Renewal, and Edit workflows.

- [ ] Draft and implement the focused swap-review/edit views described above.
- [ ] Implement Confirm Swap, Correct Swap, Create New Set, Retrieve Only, and confirmed Renewal.
- [ ] Implement discreet Other Storage / No VIN actions, custom descriptions/IDs, custom six-month rates, and confirmed prior-rate suggestions.
- [ ] Add the accessories icon and centering-rings/lug-nuts/center-caps controls, associate them with the incoming set, and carry forward important notes.
- [ ] Commit both sides of a swap atomically and retain original PDFs, period history, and field-level edit history.
- [ ] Add transaction duplicate protection and concurrency conflict handling before shared operational use.
- [ ] Test rollback on partial failure, repeated confirmations, duplicate invoices, concurrent changes, custom storage, notes/accessories, retrieval without replacement, and renewal without automatic charges.

**Exit evidence:** Every action has correct state transitions and attributable permanent history; failures cannot produce partial or duplicate transactions.

### Stage 6 — Live dashboard, filtering, and universal search

**Deliverable:** The selected dashboard powered by real records, counts, and working navigation.

- [ ] Connect category cards, record list, and Upload Invoice to working features.
- [ ] Implement due-soon/overdue calculations and days overdue without removing expired sets from storage.
- [ ] Define and document category membership: In Storage represents physically stored sets; date-based categories may be subsets. Confirm the Needs Attention counting unit and treatment of missing dates before implementation.
- [ ] Confirm the proposed 30-day threshold and due-date boundary behavior before finalizing date filters.
- [ ] Implement universal active/historical search with normalized tire sizes and excluded wheel-size matching.
- [ ] Implement category filters, Show All, and one meaningful empty state per result list.
- [ ] Verify counts against database fixtures, search combinations, history scope, failure/recovery states, keyboard use, and narrow screens.

**Exit evidence:** Counts/filter results agree with stored data, the design remains uncluttered, and no fictional demo data appears as live operational data.

### Stage 7 — Shop deployment and reliability

**Deliverable:** A shared, recoverable shop-LAN application with staff accountability and imported history.

- [ ] Confirm shop host Windows version/resources and IT network requirements.
- [ ] Implement individual staff logins; all staff may upload, edit, and search, with identity attached to audit events.
- [ ] Verify concurrency behavior with multiple employee browsers.
- [ ] Inspect existing records, map fields, run a trial import, reconcile totals/history, and preserve import provenance; review conflicts before final import.
- [ ] Configure shop-host background operation and recovery, LAN-only access, reserved IP, and restricted firewall rules.
- [ ] Back up the database and original PDFs to a separate location; document and prove a joint restore on a clean recovery target.
- [ ] Test host restart, service failure/recovery, LAN client access, original-PDF retrieval, and staff accountability.
- [ ] Deliver operating, backup/restore, and support instructions and obtain shop acceptance before using real transactions.

**Exit evidence:** Successful multi-user shop test, reconciled import, attributable edits, and demonstrated restart/recovery and complete backup restoration.

## 9. Decisions and materials still needed

| Item | Needed by |
|---|---|
| Real digital Protractor PDFs: swap, purchase/takeoffs, renewal/exception | Stage 2 extraction; Stage 4 matching |
| Storage timer date | November 10: explicit invoice/authorization date, otherwise work-order date, otherwise visible current shop-date fallback; flag conflicting explicit dates |
| Early renewal anchor | Resolved November 11: extend existing due date by six calendar months; early invoice/payment does not shorten the current period |
| Same-day / overdue renewal anchor | Clarify whether to extend the old due date or restart from invoice date before implementing these renewal cases |
| Later invoice after an authorization | Resolved: final invoice supersedes authorization; update the same event and timer, retain prior history, prevent duplicate actions |
| Exact due-soon threshold and due-date boundary rules | Before Stage 6 date filters are finalized |
| Needs Attention counting unit, membership, and missing-date handling | Before Stage 6 counts are finalized |
| Detail, swap, and edit screen drafts | Stages 3–5, before their UI implementation |
| Existing records format and import reconciliation expectations | Stage 7; inspect earlier if available |
| Shop host resources, IT LAN/firewall setup, background-service arrangement | Stage 7 |
| Separate backup destination and recovery procedure | Stage 7, before operational use |

## 10. Verification and change discipline

- Before each stage, turn its checklist into a focused implementation plan grounded in the current code and real sample inputs. This roadmap does not preselect every future API or schema detail.
- Run checks appropriate to each change. Business rules, parsing, transactions, duplicates, concurrency, search, and recovery require meaningful tests.
- Keep mock-based checks distinct from real database, real invoice, and shop-host checks.
- Document test dates, commands/results, environment limitations, and remaining acceptance tasks in VERIFICATION.
- Preserve recoverable versioned checkpoints; plan data migrations and backups before changes that affect persisted data.
- Keep secrets out of source control and reports. Preserve database volumes: the README warns that `docker compose down -v` deletes them.
- A visual mockup or acceptance of its appearance does not approve later functionality or mark a development stage complete.

**Next work:** Stage 2 accepted. Plan Stage 3 persistent business records, six-calendar-month periods, rates, and history. Prioritize working structure and data integrity; defer visual redesign and broader information-display changes.
