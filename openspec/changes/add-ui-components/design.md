# Design: add UI components and the mockup gallery

## Context

The platform change left a page frame (`templates/base.html`), three macros
(`templates/macros.html`: field, button, table), a small `static/app.css` on top of vendored Pico
CSS 2.1.1, and one temporary start page. The content security policy forbids inline scripts and
inline `style` attributes, so all styling must live in stylesheet files and use classes.
Page contents are fixed by the decisions in `plan-rollcall-rewrite/design.md` (tire set fields,
stays, tread depth, search fields, dashboard stats). See proposal.md for why mockups must be the
real templates.

## Goals / Non-Goals

**Goals:**

- One template per page and per component, used by the gallery and later by the real routes.
- A page's data is a typed object, so the sample data and the real data cannot drift apart.
- The design is found on one page (the tire set page) in a discovery phase, before any other
  page is drawn.
- Tests that keep every gallery state renderable for the rest of the project.

**Non-Goals:**

- A general design system or theming engine. One shop, one style.
- Interactive mockups beyond navigation between states (no htmx endpoints in the gallery).
- Pixel-level regression testing.

## Decisions

### 1. Mockups are the app's own templates, rendered by the app

Alternatives: a separate design tool (Figma), standalone HTML mockups, or Storybook. All three
produce something the real pages must later redraw, which is the problem this change solves.
Storybook also needs a JavaScript build step, which the project rules out. Pattern libraries for
server-rendered templates (e.g. django-pattern-library) do exactly this; Rollcall needs a small
version of the idea, not the library.

### 2. Folder layout

```
rollcall/templates/components/   one file per component, each a Jinja macro
                                 (badge.html, choice.html, tire_table.html, message.html, ...)
rollcall/templates/pages/        one file per page; extends base.html, imports components
rollcall/views/                  the data shape for each page, as frozen dataclasses
rollcall/mockups/                gallery routes, the sample data for every state, sample PDF
```

`templates/macros.html` is split into `components/` (field, button and table move there); nothing
else uses it yet.

### 3. Page data: frozen dataclasses with links included

Each page gets one dataclass, for example `TireSetPage`, built from smaller ones (`TireRow`,
`Stay`, `Link`). Templates never build URLs; every link is a value in the data. That lets the
gallery point links at other gallery states and the real routes point them at real records, with
the same template. Dataclasses over plain dicts: a typo in a field name fails when the sample is
built, not when the page is viewed. Over Pydantic: nothing here is parsed from user input, so
validation adds nothing.

### 4. Templates fail on missing values

The Jinja environment uses `StrictUndefined`, so a missing value raises an error naming it instead
of rendering as blank. Optional values are explicit `None` in the dataclasses and templates test
for them. The platform templates are adjusted where needed; their tests already cover them.

### 5. The gallery

- Enabled by `MOCKUPS=on` (`on`/`off`, default `off`; anything else is a configuration error).
  When off, the gallery's routes are not registered, so `/mockups...` is an ordinary 404.
- Routes: `/mockups` (index), `/mockups/pages/{page}/{state}`, `/mockups/components/{component}`
  (every state of one component on one page), `/mockups/sample-invoice.pdf`.
- A registry in `rollcall/mockups/samples.py` names every state: page, state name, one-line
  description, template, and the sample object. The index and the tests both read it.
- The frame gets two optional values: the navigation (the real app passes the pages that exist;
  the gallery passes the planned navigation) and the signed-in staff member (name, sign-out link).
  The gallery shows the frame as a signed-in staff member would see it, and as an admin.
- The banner is a block in `base.html`, shown only when the page is rendered by the gallery.
- Buttons that would change data are links or forms whose target is the gallery state that shows
  the result (for example "Save" on the form-error state leads to the saved detail state).

### 6. UI design discovery (phase 1 only)

Each candidate design is its own page template plus its own stylesheet
(`templates/mockups/discovery/tire_set_<a|b|c>.html`, `static/mockups/discovery-<a|b|c>.css`), so
designs can differ in layout, not only in colors. All of them take the same `TireSetPage` data
and may use different components; the components of the approved design are the ones kept.
The gallery shows each design for every sample state and the banner switches between designs
with `?design=`. Revisions are added as new letters (`d`, `e`, ...) so earlier designs stay
available for comparison until the owner approves one. Starting points, refined while building:

- **A, calm and roomy:** Pico's own look; one column; the tire table as a classic table; the
  check-in step on its own page.
- **B, compact workshop:** dense two-column layout on desktop (set details left, tires and stays
  right), large buttons for check in / check out, the check-in step opening in place.
- **C, cards and high contrast:** always light, bold status colors, each tire as a card with its
  position, DOT code and tread, suited to a bright shop floor and to phones.

When the owner approves a design, its template becomes `templates/pages/tire_set.html`, its
stylesheet is merged into `static/app.css`, its components move to `templates/components/`, and
every other candidate, the `?design=` switch and the discovery folders are deleted. The design
rules (layout pattern, colors, spacing, type sizes, how forms, tables, buttons and badges look)
are written at the top of `app.css` and in this design under "Approved design".

### 7. PDF beside the form

The PDF is shown in an `<iframe>` pointing at Rollcall's own address. The current policy
`frame-ancestors 'none'` would block that, so `SecurityHeaders` sends `frame-ancestors 'self'` on
responses whose content type is `application/pdf`, and keeps `'none'` everywhere else. Showing
Rollcall's own PDF is still "only Rollcall's own origin", so the platform requirement holds.
`add-pdf-prefill` reuses this for real uploads. Below desktop width the PDF is not embedded
(phone browsers render embedded PDFs badly); a "Open the invoice" link is shown instead.

The sample invoice is synthetic: `scripts/make_sample_invoice.py` writes a small PDF by hand (no
new dependency) laid out like a Protractor invoice, with invented names and numbers. The script and
its output (`rollcall/mockups/sample-invoice.pdf`) are committed.

### 8. Tests

`tests/test_mockups.py` walks the registry and, for every state: status 200; the banner is
present; every `href`/`src`/`action` points at a gallery state, `/static/...` or the sample PDF;
every `input`, `select` and `textarea` has a label; no `style` attributes and no inline scripts.
Plus: gallery off → 404; `MOCKUPS` validation in `test_config.py`; a dataclass missing a value
fails to render with a message naming it; the PDF response carries `frame-ancestors 'self'` while
pages keep `'none'`. The 360-pixel check is done in a real browser, by the builder and by the owner.

## Risks / Trade-offs

- [Sample data shape changes when real data arrives] → Allowed: the later change updates the
  dataclass and the samples together, and the gallery tests keep every state rendering. If the
  page's look changes visibly, the owner sees it again in the gallery before sign-off.
- [Discovery takes many rounds] → Each round changes one design and keeps the others for
  comparison, so every round narrows the choice. No page beyond the sample is built meanwhile, so
  nothing has to be redone when the design changes.
- [The gallery is reachable on the shop network when on] → Off by default; it shows only invented
  data and changes nothing. Turn it on only while reviewing.
- [`StrictUndefined` makes small template mistakes fatal] → That is the point; the gallery tests
  find them before a person does.
- [Embedded PDFs differ by browser] → Checked in the shop's browser during sign-off; the link
  fallback always works.

## Migration Plan

No data changes. Production `.env` leaves `MOCKUPS` unset. Rollback is reverting the commits.

## Approved design

To be filled in when the owner approves a design at the end of discovery.
