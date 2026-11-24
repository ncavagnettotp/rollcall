# Rollcall requirements and decision register

Draft, November 11, 2026. Authority: `../../ROLLCALL_HANDOFF.md`. Confirmed requirements below come from that handoff; proposals are not approvals. Existing source behavior is evidence of the baseline, not the target. This register supersedes conflicting legacy product rules while preserving historical verification.

## Confirmed requirements

| ID | Requirement | Planned verification |
|---|---|---|
| R01 | Extend React/FastAPI/PostgreSQL/PDF archive; use HeroUI for covered controls. | Source audit, regression checks, migration rehearsal. |
| R02 | Rollcall branding; light content, dark sidebar, orange active navigation; Dashboard, Inventory, Insights, Needs attention. | Compare with preserved references; browser navigation and mobile checks. |
| R03 | Customer name identifies customer; internal IDs remain stable; no required customer number/contact matching. | Exact normalized lookup and visible rename/conflict scenarios. |
| R04 | Optional vehicle; customer profiles group vehicles and their sets and show unassigned sets. | Multiple-vehicle and customer-only scenarios. |
| R05 | Never automatically exchange another known vehicle's set; allow explicit reassignment. | Cross-vehicle isolation and reassignment audit. |
| R06 | Clear submitted PDFs automatically apply storage actions; no universal confirmation. | One submission updates inventory; ambiguous input does not. |
| R07 | Incoming storage evidence with zero eligible sets creates a listing, one swaps, several require immediate selection. | Zero/one/multiple candidate scenarios, stale selection. |
| R08 | RO identifies transaction; later submitted source revises it without repeating action. | Duplicate bytes, revised PDF, concurrent upload and downstream history tests. |
| R09 | Latest PDF's printed date controls new storage/swap; preserve originals; no upload/today fallback. | Conflicting/missing printed dates and same-RO revision tests. |
| R10 | Six calendar months; early renewal extends due date; overdue renewal starts at printed PDF date. | Month ends, leap day, early/same-day/overdue tests. |
| R11 | Explicit renewal wording; uncertain renewal versus swap requires attention; price/season alone cannot allocate periods. | Contradictory notes and historical-charge cases. |
| R12 | Exact action label Remove; no PDF/RO needed; retain history. Clear pickup PDF can remove. | Manual and PDF removal; recovery/correction history. |
| R13 | Needs attention displays original alongside editable extraction and interpretation; unresolved action cannot partially apply. | PDF rendering, correction, concurrent resolution, rollback. |
| R14 | Tire brand/model/sizes, wheels, notes, accessories; unknown/yes/no accessories. | Missing optional fields, blank templates, historical notes. |
| R15 | Compact typed tire-size strings; formatted display; customer/vehicle/VIN/tire/RO search. | Metric/flotation formatting and equivalent-query tests. |
| R16 | Sections manually assigned in details; optional visibility toggle retains data. No PDF location inference. | Toggle, persistence and per-set editing tests. |
| R17 | Customer history exposes swaps, renewals, removals, corrections and linked sources. | Source-to-event-to-customer navigation. |
| R18 | Shop-local single host; multiple LAN browser clients; Protractor retains schedule/payments. | LAN pilot, shared data and concurrent actions. |
| R19 | No automatic expiration removal/renewal or payment collection. | Date rollover leaves physical inventory unchanged. |
| R20 | Expandable individually numbered plan; one consolidated specification review before code. Working previews at delivery gates. | Planning index and release acceptance checklist. |

## Proposed defaults for consolidated review

| ID | Recommendation | Reason / review significance |
|---|---|---|
| D01 | Normalize Unicode/case/outer and repeated whitespace for name matching; preserve display name. Never fuzzy-merge punctuation/spelling changes. | Prevent accidental duplicate or merged customer identity. Conflicts require visible correction. |
| D02 | One vehicle-assigned match with no unassigned candidates swaps automatically. Mixed assigned/unassigned candidates open grouped selection; an unassigned fallback for a known vehicle also requires selection, including none coming out. Other known vehicles are ineligible. | Avoids guessing when association is uncertain; see workflow eligibility table. |
| D03 | Same-day renewal starts at existing due date; add six calendar months with month-end clamp. | Continuous period at boundary; no additional day. |
| D04 | Missing/ambiguous required RO, customer, printed date or action evidence blocks application; missing VIN alone does not. | Avoid silent inventory changes on weak evidence. |
| D05 | Same-RO historical revision preserves original event identity and current downstream state; dependent corrections require a reconciliation preview. | Revised old paperwork cannot undo a later swap. |
| D06 | Remove defaults to current America/Chicago date, shows affected set/date before committing; correction restores only if no later dependency, otherwise reconciliation. | Recoverable human error without unsafe unconditional undo. |
| D07 | Due soon is today through 30 days inclusive; overdue is due date before today. Current means beyond 30 days. | Makes status buckets disjoint; In storage includes all physically stored sets. |
| D08 | Count unresolved ROs separately from set statuses; unclassified stored sets appear in a separate missing-date count. | An ambiguous RO is not necessarily one stored set. Adjust preview chart labels accordingly. |
| D09 | Location display initially off; allow multiple manually selected sections per set. | Optional use and split-rack storage. |
| D10 | Keep staff attribution in scope before pilot; defer historical bulk import, custom-rate operations and charge analytics pending explicit inclusion. | Inherited requirements were not reconfirmed. No silent deletion of legacy evidence or old requirements. |
| D11 | Staggered tires remain one set with multiple typed size values. Unknown size stays searchable by other fields. | Real sample evidence; no fabricated completeness. |
| D12 | Insights retains approved daily averages, check-ins/removals, renewals, inventory trend and overdue aging, using explicit effective-date definitions; no payment/revenue charts. | Preserve the approved screen while making metric meaning testable. |
| D13 | Accept clear dated work orders under the same submission rules as authorizations/invoices. | Preserves inherited supported input, while newest automatic-action language specifically named authorizations/invoices. |
| D14 | Offer an explicit new incoming listing with none coming out in the multiple/uncertain selection flow. | Allows additional sets without forcing an incorrect swap. |
| D15 | Reuse a returning historical set only with unique explicit set reference/recorded lineage and compatible ownership; otherwise create a visibly new listing with optional audited historical linking. Conflicting reliable identity blocks. | Preserves automatic clear intake and avoids false description merges; repeated seasonal listings without identifiers are a disclosed tradeoff. |

## Authority and implementation decisions

## Profile and settings refinement — November 11, 2026

**Latest tab appearance:** center all three customer tabs as a compact HeroUI-style segmented pill control, using the actual primary Tabs variant with a filled animated selection rather than the prior stretched underline layout. Keep subtle orange selection styling, counters and current tab order. This supersedes the far-right All Stored Sets alignment.

**HeroUI animated customer tabs:** use the actual installed HeroUI Tabs component and its SelectionIndicator for Vehicles / Unassigned / All Stored Sets. Preserve the reference-style orange underline, far-right all-sets tab, default Vehicles, live count updates and keyboard behavior. Selection underline slides/resizes with built-in component geometry; respect prefers-reduced-motion. Apply this component animation choice when implementing the production customer profile as well.

Latest grouped-list refinement: hide repeated vehicle descriptions beneath individual tire descriptions within Vehicles, since the expandable vehicle heading already supplies that context. Place each due date at the far right of its tire-description line. Retain vehicle association context in All Stored Sets/Unassigned where not redundant. Composition box remains below the description.

User requested preserving the selected tire/wheel icons for future reference. Canonical assets and current display guidance are recorded in [assets/ICON_REFERENCE.md](assets/ICON_REFERENCE.md); reuse tire-user.png and wheel-replacement.png rather than earlier alternatives.

Latest set-icon placement: below the tire description, put vehicle/due-date text and the composition icon box on the same secondary row, with the box immediately to the right of that text. Preserve its enlarged icons/subtle box; wrap only when narrow width requires it.

Latest set composition layout: move tire/wheel icons into their own subtle boxed area directly beneath the tire-description/size line and above secondary vehicle/due information. Increase the icons slightly (44px source frames desktop, 40px mobile). This supersedes inline placement and retains the user's supplied artwork.

Wheel source replacement: use the latest user-supplied `assets/wheel-replacement.png`, replacing the prior source. Match its visible wheel diameter to the tire height; use a transparent-looking blend/contrast presentation against the white card without the pale source-image square. Supplied original file remains intact.

Tire/wheel image display: eliminate visible pale square image backgrounds and size the wheel's actual artwork to visually match the tire. Rendering uses grayscale/contrast and blend treatment, with a larger wheel image frame to compensate for its source padding. Keep original supplied files intact.

Latest wheel artwork: use the user's supplied wheel image (`assets/wheel-user.png`) alongside the supplied tire image, replacing the drawn wheel SVG. Preserve the supplied image as provided.

Latest tire artwork: use the user's supplied solid dark tire image (`assets/tire-user.png`) for tire composition indicators, replacing the drawn tire SVG. Wheel artwork stays unchanged.

Latest vehicle-action styling: assigned-set button reads **Reassign vehicle** and uses purple styling, superseding the earlier orange Reassign treatment. Keep its far-right position and existing picker behavior.

**Latest detail refinements:** due date appears at top right beside status/notes, formatted Due MM/DD/YYYY; remove the Storage dates row. Customer context moves to a small top-page overline linking to the customer's profile; remove the Customer row from the set card. Reassign moves to the far right of the vehicle line below the notes area, preserving compact soft-orange styling. Notes present must visibly highlight the existing notes icon with soft-orange fill/outline and an exclamation badge; no-notes state stays neutral. This indicates presence, not unread status or a global alert. Set-composition vectors should closely resemble the supplied reference with defined tire tread/depth and a metallic spoked wheel, rather than thin generic outlines.

**Set composition icon placement/quality:** place composition icons immediately to the right of the tire description, not at the row's far right. Redraw tire/wheel as sharp transparent vector graphics, replacing the blurry cropped screenshot treatment. Retain tire-only, combined and wheel-only meanings and accessible names across all profile lists.

**Vehicle action placement:** place Reassign beneath the Vehicle field label in the left column, rather than under the assigned vehicle name. Use a small soft-orange rectangular button with subtle rounding. Assign Vehicle uses the same placement/style for unassigned sets; picker behavior is unchanged.

**Set-list icons and compact accessories:** display tire-only, tire-and-wheel or wheel-only imagery on each set row across vehicle groups, unassigned and all-sets lists. Use recorded set composition, not a guess from missing descriptions; the sample demonstrates typed variants. Remove the redundant Sets by vehicle / Sample records heading row. Reduce the accessory images in set details by 50% in width/height (36 × 40.2px versus 72 × 80.4px), preserving at least a 44px clickable button.

**Latest tab order overrides earlier profile layout:** Vehicles is the first/default tab, Unassigned is beside it, and All Stored Sets is aligned at the far right. Vehicles contains expandable assigned-vehicle groups only; unassigned sets move to their own tab. All Stored Sets retains the combined current inventory list. Counts and lists update together after manual reassignment, and return navigation retains the selected tab.

**Latest accessory interaction supersedes the earlier quick editor:** show only the three supplied accessory images. Remove accessory titles, status captions and Quick selection panel entirely. Clicking an icon toggles directly between full-color included and gray not included; the next click toggles back. Preserve accessible button names and pressed states without visible text. Existing unknown extraction remains unconfirmed/gray until an employee toggles it; do not silently rewrite untouched unknown evidence as No. A deliberate toggle sets Yes/No with correction history in the future production implementation.

**Accessory artwork and quick correction:** use the user's supplied lug nut/center cap/centering ring artwork. Provide Quick selection for per-set corrections, including With set, Not with set and Unknown. Included accessories are full color; absent/unconfirmed accessories are gray. Preserve the explicit difference between absence and unknown rather than reducing both to false. This manual correction must remain available after extraction or later changes; production persistence/version history is still governed by the existing correction requirements.

**Vehicle assignment interaction, latest refinement:** do not show an always-visible vehicle dropdown in set details. Display the assigned vehicle with a small quiet Reassign action underneath; unassigned sets offer Assign Vehicle. Both open a picker listing only vehicles under the current customer's profile, with a customer-only/no-vehicle choice. Cancel leaves assignment unchanged. Assignment confirmation happens within the picker, so the redundant generic Save changes button is removed. Reassignment preserves the same set, period and notes; update grouped profile displays and unassigned-set counts consistently.

Set-detail refinement: replace the accessories sentence with individual lug nut, center cap and centering ring icons while preserving explicit Yes/No/Unknown states and accessible labels. Provide a dedicated stored-set Notes section, with a notes shortcut beside In storage and a small indicator when that specific set has notes. No customer-wide or global notification is implied. Replace the confusing demonstration label Preview correction with Save changes for the vehicle-assignment action; standalone sample feedback must still disclose that it does not save a live record.

**Visual foundation priority, reaffirmed by user:** match the approved reference's spacing, colors, font appearance/sizes, sidebar, page header, cards and icons before progressing to additional workflows. A generic functional mockup is insufficient for screen approval. Verify visual similarity separately from interaction correctness; do not equate passing tests with approved design. Dashboard added to the standalone sample for a direct comparison; profile changes retain this same visual language.

Customer display name is the page heading; do not repeat it as a heading inside the card. Top-right icon/count indicators replace the summary sentence: total stored sets, vehicles, and stored sets without vehicle information. Icons need accessible names and short captions so meaning does not rely on hover alone.

Browser-comment refinement: place Stored sets and Vehicles in the upper page-level tab row, replacing demonstration-screen shortcuts. Tire descriptions are clickable links into the specific set details; remove Open set buttons and standalone Set details/Updated RO/Submission selection tabs from the customer profile. Revised-paperwork and set-selection workflows remain requirements in their relevant contexts, not profile navigation.

Direct user refinement: Customer profile defaults to **Stored sets**, showing all the customer's currently stored sets in one list. A separate **Vehicles** tab has expandable vehicle sections showing associated sets. The preview places unassigned sets in a **No vehicle information** expandable group as well as the combined stored-set list; placement can be refined after trying it.

**Settings** is a Rollcall-level utility entry, separate from customer profiles. Location visibility applies to every customer across the application, not per-customer settings. The standalone preview simulates this globally within its sample only; real shared persistence remains future implementation.

Direct user requirement: technical set/customer IDs must never appear as customer-facing labels, secondary text, feedback or accessible names. Remove the sample RC-number labels. Internal database IDs remain technical implementation details. Staff distinguish sets with descriptions, sizes, vehicle associations and linked RO/history; an ambiguous choice must expose meaningful descriptive differences rather than invented ID codes.

The handoff authorizes extension of the existing app and delegates technical choices. Rebuilding would discard proven archival/correction behavior and increase migration risk; a second parallel inventory app would split records. Extend in place with additive versioned migrations and separate source documents, RO transactions and inventory events. These are proposed implementation choices, not a new request for the user to choose a platform.

Legacy $99.99/custom-rate/account/import requirements remain recorded in MASTER_PLAN.md. They are inherited scope for review, not automatic additions to Rollcall. No payment ledger is planned. No runtime tests have been performed in this planning batch.
