# HeroUI visual refresh — November 11, 2026

User requested the existing visuals match HeroUI itself after the component migration. Scope: dashboard and document upload/review styling and library composition only. Preserve all accepted workflows, labels, date/data rules, corrections, archive navigation, and visible save/error feedback.

Direction: native HeroUI dark theme, consistent surfaces/spacing/type hierarchy, library button/field variants, semantic chips/status treatment, clear card sections and archive entries. Retain spacious two-column desktop storage categories and the selected subtle green/amber/red/slate meaning. Narrow layout must remain readable. Avoid extra dashboard density, fictitious records/counts, nonfunctional navigation, new business logic or a competing custom component system.

Use actual HeroUI components for library-covered widgets. Keep CSS for domain layout and semantic category color treatment; remove legacy hardcoded widget/theme overrides. Standard fields must remain visibly editable using appropriate library variants, rather than blending into card surfaces.

Acceptance: source/import audit, real-component frontend tests and build, independent code/library review, desktop/mobile screenshot inspection, real upload/review/select/save/reopen and focus/feedback regression checks. Save a source checkpoint excluding customer data. Backend/schema untouched.

Completed: all listed checks passed. Details and screenshot paths: docs/verification/2026-11-11-heroui-visual.md. Existing workflows and labels preserved; no new backend functionality introduced.
