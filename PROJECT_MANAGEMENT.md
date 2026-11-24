# Tire Pros — Project Management

> Current work (November 11, 2026): [Rollcall planning index](docs/rollcall/README.md), governed by [ROLLCALL_HANDOFF.md](ROLLCALL_HANDOFF.md). Planning/specification only; no new product implementation. The older Stage 3 ready-for-planning board below is historical and does not override the Rollcall workflow/visual decisions. Use the expandable 31-step checklist for current progress.

Structure adopted for Stage 1 continuation on October 30, 2026, following the user's instruction to proceed. Specialist assignments run during active work; this document does not start background services.

## Project references

- MASTER_PLAN.md defines product scope, business rules, seven delivery stages, and acceptance criteria.
- This file defines responsibilities, task tracking, dependencies, risks, and handoffs.
- README.md holds local setup instructions. VERIFICATION.md holds dated verification evidence.
- PROJECT_SKILLS.md maps installed and existing skills to manager/specialist assignments and records runtime prerequisites.
- Current stage: Stages 1 and 2 accepted. HeroUI foundational conversion completed and verified. Stage 3 is ready for planning; no later business-storage implementation has started.

## Team and accountability

| Role | Responsibilities | Boundary |
|---|---|---|
| Product owner — user | Business decisions, screen feedback, representative invoices, shop acceptance | Approves stage completion and material scope changes |
| AI project manager — coordinating agent in this chat | Maintain roadmap/board, assess dependencies and risks, prepare assignments, delegate, integrate results, report evidence and next steps | Cannot self-approve business decisions or treat a specialist's completion claim as verified acceptance |
| UI specialist — delegated when needed | React/Tailwind views, selected dark design, accessibility, responsive layout, frontend behavior | Preserve business rules and agreed API contracts |
| Backend/data specialist — delegated when needed | FastAPI, PostgreSQL, PDF extraction, matching, transactions, migrations, integrity | No silent inference, destructive data changes, or automatic renewal |
| QA/release specialist — delegated when needed | Independent review, regression checks, real database/invoice verification, deployment and restore evidence | Report untested conditions explicitly; do not approve their own implementation |

Start with the manager plus UI and backend specialists. Use a separate QA assignment at meaningful review gates. These are reusable roles, not employees continuously running in the background. Work is delegated during active runs; saved tasks and handoffs preserve continuity.

The current session supports four concurrent agents total, including the coordinator. Do not assume unlimited workers or promise parallelism when dependencies require sequential work.

## Manager's working cycle

1. Read the roadmap, current board, latest verification, and relevant code.
2. Identify the current stage's next unblocked deliverable and its acceptance evidence.
3. Make a bounded assignment: task ID, goal, inputs, allowed files, dependencies, deliverable, and checks.
4. Delegate independent work only when useful. Avoid concurrent edits to shared files; agree contracts first.
5. Review results and integrate changes. Assign independent review where warranted.
   After every major adjustment, perform the mandatory HeroUI source/dependency audit in MASTER_PLAN.md and report its result in VERIFICATION.md. Inspect changed controls, identify legacy controls separately, and flag proposed custom replacements before adoption.
6. Record verification commands/results and unresolved issues. Update the board and risks.
7. Report what changed, what was verified, what remains, and the next task.
8. Request stage acceptance only after the concrete result and evidence are ready. Do not advance stages merely because a mockup was liked.

Routine implementation choices within an authorized stage belong to the manager. Changes to business rules, shop deployment, or scope return to the product owner. Existing stage-acceptance requirements in MASTER_PLAN.md continue to apply.

## Task workflow

Statuses: Backlog → Ready → In Progress → Review → Awaiting Acceptance → Done. Use Blocked with a specific dependency and next action when progress cannot continue.

Each task records:

- ID, stage, title, owner, status, and priority.
- Dependencies and inputs; relevant files and permitted edit scope.
- Observable acceptance criteria and required verification.
- Evidence/result, blockers, and next action.

Done means implemented where applicable, checked against acceptance criteria, reviewed, documented, and checkpointed. Stage completion additionally needs user acceptance. Administrative tasks may finish without tests; operational behavior requires real evidence appropriate to its risks.

## Current board — October 30, 2026

UI, database-assessment, and independent-review assignments completed this work batch. No permanent background agents were created.

| ID | Stage | Task | Owner role | Status | Dependency / acceptance |
|---|---|---|---|---|---|
| PM-01 | Planning | Review team structure and consolidated scope | Product owner + manager | Done | User authorized manager-led continuation |
| FND-01 | 1 | Reassess current code, environment, and historical verification | Manager / QA | Done | Native PG18.6 configured; no Docker; no Git repository in this folder |
| FND-02 | 1 | Implement selected dark dashboard shell | UI | Done | Four frontend tests, build, desktop/mobile browser checks and independent review passed |
| FND-03 | 1 | Verify real PostgreSQL, persistence, and recovery | Backend / QA | Done — native test scope | Configured database connectivity plus isolated PG18 restart/persistence/recovery passed; shared service untouched; Compose untested |
| FND-04 | 1 | Review foundation and prepare stage acceptance | Manager / QA | Done | User explicitly accepted Stage 1; evidence and source checkpoint preserved |
| PDF-01 | 2 | Inspect representative Protractor PDFs | Manager / backend | Done | Eight PDFs / 15 pages reviewed November 10; user clarified dates, retrievals, authorizations/final invoice precedence, compound swap, and accessories; findings in docs/verification/2026-11-10-protractor-sample-review.md |
| PDF-02 | 2 | Upload/archive/extract/review without storage-state changes | Backend + UI | Done | Real eight-sample API acceptance; immutable original/extraction, corrections/history, duplicates, archived PDFs, revision conflicts |
| PDF-03 | 2 | Integration, restart durability, and independent review | Manager / QA | Done | 23 backend tests, 9 frontend tests/build, real browser flow and database restart review/original durability; no important review issues |
| PDF-04 | 2 | Accept working upload/review stage | Product owner | Done | User confirmed all Stage 2 checks work; local preview 5174; results in VERIFICATION.md; source checkpoint checkpoints/stage2-2026-11-10.zip |
| DATA-01 | 3 | Deliver persistent records, dates, rates, details, and history | Backend + UI | Ready for planning | Stage 2 accepted; MASTER_PLAN Stage 3 criteria |
| MATCH-01 | 4 | Deliver VIN/set proposals with provenance and uncertainty | Backend | Backlog | Stage 3 accepted; MASTER_PLAN Stage 4 criteria |
| ACT-01 | 5 | Deliver confirmed storage actions and audit trail | Backend + UI | Backlog | Stage 4 accepted; atomicity, duplicates, concurrency, and action checks |
| DASH-01 | 6 | Deliver real counts, category filters, and universal search | UI + backend | Backlog | Stage 5 accepted and date/category decisions settled |
| REL-01 | 7 | Deliver staff accounts, import, shop hosting, and recovery | Backend + QA | Backlog | Stage 6 accepted; joint database/PDF restore and shop acceptance |

Expand future-stage summary tasks into small actionable tickets when that stage is ready. Do not assign an entire future subsystem to an unattended worker before its inputs and interfaces are established.

## Dependencies and risk register

| ID | Risk / dependency | Early action | Owner |
|---|---|---|---|
| R-01 | Historical verification does not establish current live DB operation | Recheck environment and run real connectivity/persistence/recovery checks | Manager / QA |
| R-02 | Protractor formats or sparse descriptions undermine extraction/matching | Obtain real swap, purchase/takeoff, renewal/exception samples before parser design | Product owner / backend |
| R-03 | Timer/date precedence resolved November 10 | Final invoice supersedes authorization and updates the same event/timer; preserve history and prevent duplicate swaps. Earlier fallback: work-order date, then visible current shop date | Backend |
| R-04 | Duplicate confirmation or concurrent edits corrupt set state | Design uniqueness, transactions, and version checks before operational actions | Backend |
| R-05 | Search/count expectations remain partly undefined | Settle due-soon boundaries, Needs Attention unit, and history scope before Stage 6 | Manager / product owner |
| R-06 | Backups restore records but lose invoice files | Plan and demonstrate a coordinated database/PDF backup and restore | Backend / QA |
| R-07 | Parallel agents overwrite work or diverge on interfaces | Give bounded file ownership and shared contracts; integrate sequentially | Manager |
| R-08 | Agent context is lost between runs | Save board status, decisions, evidence, and next action after work | Manager |
| R-09 | Staff identity comes too late for meaningful audit history | Keep early data developmental; require attribution before real operational edits | Manager / backend |

## Specialist handoff template

Task ID and goal:

Inputs and decisions already made:

Dependencies and shared interface:

Allowed files / exclusions:

Deliverable and acceptance criteria:

Required checks:

Return: changed files, checks actually run, results, unresolved issues, and integration notes. Do not claim unrun tests passed. Do not expand scope or create additional agents without the manager's assignment allowing it.

## Reporting and continuity

November 11 rule update: early storage renewal extends the existing due date by six calendar months, starting at that due date rather than early invoice/payment date. Keep document date separately. Missing existing due date requires review. Same-day/overdue renewal behavior remains a business clarification for the period/action implementation. No runtime date logic changed in the current document-review stage.

November 11 visual update completed at user request: existing dashboard/review screens now use native HeroUI dark theme, Typography, card hierarchy, status chips, separators and secondary field variants. Removed legacy root styling overrides; no backend change. UI audit,9tests,build,real desktop/mobile behavior and independent review passed. Evidence: docs/verification/2026-11-11-heroui-visual.md. Checkpoint: checkpoints/heroui-visual-2026-11-11.zip. Stage3 remains ready for planning.

Frontend foundation completed: user requested immediate HeroUI conversion. React/styles3.2.7 are pinned, existing standard controls migrated, competing widget CSS removed, dark theme enabled. Automatic JSX/import audit added and wired into builds; real-component tests/browser checks and independent review verify behavior. Save-alert visibility regression fixed and checked on desktop/mobile. Keep function-first priority and defer broad redesign. Source-only checkpoint: checkpoints/heroui-foundation-2026-11-10.zip. See MASTER_PLAN.md and VERIFICATION.md.

Interaction correction after user review: saved-review feedback was off-screen and archived-item opening did not scroll to the loaded review. Fixed with inline save feedback, focus/scroll navigation, and dashboard Review uploaded documents entry. Stage 2 subsequently accepted by the user; regression tests/build and real browser viewport checks passed. Updated checkpoint: `checkpoints/stage2-feedback-2026-11-10.zip`.

November 10 handoff: Stage 2 implemented and verified. Applied explicit document-only migration; uploaded eight supplied samples into development archive; saved test review metadata without any business storage actions. Current checks: 23 backend tests including isolated real PG document integration, 9 frontend tests/build, browser real upload/save/reopen/duplicate/accessories/mobile checks, and original/review persistence through isolated DB restart. Stage 2 is accepted by the user. Existing machine-wide PostgreSQL service untouched. Manual frontend/API preview uses 5174/8000. Source-only checkpoint: `checkpoints/stage2-2026-11-10.zip`; customer PDFs/data/private screenshots excluded. Earlier Stage 1 handoff below is historical.

Latest handoff: dashboard shell implemented and verified; 4 frontend tests/build passed, configured database suite 7 passed, isolated restart suite 7 passed. Independent review found no important issues. See VERIFICATION.md and docs/stage-1-execution.md. Stage 1 explicitly accepted by user. Next: collect representative PDFs and check-in-date guidance for Stage 2 analysis; no Stage 2 implementation yet. Source checkpoint: `checkpoints/stage1-2026-10-30.zip` with SHA256 manifest. No Git history was created. Full isolated-cluster data and all .env secrets are excluded from the checkpoint.

After a meaningful work batch, give a short update: current stage, completed tasks, evidence, blockers/decisions, and next action. Avoid invented completion percentages or delivery dates without a basis.

At session end, persist the same facts here and in VERIFICATION.md where appropriate. A later session must reload the documents and check actual state rather than assume an earlier agent remains active.

This structure coordinates work while Codex is running. Unattended scheduled work would be a separate explicit setup with its own scope and runtime requirements; this document does not enable it.
