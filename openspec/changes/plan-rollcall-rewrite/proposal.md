# Proposal: plan the Rollcall rewrite

## Why

The first Rollcall (now in `legacy/`) grew into a heavy system: many pages, a Windows Electron
client, an automatic PDF rule engine, and more planning documents than code. Its core purpose, PDFs
updating inventory, was never finished. The shop needs a simple, robust tire inventory that many
staff can use at once, so the app is being rewritten from the ground up.

This change plans that rewrite: it fixes the product shape and stack, and defines the sequence of
OpenSpec changes that will specify and build the new app. It adds no code and no specs itself.

## What Changes

- Old code and documents moved to `legacy/` as reference material.
- OpenSpec set up as the single home for the rewrite's documentation (`openspec/config.yaml`
  carries the project-wide constraints).
- A capability map and an ordered list of follow-up changes (see design.md).
- A bundled list of product questions to settle with the shop owner before specs are written.

## Capabilities

### New Capabilities

None in this change. The capabilities below are planned and will each be introduced by their own
follow-up change:

- `platform`: containers, configuration, health checks, migrations, page shell (header,
  navigation, error pages).
- `accounts`: sign-in, sessions, first-admin bootstrap, roles, user management.
- `customers`: customer records, the root of all data; every tire set belongs to one customer.
- `tire-inventory`: tire sets kept permanently under their customer; sizes and related details; toggling
  checked in / checked out, with each stay kept; one search page for customers and sets.
- `audit-history`: what is recorded on every change and how it is shown.
- `pdf-prefill`: PDF upload, archive, suggested values, side-by-side review.
- `dashboard`: stat definitions and counting rules.
- `operations`: host, HTTPS, start after reboot, backup and restore.

### Pages (confirmed by the owner, 2026-11-24)

Six pages in total. Adding a page needs an owner decision.

| Page | Owned by | Shown on it from other capabilities |
|---|---|---|
| Sign-in (also first-admin setup on a fresh install) | `accounts` | |
| Dashboard | `dashboard` | each stat links to a filtered search |
| Search: one box finding customers and tire sets by name, size, RO, vehicle | `tire-inventory` | customers in the results |
| Customer view: details, all their sets, check in / out on each set | `customers` | sets (`tire-inventory`), history (`audit-history`) |
| Tire set form and detail, with the PDF beside it when pre-filled | `tire-inventory` | PDF review (`pdf-prefill`), stays and history (`audit-history`) |
| Admin settings: staff accounts | `accounts` | |

`platform` owns the frame around every page; `audit-history`, `pdf-prefill` and `operations` own
no page of their own. There is no separate activity log page: history is shown on each customer
and set. Rollcall is a standalone app; a planned staff scheduling app will not share its accounts,
database or pages.

### Modified Capabilities

None.

## Out of scope

Writing any code, writing the capability specs themselves, and anything listed as out of scope in
`openspec/config.yaml`.

## Impact

- Repository layout: application code will live at the root; `legacy/` is removed once the
  rewrite ships.
- Work happens on the `rewrite` branch.
