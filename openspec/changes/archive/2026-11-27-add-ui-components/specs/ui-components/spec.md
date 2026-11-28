# Spec Delta: ui-components

## Purpose
How Rollcall's pages are designed and kept looking as designed: every page is built from shared
components, approved by the owner in an in-app mockup gallery filled with sample data, and then
rendered with real data from the very same templates.

## ADDED Requirements

### Requirement: Mockup gallery
Rollcall SHALL offer a mockup gallery at `/mockups` that lists every page and every shared
component, each in all of its named states, rendered by the same templates the real pages use and
filled only with invented sample data. Every gallery page SHALL show a banner saying it is a
mockup with sample data. The gallery SHALL be available only when the `MOCKUPS` setting is `on`;
otherwise every `/mockups` address SHALL answer "Page not found".

#### Scenario: Gallery switched off
- **GIVEN** `MOCKUPS` is not set
- **WHEN** a browser opens `/mockups` or any address under it
- **THEN** the "Page not found" page is shown with status 404

#### Scenario: Gallery switched on
- **GIVEN** `MOCKUPS=on`
- **WHEN** a browser opens `/mockups`
- **THEN** a list of every page and component state is shown, each linking to its mockup

#### Scenario: Invalid setting
- **WHEN** Rollcall starts with `MOCKUPS=maybe`
- **THEN** it refuses to start and names `MOCKUPS` as the problem

#### Scenario: Mockup is clearly marked
- **WHEN** any gallery page is shown
- **THEN** a banner says it is a mockup with sample data, and the page otherwise looks exactly as
  the real page will

#### Scenario: Clicking through
- **WHEN** a link or button on a mockup page leads to another page or step
- **THEN** it opens the gallery state for that page or step, never a dead link and never a real
  record

#### Scenario: No real data
- **WHEN** the gallery's sample data is inspected
- **THEN** every customer, phone, VIN, plate and RO number in it is invented; none comes from a
  real invoice

### Requirement: Pages built from shared components
Every page SHALL be assembled from shared components, so a part that appears on several pages
(status badge, unknown/yes/no choice, message, history list, stat card, form field,
button) looks and behaves the same everywhere. Each page SHALL receive one fixed shape of data
holding everything it shows, including every link, and the sample data in the gallery SHALL use
that same shape.

#### Scenario: Same part, same look
- **WHEN** a tire set's status badge appears on the customer view, in search results and on the
  tire set page
- **THEN** it is produced by the same component and looks the same in all three

#### Scenario: Missing value is caught
- **WHEN** a page is rendered with data that lacks a value the page shows
- **THEN** rendering fails with an error naming the missing value, instead of showing a blank

#### Scenario: A later change keeps the approved look
- **WHEN** a later change edits a component or page template
- **THEN** the automated tests render every gallery state again and fail if any of them can no
  longer be rendered, has a dead link or has a field without a label

### Requirement: Mockup states cover the awkward cases
Each page in the gallery SHALL include, where they apply to that page: an empty state, a full
state, very long text (names, notes, wheel descriptions), form errors, a "changed by someone else"
save conflict, and a 360-pixel-wide view. Pages SHALL use the wording they will use for real.

#### Scenario: Long text on a phone
- **WHEN** a mockup state with very long names and notes is shown 360 pixels wide
- **THEN** nothing scrolls sideways and all text can be read

#### Scenario: Save conflict shown
- **WHEN** the save-conflict state of a form is shown
- **THEN** the message says the record was changed by someone else, names who and when, and keeps
  the values that were typed

#### Scenario: Form errors shown
- **WHEN** the form-error state of a form is shown
- **THEN** each wrong field is marked, has its message next to it, and keeps its typed value

### Requirement: UI design discovery on one sample page
Rollcall's design (layout, colors, spacing, density, type sizes) SHALL be found on one sample
page, the tire set page, before any other page is mocked up. The gallery SHALL show two or three
distinct designs of it, differing in layout as well as look, all with the same sample data. The
owner MAY pick one, ask for changes or combine parts; revising SHALL continue until the owner is
happy.

#### Scenario: Comparing designs
- **GIVEN** discovery is under way
- **WHEN** the owner opens the sample page in the gallery
- **THEN** they can switch between the designs and see the same data in each

#### Scenario: Revising a design
- **GIVEN** the owner asks for changes to a design, or for parts of two designs combined
- **WHEN** the revised design is ready
- **THEN** it appears in the gallery next to the earlier ones, and revising continues until the
  owner is happy

#### Scenario: Other pages wait
- **GIVEN** the owner has not yet approved a design
- **WHEN** the gallery is inspected
- **THEN** it contains no mockups of pages other than the sample page

### Requirement: One approved design
Once the owner approves a design, it SHALL become the app's only design, written down as a short
list of design rules covering its light and its dark mode, and the other designs SHALL be removed.

#### Scenario: After the choice
- **GIVEN** the owner has approved a design
- **WHEN** any page is shown, in the gallery or for real
- **THEN** it uses the approved design, and no switch between designs remains

### Requirement: Light and dark mode
Every page SHALL have a light mode and a dark mode, both part of the approved design. The page
frame SHALL offer a Light / Dark / Device switch whose choice is remembered in that browser;
Device, the default, follows the device's own setting. In both modes text SHALL keep a contrast
of at least 4.5:1 with its background, and large text, icons and borders at least 3:1.

#### Scenario: Following the device
- **GIVEN** the switch is on Device, as it is until someone changes it
- **WHEN** a page is opened on a phone or PC set to dark mode
- **THEN** the page is shown in its dark mode, with the same layout and content as in light mode

#### Scenario: Choosing a mode
- **WHEN** a staff member picks Dark in the switch
- **THEN** the page they were on is shown again in dark mode, and every later page in that
  browser opens in dark mode, without first flashing light, until another mode is picked

#### Scenario: Reviewing both modes in the gallery
- **WHEN** the owner picks Light or Dark on a gallery page
- **THEN** that state is shown in the chosen mode, so both modes can be reviewed on one device

#### Scenario: Readable in both modes
- **WHEN** any gallery state is shown in either mode
- **THEN** all text, pills and status colors meet the contrast limits, and no status is shown by
  color alone

#### Scenario: The switch stays inside Rollcall
- **WHEN** the switch is sent with a return address outside Rollcall
- **THEN** the browser is sent to the start page instead

### Requirement: Owner sign-off per page
A page's mockup SHALL count as approved only after the owner has signed it off in the gallery.
Later changes SHALL render approved pages from their templates and SHALL NOT redraw them.

#### Scenario: Building a real page later
- **WHEN** a later change makes a page work with real data
- **THEN** its route fills the approved page template with data of the same shape as the sample
  data, and the gallery still renders that page from sample data

### Requirement: Sample PDF beside the form
The tire set form's "filled from a PDF" state SHALL show a synthetic sample invoice beside the
form, served by Rollcall and displayed inside the page. Only PDF responses MAY be shown inside
Rollcall's own pages; every other response SHALL still refuse to be shown inside any page.

#### Scenario: PDF shown beside the form
- **WHEN** the "filled from a PDF" state is shown on a desktop-wide screen
- **THEN** the sample invoice is visible next to the form, without any download

#### Scenario: Pages still cannot be framed
- **WHEN** any non-PDF response is inspected
- **THEN** its content security policy still forbids showing it inside any page
