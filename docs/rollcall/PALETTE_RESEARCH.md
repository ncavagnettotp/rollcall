# Rollcall supporting palette

November 11, 2026. Graphic-design skill research. This is a recommendation for the continuing preview, not an objective claim that one palette is universally best. Existing orange selection styling is retained in this pass.

- Charcoal #202526: Sidebar
- Orange #F58B00: Selection and brand accent
- Mist #F5F6F8: Workspace
- White #FFFFFF: Content cards and active-tab surround
- Pale blue #EDF4FD: Customer information header
- Slate #596579: Supporting text and metadata
- Ink #263442: Headings and primary text
- Cream #FFF8EE: Quiet tab rail
- Steel blue #587898: Secondary icons

Use most area for neutral workspace and white cards; pale blue identifies the customer header, cream gently groups tabs, and orange identifies selection. Slate blue balances the warm accent. Status colors keep their existing meanings.

Measured solid-color contrast ratios:

- Ink on white: 12.71:1
- Slate on white: 5.90:1
- Slate on pale blue: 5.32:1
- Ink on orange: 5.19:1
- White on orange: 2.45:1

Normal text targets 4.5:1. Dark ink is the recommended label color on bright orange for a future contrast pass. Existing white-on-orange gradients have not been changed or represented as conformant; actual gradient stops also need checking.

Sources:
- https://m3.material.io/styles/color/the-color-system/ — neutral surface roles and container hierarchy.
- https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum — text contrast requirements.

Exact hex choices and their pairing are design judgment; the sources do not prescribe this Rollcall palette.

Superseding visual decision: user accepted a simpler neutral scheme. Header/cards are white, workspace is #F5F5F6, tab rail is #F0F0F2, supporting text/icons use neutral gray, and orange remains the selection accent. Pale-blue and cream surfaces were removed from the customer profile to reduce competing tints. The earlier table is research history, not the current surface direction.

Latest user-selected palette: supplied reference saved as references/accepted-palette-reference.png. Approximate swatches: ivory #E2E0D3, charcoal #30302F, warm gray #706969, slate #353C46. Use lighter ivory tints for readable surfaces. Preserve the existing Rollcall orange gradient; do not adopt the reference's burnt orange. This supersedes previous neutral surface experiments.

Latest direction: reverted to original dashboard reference colors at the user's request. Dark charcoal gradient sidebar, cool light-gray workspace, white cards/header, muted slate text and orange selection accents. Current layouts, custom icons, curved white tab joins and animations remain. Supersedes the warm ivory reference palette.
