# Rollcall — information, screens, and shop operation

Specification draft, November 11, 2026. Covers planning checklist 13–17 and 19–22. Authority: [ROLLCALL_HANDOFF.md](../../ROLLCALL_HANDOFF.md). This document defines proposed behavior; it is not an implementation or runtime verification report.

Status labels: **Confirmed** records a direct decision in the handoff. **Proposed** is a technical/default recommendation for consolidated specification review. **Inherited** is older scope awaiting an explicit inclusion/deferment decision. Stable IDs below support later acceptance checks.

## Information model

**Confirmed:** customer names are the staff-facing customer identifier. Internal IDs remain implementation details. A customer can have many vehicles and many independently identified sets. A set belongs to one customer and optionally one of that customer's vehicles. No VIN or vehicle is required for customer-only storage. Customer profiles expose both vehicle groupings and all sets.

**Proposed — INFO-01:** use relational records with database-enforced foreign keys and version numbers rather than keeping the inventory inside mutable document JSON. These are logical entities; exact table names and migrations belong to implementation planning.

| Entity | Relationships and retained information |
|---|---|
| Customer | Stable ID, display name, normalized lookup name, optional contact, creation/update history. Renaming preserves ID and former spelling in history; no silent fuzzy merge. |
| Vehicle | Customer ID, optional VIN, year/make/model/free description. Known VIN conflicts require correction; a missing VIN does not prevent storage. |
| Set | Customer ID, optional vehicle ID, tire/wheel description, operational notes, accessories, multiple tire-size entries, active storage state, version. Reassignment changes association with history; it does not invent a swap. |
| Storage period | Set ID, source transaction/revision, effective start/due dates, preceding period where applicable, rule/provenance, superseded/corrected history. Period expiration does not close active storage. |
| Transaction | Canonical RO, customer, action, affected set IDs, state, current revision, apply timestamp. Manual Remove/corrections use an internal ID without requiring an RO. |
| Transaction revision | Prior revision, accepted printed date, corrected fields, interpretation, source PDF IDs, actor, recorded timestamp, effective date, reconciliation outcome. Preserve every revision. |
| Source document | Existing immutable PDF hash/archive, original extraction/raw text, original filename, pages, submission timestamp, corrections/provenance; link to a transaction/revision. Preserve existing invoice-number evidence without a new invoice-number product field. |
| History event | Customer/set/transaction links, action, previous/new values, actor, effective date and recorded timestamp. Includes swap, renewal, removal, association changes, date/RO corrections. |
| Section / set-section | Manually maintained labels and optional set associations. Proposed many-to-many allows a split set without splitting its identity. |
| Settings | Proposed shop-wide location visibility, timezone, and maintained section labels. Persist changes with attribution. |
| Staff identity | Proposed named accounts and permissions before shop pilot; exact sign-in choice needs specification approval. No anonymous real operational writes. |

**Proposed — INFO-02:** current inventory is derived from applied transactions and explicit corrections, with a current-state projection for fast reads. Enforce atomic changes to both swap sides and linked periods. Pending selection/attention cannot produce partial inventory. Linking and correcting an RO is an explicit versioned operation, not editing an immutable extraction. Do not rebuild or replay historical transactions merely to render a screen.

**Proposed — INFO-03:** keep both effective dates (the business date printed/corrected for the event) and recorded timestamps (when Rollcall received/applied/revised it). Display both in detailed history. Late uploads therefore explain why a past effective date was recorded today. Future-dated valid PDFs apply immediately under the confirmed submission rule; show that source date plainly rather than implying physical completion or delaying application.

## Fields, size handling, accessories, and sections

**Confirmed — FIELD-01:** set details support tire brand, model, size, wheel description, lug nuts, center caps, centering rings, and operational notes. Missing descriptive fields display as unknown/unprovided and do not become artificial required data. Keep notes visible in set details and customer history. Preserve original text alongside structured values.

**Proposed — FIELD-02:** a set has zero or more typed size entries. Keep the compact normalized value as a string and the original supplied representation. Store type explicitly (`metric`, `flotation`, or `unparsed`) and optional position (`front`, `rear`, `unspecified`). Staggered tires remain one set; either size finds it once. Ambiguous size text remains searchable as text and editable, without guessing type or changing set count.

| Type | Compact | Display | Equivalent size query |
|---|---|---|---|
| Metric | `2255517` | `225/55R17` | `2255517`, `225/55R17`, `225/55 R17` |
| Flotation | `35125020` | `35x12.50R20` | `35125020`, `35x12.50R20`, `35 x 12.50 R20` |

**Proposed — FIELD-03:** match a recognized full normalized size exactly in the dedicated size filter. A free search can match partial text; do not silently interpret a short digit string as a complete size. Preserve leading zeros and fractional precision. Do not normalize wheel dimensions into tire-size matches.

**Confirmed — FIELD-04:** accessories retain `unknown`, `yes`, or `no`. A blank Y/N template remains unknown. Associate accessories with the set, not a vehicle generally. Proposed correction UI gives explicit three-way choices and preserves prior values/provenance.

**Confirmed — FIELD-05:** Section is manually assigned from set details, never extracted from a PDF. Settings can hide all location fields/columns while retaining data. **Proposed defaults for review:** locations initially hidden; multiple sections per set; a shop-wide toggle so workstations present a consistent feature. When reenabled, show that labels are last recorded assignments, not proof of current physical placement. Removing/switching a set does not transfer its section to another set automatically. Retain past section assignments in history; require an explicit assignment for an incoming set.

## Shared screen behavior

**Set vehicle picker refinement:** assigned vehicle is read-only text plus a subtle Reassign link below; unassigned sets have Assign Vehicle. Open a dialog containing this customer's vehicle choices and an unassigned choice. Confirm in the dialog, or Cancel without effects; no permanent dropdown or generic Save changes button. In the standalone sample, assignment updates the set's session state, grouped vehicle lists and unassigned counter; refresh resets it. Keep notes attached to the set when its vehicle changes.

**Reference fidelity before further workflow refinement:** the user explicitly requests reference-matched styling, not merely working sample controls. The standalone sample uses `preview.css` for a shared reference-style shell, dark ~302px sidebar at 1584px, ~94px header, light workspace, rounded cards, orange active navigation and locally bundled Nunito typography. Nunito is a selected visual match; the original raster reference does not establish its source font family. Supporting customer/profile screens share these tokens while retaining the user's tab, description-link, counter and app-wide Settings requirements. Dashboard exists as a visual comparison sample. Header bell/account graphics are visual placeholders, not implemented notifications/account features. The approved logo is displayed through a clipped reference image; a dedicated production logo asset remains to be prepared.

**Customer header refinement:** use the customer's display name as the page heading instead of “Customer profile,” and remove the repeated name inside the content card. Replace the inline summary sentence with compact icon-and-count indicators at the top right: stored sets, vehicles, and stored sets without vehicle information. Use tire/storage, car, and unknown-vehicle icons with accessible names and short captions; wrap on narrow screens. These are customer-specific counts; Settings remains app-wide.

**Latest profile navigation refinement:** Stored sets and Vehicles occupy the upper customer-profile tab row beneath the page heading, outside the customer card. Remove the supporting-demo tab bar (Customer profile / Set details / Submission selection / Updated RO). Open set details by clicking the tire description in either stored-set or expanded vehicle lists; do not use separate Open set buttons or a Set details tab. Return to the customer profile preserves its selected tab. Revised-RO handling belongs to relevant source/history/attention workflows, not a permanent customer-profile tab; multiple-set selection belongs to submission.

**November 11 user refinement — customer profile and settings:** profile opens on a **Stored sets** tab with every currently stored set under the customer. Separate **Vehicles** tab uses expandable groups per vehicle to reveal sets. Customer-only sets remain in the combined list; the preview also groups them under **No vehicle information** in Vehicles. Settings is a Rollcall-level utility in app navigation, with the location switch applying to every customer. Internal IDs such as the sample RC-number codes must not appear in visible labels, feedback, or accessible control names. Use tire descriptions, sizes, vehicle association and RO/history to distinguish sets. These refinements supersede earlier profile grouping/layout text where inconsistent.

**Confirmed — SCREEN-01:** primary navigation is Dashboard, Inventory, Insights, Needs attention. Match approved light content, dark sidebar, orange active navigation, rounded cards, and HeroUI controls. Settings is a secondary utility entry, not a fifth primary tab. Upload is available within relevant workflows and as a shared action; documents remain accessible without a Documents tab.

**Proposed — SCREEN-02:** use real routes/deep links for customers, sets, RO transactions, and attention items. Browser Back restores relevant search/filter context. A stale or removed entity gets an explanatory state and a history link where applicable, never a blank screen. On narrow screens navigation collapses; PDF and editor stack with an explicit switch while retaining edits. Keyboard focus follows opened views and save outcomes; statuses include text rather than color alone.

**Proposed — SCREEN-03:** every data view distinguishes initial loading, successful zero results, filtered zero results, stale data, permission failure, and backend failure. Keep form edits after network/conflict errors. A failed query never becomes a zero count. Retry is visible. Upload responses show one of applied, selection required, Needs attention, unrelated/no inventory change, duplicate, or failed. Show linked affected sets and RO after application; no universal confirmation gate.

### Dashboard and metric meanings

**Proposed — METRIC-01, consequential review item:** inventory counts are sets, while Needs attention counts unresolved RO transactions. Label the units and keep queue count outside an exclusive inventory-status donut. An unresolved unrelated document without a usable RO remains one submission issue with an internal ID; it joins the RO issue if later linked, rather than inflating the queue count per uploaded PDF.

| Metric/status | Proposed exact meaning, using America/Chicago shop date `D` |
|---|---|
| In storage | All active stored sets, regardless of due date. Includes customer-only sets and expired sets. |
| Current | Active set with due date later than `D + 30 days`. |
| Due soon | Active set with due date from `D` through `D + 30 days`, inclusive. |
| Overdue | Active set with due date before `D`. Days overdue = calendar-date difference. |
| Date unavailable | Active set whose date remains unknown in a legitimate migrated/corrected record. Explicit separate bucket; never classify as current. |
| Needs attention | Unresolved transaction/submission issues, counted once by queue item as above; independent of set status. Selection-only uploads do not enter this count. |

**Proposed — METRIC-02:** Current + Due soon + Overdue + Date unavailable equals In storage. If the donut omits Date unavailable because its count is zero, retain an explicit legend/definition and add it when needed. Total In storage is a superset, not a slice alongside its subsets. Cards link to matching filtered Inventory or attention queue; chart and table share query boundaries. Proposed Due soon threshold is 30 calendar days, still subject to user review.

**Proposed — SCREEN-04:** Dashboard provides the approved overview, upload action, links into active inventory, and recent activity. Recent activity is ordered by recorded timestamp with effective date visible where different; it is not a duplicate transaction count. Preview numbers are sample data only.

### Inventory, customer profile, and set details

**Confirmed — SCREEN-05:** Inventory supports tire-size-first filtering plus customer, vehicle/VIN, tire brand/model, and RO search. Rows open set details; customer names open profiles. Profiles show all vehicles, sets grouped under each vehicle, unassigned sets, and a combined all-sets view. View history independently of whether a set is active.

**Proposed — SCREEN-06:** active storage is the initial inventory scope, with an explicit All history scope. Controls preserve combined search, status, size, and scope across navigation. Rows expose customer, vehicle or “No vehicle assigned,” tire sizes/description, due date/status, and optional Section. Stable sorting and pagination avoid silently dropping results. Set history is expandable below current details rather than mixing removed sets into an active-only list.

**Confirmed — SCREEN-07:** set detail includes descriptions, dates, accessories, operational notes, linked RO/PDFs, vehicle assignment, history, and **Remove**. Profile supports assigning an unassigned set to an existing customer vehicle and manual cross-vehicle reassignment. **Proposed:** an Edit action preserves field-level history and requires a correction reason for identity/date changes; Section opens a picker only when locations are visible. No extra fictitious required fields from mockups.

### Selection and Needs attention

**Confirmed — SCREEN-08:** an incoming third active set for a known vehicle triggers a submission-time selector to identify which set is coming out. Show customer, vehicle associations, size/description, and dates for candidate sets. Make known different-vehicle sets visibly ineligible for automatic swapping. Do not auto-select the first row. **Proposed:** unfinished selection is recoverable under a visible pending-submissions entry in the upload workflow; leaving the page does not imply application, removal, or loss of the PDF. Final mixed assigned/unassigned eligibility is specified in workflows.md.

**Confirmed — SCREEN-09:** Needs attention opens the original submitted PDF beside editable extracted/translated details. Show the specific ambiguity, proposed interpretation, affected sets, source date, RO, and current corrections. Staff can correct relevant fields/lines, interpretation, and associations, then resolve/apply the transaction. Preserve originals. A missing VIN alone does not cause attention. **Proposed:** resolve button describes the resulting action; version conflicts retain local edits and offer current data/recomparison. Unreadable PDF viewer failure offers access to the original and retry without discarding fields. Older sources remain accessible when an RO has revised PDFs.

### Insights and Settings

**Confirmed visual scope / proposed definitions — SCREEN-10:** preserve the approved Insights content: average stored sets, average overdue sets/percentage, check-ins, pickups, renewal periods, due in the next 30 days, overdue now, inventory trend, and overdue aging. Use applied inventory events and an explicit date range; no payment balance, revenue, or inferred period count from charge multiples. Pending, unrelated, duplicate, and superseded revisions do not add event counts. The definitions below clarify the approved visuals rather than replacing them with unrelated analytics.

**Proposed — METRIC-03, consequential review item:** Insights defaults to effective business dates, while audit/recent activity uses recorded timestamps. Correcting effective dates recalculates affected historical buckets and displays a “revised history” notice with source links. Historical charts use daily end-of-day snapshots in America/Chicago. Each date includes all applicable actions effective on or before that date, with only the accepted revision of each action. Keep an explicit effective event sequence for same-day actions, consistent with predecessor/dependency order; use the server-assigned apply sequence as the deterministic tie-breaker for independent actions. Do not infer ordering from PDF filenames, random IDs, or browser timestamps. A later correction that would reverse dependency order requires reconciliation, not automatic historical replay. Future-effective events affect current operational inventory immediately under the confirmed submission rule but enter an effective-date historical snapshot only on their effective date; disclose this distinction whenever current and historical totals differ.

Let the selected historical range be the inclusive calendar dates `S..E`, `N` their count, `A(d)` the active set count at the end of date `d`, and `O(d)` the subset of those active sets whose accepted due date is before `d`. Include zero-inventory dates in `N`. Limit historical averages/trend to completed dates, ending yesterday when a range includes today, and show that cutoff. A range containing no completed date has unavailable historical averages. Current cards use live applied state as of the displayed “updated” time, not a fabricated end-of-day estimate.

| Approved Insights item | Proposed formula / behavior |
|---|---|
| Average stored sets | `sum(A(d)) / N`; retain fractional values, rounding for display only. |
| Average overdue sets | `sum(O(d)) / N`. A set due on `d` is not overdue until the next calendar date. |
| Average overdue percentage | `100 * sum(O(d)) / sum(A(d))`, a ratio of overdue set-days to active set-days; not an unweighted mean of daily percentages. Label this definition in help text. If denominator is zero, display unavailable, not 0%. |
| Check-ins | Count applied incoming set sides effective in `S..E`: initial storage contributes one; a swap contributes one; renewal and vehicle reassignment contribute zero. |
| Pickups | Count applied outgoing set sides effective in `S..E`: manual Remove or clear pickup-only contributes one; a swap contributes one; renewal/reassignment contributes zero. Use the approved Insights label Pickups while the operational action remains exactly Remove. |
| Renewal periods | Count new renewal periods established by applied renewal actions effective in `S..E`. One six-month renewal adds one, including early extension. Revising that same RO/date/period adds zero. Do not derive extra periods from invoice price. |
| Due in next 30 days | Live active sets with accepted due dates `D..D+30`, inclusive; same boundary as Due soon. Label as “as of today,” independent of historical chart range. |
| Overdue now | Live active sets with accepted due dates before `D`, independent of historical chart range. |
| Inventory trend | End-of-day `A(d)` across the covered selected dates. If overdue series is shown, it is `O(d)` and remains a subset, not an additional inventory total. |
| Overdue aging | Live overdue sets partitioned by calendar days overdue: `1–30`, `31–60`, `61+`. The preview's `60+` label overlaps the preceding bucket; use `61+` to make buckets disjoint. The three buckets sum to Overdue now. |

Coverage begins only at a documented opening inventory/effective-history boundary. If coverage before that boundary is unknown, affected historical averages, trend intervals, and activity totals are unavailable/incomplete with the boundary stated; never fill unknown dates with zero or claim that a first PDF establishes all prior inventory. Average overdue sets/percentage is unavailable when any contributing active set has an unknown historical due date. Current count and aging can still show known results, but label missing-date exclusions and show the separate Date unavailable count. Restore/migration must retain the coverage boundary. Display genuine zero only when the relevant interval/state was successfully queried and is completely known. Proposed date presets and chart arrangements may be refined without changing these meanings.

**Confirmed — SCREEN-11:** Settings exposes location visibility. **Proposed:** secondary settings page also explains shop timezone and section labels. Account/admin management is shown only if approved for the pilot. Do not introduce customer-facing settings, remote-sharing controls, schedule integration, or automated placement.

**Confirmed Settings scope:** Launch with one editable shop-wide control, **Show storage locations**. Turning it off hides section fields and columns across Rollcall and retains existing assignments. Turning it on shows the saved sections again. Staff assign or change a set's section from its details. The proposed initial state is off.

## Shop operation

**Confirmed — OPS-01:** one shop Windows computer hosts application, PostgreSQL, and PDF archive; multiple LAN browsers use the same database. No external hosting, port forwarding, or remote access. Protractor supplies scheduling. Pulling a set ahead of an appointment does not create a storage transaction.

**Proposed — OPS-02:** production serves built frontend and API through one stable LAN origin. Keep database and archive inaccessible as direct network shares to browser clients. Reserve host IP/DNS with shop IT and restrict inbound application access to the shop network. Development remains loopback/manual startup; do not repurpose the current shared PostgreSQL service or alter its settings during planning. Host selection, LAN addressing, service account, backup destination, retention and recovery objectives are deployment prerequisites, not blockers to writing this specification.

**Proposed — OPS-03:** before pilot, configure project-owned automatic startup/recovery for production services and controlled maintenance/update procedures, with logs excluding PDF contents and credentials. Keep development and shop data separate. An application upgrade takes a restorable coordinated backup, applies explicit migrations, checks readiness and representative reads/writes, and retains a compatible rollback/recovery path. Never assume an older binary can safely use an upgraded schema.

**Proposed — OPS-04:** place PostgreSQL data, immutable PDFs, settings, and operational logs in documented persistent directories outside transient build folders. Store secrets outside source/checkpoints. Monitor disk space and archive/database readiness; archive or DB failure blocks inventory writes with a recoverable error. Orphaned immutable files from a failed transaction may be reconciled; missing referenced files are integrity failures to repair, not silent document deletion.

### Concurrent activity and workstation freshness

**Proposed — OPS-05:** enforce RO identity/idempotency and set-version checks at the database boundary. Concurrent uploads of the same RO serialize; any conflicting identity or action goes to reconciliation before applying conflicting changes. Swaps, removal, renewal, and revisions use short transactions and verify all affected versions. Conflicts return the latest version metadata with a visible reload/recompare action. No “last save wins.” Repeated clicks, browser retries, lost responses, and simultaneous workstations cannot repeat an applied action.

**Proposed — OPS-06:** refresh affected lists immediately after local mutations, on browser focus, and with a lightweight server change-version poll every 15 seconds while visible. This is a technical starting default, not a guarantee of instantaneous synchronization. Show last successful update and a stale/offline state. Do not replace fields while someone is editing; show a change notice and recheck versions on submit. Background refresh failures preserve the last data with a stale label. No offline mutation queue in the initial release.

**Inherited — OPS-07, consequential review item:** individual staff accounts existed in the old roadmap but were not reconfirmed. Recommend named staff sign-in before shop pilot, with all automatic submissions/actions attributed to the submitting person and background processing attributed to that submission. A shared workstation session must visibly identify the active person and support switching/locking. Admin operations cover account/settings/restore; routine advisors can submit and correct inventory. Development can use an explicitly labeled development identity with synthetic data. LAN restriction alone does not establish who made a change. Exact credential and account recovery design belongs in the approved implementation plan.

### Coordinated backup and recovery

**Proposed — OPS-08:** back up PostgreSQL and every referenced original PDF as one versioned recovery set, including required configuration, migration/app version, and a manifest of source hashes. A database dump alone is insufficient. Recommend nightly backups plus a pre-upgrade backup to a separate shop-controlled destination; retention and acceptable loss/downtime need shop agreement before pilot. Avoid silently introducing a cloud destination.

**Proposed — OPS-09:** use a bounded application maintenance/write pause to produce a consistent database dump and PDF manifest/copy, or a documented equivalent snapshot protocol. Retained immutable PDFs may be copied conservatively beyond those referenced by the snapshot; the restore manifest must prove every referenced PDF exists and hashes correctly. Release the pause only after a recoverable snapshot is secured; report backup failure. Document encryption/access and restoration of secrets separately from source-only checkpoints.

**Proposed — OPS-10:** before pilot, restore to an isolated project-owned instance and archive directory. Verify schema/version, customer/set counts, period dates, source links, PDF hashes, history/revisions, pending attention/selection states, settings, staff access, and post-restore write/idempotency behavior. Restart and recheck. Record measured recovery duration and recovery point. Never run a restore drill over the live database/shared machine-wide service. Backups are not considered proven merely because files were copied.

## Planned acceptance evidence

These checks are requirements for future implementation; none were run in this planning task.

| Check | Observable result |
|---|---|
| SA-01 relationships | Customer has two vehicles, vehicle-specific sets and an unassigned set; profile/all-sets views agree. Reassignment retains identity and history. |
| SA-02 typed sizes | Compact/formatted metric and flotation queries return the same set; staggered sizes return it once; wheel-only dimensions do not produce tire-size matches. |
| SA-03 accessories/locations | Unknown survives blank input; explicit yes/no persists. Hiding locations retains data and removes columns/fields across workstations. Incoming sets never inherit locations automatically. |
| SA-04 count boundaries | Fixtures on `D-1`, `D`, `D+30`, `D+31`, missing date, and removed state prove status partition; attention count is independent and deduplicated by issue. |
| SA-05 scope/navigation | Active/all-history search, RO, filters, browser Back, direct links, empty/error states, keyboard focus, and narrow layout behave as specified. |
| SA-06 attention | Original PDF visible alongside correction; no partial inventory before resolve; failed/conflicting resolution retains edits and originals. |
| SA-07 metrics | Swap contributes one check-in and one pickup, while one renewal contributes one renewal period; duplicate/revised PDFs add none. Same-day dependent actions produce deterministic end-of-day state. Date corrections move historical buckets with disclosure. Verify average set/overdue formulas and zero denominator; unknown coverage/due dates produce unavailable historical metrics. Aging boundaries 30/31/60/61 partition Overdue now; current cards remain clearly separate from historical range. |
| SA-08 multi-client | Two clients changing one set or RO cannot lose edits or repeat actions; stale data is labeled and refreshes under the chosen polling contract. |
| SA-09 restart | Project-owned app/database restart retains business data, originals, settings, pending work, history, and staff attribution. |
| SA-10 recovery | Isolated database/PDF restore verifies referenced hashes and meaningful operations; recorded evidence includes duration and recovery point. |

## Scope and review decisions

- Confirm the recommended independent Needs attention count and disjoint set-status chart, including a Date unavailable bucket when necessary.
- Confirm 30-day Due soon boundaries and effective-date Insights with historical recalculation. Omit unsupported averages rather than inventing history.
- Confirm locations initially off, multiple section associations, and a shop-wide visibility setting.
- Confirm named staff access before pilot. Exact host/backup destination can remain deployment prerequisites.
- **Inherited scope:** historical bulk import, custom rates/custom storage, and older charge tracking were not reconfirmed. Recommend defer import and custom billing workflows until supplied data/examples justify them; retain extensible fields without exposed unused controls. Explicitly exclude payment collection as confirmed. Any retained storage-price metadata uses exact decimal values; it does not become revenue or outstanding-balance tracking.

## Source inspection evidence and limits

Read-only inspection on November 11 corroborated the handoff: `backend/app/main.py` exposes placeholder dashboard counts; `frontend/src/App.jsx` has dashboard/document local-state navigation and disabled search; `backend/app/document_store.py` defines only the document business table and separate immutable extraction/correction fields; `DocumentReview.jsx` saves review only and already uses HeroUI; `frontend/package.json` pins HeroUI 3.2.7 and binds development to loopback; `compose.yaml` binds PostgreSQL loopback and disables automatic restart; `document_parser.py` still supplies today's fallback date and historical-season renewal heuristics. The proposed inventory, metrics, routing, production startup, staff access, and coordinated restore features are new work. No services, secrets, archived customer data, database records, product code, or deployment configuration were changed. No runtime tests were run.

### Corrections preview — November 12

Approved correction-detail direction: source PDF on left, adaptive correction controls on right, and an Edit details button opening a sliding manual editor for all extracted details and supported actions. Preserve original evidence; stage edits until applied, allow Cancel, and resolve only after required information is present. User explicitly notes sidebar drift: retain original sidebar authority and defer sidebar adjustment. Working standalone sample is available from Corrections → Review; no live processing is connected.

### Fixed-layout review and PDF paging — November 12

Confirmed refinement: correction review always places the PDF at left and the review/editor at right. Reduce the overall app canvas proportionately to a 70% floor as the window shrinks; below the floor clip the view rather than stack columns or keep shrinking. Reference preview canvas: 1584 × 1000. Scale uses available window width and height, capped at 100%. This replaces the earlier Corrections narrow-screen stacking plan.

Multipage originals use Previous/Next arrows with a page indicator, showing one page at a time. Next slides right-to-left; Previous reverses it; respect reduced motion. No vertical page list. The preview uses the supplied two-page invoice 215798 (RO 246408), rendered locally; interpretation and stored-set choices remain a labeled demonstration.

### Adaptive compact-window workspace — supersedes 70% clipping

November 12 user clarification: both panes should fit a small window and expand with larger/fullscreen windows. Replace the fixed 1584px canvas, global scaling floor and deliberate clipping with flexible viewport-sized panes. PDF remains left and review/manual editor right. Compact navigation becomes an accessible icon rail; preserve the original sidebar visual direction in wide windows. Use tighter spacing and readable text sizes, adapt fields to one column within the right pane, and scroll review/editor independently. Fit the original PDF page to its pane; provide Fit and ± zoom with internal scroll/pan to read fine print without enlarging the review controls. Preserve Previous/Next horizontal page transitions and reduced-motion support. The latest requirement takes precedence over earlier 70% minimum/clipping wording.

PDF interaction refinement: mouse wheel over the PDF zooms at the pointer (fit to 5× fit). Shift+wheel or horizontal wheel/scrollbars pan; Fit resets. Wheel over the review/editor scrolls that pane normally. Keep keyboard-accessible Fit/± controls.

Inventory resize refinement (November 12): descriptions stay on one line and clip with a short fluid fade before the reserved type-icon/due-date area. Keep due dates visible without wrapping the row. Do not modify stored/display strings character by character; use available-width layout clipping and retain full accessible text and details navigation. Apply consistently to Vehicles, All Stored Sets and Unassigned.

### Sidebar and profile tab strip — latest November 12 refinement

Keep the original full-width (248px), text-labeled sidebar on the left at every width; do not convert it to a top bar or icon-only rail. When height is insufficient, the sidebar scrolls independently and fades vertically at the hidden edges. Minimum supported app canvas is 576×384 CSS pixels (6×4 CSS inches); a web page cannot lock the OS window to a physical size. Below that minimum, allow access by scrolling.

Profile tabs remain a single readable horizontal strip, fading near the clipped left/right boundary. Wheel over the overflowing strip scrolls only that strip, including containing wheel at the ends. Wheel outside it keeps normal page behavior; when all tabs fit, the strip does not capture wheel. Keep the real HeroUI tabs, selected indicator, focus/keyboard interaction and complete labels. This replaces prior icon-rail direction; original full labels are the latest user instruction.

### Stable tab geometry and latest interaction refinements — November 12

Treat the selected tab's two smooth concave lower corners and connected white content surround as persistent visual requirements. tabs-layout.css owns these invariants: fixed 16px corner geometry, 14px bridge, protected 26px outer padding and adjacent 8px tab gaps. All Stored Sets belongs next to Vehicles/Unassigned; no automatic spacer. Preserve this styling through future scroll/responsive changes; dedicated browser regression verifies every selected tab at compact and wide sizes. Wheel motion over the overflowing strip is interpolated smoothly; respect reduced motion and keep it local to the strip.

PDF panning uses click-and-drag in both axes, replacing the Shift+scroll instruction; retain wheel zoom and Fit. Inventory type indicators use fixed tire-left/wheel-right columns, leaving the absent type's position empty. Source PDF/set data stays unchanged by these presentation refinements.

Latest selected-tab corner geometry (November 12): both lower white corners must be true reverse curves of the upper circular surround, with matching 28px radii and tangent connections to the vertical sides and horizontal view-panel edge. Position arcs relative to the white surround's 7px inset, not the pill edge. Scroll padding derives from radius + inset + clearance so corners are not clipped. This supersedes the former 16px radius at explicit user request; preserve the tangent relationship in future changes. Browser geometry checks now enforce radius equality and tangent offsets, alongside visual close-up review.

Corner rendering invariant refinement (November 12): use one shared quarter-circle shape and a horizontal mirror for the opposite side, rather than independently drawn corner approximations. Retain equal radii and tangent offsets; seal fractional-pixel gaps at both tips. Current implementation uses one inline SVG path with scaleX(-1) and a 1 CSS px white base seal. Verify at common fractional display scales as well as compact/wide windows.

### Approved underline design — November 13 (current authority)

User approved promoting option 3 into the main mockup. Use the shared underline-tabs.css on both main and comparison entries: 22px wide / 20px compact labels, existing icons/counts, original off-grey shelf, darker grey 2px guideline centered under the orange 4px selector, and identical surrounding palette. Preserve smooth local wheel scrolling, edge fades and keyboard selection. This explicit approval supersedes the earlier requirement for connected white lower corners in the MAIN mockup; the connected version remains archived separately for reference. No change to business workflows or production scope.

### Inventory mobile priorities — November 13 (latest confirmed direction)

Support actual phones and small desktop windows for Inventory first. Always show vehicle association (or explicit no-vehicle status) and tire/wheel type icons. Tire description can fade at a fluid boundary; compact list due dates may hide, with dates retained in set details. Sidebar may collapse to icons at a narrow-width breakpoint; a small button must open its full labeled view. Preserve existing palette, underline-tab behavior and fixed tire/wheel slots.

The initial mockup collapses below/equal to 1000 CSS px, using a 64px rail and HeroUI full-navigation modal. This breakpoint is an implementation default for review. The older 576px minimum canvas and always-full-width sidebar are superseded only for Inventory/profile and its detail views; other screens are outside this mobile pass. Touch swipe for overflowing tabs, keyboard/desktop wheel behavior and vehicle reassignment must remain usable.

Approved November 15: the Corrections mobile concept is accepted and now available in the main interaction preview. Desktop keeps PDF-left/review-right. Phone layout uses Review/PDF switching with retained draft edits, PDF page and zoom; compact navigation uses the full labeled menu pattern. Initial implementation breakpoints: 700px for pane switching and 1000px for compact navigation. These accepted mobile rules supersede the prior minimum-width/two-pane-only constraints for Corrections. Inventory stays the initial view.
