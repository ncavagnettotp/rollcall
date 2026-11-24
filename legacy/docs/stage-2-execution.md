# Stage 2 execution record — November 10, 2026

Spec: docs/stage-2-design.md; business authority MASTER_PLAN.md and sample clarification report. User requested Stage 2 after completing sample questions; existing manager-led execution authorization applies.

## Bounded tasks

- [x] Backend: explicit documents schema migration, local original archive, digital text extraction, raw upload/list/get/PDF/PATCH routes, revision history and validation. Own backend only. Test parser against synthetic edge cases and all eight real samples; isolate API test data. No business tables/actions.
- [x] Frontend: dedicated upload/review view, simple editable fields, source evidence/warnings, expandable accessory selectors, save/reopen/duplicate/conflict/error handling. Own frontend only. Update foundation tests for enabled upload and disabled search; build.
- [x] Integration: inspect migration, apply explicitly to development DB, start manual local servers; real browser upload/edit/save/reopen/original/duplicate and narrow-layout checks. Coordinator owns work scripts, docs, evidence. Validate error cases and durable reload independently of agent test claims.
- [x] Independent review: fresh read-only specialist examines final modules; fix important findings with regression checks; rerun affected suites.
- [ ] Delivery: record evidence/limitations and source-only archive excluding source/customer PDFs, extracted data, environment secrets, database files, dependencies, and private screenshots. Request Stage 2 acceptance only after concrete working result.

## Rulings

- Reuse current checkout; no Git repository was established. Continue dated source archives rather than creating history implicitly.
- Raw PDF request body avoids a multipart dependency. Frontend supplies encoded filename header; backend treats filename as display-only, never a filesystem path.
- PostgreSQL metadata plus filesystem originals satisfies local shared persistence. Schema is explicitly applied; no app-startup mutation.
- Stage 2 suggestions are preliminary extraction, not VIN-history matching. Uploaded documents and saved reviews never execute storage actions.
- Pure-Python pypdf 6.21.4 installed in project virtual environment. No OCR, external model calls, or cloud transmission.
- Related authorization/invoice originals remain separate; shared work-order warning is sufficient here. The final-invoice precedence rule will be applied when later stages implement actual period/event linking.

## Evidence

23 backend tests passed against isolated real PostgreSQL; 9 frontend tests and production build passed. All 8 PDFs passed real API acceptance, original-byte and duplicate checks. Browser upload/save/reopen/accessories/mobile checks passed. Original PDF and corrected review survived real isolated database restart. Independent review found no important issues. See VERIFICATION.md for commands, artifacts, and limits. Delivery checkpoint/user acceptance remain tracked on project board.

Rulings/fixes: corrected stale physical-check-in warning; limited contacts to customer header; retained wrapped customer requests; supported common storage heading variants; added explicit accessory select accessible names after browser checks exposed ambiguous nested labels. User's final-invoice precedence takes priority over an earlier broad conflicting-date sentence; same-priority conflicts still warn. Pinned tzdata for fresh Windows installs.
