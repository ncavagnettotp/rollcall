# Foundation Dashboard Implementation Plan

> For agentic workers: implement the bounded frontend assignment; do not advance product stages.

**Goal:** Apply the selected dark dashboard while preserving truthful Stage 1 behavior.

**Architecture:** Keep the existing health/dashboard requests and refresh state. Render a stable four-card shell using the existing API labels as lookup keys, with `Stored` presented as `In Storage`.

**Tech Stack:** React, Tailwind CSS, Vite, Vitest, Testing Library.

**Spec:** MASTER_PLAN.md, Stage 1 and selected dashboard direction.

## Constraints and review focus

- No real/fake storage records, uploads, search, or business counts added.
- Future controls are visibly unavailable and programmatically disabled.
- API/database errors and refresh recovery remain truthful.
- Category cards remain visible during loading/failure with em dashes.
- Desktop uses a spacious 2 × 2 grid; narrow screens stack without overflow.

## Task 1 — Dashboard shell

Files: frontend/src/App.jsx, frontend/src/styles.css, frontend/src/App.test.jsx.

- [x] Add a failing behavior check for disabled future controls, the single records placeholder, and stable categories during API failure.
- [x] Run Vitest and confirm the intended failures: two failed, two passed before implementation.
- [x] Implement the dark shell, subtle category tints, icons, and truthful placeholder content. Keep refresh requests and API contract unchanged.
- [x] Run the complete frontend test suite and production build: four tests passed; Vite built 29 modules.
- [x] Report evidence and changed files to the coordinator for browser verification and independent review.

No backend, dependency, service, or deployment changes belong to this task.
