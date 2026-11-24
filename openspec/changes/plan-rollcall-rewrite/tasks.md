# Tasks: plan the Rollcall rewrite

**Goal:** Produce six reviewed, valid OpenSpec changes that fully specify the rewritten Rollcall,
ready to build in order. No application code is written in this change.

**Approach:** Work through design.md's roadmap: finish setup, record v1 lessons, confirm the
capability map, settle product questions in one bundled review, then write the follow-up changes
in build order. Each follow-up change is written with the `openspec-propose` skill (or
`openspec new change` + `openspec instructions <artifact>`) and must pass
`openspec validate <name>` before the owner reviews it.

**Source:** `proposal.md` and `design.md` in this folder; project constraints in
`openspec/config.yaml` (every spec must follow its rules, including the two-users-save scenario
and the history scenario).

**Review focus** (cases the specs must cover even though nobody has mentioned them; check each
when writing the owning change):

- Two people creating the first account on a fresh install at the same moment: exactly one becomes
  admin (`add-accounts`).
- Two staff toggling the same tire set in or out at the same moment: one wins, the other sees the
  current state; no duplicate or overlapping stay (`add-customers-and-tire-inventory`).
- Checking in a set that is already checked in, or out one already out: refused with a clear
  message (`add-customers-and-tire-inventory`).
- A PDF upload that is abandoned (form never saved): nothing changes in inventory or history; the
  stored PDF is not attached to any record (`add-pdf-prefill`).
- A deactivated staff member who is still signed in: their next action is refused and they are
  signed out (`add-accounts`).

## 1. Setup

- [x] 1.1 Create the `rewrite` branch and move v1 into `legacy/`. Verify: `git status` shows renames
  into `legacy/`; `git check-ignore legacy/backend/.venv` succeeds.
- [x] 1.2 Run `openspec init --tools claude`, write project constraints in `openspec/config.yaml`.
  Verify: `openspec validate plan-rollcall-rewrite` passes.
- [x] 1.3 Commit the setup on `rewrite` (`chore: move v1 to legacy/ and set up OpenSpec`). Verify:
  `git log -1 --stat` shows the renames, `openspec/` and `.gitignore`.

## 2. v1 lessons

- [ ] 2.1 Write `openspec/changes/plan-rollcall-rewrite/v1-lessons.md` (two pages at most) covering:
  Protractor PDF layout and which labels hold which fields (from
  `legacy/PROTRACTOR_INVOICE_PDF_HANDOFF.md` and `legacy/backend/app/document_parser.py`); tire size
  formats (`225/55R17` ↔ `2255517`, `35x12.50R20` ↔ `35125020`); accessories as unknown/yes/no;
  the archive and version-checked save patterns in `legacy/backend/app/document_store.py`; the backup
  approach in `legacy/backend/backup_rollcall.py`; and what went wrong in v1 (scope growth, page
  count, planning sprawl, never-finished core workflow). Every claim cites the `legacy/` file it
  came from. Verify: owner reads it; each cited path exists.

## 3. Capability map

- [ ] 3.1 Present the eight capabilities from proposal.md to the owner, with the pages each one
  owns (sign-in, dashboard, tire list/search, customer view with its tire sets, tire set form with
  PDF review, admin settings). Record any merge/split in proposal.md. Verify: owner confirms;
  `openspec validate plan-rollcall-rewrite` passes.

## 4. Product questions

- [ ] 4.1 Add a "Product questions" section to design.md with a recommendation for each: tire set
  fields and units (tread depth in 32nds of an inch, per wheel position); whether a stored item is
  always a set of four or can be fewer/more (e.g. staggered sizes, a single spare); customer fields;
  vehicles as their own records or text on the set; what "remove" means for a set and for a
  customer (recommended: archive, never delete, history stays); dashboard stats and the
  "too long" threshold; search fields; which PDF fields pre-fill; storage location on/off. Verify:
  every item has a recommendation and states what it changes.
- [ ] 4.2 Walk the owner through 4.1 in one message, most consequential first; record answers in
  design.md Decisions with source "Owner". Verify: no "confirm in Phase 2" entries remain in the
  Decisions table.

## 5. Follow-up changes (in build order)

Each task: create the change, write proposal, specs, design (when the schema says it is needed)
and tasks; cover the Review focus items it owns; run `openspec validate <name>`; get owner review.
Verify each with a passing validate and owner approval.

- [ ] 5.1 `add-platform-foundation`: Docker Compose (app + PostgreSQL), configuration, health check,
  database migrations, base page layout, vendored htmx, styling conventions, test setup.
- [ ] 5.2 `add-accounts`: first-admin bootstrap, sign-in/out, sessions, admin user management
  (create with temporary password, reset, promote/demote, deactivate), last-admin protection.
- [ ] 5.3 `add-customers-and-tire-inventory`: customers as root records; tire sets under them;
  check in / check out with stays kept; list and search; version-checked saves; change history
  with staff name (fold in `audit-history`, or split into `add-audit-history` if the spec exceeds
  roughly ten requirements; record the choice in its proposal).
- [ ] 5.4 `add-pdf-prefill`: upload limits, PDF archive, suggested values, side-by-side review,
  customer suggestions by similar name, synthetic test PDFs, `samples/private/` for real ones.
- [ ] 5.5 `add-dashboard`: each stat with its exact counting rule, using check-in state and the
  current stay.
- [ ] 5.6 `add-operations`: host choice, HTTPS with a shop-trusted certificate, start after
  reboot, coordinated database + PDF backup, restore drill, install guide, full rehearsal before
  go-live.

## 6. Final check

- [ ] 6.1 Cross-check the six changes together: every Decision in design.md and every Review
  focus item is covered by a requirement in some change; names (customer, staff account, tire set,
  stay, checked in/out) are used the same way everywhere. Verify: `openspec list` shows all six;
  `openspec validate --all` passes; owner gives final go-ahead to start building `add-platform-foundation`.

## Workflow follow-up

- Archive this planning change with `openspec archive plan-rollcall-rewrite --skip-specs` once 6.1
  is done.
- Then build the six changes in order with the `openspec-apply-change` skill, archiving each
  before starting the next (design.md, Phase 4).
