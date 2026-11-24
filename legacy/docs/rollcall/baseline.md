# Rollcall baseline and preservation decisions

Read-only source inspection and reference preservation, November 11, 2026. No claim of current runtime verification.

| Area | Preserve / replace / add | Evidence and implication |
|---|---|---|
| Frameworks | Preserve | `frontend/package.json`: React 19.1.0, HeroUI React/styles 3.2.7. FastAPI/PostgreSQL in backend. |
| Originals | Preserve | `backend/app/document_store.py`: SHA-256 unique originals, advisory locks, atomic archive writes, immutable extracted JSON/text. |
| Review history | Preserve patterns | Document corrections and versions exist; business transaction audit and staff attribution must be added. |
| Upload API | Extend | `backend/app/documents.py`: bounded 10 MiB upload and archive/review. Existing review save does not change inventory. Add explicit processing result and RO transaction link. |
| Dates | Replace target behavior | `document_parser.py` currently falls back to current date and prioritizes date labels. Rollcall requires latest submitted source's printed date, blocking ambiguity. |
| Classification | Replace heuristics | Historical-season renewal and rotation-heading inference do not establish clear action evidence under Rollcall rules. |
| Identity | Extend | Parser has invoice and RO fields; related-source check uses original RO. Product must use corrected/canonical RO transaction links; keep legacy invoice evidence without mandatory invoice-number UI. |
| Inventory | Add | Current schema defines document metadata only; no durable customer/set/period/action domain. |
| Screens | Replace shell, preserve behavior | `App.jsx` dashboard/review local-state navigation, placeholder counts, disabled search. Add addressable screens and profiles; preserve accessible save/conflict feedback. |
| UI audit | Preserve and extend | `frontend/scripts/audit-ui-library.mjs`, build audit, actual HeroUI import inspection. Standard widgets must remain HeroUI in implementation. |
| Runtime | Unverified this batch | `backend/.venv/Scripts/python.exe` absent. Historical passing checks are retained; establish current interpreter/environment before implementation verification. |
| Hosting | Later local pilot | Loopback Vite development is not LAN production hosting. No changes to existing shared PostgreSQL service. |

## Preserved approved references

Copied from temporary attachment paths into `references/`: dashboard.png, inventory.png, insights.png, needs-attention.png. These are visual references with fictional values. Preview Documents becomes Insights. Bell/avatar artwork does not independently authorize notifications or an account workflow. Universal review wording is superseded by clear automatic actions.

All four references visually inspected during this batch: dark left navigation, orange selected item, light workspace, search/status tabs and set tables, upload dashboard, trend/aging Insights, and RO-based attention queue. Superseded details: Documents label, universal review text, multiple-set choice as attention, and attention as a set-chart slice. Optional unknown accessories alone do not require attention. No screenshot represents a running Rollcall inventory feature.

## Historical samples

`../verification/2026-11-10-protractor-sample-review.md` supplies prior sample observations, not current decision authority. Important retained scenarios: staggered sizes in one set; pickup with storage charges; unrelated tire purchase without intake; compound purchase/disposal/storage; missing vehicle; accessories and replacement notes. Old mandatory confirmation/date-fallback rules are superseded.

## Runtime baseline gate

Before claiming operational preservation: resolve Python environment without changing shared services; run applicable existing frontend/backend suites, UI audit/build and browser flows; establish isolated PostgreSQL fixture and migration/restore evidence. No secrets/customer archive need to be copied into documentation. Failures remain visible blockers, never historical passes relabeled as fresh results.
