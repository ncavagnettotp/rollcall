# Rollcall workflow specification

Draft for consolidated specification review — November 11, 2026. Covers planning steps 6–12. This is proposed software behavior, not implemented or runtime-verified functionality.

Authority: `ROLLCALL_HANDOFF.md` records confirmed decisions and supersedes conflicting historical requirements. **Confirmed** below means recorded there. **Default** means a recommended technical or reversible behavior for specification review. **Decision** marks a consequential recommendation requiring that consolidated review. Acceptance IDs `WF-*` identify future checks, not passed tests.

## Submission and transaction states

**Confirmed:** A clear authorization/invoice submission authorizes its storage action without a universal approval screen. Physical completion is not an application prerequisite. RO identifies one transaction; later PDFs revise that transaction. Lookup or physical pre-pulling does not change inventory.

**Default:** Each submission archives immutable PDF bytes and extraction first, then classifies the current corrected evidence as incoming storage, renewal, retrieval, unrelated work, or unclear. A storage charge, boilerplate, tire purchase, or seasonal heading alone does not prove incoming storage. Evidence must identify the intended storage activity. Preserve extracted line references so staff can inspect why it was classified.

| State | Entry condition | Inventory effect | Next interaction |
|---|---|---|---|
| Processing | Archived valid input is being classified/matched | None yet | Show bounded progress and recoverable failure |
| Awaiting set selection | Incoming would be a third active set for the vehicle, or a stated replacement lacks a unique target | None | Show immediate selection within submission |
| Needs attention | Material action/identity/date conflict or missing evidence | None from unresolved revision | Open original PDF alongside editable fields |
| Applied | Clear action and all required inputs resolved | Atomic update | Show outcome, affected sets, dates, and RO |
| No storage activity | Unrelated/purchase-only source | None | Report this explicitly; retain original as evidence |
| Duplicate | Exact original already submitted | None beyond original result | Reopen existing transaction/current revision |

These states describe processing; they are not mutually exclusive physical set statuses. A pending revision of an already applied RO does not undo that RO's prior committed effect. It displays the existing applied result plus the pending revision separately. Retry after an uncertain response returns the recorded result rather than applying again.

**Decision — work orders:** Older accepted requirements allow work orders as operational inputs, while the newest automatic-action wording explicitly names authorizations/invoices. Recommend accepting clear dated work orders under the same rules; include this in the consolidated scope decision rather than silently dropping or expanding support.

## Customer and vehicle identity

**Confirmed:** Customer name is the visible identifier; stable IDs are internal. Do not require customer numbers/contact matching or invent duplicate-name workflows. Vehicle data is optional, with direct customer-owned sets supported.

**Default:** Normalize names using Unicode normalization, trimmed/collapsed whitespace, and case-insensitive comparison, while preserving entered display spelling. Do not remove punctuation, reorder words, or fuzzy-merge different names automatically. A genuinely new normalized name may create a customer. If a PDF VIN already belongs to a differently named customer, stop for correction rather than creating a second owner or silently transferring the vehicle. Staff can explicitly select an existing customer or confirm the new name; rename preserves the internal ID, previous spelling, author, timestamp, and affected transaction link.

An exact full VIN identifies an existing vehicle under that customer. A previously unseen full VIN creates a vehicle under that customer. When the PDF explicitly identifies a new vehicle without VIN, retain its supplied vehicle details under the customer with VIN blank; VIN is optional, not a prerequisite to creating a vehicle. Do not assume a partial make/model description uniquely identifies a vehicle or automatically merge it into a similar existing vehicle. Where evidence cannot distinguish an association, keep the set customer-only with the supplied description preserved and offer explicit association/correction. Missing VIN alone is not an attention reason. A genuinely conflicting known association requires resolution.

Manual reassignment opens a customer's set and selects one of that customer's vehicles, or no vehicle. It records a dated correction without removing or adding storage inventory. Cross-customer ownership transfer is outside this automatic workflow and must never be inferred. Changing association does not rewrite original PDFs or historical vehicle associations.

## Incoming storage and eligible outgoing sets

**Confirmed:** For a known vehicle, file the incoming set when it would be the first or second active set, unless the PDF clearly identifies an existing set to replace. If the incoming set would be the third, ask during submission which existing set is coming out or being replaced. Apply that replacement atomically after selection. Never take a set assigned to a different known vehicle. Missing vehicle evidence allows customer-level lookup.

**Confirmed — missing vehicle match:** If the PDF identifies the customer but does not establish a vehicle match, file a clear incoming set under that customer with no vehicle assigned. Staff can link it later from the customer profile.

**Decision — mixed vehicle associations:** Recommend this explicit eligibility policy:

| Source vehicle | Current stored sets | Result |
|---|---|---|
| Known vehicle | Zero or one active set assigned to that vehicle | Add incoming as the first or second set unless a replacement is explicitly identified |
| Known vehicle | Two or more active sets assigned to that vehicle | Ask which assigned set is coming out before applying the incoming set |
| Known vehicle | Assigned matches plus unassigned sets | Apply the threshold using assigned sets. Show unassigned sets as context without counting them against the vehicle |
| Known vehicle | No assigned match, but unassigned sets exist | Add the first assigned set unless the PDF explicitly identifies an unassigned outgoing set |
| Known new/different vehicle | Only sets assigned to other known vehicles | New incoming listing; show existing associations as context, never auto-select |
| No known vehicle | One customer stored set | Use it only for a clearly identified replacement; otherwise file the incoming listing |
| No known vehicle | Multiple customer stored sets | Show vehicle associations if an outgoing set must be identified; the per-vehicle threshold requires vehicle identity |
| Any | No eligible stored sets | New incoming listing |

For a known vehicle with multiple assigned matches, selection may also explicitly choose a new incoming listing with no outgoing set. This accommodates a second stored set without forcing an incorrect swap. Other-vehicle entries may be visible as disabled contextual rows with a link to manual reassignment; they are not ordinary selectable outgoing options.

Choosing a set is part of submission, not attention by itself. Cancelling leaves a resumable pending submission with no inventory changes and an explicit pending-selection indicator, separate from the attention queue. The final selection must revalidate inventory versions; another workstation may have removed/swapped a candidate meanwhile.

For an applied swap, atomically close the selected outgoing set's open storage period and open an incoming set period at the source date. Keep outgoing identity and history. **Decision D15:** automatically reuse an incoming historical set only when an explicit existing set reference or recorded transaction lineage uniquely identifies an inactive set under the same customer and compatible vehicle. Brand/size/wheel-description similarity alone is insufficient. A reused set receives a successive period, never a new identity. If no reliable identity exists, apply the clear intake as an explicitly labeled new listing and show any possible historical matches in its result/details for optional audited linking. Linking requires staff choice, compatible customer/vehicle history, no overlapping occupancy, and atomic correction of references; retain the superseded listing as an alias/history reference, not hard deletion. Conflicting reliable evidence blocks the action. This recommends preserving automatic clear intake while preventing automatic false merges; repeated seasonal listings without reliable identifiers are a disclosed tradeoff for consolidated review.

## RO identity, revised PDFs, and downstream history

**Confirmed:** RO is the visible transaction identifier. Preserve original invoice evidence without requiring a separate invoice-number field. Updated PDFs with the same RO must never execute another swap or create duplicate periods. The latest submitted PDF for that work order is the authoritative source for updated information, including the printed date. Invoice number and document type do not determine precedence.

**Default:** Preserve RO as a string, trim whitespace and an unambiguous label prefix, retain meaningful leading zeroes. No fuzzy numeric matching. Apply a database uniqueness constraint to the canonical RO within this one-shop application. RO/customer identity conflict goes to attention rather than merging unrelated records. A future RO reuse/import policy is required if Protractor ever reuses RO values.

Order distinct submissions by server-recorded acceptance sequence, not file timestamp or client clock. Retain immutable source order, actor, effective printed date, extracted values, corrected values, and revision lineage. Exact-file retry does not promote an older source to latest or erase newer evidence. An intentional rollback to an earlier source is an explicit audited correction. Missing RO blocks automatic PDF transaction application; manual **Remove** does not require RO.

For a revised RO:

1. Archive and link the new source; preserve all older sources.
2. Compare corrected effective fields and action with the last applied revision.
   Any change to an already applied action type, customer, incoming/outgoing set identity, or interpretation as no storage activity stages the entire revision for explicit correction, even when no downstream event exists. Only safe supporting-field/date revisions are eligible for automatic revision; changing interpretation cannot silently undo or replace the prior action.
3. Classify the entire revision before changing business fields. A fully safe revision can automatically update supporting details atomically, retaining historical values. Replace source-derived fields only; do not silently erase staff-entered notes, manual section assignments, or independent corrections. Show conflicts in attention.
4. If no subsequent transaction depends on the affected periods/sets, revise source dates and derived dates in place as an audited version of the same event, after validating period ordering. Never execute the action twice.
5. If a later swap/removal/renewal depends on a consequential changed field, stage the entire new revision in attention and retain all previously applied business fields, inventory and downstream history. Archive/extraction and draft corrections may persist, but even nonconflicting business supporting fields wait for that revision's resolution. Show before/after and affected-event preview. Resolution must revise the dependent chain atomically or preserve the applied chain with an explicit correction explanation. No automatic replay against current inventory and no partially applied blocked revision.

**Confirmed — historical revisions:** Use the latest PDF for the work order as the source. If applying its changes would alter a later swap, renewal, or removal, stage the revision for staff review and keep the applied inventory history intact until reconciliation. Display the latest printed date as pending source evidence until the revised business date is applied.

Correcting an RO to an unused RO preserves the transaction's internal ID and logs the former identifier. Correcting to an existing RO opens a relinking/conflict view; never automatically merge two applied transactions. An incorrect linked document can be reassigned while preserving archive and audit links. If the wrong RO already caused inventory changes, correcting the text alone cannot count as repairing those changes; show and resolve both transaction effects together.

## Date rules and renewals

**Confirmed:** Six calendar months; printed source date from latest PDF; early renewal extends existing due date; overdue renewal starts from printed renewal date. Upload/appointment/footer/current date are not substitutes. No automatic renewal or inventory removal at expiry. Charges do not establish periods or count.

**Default:** Read the explicitly labeled date appropriate to the submitted document (Invoice Date, Authorization Date, or Work Order Date), retaining page/label/value provenance. Multiple plausible conflicting source dates require correction. Missing date may be entered by the advisor based on the original, labeled as a manual correction. Do not silently fill today's date. A date-independent unrelated document may be archived without a usable source date.

Calendar-month addition preserves day of month where available and otherwise clamps to the destination month's last day. Calculate each new six-month period from its actual anchor; do not invent an end-of-month preservation rule.

| Action | Anchor | New due date |
|---|---|---|
| Incoming storage/swap | Printed source date | Anchor + 6 calendar months |
| Early renewal: printed date before existing due | Existing due date | Existing due + 6 calendar months |
| Same-day renewal: printed date equals existing due | Existing due date (default) | Existing due + 6 calendar months |
| Overdue renewal: printed date after existing due | Printed renewal date | Printed date + 6 calendar months |

Classify early/overdue relative to the printed renewal date, not today's upload date. Preserve transaction date and period start separately. Missing current due date or uncertain renewal target requires attention. Multiple eligible renewal targets use the same immediate selection interaction; unclear renewal-versus-swap wording requires attention. Each explicit renewal adds exactly one six-month period; historical seasons or multiple-price amounts do not generate extra renewals.

Examples: January 31, 2026 → July 31, 2026; August 31, 2026 → February 28, 2027; August 31, 2027 → February 29, 2028; February 29, 2028 → August 29, 2028. Due April 30 with printed renewal April 9 → October 30; due April 30 with printed renewal May 9 → November 9. A corrected renewal PDF recalculates that same renewal from its recorded predecessor due date, never from its already extended due date.

## Remove and correction

**Confirmed:** Action label is exactly **Remove**; no PDF/RO required; retain history. Clear pickup-only PDF may remove the matched stored set without incoming storage.

**Default:** Manual **Remove** opens a compact confirmation showing customer, vehicle, set, and effective date defaulted visibly to today's America/Chicago date. Permit an advisor-entered backdate with a reason; block future dates and chronological conflicts. Submission carries a stable request ID to prevent double removal. Record actor, timestamp, reason, prior state, and optional PDF/RO. This confirmation is specific to a manual action, not a universal PDF approval step.

Offer **Undo removal** when the set has no dependent later transaction. Undo records a compensating history entry and restores the prior open period/date, rather than deleting removal history. If later changes exist, provide a correction flow showing affected history; do not silently restore an outdated state. PDF retrieval uses its printed date and must resolve multiple candidate sets before applying. If no eligible stored set exists, record no inventory change and send the mismatch to attention; do not invent a set just to remove it.

## Needs attention and resolution

**Confirmed:** Show submitted original alongside translated/extracted fields and permit correction of relevant lines/fields and interpretation. Preserve originals and extraction. Missing VIN alone and normal multiple-set choice are not attention issues.

Attention reasons include unclear action, missing/conflicting RO or required date, customer/VIN conflict, contradictory descriptions, retrieval/renewal without a target, and historical correction affecting downstream events. Show specific reasons rather than a generic confidence score. Do not require absent brand/model/accessories merely to match a visual example.

On desktop display embedded PDF beside editable interpreted fields, with controls to open/download the original if inline viewing fails. On narrow screens provide adjacent PDF/fields tabs while retaining access to the same source. A source load failure remains visible and retryable; do not imply it was reviewed. Advisor can correct customer, vehicle association, RO, printed date, action, incoming description, target set, tire sizes, accessories, and operational notes. Preserve raw line evidence even when translated fields change.

**Default:** Resolution previews the resulting action and uses **Apply correction** to apply an explicit repaired interpretation. Validate current versions and transaction invariants at commit. Archive/correction history can persist while the entire business mutation succeeds atomically or makes no change. Refresh queue and inventory after commit; conflict keeps local changes available and requires explicit reconciliation. **No storage activity** is a legitimate resolution with retained evidence and no inventory change.

## Scenario walkthrough and future acceptance checks

These are design walkthroughs grounded in the historical sample findings and synthetic boundary cases. No PDFs were reprocessed or runtime checks run for this document. Historical findings describe filenames by invoice number; actual Rollcall identity must be extracted RO, not those filenames or invoice numbers. Earlier sample-review approval/date rules are superseded.

| Acceptance ID | Evidence/scenario | Required result |
|---|---|---|
| WF-01 | Incoming PDF with one active vehicle set and no identified outgoing set | File the incoming set as the second active set; leave the first active |
| WF-02 | Incoming PDF would create a third active vehicle set | Immediate association-aware selection; no inventory change before selection; not attention solely for multiplicity |
| WF-03 | Authorization WO246537; compound purchase/disposal/storage | Incoming Michelin/Asanti storage evidence is distinct from Nokian purchase and discarded Continentals; unclear target identity requires resolution, never store purchased tires by heading alone |
| WF-04 | Clear pickup sample labeled invoice 210874 with storage charge 199.98 | Retrieval of selected eligible set; no renewal or new period inferred from amount |
| WF-05 | Install-from-storage sample labeled invoice 215777 | Retrieval supported without incoming storage package; preserve note; create no incoming listing |
| WF-06 | Purchase-only samples labeled 215885 / internally 213906 | Archive evidence, report no storage activity, create no set or period; filename/invoice mismatch cannot determine RO |
| WF-07 | Renewal sample labeled 210794 without VIN | Customer lookup valid; eligible set selection as needed; no missing-VIN attention and no charge-multiple period inference |
| WF-08 | Renewal sample labeled 210893 with staggered sizes | Keep two sizes in one set; ambiguous historical-season wording requires interpretation rather than automatic period allocation |
| WF-09 | Exact same PDF submitted twice, including after newer PDF | Same result, no duplicate effect, no promotion over newer revision |
| WF-10 | New PDF same RO changes date before dependent actions | Same event/set IDs; recalculated same period; old evidence retained; no second swap |
| WF-11 | Older RO updated after later swap/removal | Preserve current state; reconcile material correction and dependent chain; never replay old swap |
| WF-12 | Printed date missing/conflicting | Attention before date-dependent action; never fallback to upload/today/footer |
| WF-13 | Early/same-day/overdue renewal; corrected renewal uploaded again | Correct anchors above; revision never adds another six months |
| WF-14 | Month ends and leap years | Exact example dates above; dates remain date-only in shop context |
| WF-15 | Known different vehicle's stored set is customer's only set | Create incoming listing for new vehicle; never swap different vehicle automatically |
| WF-16 | Known vehicle plus mixed matching/unassigned candidates | Follow explicit reviewed mixed policy; no unassigned selection by guess |
| WF-17 | Customer name spacing/case variant versus conflicting spelling/VIN owner | Normalize safe variants; preserve display; explicit correction for conflicting identity |
| WF-18 | Reassign customer's set to replacement vehicle | Same set/period IDs, unchanged inventory count, preserved association history |
| WF-19 | Two workstations submit same RO or select same outgoing set | Serialize/revalidate; one valid effect, explicit conflict/revised result for other; no partial swap |
| WF-20 | Manual Remove, retry, undo, then attempted undo after downstream use | One removal; audit retained on undo; dependent case enters correction flow |
| WF-21 | Unresolved revised PDF for applied RO | Existing applied inventory remains, pending revision visible, no partially applied corrections |
| WF-22 | Correct RO to another applied RO | Explicit relink/reconciliation of both effects; never silent merge |
| WF-23 | Expiration or appointment lookup/pre-pull | No new period, removal, or transaction |
| WF-24 | Two-season return explicitly linked to inactive known set | Same incoming set ID with a successive period; outgoing set selection is separate; no extra set identity |
| WF-25 | Several similar inactive historical sets, no reliable incoming link | Never silently merge on brand/size; explicit new-listing result with possible-match correction; reliable contradictory identity blocks rather than guesses (D15) |
| WF-26 | Revised same-RO PDF changes description and a blocked date/action | Entire business revision remains staged; original applied description/date remain together until atomic resolution; new PDF/extraction remain visible as pending |
| WF-27 | New identified vehicle without VIN versus no vehicle information | Retain explicit new vehicle under customer with blank VIN; truly absent/uncertain association stays customer-only without missing-VIN attention |

## Consolidated-review recommendations

Bundle these with the main specification's review package, rather than asking serial questions: mixed assigned/unassigned selection and explicit no-outgoing option; dependent historical revision policy; accepting work orders like authorizations; manual Remove default/backdating/undo behavior; returning historical set identity linking. Routine normalization, request deduplication, atomic commits, date provenance, and same-day renewal are technical defaults documented above.
