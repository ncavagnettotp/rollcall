# Stage 1 continuation — October 30, 2026

User authorized continuing the current stage and using the project-manager structure. Scope: close foundation gaps; do not start invoice ingestion or later workflows.

Sources: MASTER_PLAN.md, PROJECT_MANAGEMENT.md, README.md, VERIFICATION.md, and selected dark dashboard mockup.

## Tasks and ownership

- [x] FND-01: Assess source, runtime, database/service state, and previous evidence. Manager and database-assessment agent; read-only inspection first. Never print secrets.
- [x] FND-02: Update frontend/src/App.jsx, styles.css, App.test.jsx to the selected dark dashboard. UI agent owns these files. Retain real health requests, refresh/recovery, four null counts, and a single empty record area. Upload/search remain explicitly disabled future functions. Keep backend Stored API label compatible; display In Storage.
- [x] FND-03: Run backend suite and live DB probe if configured. Verify persistence/recovery only against an identified project-owned database; never stop an unrelated/shared service. If unavailable, record exact prerequisite rather than claiming readiness.
- [x] FND-04: Independently run frontend checks/build, browser desktop/mobile/failure checks, review implementation, record results, and create a source checkpoint.

## Verification contract

Frontend: run existing Vitest suite, with meaningful assertions covering selected category labels, null counts, unavailable future controls, and existing failure/refresh behavior. Build with Vite. Browser-check actual API proxy, disabled controls, empty state, narrow-width overflow, status refresh, and screenshot the new appearance.

Backend: existing pytest suite must pass; real PostgreSQL integration remains explicitly skipped unless configured and actually exercised. Persistence requires writing and reading the probe across an appropriate restart, not merely repeated SELECT 1.

Review checks: no fictional live counts or records; no enabled nonworking search/upload/filter controls; no lost API/database error states; no automatic startup; no later-stage schema/actions.

## Environment rulings and progress

- Initial inspection: this folder is not a Git repository. Use a dated source archive checkpoint rather than creating/committing repository history without an established repository. Archive excludes secrets, dependencies, caches, and itself.
- Delegation: UI edits are isolated by file ownership; database assessment is read-only. Manager owns evidence/management documents and browser verification scripts.
- Stage acceptance remains separate from the user's authorization to carry out this work. Complete concrete checks first, then report any outstanding acceptance prerequisites.
- FND-03 ruling: existing native PG18.6 service is automatic and potentially shared. Leave it unchanged. Verify its actual connection, then use a manually controlled isolated PG18.6 cluster to demonstrate restart persistence and readiness recovery. This does not prove configured-service restart or PG17/Compose behavior.
- FND-02 complete: 4 tests passed, build passed (29 modules), browser live proxy/status checks and simulated request failure/recovery passed at desktop/mobile widths. Screenshots refreshed after final copy.
- Independent review: no important issues. Strengthened browser card-count check and reran browser acceptance successfully.
- FND-04 evidence/review prepared; source checkpoint and user acceptance tracked in PROJECT_MANAGEMENT.md.
