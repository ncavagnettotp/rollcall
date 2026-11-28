"""Colour contrast of the approved design in light and dark mode (spec: Light and dark mode).

Reads the colour tokens from static/app.css: the light values in its `:root { }` block
and the dark values in its `:root[data-theme="dark"] { }` block (repeated, identical, for devices
set to dark). Every pair of a text colour and the background it is drawn on must reach 4.5:1;
icons and control borders 3:1 (WCAG 2.1 levels AA, 1.4.3 and 1.4.11).
"""

import re

import pytest

from rollcall.web import STATIC_DIR

STYLESHEET = STATIC_DIR / "app.css"

TEXT = 4.5
NON_TEXT = 3.0

# (foreground token, background token, minimum, what it is)
PAIRS = [
    ("ink", "card", TEXT, "headings and values on cards"),
    ("ink", "ground", TEXT, "the page title"),
    ("text", "card", TEXT, "body text on cards"),
    ("text", "ground", TEXT, "body text on the page"),
    ("muted", "card", TEXT, "labels and hints on cards"),
    ("muted", "ground", TEXT, "phone numbers beside the title"),
    ("link", "card", TEXT, "links and quiet buttons on cards"),
    ("link", "ground", TEXT, "links on the page"),
    ("accent", "card", TEXT, "the chosen segment"),
    ("slate", "slate-soft", TEXT, "segments not chosen, grey pills"),
    ("green", "green-soft", TEXT, "green pills, success messages"),
    ("red", "red-soft", TEXT, "red pills, error messages"),
    ("amber", "amber-soft", TEXT, "amber pills"),
    ("blue", "blue-soft", TEXT, "blue pills"),
    ("text", "amber-soft", TEXT, "notes"),
    ("red", "card", TEXT, "error text under a field"),
    ("on-primary", "orange", TEXT, "main buttons"),
    ("on-header", "navy", TEXT, "header links, left end"),
    ("on-header", "indigo", TEXT, "header links, right end"),
    ("field-border", "card", NON_TEXT, "input borders"),
    ("orange-ink", "orange-soft", NON_TEXT, "orange icon tiles"),
    ("accent", "card", NON_TEXT, "focus outlines"),
    ("on-primary", "check", NON_TEXT, "the tick in a ticked checkbox"),
    ("check", "card", NON_TEXT, "a ticked checkbox on a card"),
    ("on-banner", "banner", TEXT, "the mockup banner"),
]


def tokens(block: str) -> dict[str, str]:
    return dict(re.findall(r"--rc-([a-z-]+):\s*(#[0-9a-fA-F]{6})\b", block))


def block_after(css: str, selector: str) -> str:
    start = css.index(selector + " {")
    return css[start : css.index("}", start)]


@pytest.fixture(scope="module")
def css() -> str:
    return STYLESHEET.read_text()


def luminance(colour: str) -> float:
    def channel(value: int) -> float:
        c = value / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (int(colour[i : i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast(a: str, b: str) -> float:
    high, low = sorted((luminance(a), luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def test_contrast_formula():
    assert round(contrast("#000000", "#ffffff"), 1) == 21.0
    assert round(contrast("#767676", "#ffffff"), 2) == 4.54


def test_dark_tokens_are_the_same_for_the_device_and_the_switch(css):
    """Devices set to dark and the Dark switch must look identical."""
    media = css[css.index("@media (prefers-color-scheme: dark)") :]
    assert tokens(block_after(media, ':root:not([data-theme="light"])')) == tokens(
        block_after(css, ':root[data-theme="dark"]')
    )


@pytest.mark.parametrize("mode", ["light", "dark"])
@pytest.mark.parametrize(("fg", "bg", "minimum", "what"), PAIRS)
def test_colour_pairs_are_readable(css, mode, fg, bg, minimum, what):
    selector = ":root" if mode == "light" else ':root[data-theme="dark"]'
    palette = tokens(block_after(css, selector))
    assert fg in palette and bg in palette, f"{fg} or {bg} missing in {mode} tokens"
    ratio = contrast(palette[fg], palette[bg])
    assert ratio >= minimum, f"{what} ({mode}): {fg} on {bg} is {ratio:.2f}:1, needs {minimum}:1"
