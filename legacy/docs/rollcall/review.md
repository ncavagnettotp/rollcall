# Rollcall independent specification review

November 11, 2026. Reviewed the handoff and requirements, baseline, central specification, workflows, and screens/operations drafts. Scope is document consistency and implementability only. No product code, customer records, services or deployment configuration changed; no runtime tests performed. Insights metric definitions and the supporting preview were being completed independently during this review.

## Findings to resolve before consolidated approval

### P1 — Define incoming historical-set reuse consistently

The central specification invariant 5 requires a returning known set to retain identity, while workflows permits a new stable identity when history cannot establish the returning set. Those can coexist, but the draft never defines what establishes a known returning set, nor provides an incoming identity choice when more than one historical set could match. Outgoing selection cannot settle incoming identity. A builder could duplicate the same seasonal set every visit or silently merge on tire description.

Recommendation: define distinct incoming identity resolution: reuse an explicitly linked/verified historical set; never match on description alone; provide a separate incoming historical-set choice when evidence is ambiguous; otherwise create a new identity visibly and allow audited linking/correction. State which ambiguity blocks automatic action and which genuinely new set may apply automatically. Add a two-season return scenario plus ambiguous matching historical sets. This is a proposed workflow refinement for the review bundle, not an already confirmed requirement.

### P1 — Resolve partial supporting-detail application during a blocked revision

The central invariants forbid partially applying unresolved transactions. Workflow revision steps 3 and 5 nevertheless apply nonconflicting supporting details while material date/action/set changes remain unresolved. Without separate field/revision provenance this can make an applied transaction display a mixture of the pending source and prior committed business state, despite a single current revision pointer.

Recommendation: retain a complete applied business revision and a separately staged latest-source revision; an unresolved material revision changes no business fields until resolution. Latest source/extracted evidence may be visible immediately, clearly labeled pending. Alternatively model separately committed supporting corrections with explicit audit/revision links, but do not leave the choice implicit. Include a later same-RO PDF that changes both a tire description and a conflicting date/action, with and without downstream events.

### P2 — Align optional-VIN new-vehicle behavior

The handoff says a PDF identifying a new vehicle adds its information under the customer; VIN is optional in the information model. Workflow text creates a vehicle for a new full VIN, but describes missing-VIN behavior as customer-only unless details identify an existing vehicle. That omits creating an identifiable new no-VIN vehicle and could discard supplied vehicle information.

Recommendation: preserve supplied vehicle description even when no VIN exists. Define new no-VIN vehicle creation when the document clearly identifies a different/new vehicle; use customer-only association only when no vehicle is identified or association is uncertain. Never fuzzy-merge same year/make/model into an existing vehicle. Add explicit supplied-vehicle/no-VIN and genuinely no-vehicle scenarios.

### P2 — Keep the mixed-candidate policy identical in the summary

Requirements D02 and the workflow table require immediate grouped selection for known-vehicle plus unassigned candidates, including a known vehicle with only one unassigned fallback. The central review table instead says “Prefer the known vehicle's eligible sets; customer-only fallback is visible,” which can be read as automatically choosing the assigned match and ignoring unassigned candidates.

Recommendation: copy the precise D02 policy into the central review table. Label selection in the one-unassigned fallback case as an association-uncertainty recommendation overriding the ordinary one-clear-eligible-set shortcut; it is not a new universal confirmation.

### P2 — Put all consequential workflow recommendations in the review entry point

The central D01–D12 review bundle does not explicitly list accepting plain work orders for automatic action, the no-outgoing option when stored candidates exist, incoming historical identity handling, or manual Remove backdating/undo. Those decisions are called consequential in workflows and materially alter what staff can do.

Recommendation: add stable decision IDs or an explicit linked supplemental decisions table to the review entry point. Distinguish proposed changes from confirmed automatic authorization/invoice behavior, and avoid requiring a second discovery round merely to locate them.

## Coverage and limits

The documents preserve the primary confirmed direction: automatic clear submissions, RO-based revisions, no mandatory global confirmation, legitimate customer-only storage, different-vehicle protection, early/overdue renewal anchors, permanent history, manual Remove, optional manual sections, and local LAN hosting. They explicitly preserve original evidence and distinguish historical tests from fresh verification. Atomicity, version checks, stale selection, duplicate response recovery, dependent-history correction, RO relinking, source-date provenance, and unrelated purchases are addressed.

Missing-RO attention items are accounted for in screens/operations as submission issues with internal IDs that later deduplicate into an RO issue. Keep the UI label “unresolved issues” accurate when the queue includes items without an RO; “ROs awaiting review” alone would underdescribe that state.

Runtime baseline, browser mockup verification, actual migrations/concurrency/restore demonstrations, and specification approval remain outstanding gates. This review does not approve product implementation or establish that proposed behavior already works.

## Follow-up disposition

Re-read updated specification, requirements, and workflows on November 11, 2026. The original five findings are addressed in the draft:

- Incoming reuse criteria and the new-listing/linking tradeoff are explicit in D15 and WF-24/25. Description similarity cannot silently merge sets; reliable contradictory identity blocks.
- Workflow revisions classify the whole revision first and stage all business fields when blocked. WF-26 checks the description-plus-conflicting-date case.
- New identified no-VIN vehicles are retained; WF-27 distinguishes that from absent/uncertain vehicle information.
- The central mixed-candidate summary now matches D02 and the eligibility table.
- D13–D15 and the central review table expose work-order, no-outgoing, incoming identity, and Remove correction recommendations.

One narrow clarification remained at this follow-up: for an already applied RO, a changed action type/customer/set identity with **no downstream event** is not explicitly routed. Revision step 4 handles safe dates, while step 5 describes dependent history. Recommend staging any material applied action/customer/set change for explicit correction regardless of downstream dependencies, including a new “no storage activity” interpretation. Limit automatic changes to nonconflicting supporting fields and safe dates. This prevents a builder treating an action change as an ordinary supporting-field update.

Preview verification is reported separately: jsdom interaction checks do not replace browser visual/mobile verification; the attempted browser environment failed and that gate must remain open. No application runtime verification is implied by this document follow-up.

Final clarification rechecked: workflow revision step 2 now explicitly stages every changed applied action/customer/incoming or outgoing identity/no-storage interpretation, regardless of downstream dependencies. Automatic revisions are limited to safe supporting fields/dates. The narrow follow-up gap above is resolved. No further consequential document contradiction was identified within this review scope. Proposed business defaults still require the consolidated user review, and runtime/browser gates remain open as recorded.
