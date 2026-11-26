"""Shared components and strict templates (spec: Pages built from shared components)."""

import re
from dataclasses import dataclass
from zoneinfo import ZoneInfo

import pytest
from jinja2 import UndefinedError

from rollcall.web import make_templates


@pytest.fixture
def env():
    return make_templates(ZoneInfo("America/Chicago"), nav_items=[]).env


@dataclass(frozen=True)
class Customer:
    first_name: str


# --- a missing value is an error, never a blank ----------------------------------------------


def test_missing_field_on_the_page_data_names_the_field(env):
    page = env.from_string("<h1>{{ customer.first_name }} {{ customer.last_name }}</h1>")
    with pytest.raises(UndefinedError) as caught:
        page.render(customer=Customer(first_name="Dana"))
    assert "last_name" in str(caught.value)


def test_missing_page_data_names_it(env):
    with pytest.raises(UndefinedError) as caught:
        env.from_string("<p>{{ tire_set.size }}</p>").render()
    assert "tire_set" in str(caught.value)


def test_missing_value_in_a_test_is_also_an_error(env):
    with pytest.raises(UndefinedError):
        env.from_string("{% if customer.notes %}notes{% endif %}").render(customer=Customer("Dana"))


def test_optional_values_are_explicit_none(env):
    page = env.from_string("{% if notes %}{{ notes }}{% else %}No notes{% endif %}")
    assert page.render(notes=None) == "No notes"


def test_shop_date_filter(env):
    from datetime import date

    assert env.from_string("{{ day | shop_date }}").render(day=date(2026, 3, 2)) == "3/2/2026"


# --- components -------------------------------------------------------------------------------


def render_component(env, source: str, **values) -> str:
    return env.from_string(source).render(**values)


def test_field_component(env):
    html = render_component(
        env,
        '{% from "components/field.html" import field %}'
        '{{ field("ro", "RO number", value="48213", error="Use digits only") }}',
    )
    assert '<label for="f-ro">RO number' in html
    assert 'id="f-ro" name="ro" type="text" value="48213"' in html
    assert 'aria-invalid="true" aria-describedby="e-ro"' in html
    assert '<small id="e-ro">Use digits only</small>' in html


def test_field_component_without_error_shows_the_hint(env):
    html = render_component(
        env,
        '{% from "components/field.html" import field %}'
        '{{ field("dot", "DOT code", hint="Week and year, e.g. 2319", required=True) }}',
    )
    assert "aria-invalid" not in html
    assert "<small>Week and year, e.g. 2319</small>" in html
    assert " required" in html


def test_button_component(env):
    source = '{% from "components/button.html" import button %}'
    assert render_component(env, source + '{{ button("Save") }}') == (
        '<button type="submit" class="rc-button rc-primary">Save</button>'
    )
    assert render_component(env, source + '{{ button("Cancel", "link", "button") }}') == (
        '<button type="button" class="rc-link-button">Cancel</button>'
    )
    edit = '{{ button("Edit", "secondary", icon_name="edit") }}'
    with_icon = render_component(env, source + edit)
    assert with_icon.startswith('<button type="submit" class="rc-button rc-secondary"><svg')
    assert with_icon.endswith("</svg>Edit</button>")


def test_table_component(env):
    source = '{% from "components/table.html" import table %}{{ table(headers, rows) }}'
    html = render_component(env, source, headers=["Size", "Brand"], rows=[["225/55R17", "Nokian"]])
    assert '<th scope="col">Size</th>' in html
    assert "<td>225/55R17</td>" in html


def test_empty_table_says_so(env):
    source = '{% from "components/table.html" import table %}{{ table(["Size"], [], "No tires") }}'
    assert '<td colspan="1">No tires</td>' in render_component(env, source)


def test_old_macros_file_is_gone():
    from rollcall.web import TEMPLATES_DIR

    assert not (TEMPLATES_DIR / "macros.html").exists()


def test_pages_define_no_components_of_their_own():
    """Pages import their parts from components/, so a part looks the same on every page."""
    from rollcall.web import TEMPLATES_DIR

    pages = sorted((TEMPLATES_DIR / "pages").glob("*.html"))
    assert pages
    for page in pages:
        assert "{% macro" not in page.read_text(), page.name


@pytest.mark.parametrize(
    "source",
    [
        '{% from "components/badge.html" import status_badge %}{{ status_badge(s, True) }}',
        '{% from "components/tread.html" import tread %}{{ tread("LF", 3) }}',
    ],
)
def test_pills_always_carry_a_word(env, source):
    """Colour is never the only signal (spec: Light and dark mode, Readable in both modes)."""
    from rollcall.views.tire_set import Status

    html = render_component(env, source, s=Status.IN_SHOP)
    assert re.sub(r"<[^>]+>", "", html).strip()
