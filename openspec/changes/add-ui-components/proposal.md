# Proposal: add UI components and the mockup gallery

## Why

Mockups usually look better than the pages finally built from them, because building means
redrawing the design and every redraw loses details. Rollcall is about to gain all of its real
screens (accounts, customers, tire sets, PDF review, dashboard), so now is the cheapest moment to
fix the look. This change makes the mockups the real templates: each page is designed once, as
the template the app itself will render, filled with invented sample data. Later changes only
connect real data to templates the owner has already approved; they never redraw a page.

Decided with the owner on 2026-11-25: the work starts with a **UI design discovery** phase on
one sample page. Only once the owner is happy with that design are the other pages mocked up.

## What Changes

- **Components:** shared parts (status badge, unknown/yes/no choice, tire table, stat card,
  message, history list, and others as pages need them) become reusable templates. Every page is
  assembled from them.
- **Page templates fed by a fixed shape of data:** each page template receives one object
  describing everything it shows, including every link. The sample data and the real data later
  use the same shape, so a page cannot look different once it is wired up.
- **Mockup gallery** at `/mockups`, inside the app: every page and component in each of its
  states (empty, full, long text, errors, "changed by someone else"), filled with invented data,
  marked with a "Mockup: sample data" banner. Off unless the `MOCKUPS` setting is `on`. Because
  the app is reachable on the shop network, the gallery can be checked on a phone.
- **Phase 1, UI design discovery:** the tire set page (detail, form, check-in step, PDF beside
  the form) is mocked up in two or three distinct designs, each with its own look and layout,
  shown side by side in the gallery with the same sample data. The owner picks one, or asks for
  changes or a mix of them, and the design is adjusted until the owner is happy with it. That
  design becomes the app's only design, written down as short design rules; the other mockups are
  removed.
- **Phase 2, the other pages, only after discovery is finished:** customer view, search, dashboard, sign-in (with first-admin setup)
  and admin settings, one at a time, each signed off by the owner in the gallery.
- **Tests** render every gallery entry and fail on a missing value, a dead link, an unlabeled
  field or a style attribute, so a later change cannot silently break an approved page.
- The planning change gets this change as step 5.2 (accounts and the rest move down by one).

## Capabilities

### New Capabilities

- `ui-components`: the mockup gallery, the rule that pages are built only from shared components
  and receive a fixed shape of data, and the approved style.

### Modified Capabilities

None. The page frame (`platform`) stays as specified: its navigation still lists only pages that
exist. The gallery shows the frame with sample navigation and a sample signed-in staff member.

## Out of scope

- Any real data, database tables or routes for customers, tire sets, accounts or the dashboard.
  Forms in the gallery do not save; buttons that would change data lead to gallery states instead.
- htmx behavior beyond what a gallery state can show (each step of an interaction is its own
  state, for example "check-in form open").
- Automated screenshot comparison. Can be added later if approved pages start drifting.
- Changing what any page contains: page contents come from the decisions in
  `plan-rollcall-rewrite/design.md`. The owner may still adjust them while reviewing a mockup,
  and those changes are recorded there.
- Anything out of scope in `openspec/config.yaml`.

## Impact

- New: `rollcall/templates/components/`, `rollcall/templates/pages/`, `rollcall/views/` (data
  shapes), `rollcall/mockups/` (sample data, gallery routes, a synthetic sample invoice PDF).
- Changed: `rollcall/config.py` and `.env.example` (`MOCKUPS` setting), `rollcall/web.py`
  (templates fail on missing values; PDF responses may be shown inside Rollcall's own pages),
  `rollcall/templates/base.html` (header can show the signed-in staff member),
  `rollcall/static/app.css` (the chosen style).
- Planning: `plan-rollcall-rewrite/tasks.md` and `design.md` (new step 5.2, template decisions).
- No new dependencies.
