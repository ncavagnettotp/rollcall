# Rollcall next-chat continuation

Saved November 20, 2026. This is the current handoff for the installed Rollcall rehearsal.

## Current status and next step

The edited [desktop and LAN design plan](desktop-lan-design-plan.md) governs delivery. The Electron 0.1.0 rehearsal client is installed on the development PC and opens from **Start → Rollcall**. The latest window was opened after the sidebar sizing fix. Electron loads the live React build from `https://localhost:8443`; updating `frontend/dist` and opening a fresh window picks up UI changes. Use [the proof record](desktop-lan-proof.md) for the server and installer details.

### Implemented and verified in this session

- **Dashboard** uses the approved branding, sidebar, metric cards and upload area. Choose or drop a PDF on Dashboard, then click **Upload PDF**. A successful upload opens that document’s review. The line “Clear submissions update inventory. Ambiguous details need attention.” is labeled **Planned workflow** because the inventory automation is pending.
- **Corrections** opens directly to its review queue from the sidebar. Upload controls belong on Dashboard. An opened review displays the archived original on the left and the review or editor on the right. Compact **Review** and **PDF** tabs preserve the draft, PDF page and zoom. The viewer supports arrows, pointer-anchored wheel zoom, drag-to-pan and **Fit**. **Save review** updates the document and review history. The rehearsal database has a two-page entry named `Rollcall synthetic correction.pdf` for testing.
- **Sidebar** folds out in place from the compact icon rail. The Dashboard is the sizing reference for every tab. The latest fix reserves scrollbar space and disables the nav-button press scale so the labels and icons stay the same size when switching pages. **Ctrl + wheel** over the sidebar scales the whole interface from 100% to 300%.
- **Backups** bundle a PostgreSQL snapshot and the original PDFs it references, with checksum verification and a verified isolated restore. The shop’s nightly schedule, alerts and off-site rotation need an encrypted destination and backup owner. See [backup and restore](backup-and-restore.md).

Verification at this save point: 12 frontend tests, HeroUI audit and production build passed. Live browser checks covered the Dashboard upload, Corrections queue and two-page PDF, navigation between compact panes, and save/reopen. The final sidebar check compared selected label font size, icon dimensions and rail width across all five tabs at 1005, 1010, 1255, 1260 and 1280 pixels, including the icon during mouse press. The updated installed window opened successfully.

### Resume here

1. Start with the latest sidebar acceptance check. At the same window width, click Dashboard, Inventory, Insights, Corrections and Settings. The highlight moves while the label and icon sizes stay fixed. Include a short **What to test** checklist whenever posting a build.
2. The local server uses a disposable PostgreSQL database on loopback port 55439 and a private synthetic archive. The configuration is `%ProgramData%\Rollcall\server.json`. The temporary localhost certificate was approved and trusted for the current Windows user. The HTTPS server and database are manually started. Check readiness at `https://localhost:8443/api/health/db` before launching. Rehearsal runtime files are in the ignored `tmp/desktop-proof/local-rehearsal` directory. Keep its private key and credentials out of handoffs.
3. **Step B remains open** for the laptop launch over LAN using normal certificate trust, the planned hostname and scoped firewall rules. The current server binds loopback and uses synthetic data while staff authentication is pending. The 0.1.0 rehearsal ZIP is unsigned and was tested locally.
4. **Step C is the next product milestone.** Connect the approved Inventory views to PostgreSQL-backed list, search and set/profile reads with synthetic records. Inventory, Insights and Settings currently show availability messages. Automatic inventory actions and the shop rehearsal are later plan steps.

The user authorized moving toward the real build and confirmed Electron is the desktop framework they had in mind. Use an installed Windows client with its own Rollcall window and connect it to one shared FastAPI server, PostgreSQL database, and PDF archive on the shop LAN. Reuse the React frontend. The first milestone is a desktop client searching shared inventory from a second workstation. Verify the existing PDF baseline before changing intake behavior.

Inventory, Corrections, and Dashboard mobile layouts are accepted and included in the main standalone mockup. The Dashboard layout was approved November 18, 2026. The selected Insights report is integrated in the main mockup. Storage activity shows totals, Daily averages shows stored and overdue sets, and Today stays fixed when the sample date range changes. Settings scope is confirmed as one shop-wide control, **Show storage locations**.

Main: docs/rollcall/interaction-preview.html (starts on Riley Bennett's sample customer profile). Select Inventory to open the shop-wide list based on references/inventory.png. The list uses sample data and includes search, status tabs, a set-type filter, customer and set links, and the Settings location toggle.
Standalone Dashboard review entry: docs/rollcall/dashboard-mobile-concept.html (starts on Dashboard).

The visual acceptance applied to the mockup. The subsequent desktop plan governs implementation and the conditions for deployment.

## Workflow decisions confirmed November 20, 2026

- File a first or second active set for a known vehicle unless the PDF explicitly identifies a replacement. If intake would add a third active set, ask which existing set is coming out before applying the change. This supersedes the earlier automatic-swap rule for one existing set.
- Use the latest submitted PDF for the same work order as the source for updated information. Preserve earlier PDFs and revise the same transaction without applying its inventory action again.
- Remove takes the set out of active inventory and keeps the event in vehicle history, or customer history if no vehicle is assigned. Renewal extends the existing set's storage period under the saved renewal rules and records the updated renewal information.

## Preserve accepted behavior

For PDF intake, an identified customer with no clear vehicle match can receive an unassigned set that staff link later. A same-work-order revision that would change a later swap, renewal, or removal requires staff review before it is applied. Both decisions were approved by the user.

- Current orange/off-grey/white/charcoal colors, typography and icon artwork; real HeroUI for new controls.
- Inventory underline tabs: shelf #ebedf4, guideline #b6bccb 2px, orange #ff8900 selector 4px. Larger labels, adjacent tabs, edge fades, smooth hover-local wheel scrolling and phone swiping.
- Sidebar stays left with full labels wide and a 64px icon rail at compact widths. The live app’s menu button folds out the sidebar in place. Keep Dashboard-sized labels and icons across tabs.
- Compact Inventory retains vehicle information and fixed tire-left/wheel-right slots. Missing item leaves slot empty. Dates may hide in lists; descriptions fade before icons. Full details remain available.
- Corrections: PDF left/review right desktop; <=700px Review details / Original PDF switch preserves draft/page/zoom. One PDF page at a time with arrow slide animation. Pointer-anchored wheel zoom, click/touch drag both axes, Fit reset, independent pane scrolling.
- Supplied PDF rendered locally: Julian Ocampo, RO 246408. Queue/actions are illustrative. Keep documents local.
- Do not restore the old 576x384 minimum canvas on accepted phone layouts.

## Accepted Dashboard layout

Desktop >1000px keeps current geometry. Compact order: total inventory, paired Due soon/Overdue, upload, status chart. Shared compact sidebar/menu. Phone upload says Upload a document / Choose PDF. The mockup uses illustrative counts and a demo upload. The live Dashboard shows blank inventory counts and uploads real PDFs to the rehearsal archive.

## Source and verification

Shared bundle source: docs/rollcall/preview-tabs.jsx, importing inventory-mobile.jsx and corrections-preview.jsx. Shared navigation in inventory-mobile.jsx enables the compact Dashboard menu in both entries. Only the standalone Dashboard preview auto-opens Dashboard. Main starts Inventory.
Styles: inventory-mobile.css, corrections-mobile.css, underline-tabs.css; shared Dashboard styles dashboard-mobile-concept.css. Scope changes instead of disturbing historical preview.css overrides. Historical alternatives remain preserved.
Build from root: node work/build-rollcall-preview-tabs.cjs (writes docs/rollcall/assets/preview-tabs.js).

Real Edge verification scripts:
- node work/verify-dashboard-mobile-concept.cjs (desktop unchanged, main startup, 320/390/576/800px fit, navigation, upload demo)
- node work/verify-inventory-mobile.cjs
- node work/verify-corrections-mobile-concept.cjs (tests accepted main layout despite name)

Existing Playwright scripts use installed Edge; sandbox escalation is needed for browser launch. Wait for .screen-leaving and .workspace[data-entering] transitions to finish before geometry assertions. Transient cloned outgoing pages can appear to overflow. 

Screenshots: output/rollcall-visual/dashboard-concept-phone.png and dashboard-concept-{320,390,576,800,desktop}.png.
Detailed evidence: docs/rollcall/verification.md. Planning index: docs/rollcall/README.md. Latest decisions: docs/rollcall/screens-and-operations.md. Business scope: docs/rollcall/specification.md and original ROLLCALL_HANDOFF.md (older status paragraphs are historical).

User prefers concrete previews and autonomous progress with few repetitive questions. Preserve desktop appearance while adding mobile behavior. Keep unapproved concepts separate. Give absolute local Markdown links for previews. User requested a progress save for another chat; do not create a new chat without an explicit request.
