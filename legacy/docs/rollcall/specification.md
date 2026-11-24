# Rollcall software specification

Draft for consolidated review — November 11, 2026. **Not approved for product implementation.** This is the central specification; the linked documents define its detailed rules and checks.

## Purpose and outcome

Rollcall lets shop staff find customer tire/wheel sets, submit Protractor PDFs, and maintain shared storage inventory. Clear submissions apply automatically; genuine uncertainty presents the source PDF and relevant choices. Staff can locate sets before appointments without recording a storage transaction. Protractor remains responsible for scheduling and payments.

## Authority and approach

Confirmed decisions are recorded in [requirements](requirements.md), traced to `../../ROLLCALL_HANDOFF.md`. Proposed defaults D01–D15 are visibly separate and remain subject to the consolidated review. Earlier accepted stages establish reusable foundation/document behavior, not approval of contradictory legacy workflows.

Extend the existing React/HeroUI, FastAPI and PostgreSQL app. Preserve originals, extracted evidence, correction history and bounded uploads. Add a separate RO transaction and inventory-event layer rather than treating saved document reviews as completed actions. A rebuild discards useful archival behavior; a parallel new app creates duplicate sources of inventory truth. The handoff delegates this architectural choice and recommends extension.

## Scope

Include customer profiles, optional vehicles, distinct sets, periods/events/history, PDF intake and same-RO revisions, automatic clear actions, immediate replacement selection when an incoming set would be the third for a vehicle, Needs attention resolution, Remove, manual reassignment, tire-size search, optional sections, real dashboard/Insights metrics, and LAN operation with recoverable records and sources.

No OCR, scheduling integration, pre-pull tracking, external hosting/access, automatic renewal, payment collection, or physical-movement inference. Staff access is a pilot prerequisite; exact host/backup destination can be supplied later. Inherited import/custom-rate/charge requirements are listed for review rather than silently included or erased.

## Core invariants

1. PDF evidence alone must establish storage activity; unrelated work never creates incoming inventory.
2. RO has one canonical transaction identity with many retained source revisions. Exact re-upload cannot replay an action.
3. Automatic application requires clear action, required identity/date evidence and safe set selection. Missing VIN alone is legitimate.
4. Inventory, period, RO state and audit changes commit atomically. Unresolved transactions do not partially update inventory.
5. Set identity survives swaps, retrievals, reassignment and corrections. Reuse a reliably identified returning set; never merge by similar description alone. A new listing without reliable historical identity is explicit and can be corrected/linked with history (D15).
6. Another known vehicle's set is never automatically swapped out. Mixed/uncertain candidates require visible choice.
7. Source dates and recorded timestamps are separate. Use America/Chicago for operational today; preserve actual instants for audit ordering.
8. A historical source revision cannot overwrite a later set state. Reconciliation exposes downstream effects before applying a correction.
9. Expiration changes date status, never physical storage state. Financial charge multiples cannot allocate periods.
10. All originals and original extractions remain accessible alongside corrections and event history. No hard deletion of history.

## Detailed specification

Latest user refinements: customer profile defaults to all **Stored sets**, with a separate **Vehicles** tab containing expandable vehicle/set groups; unassigned sets remain visible. **Settings** is an app-wide Rollcall utility, and location visibility affects every customer. Internal set IDs are never shown in screens or feedback. See the updated requirements/screens documents and interaction preview.

- [Requirements and proposed defaults](requirements.md): authority, scope and test traceability.
- [Baseline and preservation](baseline.md): inspected sources, reusable functionality and verification limits.
- [Business workflows](workflows.md): matching, automatic actions, revisions, renewal/removal and scenario acceptance matrix.
- [Screens, information and shop operation](screens-and-operations.md): relationships, fields, search/count semantics, LAN/concurrency and recovery.
- [Supporting interaction preview](interaction-preview.html): fictional local exploration only; no saved inventory or connected PDF processing.

The approved four screenshots in `references/` govern visual direction. Supporting previews must label sample data and proposed interactions. Production must use actual HeroUI components; mockup controls do not establish implementation compliance.

## Processing contract

A submission returns one clear result: applied, unchanged duplicate, awaiting set selection, needs attention, unrelated/no inventory action, or failed with retry guidance. Applied result names customer, incoming/outgoing set, effective date and RO with links to details/history. Selection and attention retain a pending submission identifier/version so a second workstation cannot apply a stale choice.

Separate source storage from action application: a valid original may be safely archived even when processing is pending or fails. Expose the processing state and retry rather than silently claiming inventory success. Required metadata conflicts block the action, not preservation of its evidence. No application-startup schema creation or silent reinterpretation of historical reviews as business events.

## Acceptance gates

Each delivery stage provides a working local preview and a concise list of what works, what remains sample data, and what to try. Checks must demonstrate actual behavior, not package presence or mockup appearance. Backend coverage includes real isolated PostgreSQL transactions, concurrent duplicate submissions, stale edits, rollback and restart. Frontend coverage includes automatic result/selection/attention flows, navigation, keyboard use, mobile fit, failures and HeroUI source audit. Production pilot additionally requires LAN multi-client checks, staff attribution and coordinated database/PDF restore.

No runtime tests were run in this planning batch. Historical results are not current verification. Detailed implementation tasks follow specification approval, in keeping with the handoff.

## Consolidated review decisions

Review D01–D15 in the requirements register as a bundle. The choices most likely to affect daily work are:

| Topic | Recommended behavior |
|---|---|
| Old RO revised after later work | Revise evidence/history; require reconciliation if changed dates/action/identity affect dependent events. Never repeat the swap. |
| Mixed vehicle/unassigned sets | One vehicle match with no unassigned candidates swaps automatically. Mixed or unassigned-only candidates for a known vehicle require grouped selection; never auto-use another known vehicle. |
| Remove/corrections | Show set and effective date, default today; allow reasoned backdating with chronology checks, and audited undo only when no later dependency exists. |
| Status and Insights | Due soon includes today through 30 days; overdue starts next day. Separate unresolved RO count from stored-set statuses. |
| Optional sections | Initially hidden; support multiple manual sections and preserve hidden values. |
| Inherited scope | Include staff attribution before pilot. Defer bulk history import, custom-rate operations and financial analytics unless requested. |
| Work-order and returning-set scope | Accept clear dated work orders like authorizations; make none-coming-out selection available; use reliable evidence or an explicit correction to link returning historical sets. |

Pending specification review is required by the handoff's explicit instruction: “One consolidated specification review before implementation.” No per-step implementation permission is proposed.
