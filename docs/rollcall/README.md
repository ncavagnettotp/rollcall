> Current screen-review status (November 18, 2026). Inventory, Corrections, and Dashboard mobile layouts are accepted and available in the [main mockup](interaction-preview.html). Insights and Settings review follow. Consolidated specification approval is still pending.

> Accepted visual direction, November 11, 2026: the user selected the graphic-design study as the continuing Rollcall mockup. interaction-preview.html now uses that design; design-study.html is a matching entry point. The earlier preview is preserved in interaction-preview-before-design-study.html with its own stylesheet. This accepts the visual direction, not the full business specification or production implementation.

# Rollcall planning index

Updated November 11, 2026. Planning only. Governing continuation: `../../ROLLCALL_HANDOFF.md`. [Specification](specification.md) is the consolidated review entry point. `[x]` means documented and checked within the stated scope; partial steps remain unchecked.

Discovery topics: 13/13 covered historically. This is not implementation progress. Product code, live database records and deployment configuration remain unchanged by this planning batch.

<details open>
<summary><strong>Planning Stage 1 — Consolidate what we know</strong></summary>

- [x] 1. Create [requirements/decision register](requirements.md), with stable R/D IDs.
- [x] 2. Preserve four approved previews in references/ and record navigation/HeroUI authority.
- [ ] 3. Establish verified software baseline. [Source audit](baseline.md) complete; fresh runtime baseline remains pending.
- [x] 4. Add current-planning pointers to historical governing documents; preserve old evidence.
- [x] 5. Record preserve/replace/add decisions and complete independent source/specification review. Runtime baseline remains separately open at step 3.

</details>
<details open>
<summary><strong>Planning Stage 2 — Define business workflows</strong></summary>

- [x] 6. Customer/vehicle matching and reassignment.
- [x] 7. New storage, swaps, and selection.
- [x] 8. Updated PDFs, RO identity, dates and idempotency.
- [x] 9. Renewal detection and dates.
- [x] 10. Remove, history and correction behavior.
- [x] 11. Needs attention and resolution.
- [x] 12. Scenario walkthrough and internal consistency check.

Deliverable: [workflows](workflows.md). Document consistency reviewed, including 27 planned scenario checks; these are design walkthroughs, not executed application tests.
</details>
<details>
<summary><strong>Planning Stage 3 — Define information and screens</strong></summary>

- [x] 13. Records and relationships.
- [x] 14. Fields, sizes, accessories, notes, sections.
- [x] 15. Approved screens and metric/status meanings.
- [x] 16. Profiles, details, selection and Settings.
- [x] 17. Search/filter/history behavior.
- [ ] 18. Empty/error states and useful clickable previews. Current dashboard/profile design preview has real Edge desktop/mobile screenshots and interaction checks; user visual review and remaining screen previews are still in progress.

Deliverables: [screens/operation](screens-and-operations.md), [sample interaction preview](interaction-preview.html).
</details>
<details>
<summary><strong>Planning Stage 4 — Define shop operation</strong></summary>

- [x] 19. Local host and LAN access.
- [x] 20. Concurrent uploads/edits and refresh.
- [x] 21. Staff access, startup, maintenance and data locations.
- [x] 22. Coordinated database/PDF backup and recovery acceptance.

This stage defines acceptance requirements; a real shop restore test belongs to implementation/pilot.
</details>
<details open>
<summary><strong>Planning Stage 5 — Assemble and review specification</strong></summary>

- [x] 23. Consolidated specification assembled and integration-reviewed.
- [x] 24. Independent review of contradictions, gaps and scope.
- [x] 25. Present bundled consequential decisions with recommendations.
- [ ] 26. Revise and obtain one explicit specification approval.

</details>
<details>
<summary><strong>Planning Stage 6 — Produce implementation plan</strong></summary>

- [ ] 27. Dependency-ordered delivery stages with usable outcomes.
- [ ] 28. Individual tasks, file ownership and interfaces.
- [ ] 29. Acceptance checks and meaningful tests.
- [ ] 30. Working previews, user checkpoints, continuity and recovery checkpoints.
- [ ] 31. Review/fine-tune implementation plan; surface material changes only.

Detailed implementation plan follows approved specification. No implementation has been authorized by completion of discovery alone.
</details>

## Current evidence and next action

Customer profile tabs now use actual HeroUI components and a locally bundled React island; see preview-tabs.jsx and verification.md. Rebuild the standalone tab bundle with `node work/build-rollcall-preview-tabs.cjs` after changing that source. This adds real component animation to the design preview without changing production/backend scope.

Review package prepared: [specification](specification.md), [independent review](review.md), requirements, workflows, screens/operation and sample interaction preview. Approved references preserved and inspected. User requested reference-style fidelity first; preview shell, typography, cards and dashboard comparison rebuilt. Real Edge desktop/390px/320px screenshots and navigation/overflow checks now pass; this supersedes the earlier browser launch limitation. User visual review and remaining screen previews continue at step 18. Fresh application runtime baseline remains open at step 3. Next: finish the requested visual foundation review, then consolidated specification review/approval (step 26) before detailed implementation planning. No production product implementation or fresh application runtime tests in this batch.

Corrections preview refinement (November 12): fixed PDF-left/review-right workspace; overall canvas scales down to 70% then clips. Previous/Next page arrows now show the supplied two-page invoice with horizontal transitions. Review fields follow that source; correction scenario and stored-set choices are demonstrations. Fresh browser evidence is recorded in verification.md. This replaces Corrections mobile stacking only; no production implementation is implied.

Latest correction-layout clarification (November 12): the 70% fixed-canvas/clipping approach is superseded. Both panes now fit compact windows and expand to fullscreen; compact navigation uses an icon rail, review/editor scrolls independently, and PDF has Fit/± zoom with internal pan. Verified in Edge at 360–1920px widths, including 480×690 compact preview. See verification.md for evidence and limits.

Latest resize/navigation changes (November 12): original 248px labeled sidebar stays left at all widths, with independent scrolling and vertical edge fades. Supported app layout minimum: 576×384 CSS pixels; smaller host windows can scroll the minimum canvas. Inventory profile tabs now fade horizontally and use mouse-wheel scrolling only while hovered and overflowing. Original labeled sidebar replaces the intermediate icon rail. Current browser evidence is in verification.md.

Stable profile-tab styling (November 12): tabs-layout.css now owns both concave bottom corners and the continuous white connection to the view panel. Keep all tabs adjacent, including All Stored Sets. Dedicated geometry and smooth-motion browser checks guard these requirements. PDF now supports click-drag pan plus wheel zoom; Inventory type boxes reserve aligned tire-left/wheel-right slots. See verification.md for current evidence.

Separate visual option for review (November 13): [Underline tabs preview](underline-tabs-preview.html) reuses current icons, sizes, colors and behavior with an isolated underline style. The main interaction preview remains on the existing connected-tab design. No new visual choice has been accepted yet.

Current approved profile-tab design (November 13): underline style is now in interaction-preview.html with larger labels (22px wide / 20px compact), the same preview palette, off-grey shelf and 2px grey guide beneath the 4px orange selector. Both main and comparison entries share the same versioned stylesheet URL. Previous connected tabs are preserved in interaction-preview-connected-tabs.html; this latest approval supersedes their former main-mockup styling requirement.

Latest mobile scope (November 13): Inventory/profile and its set details now adapt to phone/small-desktop widths. Sidebar collapses to a 64px icon rail at 1000px; the small menu button opens full labeled navigation. Compact rows keep vehicle information, type icons and fading descriptions while hiding list dates. Other screens retain their existing layout. Verified in touch-emulated Edge at 320–1280px; refresh interaction-preview.html to try it. Evidence/screenshots: verification.md and output/rollcall-visual/inventory-phone-preview.png.

Separate Corrections mobile proposal (November 15): [Open concept](corrections-mobile-concept.html). Main mockup's Corrections remains unchanged. The concept preserves desktop PDF-left/review-right; phones use a Review/PDF switch with retained draft edits, PDF page and zoom. Inventory-style compact navigation is included only in the separate concept. These are review defaults, not accepted changes to the main Corrections workflow.

Corrections mobile approved (November 15): promoted to interaction-preview.html. Open Corrections → Review. Desktop retains its two-pane setup; phones use Review/PDF switching with drafts/page/zoom preserved. Inventory remains the opening screen. Separate concept remains available for reference.
