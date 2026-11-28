# Tasks: plan the Rollcall rewrite

**Goal:** The master checklist for the whole rewrite: settle the shared decisions, then specify
and build seven OpenSpec changes one at a time until Rollcall is ready for staff. This planning
change holds no application code; each build change has its own detailed tasks.md.

**Approach:** Work through design.md's roadmap: finish setup, record v1 lessons, confirm the
capability map, settle product questions in one bundled review, then spec and build each change
in order, archiving it before the next. Each follow-up change is written with the `openspec-propose` skill (or
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

- [x] 2.1 Write `openspec/changes/plan-rollcall-rewrite/v1-lessons.md` (two pages at most) covering:
  Protractor PDF layout and which labels hold which fields (from
  `legacy/backend/app/document_parser.py` and its tests); tire size
  formats (`225/55R17` ↔ `2255517`, `35x12.50R20` ↔ `35125020`); accessories as unknown/yes/no;
  the archive and version-checked save patterns in `legacy/backend/app/document_store.py`; the backup
  approach in `legacy/backend/backup_rollcall.py`; and what went wrong in v1 (scope growth, page
  count, planning sprawl, never-finished core workflow). Every claim cites the `legacy/` file it
  came from. Verify: owner reads it; each cited path exists.

## 3. Capability map

- [x] 3.1 Present the eight capabilities from proposal.md to the owner, with the pages each one
  owns (sign-in, dashboard, tire list/search, customer view with its tire sets, tire set form with
  PDF review, admin settings). Record any merge/split in proposal.md. Verify: owner confirms;
  `openspec validate plan-rollcall-rewrite` passes.

## 4. Product questions

- [x] 4.1 Add a "Product questions" section to design.md with a recommendation for each: tire set
  fields and units (tread depth in 32nds of an inch, per wheel position); whether a stored item is
  always a set of four or can be fewer/more (e.g. staggered sizes, a single spare); customer fields;
  vehicles as their own records or text on the set; what "remove" means for a set and for a
  customer (recommended: archive, never delete, history stays); dashboard stats and the
  "too long" threshold; search fields; which PDF fields pre-fill; storage location on/off. Verify:
  every item has a recommendation and states what it changes.
- [x] 4.2 Walk the owner through 4.1 in one message, most consequential first; record answers in
  design.md Decisions with source "Owner". Verify: no "confirm in Phase 2" entries remain in the
  Decisions table.

## 5. Spec and build, one change at a time (in order)

Each task is one full cycle (design.md, Phase 3): write the change (proposal, specs, design, tasks)
covering the Review focus items it owns; `openspec validate <name>` passes; owner reviews the spec;
build it test-first from its own tasks.md; owner signs off with its "What to try" list;
`openspec archive <name>`. Verify: the change appears under `openspec/changes/archive/` and its
specs under `openspec/specs/`. Do not start the next task until the previous one is archived.

- [x] 5.1 `add-platform-foundation`: Docker Compose (app + PostgreSQL), configuration, health check,
  database migrations, base page layout, vendored htmx, styling conventions, test setup.
- [x] 5.2 `add-ui-components`: page and component templates shown in a `/mockups` gallery with
  invented sample data, in two phases. **UI design discovery:** two or three distinct designs of
  one sample page (the tire set page); the owner picks one or has them adjusted or combined until
  happy. **Mock up the rest:** only then are the other five pages mocked up in that design and
  signed off one at a time. Later changes wire real data into these templates. Done 2026-11-27:
  archived as `archive/2026-11-27-add-ui-components`; spec in `openspec/specs/ui-components/`.
- [ ] 5.3 `add-accounts`: first-admin bootstrap, sign-in/out, sessions, admin user management
  (create with temporary password, reset, promote/demote, deactivate), last-admin protection.
- [ ] 5.4 `add-customers-and-tire-inventory`: customers as root records; tire sets under them;
  check in / check out with stays kept; list and search; version-checked saves; change history
  with staff name (fold in `audit-history`, or split into `add-audit-history` if the spec exceeds
  roughly ten requirements; record the choice in its proposal).
- [ ] 5.5 `add-pdf-prefill`: upload limits, PDF archive, suggested values, side-by-side review,
  customer suggestions by similar name, synthetic test PDFs, `samples/private/` for real ones.
- [ ] 5.6 `add-dashboard`: each stat with its exact counting rule, using check-in state and the
  current stay.
- [ ] 5.7 `add-operations`: host choice, HTTPS with a shop-trusted certificate, start after
  reboot, coordinated database + PDF backup, restore drill, install guide, full rehearsal before
  go-live.

## 6. Go-live check

- [ ] 6.1 Confirm every Decision in design.md and every Review focus item is covered by a
  requirement in `openspec/specs/`, and the names (customer, staff account, tire set, stay,
  checked in/out) are used the same way everywhere. Verify: `openspec validate --all` passes;
  owner gives the go-ahead for staff to start using Rollcall.

## Workflow follow-up

- Archive this planning change with `openspec archive plan-rollcall-rewrite --skip-specs` once 6.1
  is done.
