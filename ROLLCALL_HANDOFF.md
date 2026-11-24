> Latest continuation saved November 18, 2026: read [next-chat handoff](docs/rollcall/CHAT_CONTINUATION.md) first. Inventory, Corrections, and Dashboard mobile layouts are accepted and integrated in the main mockup. Historical status below is retained.

> Accepted visual direction, November 11, 2026: the user selected the graphic-design study as the continuing Rollcall mockup. interaction-preview.html now uses that design; design-study.html is a matching entry point. The earlier preview is preserved in interaction-preview-before-design-study.html with its own stylesheet. This accepts the visual direction, not the full business specification or production implementation.

# Rollcall planning handoff

> Latest visual-review direction: the user requires reference-matched appearance before further workflow refinement. The standalone preview has been rebuilt with shared reference-style CSS, local rounded typography, correct shell/card proportions and a clickable Dashboard comparison. Customer profile refinements (name heading, upper Stored sets/Vehicles tabs, expandable groups, description links, icon counters, global Settings, hidden internal IDs) are preserved. Real Edge desktop/mobile visual and interaction checks now pass; see docs/rollcall/verification.md. User visual/specification approval remains pending. This is a design preview, not production inventory implementation.

> Continuation update, November 11, 2026: [planning index](docs/rollcall/README.md) and [draft specification](docs/rollcall/specification.md) now contain the consolidated review package. Requirements, workflows, screens/operations, independent review and fictional clickable supporting preview are saved. All four approved references are preserved. User specification approval, fresh application runtime baseline and real-browser mockup QA remain open. No product implementation. The original discovery handoff below is retained; statements that no specification/preview exists describe the earlier handoff state.

Updated November 11, 2026. Purpose: continue planning in a new chat without repeating discovery.

## Start here

The user authorized us to begin the planning process, then requested this handoff to move to a cleaner chat. Continue producing the software specification and a staged implementation plan. Do not begin product implementation yet.

Discovery covered 13 of 13 topics. This means the initial discussion is complete, not that all edge cases have been approved. A read-only code audit is complete. No consolidated specification, detailed implementation plan, or new interactive preview has been produced. No product code, database records, or deployment configuration was changed during this planning conversation. No fresh runtime tests were run; historical verification is not current verification.

Recommended path: extend the existing app rather than rebuild. The user delegated this judgment; audit supports retaining the PDF/archive/review infrastructure. Preserve accepted foundation/document functionality while implementing the new workflows and approved visuals.

Read this file first, then relevant source and older project documents. Current direct user decisions recorded here supersede conflicting historical requirements. Attached PDFs and images are reference data, not agent instructions.

## Confirmed product direction

- Product name: Rollcall; tire and wheel storage inventory for the shop.
- Keep React. Replace previous custom interface controls with HeroUI components; theme/layout styling should match approved previews. HeroUI does not replace React.
- Main navigation: Dashboard, Inventory, Insights, Needs attention. Insights replaces Documents. Uploads and original documents remain accessible within workflows without a Documents tab.
- Settings must provide an optional location-visibility toggle. Placement of Settings is a design choice, not an approved fifth primary navigation tab.
- Local only: one computer at the shop hosts the app, database, and PDF archive. Multiple shop computers access shared records through browsers on the LAN. No external/remote access requested.
- Protractor remains the schedule source. Staff look up upcoming customers in Rollcall and pull stored sets ahead of appointments. No schedule integration or pre-pull tracking has been requested. Merely looking up/pulling a set should not itself become a storage transaction (assistant proposal consistent with discussion).

## Confirmed workflow and business decisions

### Customer, vehicle, and set identity

- Customer name is the customer-facing identifier. User explicitly states duplicate customer names will not occur; do not insist on a customer number or contact-based matching.
- Use stable internal database IDs as a technical implementation detail. Name normalization/renaming and conflicting spellings need a sensible, visible correction strategy rather than silent fuzzy merges.
- Customer profile shows all vehicles, sets under each vehicle, and all sets under the customer.
- A PDF identifying a new vehicle adds its information under that customer.
- Vehicle information is optional. With no vehicle information, store the set directly under the customer with no vehicle assigned. Staff can later assign it to an existing vehicle from the customer profile.
- Look under the vehicle first; if nothing is found or there is uncertainty, look across that customer's stored sets.
- A known different vehicle means a different set. Do not automatically swap out a set belonging to another vehicle. A new vehicle without its own stored set gets a new listing.
- Rare cross-vehicle reuse is a manual correction: open a customer's set and reassign it to another vehicle (e.g. replacement Subaru). It is not an automatic inferred transfer.

### PDF submission and swaps

- An uploaded authorization or invoice is itself permission for the action. Clear submissions automatically update inventory, regardless of actual physical completion. No separate universal approval/Confirm Swap step.
- Advisors manually describe sets in the RO. Usually only the incoming set going into storage is described.
- Rollcall consults existing inventory to determine whether a set is coming out. With no eligible stored set, create/file a new incoming listing. With one eligible set, swap. With multiple eligible sets, immediately show the customer's current stored sets and ask which is coming out.
- Multiple-set selection is part of submission, NOT a Needs attention issue by itself. Show vehicle associations so staff do not accidentally select a known different vehicle's set. Final treatment of mixed assigned/unassigned candidates belongs in the specification as an explicit recommendation.
- RO/work-order number is the transaction identifier. User does not want a separate invoice-number field or invoice-number tracking requirement. Preserve original PDFs and existing immutable evidence; this does not authorize deleting legacy evidence.
- Updated authorization/final invoice with the same RO updates that same transaction and supporting details. Never repeat the swap or create duplicate periods merely because another PDF arrives.
- The latest submitted PDF for that RO supplies the printed source date. Do not substitute upload date, appointment date, export/footer timestamp, or today's date. Missing/ambiguous printed date requires resolution before a date-dependent action (recommended consequence, not separately user-confirmed).

### Dates and renewals

- Standard period: six calendar months, with correct month-end behavior.
- New storage/swap start date: date printed on the latest submitted PDF for the RO. Later PDF revises the same transaction/date, not another swap.
- Early renewal: extend the existing due date by six calendar months; keep document date separately.
- Overdue renewal: begin six calendar months from the printed renewal PDF date.
- Same-day renewal boundary can be handled as a stated technical default; no additional user question is needed unless it changes an outcome.
- Renewal signals are advisor notes such as "renewal" or "storage extension". Terminology is still evolving at the shop.
- Unclear renewal versus swap goes to Needs attention. Do not infer period count/boundaries from price multiples or historical seasons alone.
- Expiration does not itself renew a period or remove inventory. No payment collection requested; Protractor handles payments.

### Removal

- Provide an action labeled exactly **Remove**, not "Mark as picked up".
- No PDF or RO required to manually remove a set from active storage.
- Preserve set/customer history rather than hard-delete the record.
- A clear "pickup only" PDF can record removal as well. Do not focus the workflow on obtaining pickup paperwork.
- Removal date default/backdating, confirmation or undo, and correction after downstream changes were not answered. Propose reversible behavior and label defaults for review.

### Needs attention

- Use for genuinely ambiguous/missing/conflicting details, explicitly including unclear renewal-versus-swap wording.
- Always bring up the submitted original PDF so an advisor can read it alongside translated/extracted fields.
- Staff must be able to edit any relevant extracted line/field, correct interpretation, and resolve/apply the transaction.
- Preserve original PDF and original extraction separately from corrections/history.
- Missing VIN alone is not an error requiring Needs attention; customer-only sets are legitimate.
- Valid transactions do not pass through mandatory review. Unresolved transactions should not partially change inventory (recommended transaction integrity rule).

### Set details and tire-size search

- Agreed detail scope: tire brand/model/size, wheel description, lug nuts, center caps, centering rings, and operational notes (e.g. "needs tires replaced"). Do not require details absent from the PDF just to match a visual example.
- Accessories should preserve unknown/yes/no, not treat blank templates as false (existing source behavior and sensible retained default).
- Search/filter by customer, vehicle/VIN, tire brand/model/size, and RO. Tire size is expected to be the primary filter.
- Store/search compact size strings; format for display:

| Type | Compact value | Display |
|---|---|---|
| Metric | `2255517` | `225/55R17` |
| Truck/flotation | `35125020` | `35x12.50R20` |

- Keep size values as strings and distinguish size type; normalize compact/formatted queries to the same result.
- Existing sample analysis includes staggered sizes. Support multiple sizes in one set rather than splitting it into two sets (audit recommendation).
- Customer history should expose past swaps, renewals, removals, corrections, and linked PDFs.

### Optional sections/locations

- Location is NEVER supplied by the PDF. Staff assign it manually and individually in a set's detail screen: click Section and choose a section.
- Simple rack/section labels such as A, B, C, D. No automated placement or advance assignment.
- Optional Settings toggle hides location fields and columns while retaining entered data. Do not claim hidden locations continue to track physical moves automatically.
- Starting with location display off and allowing multiple sections per set (because sets can be split across racks) were assistant recommendations consistent with the user's explanation, not separately approved details. Mark them as defaults for specification review.

## Approved visual references

Four attached PNGs were explicitly approved UI previews. Preserve the approved light content area, dark sidebar, orange active navigation, rounded cards, and overall visual direction while using HeroUI controls. The existing dark dashboard is an older direction.

| Screen | Original attachment path |
|---|---|
| Needs attention | `C:/Users/ndcav/AppData/Local/Temp/codex-clipboard-d1563d60-e834-491e-b1e3-4451cad6560b.png` |
| Insights | `C:/Users/ndcav/AppData/Local/Temp/codex-clipboard-7c8b6690-1b6a-40f9-b3b0-ada3e6e6c7bb.png` |
| Inventory | `C:/Users/ndcav/AppData/Local/Temp/codex-clipboard-d64e6f29-b106-43a4-87a6-af8b45235e9d.png` |
| Dashboard | `C:/Users/ndcav/AppData/Local/Temp/codex-clipboard-e6c63e46-a869-4bfa-8a82-0398f3e6006d.png` |

These are temporary paths; preserve copies under project docs if available before relying on their longevity. Fictional preview counts are not acceptance targets or real data. Preview text requiring universal review and the Documents tab are superseded by this conversation.

PDF specifically supplied in this conversation:
`C:/Users/ndcav/Downloads/Storage Examples/Tire-and-Wheel-Swap-With-Storage-And-Notes-Invoice-215798-Invoice.pdf`

Its first page was rendered and visually inspected. Header contains customer/contact, vehicle/VIN, separate invoice and work-order numbers, printed date labels. The example demonstrates invoice and RO numbers differ; RO is the product identifier. Other historical sample findings are in `docs/verification/2026-11-10-protractor-sample-review.md`; do not repeat its outdated approval/date rules.

## Code audit: actual baseline

An independent agent performed a read-only source audit, corroborating the main agent's inspection. No new runtime tests, services, secret reads, or archived customer-data inspection were performed.

| Area | Reuse / change | Evidence |
|---|---|---|
| Stack | Retain React/Vite/Tailwind, FastAPI, PostgreSQL, pypdf. | `frontend/package.json`, `backend/app/` |
| HeroUI | React/styles pinned at 3.2.7; already integrated. Retain import/source audit for covered controls. | `frontend/package.json`, `frontend/scripts/audit-ui-library.mjs` |
| Upload | Bounded PDF upload, all-page extraction, malformed/encrypted rejection; scanned/no-text retained for manual handling without OCR. | `backend/app/documents.py`, `document_parser.py` |
| Archive | SHA-256 originals, atomic file replacement, exact-file deduplication, database locking. | `backend/app/document_store.py` |
| Corrections | Immutable extraction, correction history, row locking, version conflicts. Reuse patterns. | `document_store.py`, `DocumentReview.jsx` |
| Inventory | Not implemented. Only document business table exists; dashboard counts are placeholders and search disabled. | `document_store.py`, `backend/app/main.py`, `frontend/src/App.jsx` |
| Navigation | Only dashboard/review local-state switching. Approved sidebar/screens/profiles/deep links require work. | `frontend/src/App.jsx` |
| PDF comparison | Currently opens another tab; side-by-side Needs attention is new work. | `frontend/src/DocumentReview.jsx` |
| Action processing | Current save changes review only. Automatic clear-action application, selection, and blocking states are new. | `documents.py`, `DocumentReview.jsx` |
| Dates | Parser currently falls back to today's shop date; incompatible with new automatic printed-date rule. | `document_parser.py` |
| Identifiers | Current parser/form exposes invoice plus RO. New product uses RO only. Existing related-document warning consults immutable extracted RO, not corrected identity; explicit linking design required. | `document_parser.py`, `document_store.py`, `DocumentReview.jsx` |
| Action inference | Historical-season renewal heuristics and rotation-heading swap detection need replacement with agreed rules. | `document_parser.py` |
| Deployment | Development frontend binds loopback. Production LAN serving, startup, coordinated backups/restore remain to be designed. | `frontend/package.json`, `README.md` |

Historical Stages 1 and 2 are documented as user-accepted. Those historical stage numbers differ from the six planning stages below. Backend virtual environment described in README was absent at the expected path during inspection; do not assume documented test commands currently work. Existing machine-wide PostgreSQL service is not project-owned; do not stop/reconfigure it casually.

## Important specification decisions to resolve or propose

1. Updated older RO after subsequent swaps/removals: preserve downstream history and avoid overwriting current set state. Define revisions/reconciliation rather than replaying a swap.
2. Mixed vehicle-assigned and customer-only candidates: make eligibility and selection explicit; never silently use another known vehicle's set.
3. Name normalization and manual correction, RO correction/relinking, and corrected dates after dependent transactions.
4. Analytics/count units: preview donut treats Needs attention like an exclusive set status, but the queue is RO-based. Recommend separate queue count and disjoint current/due-soon/overdue set totals; disclose this visual adjustment for review.
5. Due Soon threshold (30 days is a historical proposal), inclusive boundaries, effective-date history, daily averages, renewal counts, and retroactive recalculation.
6. Original concepts mention staff logins, historical import, custom storage/rates, and charge tracking. They were not reconfirmed here. Identify inherited scope explicitly and recommend inclusion/deferment; do not silently add or delete requirements.
7. Resolve staff access/attribution before shop pilot; exact host machine and backup destination can remain deployment prerequisites without blocking specification drafting.
8. PDFs with no storage activity must not create inventory merely because a customer has no stored sets. Distinguish incoming storage evidence, renewal, clear retrieval, and unrelated work.

These do not require reopening discovery one question at a time. Settle technical details independently and bundle consequential business decisions with clear recommendations.

## User collaboration preferences and authority

- User wants an individually numbered plan grouped into expandable/dropdown stages so each can be fine-tuned.
- Show honest progress against the saved checklist. Earlier "13/13 topics" counted discovery topics, not fixed questions or completed implementation.
- User dislikes excessive serial questioning. No blocking question was identified before the audit; surface newly discovered consequential issues together.
- Proceed independently on reversible planning work, source inspection, technical defaults, and reviews. Existing decisions are authorization; do not ask again.
- User authorized focused agents and independent review. Main agent remains accountable. Model selection for delegated agents is explicitly authorized; select appropriate available models when useful. Main chat model is controlled by the user.
- One consolidated specification review before implementation. Routine technical steps do not need individual approval. Material scope/workflow changes do need user review.
- Each meaningful implementation stage must have a working preview and a concise "what works / what is sample data / what to try" checklist.
- Screen planning should include clickable supporting-screen previews where useful. Do not pass a mockup off as a running connected app.
- No new chat has been created. User requested this Markdown handoff, not automatic chat creation.

## Planning checklist (31 steps, six stages)

Status key: `[ ]` not complete; partial progress described explicitly. Do not mark a stage complete just because discussion covered its topic.

<details open>
<summary><strong>Planning Stage 1 — Consolidate what we know</strong></summary>

- [ ] 1. Create the requirements register. This handoff captures decisions; structured register still needed.
- [ ] 2. Organize and preserve approved previews, HeroUI requirements, navigation.
- [ ] 3. Establish verified software baseline. Read-only source audit complete above; any claimed runtime behavior still needs current evidence.
- [ ] 4. Reconcile outdated documentation. Conflicts identified, governing documents not yet updated.
- [ ] 5. Record preserve/replace/add decisions and perform internal baseline review.

Result: reliable product and existing-software baseline.

</details>

<details>
<summary><strong>Planning Stage 2 — Define business workflows</strong></summary>

- [ ] 6. Specify customer/vehicle matching and manual reassignment.
- [ ] 7. Specify new storage, swaps, and set selection.
- [ ] 8. Specify updated PDFs, RO matching, dates, and idempotency.
- [ ] 9. Specify renewal detection and dates.
- [ ] 10. Specify Remove, history, and correction behavior.
- [ ] 11. Specify Needs attention and resolution.
- [ ] 12. Walk sample PDFs/scenarios through the rules; internally check consistency.

Result: explicit rules for inventory changes, with recommendations marked.

</details>

<details>
<summary><strong>Planning Stage 3 — Define information and screens</strong></summary>

- [ ] 13. Define records and relationships.
- [ ] 14. Define fields, tire sizes, accessories, notes, and sections.
- [ ] 15. Specify approved screens and metric/status meanings.
- [ ] 16. Specify supporting profiles, details, selection, and Settings.
- [ ] 17. Specify search/filter behavior and history.
- [ ] 18. Review interactions/empty/error states; produce useful clickable previews for user review.

Result: functional screen specification and supporting interaction previews.

</details>

<details>
<summary><strong>Planning Stage 4 — Define shop operation</strong></summary>

- [ ] 19. Define local host and LAN browser access.
- [ ] 20. Define concurrent uploads/edits and cross-workstation refresh behavior.
- [ ] 21. Define staff access, startup, maintenance, and data locations.
- [ ] 22. Define coordinated database/PDF backup and tested recovery.

Result: operational specification; host/backup destination can be later prerequisites.

</details>

<details>
<summary><strong>Planning Stage 5 — Assemble and review specification</strong></summary>

- [ ] 23. Consolidate into a design/specification document.
- [ ] 24. Independently review gaps, contradictions, workflow examples, and scope.
- [ ] 25. Present consequential unresolved decisions together with recommendations.
- [ ] 26. Revise and obtain one explicit specification review/approval before product implementation.

Result: approved definition of the software. Do not ask for approval until a concrete reviewable document exists.

</details>

<details>
<summary><strong>Planning Stage 6 — Produce implementation plan</strong></summary>

- [ ] 27. Define dependency-ordered delivery stages with usable outcomes.
- [ ] 28. Break stages into individual tasks, file ownership, and interfaces.
- [ ] 29. Define acceptance checks and meaningful tests per task/stage.
- [ ] 30. Include working previews, user review checkpoints, continuity documentation, and recovery checkpoints.
- [ ] 31. Review/fine-tune the implementation plan; surface material changes only.

Result: detailed build plan. Use the writing-plans skill after specification approval, following applicable skill instructions.

</details>

## Next chat: concrete next actions

1. Read this handoff and applicable skills; inspect the approved images while available and preserve reference copies.
2. Create a central expandable planning index and requirements/decision register. Use stable IDs to trace requirements to later tasks/checks.
3. Finish Planning Stages 1–4 as documentation/design work using code-audit evidence, clearly labeled recommendations, and scenario walkthroughs. Update governing docs with a prominent current-planning pointer while preserving historical evidence.
4. Prepare supporting interaction previews as needed; the approved four screens are not an invitation for an unrelated redesign.
5. Write the consolidated specification, ask an independent agent for consequential planning gaps, fix internally answerable issues, and bundle remaining business decisions for the user's review.
6. After specification approval, produce the detailed staged implementation plan with user-interactable previews at meaningful delivery gates. Only then begin authorized implementation.

Suggested continuation prompt:

> Read ROLLCALL_HANDOFF.md in this workspace and continue the authorized planning work. Preserve our confirmed decisions, use agents where useful, and keep the staged checklist updated. Prepare the specification and review package before implementation; bundle consequential questions rather than restarting discovery.
