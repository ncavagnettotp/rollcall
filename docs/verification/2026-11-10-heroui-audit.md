# HeroUI conversion verification — November 10, 2026

User requested immediate foundational conversion. @heroui/react and @heroui/styles are pinned at 3.2.7 in package.json and pnpm-lock.yaml. React19/Tailwind4 maintained. No backend, schema, or business workflow change.

## Source and dependency audit

| File | Actual HeroUI components |
|---|---|
| src/App.jsx | Alert, Button, Card, Description, SearchField |
| src/DocumentReview.jsx | Alert, Button, Card, Description, Disclosure, Fieldset, Form, Input, Label, Link, ListBox, Select, TextArea, TextField |
| src/main.jsx | Application composition only |
| src/styles.css | Tailwind import followed by HeroUI styles; layout, category colors, documented theme tokens |
| src/DocumentReview.css | Layout/prose styling; legacy widget CSS removed |
| index.html | Dark class and data-theme enabled |

No raw standard widget JSX or custom-lookalike replacements remain. File upload is the actual HeroUI Input with type=file; confirmed against installed primitive implementation. Native semantic structure, headings, evidence definition lists, lists, and domain SVGs remain. Theme-token values distinguish field borders/backgrounds without replacing library controls.

Automated guard: scripts/audit-ui-library.mjs parses production JS/JSX/TS/TSX, checks actual import provenance, exact package pins and style order, and rejects native standard widgets, recognized lookalikes, role-based handwritten controls and raw click targets. Self-test fixtures prove rejection/acceptance paths. npm run audit:ui exposes it; npm run build invokes it before Vite. The guard is a source-pattern check, not a proof against every possible dynamic/custom widget, so independent review remains required.

## Verification results

- UI audit and self-test: PASS.
- Final frontend suite with real HeroUI (no library mocks): **9 tests passed**, 10.97s.
- Tests use real Select popovers/keyboard and verify saved selected action, corrections/evidence, duplicate/reopen, validation, conflict/local-edit retention and return navigation.
- Production build through normal pnpm run build: **PASS**, including mandatory audit, 1,783 modules.
- Real Edge Stage2 flow: **PASS**, real upload/duplicate reopening, actual accessory popover No→Yes selection, original link, save/reload/reopen, mobile fit, no page errors.
- Desktop/mobile feedback viewport regression: **PASS** at1280 and390px after opening archived reviews and saving.
- Dashboard: **PASS**, live API/PostgreSQL, four honest placeholders, disabled search, actual HeroUI Card/Button DOM slots/classes, mobile fit, simulated API failure and refresh recovery.
- Independent source review: no important correctness/compliance findings. Broadened automated audit beyond .jsx and fixed stale success feedback after later edits.
- Screenshots: output/playwright/heroui-dashboard-desktop.png, heroui-dashboard-mobile.png; customer review screenshots remain under ignored output/stage2-private.

## Findings resolved and limits

Taller HeroUI success alerts initially overflowed the visible viewport; existing browser assertions failed before nearest-scroll feedback handling and passed afterward. A regression test also failed for stale saved success after subsequent field edits; success now clears when fields change.

Build emits two non-failing CSS optimization warnings for upstream @property declarations --scroll-shadow-start-fade/end-fade. Browser checks and build succeed; warnings remain visible, not suppressed. Do not treat this as an untested guarantee for every HeroUI component; only existing app widgets/workflows were exercised.

Source checkpoint: checkpoints/heroui-foundation-2026-11-10.zip and SHA256 manifest; excludes customer documents, archive metadata/data, secrets, dependencies and private screenshots. Stage1/2 acceptance remains recorded; Stage3 is ready for planning.
