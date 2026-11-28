# Tasks: add UI components and the mockup gallery

Spec: `specs/ui-components/spec.md`. Design: `design.md`. Each behavior is test-first: write the
test, see it fail, implement, see it pass. Sample data is always invented; nothing from
`samples/private/` is copied into code, samples or tests.

## 1. Gallery and component setup

- [x] 1.1 Write tests: `MOCKUPS` accepts `on`/`off`, defaults to off, rejects other values naming
  the setting (`tests/test_config.py`); with the gallery off, `/mockups` and
  `/mockups/pages/x/y` are 404 (`tests/test_mockups.py`). Then add the setting to
  `rollcall/config.py` and `.env.example` (commented). Verify: the tests pass.
- [x] 1.2 Write a test that rendering a page with a dataclass missing a shown value fails with an
  error naming it. Then switch the Jinja environment to `StrictUndefined`, fix the platform
  templates if needed, and move `macros.html` into `templates/components/` (field, button,
  table). Verify: the new test and all existing tests pass.
- [x] 1.3 Write the gallery tests from design.md decision 8 against a registry with one trivial
  test state. Then build `rollcall/mockups/` (registry, index, page and component routes, banner
  block in `base.html`, optional navigation and signed-in staff in the frame). Verify:
  `scripts/test.sh` passes; `http://localhost:8080/mockups` lists the trivial state with
  `MOCKUPS=on`.
- [x] 1.4 Write a test that `/mockups/sample-invoice.pdf` is served as `application/pdf` with
  `frame-ancestors 'self'` while pages keep `'none'`. Then write `scripts/make_sample_invoice.py`,
  commit its synthetic output and adjust `SecurityHeaders`. Verify: the tests pass; the PDF opens
  in a browser and shows an invented customer.

## 2. Phase 1: UI design discovery (the tire set page only)

- [x] 2.1 Define `rollcall/views/tire_set.py` (the tire set page's data) and its sample states in
  the registry: checked in; checked out with three past stays; new set (four empty tire rows);
  filled from a PDF with the invoice beside it; check-in step (RO, location, tread per tire);
  staggered set with five tires and very long text; form errors; save conflict; archived. Write
  the tests first (each state renders, the states link to each other). Verify: tests pass.
  Changed 2026-11-27 at the owner's request: no tread, DOT codes or tire rows (the staggered set
  no longer lists five tires).
- [x] 2.2 Build designs A, B and C of the tire set page (design.md decision 6), each with its own
  template, stylesheet and components, with the `?design=` switch in the banner. Verify:
  `scripts/test.sh` passes for every design and state; every state of every design checked by the
  builder in a browser at 360 px and desktop width with nothing scrolling sideways.
- [x] 2.3 Owner compares the designs in the gallery, on a desktop and a phone, then picks one,
  asks for changes or asks for a mix. Each revision is added as a new design next to the others.
  Repeat until the owner says they are happy with the look. Verify: owner names the approved
  design. Done 2026-11-25: design D (light look), see design.md decision 6.
- [x] 2.4 Write tests for the light/dark switch (design.md decision 9): `POST /theme` with
  `light`, `dark` or `device` sets or clears the cookie and answers 303 to `next`; other modes are
  refused; a `next` outside Rollcall leads to `/`; a page rendered with the cookie carries that
  `data-theme`, without it none; the switch is in the header of real and gallery pages with the
  current mode marked. Then build the switch, and give the approved design a dark mode built from
  colour tokens, its light look unchanged. Verify: tests pass; every state checked by the builder
  in a browser in light and dark at 360 px and desktop width; every text/background token pair
  measured within the spec's contrast limits.
- [x] 2.5 Owner reviews the dark mode in the gallery with the switch, on a desktop and a phone,
  asking for changes until happy. Verify: owner approves the dark mode. Done 2026-11-25: design D's
  dark mode approved as built in 2.4.
- [x] 2.6 Make the approved design the real one: its template becomes
  `templates/pages/tire_set.html`, its components move to `templates/components/`, its stylesheet
  with its light and dark tokens is merged into `static/app.css`; delete the other designs, the
  design switch and the discovery folders; write the design rules for both modes at the top of
  `app.css` and under "Approved design" in design.md. Verify: tests pass;
  `git grep -i discovery rollcall/` is empty; the page looks the same as the approved design in
  both modes. Done 2026-11-26: 59 of 60 before/after screenshots pixel-identical (the 60th
  differs only inside the headless browser's PDF viewer).
- [x] 2.7 Owner signs off the tire set page in its final place, in light and dark mode. Verify:
  owner confirms. Done 2026-11-27: approved after tread depth, DOT codes and tire positions were
  dropped.

## 3. Phase 2: mock up the other pages (one at a time, only after 2.7)

For each page, in the approved design and reusing its components: data shape in
`rollcall/views/`, sample states in the registry and tests first; then any new components and the
page template; builder checks it at 360 px and desktop width, in light and dark mode;
owner reviews in the gallery, revisions, sign-off. Page contents follow
`plan-rollcall-rewrite/design.md`.

- [x] 3.1 Customer view: details and phones; sets in shop, out and archived; check in / check out
  on each set; history; states for a new customer, many sets, long notes, archived customer,
  save conflict. Verify: owner signs off. Done 2026-11-27: approved as built (11 states).
- [x] 3.2 Search: one box and the in shop / out / too long / archived filters; results showing
  customers with their sets; states for no query, no results, many results, size typed as digits,
  a "too long" filter from the dashboard. Verify: owner signs off. Done 2026-11-27: approved as
  built (7 states).
- [x] 3.3 Dashboard: the five stats, each linking to its search; states for an empty shop and a
  busy one. Verify: owner signs off. Done 2026-11-27: approved with centered number cards; the
  two weekly numbers open this week's list on the dashboard (search has no date filter).
- [x] 3.4 Sign-in: sign-in form, wrong password, deactivated account, first-admin setup on a fresh
  install, temporary password must be changed. Verify: owner signs off. Done 2026-11-27: approved
  as built (8 states; username sign-in, passwords of at least 12 characters).
- [x] 3.5 Admin settings: staff accounts (create with temporary password, reset, promote/demote,
  deactivate, last admin protected) and the "too long" threshold; states for one admin only, many
  staff, form errors, save conflict. Verify: owner signs off. Done 2026-11-27: approved as built
  (8 states).

## 4. Wrap-up

- [x] 4.1 Full check: `scripts/test.sh` passes; every gallery state checked in a browser at 360
  px in light and dark mode; `openspec validate add-ui-components --strict` passes. Verify: all
  commands pass. Done 2026-11-27: 656 tests pass; all 49 states at 360 and 1280 px in light,
  dark by the switch and dark by the device (294 views) plus the index and components, with no
  sideways scroll and no browser errors. Fixed on the way: Pico's built-in icons were data:
  images the security policy blocked (now Rollcall's own files), a ticked checkbox had no tick
  and a pale fill in dark mode, no tab icon; the unused "mocked up later" page is gone.

## 5. What to try (shop owner, in a browser)

- [ ] 5.1 Owner sign-off:
  1. Add `MOCKUPS=on` to `.env` and run `docker compose up -d`.
  2. Open http://localhost:8080/mockups. Every page is listed with its states.
  3. Click through the tire set page from "checked out" to "check-in step" to "checked in".
     It looks like the design you approved in discovery, with no design switch left.
  4. Open the "filled from a PDF" state on a desktop: the sample invoice is beside the form.
  5. Open the gallery on a phone at http://<this PC's IP>:8080/mockups. Nothing scrolls sideways.
  6. Use the Light / Dark / Device switch in the header: the page turns dark or light at once,
     the next page opens the same way, and everything stays readable. Pick Device and set the
     phone to dark mode: Rollcall follows it.
  7. Remove `MOCKUPS=on` from `.env`, run `docker compose up -d`, open `/mockups`: "Page not
     found".

## Workflow follow-up

- After owner sign-off: `openspec archive add-ui-components`, verify
  `openspec/specs/ui-components/spec.md` exists, then tick 5.2 in `plan-rollcall-rewrite/tasks.md`.
