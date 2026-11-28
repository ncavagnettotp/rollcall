"""The mockup gallery (spec: Mockup gallery, Pages built from shared components, Mockup states
cover the awkward cases).

Every page state and component in the registry is rendered and checked: it answers, carries the
mockup banner, every link and form target leads to a gallery page that answers, every form field
has a label, and there are no inline styles or scripts (the content security policy blocks them).
"""

import dataclasses
import re
import runpy
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

import pytest
from fastapi.testclient import TestClient

from rollcall.main import create_app
from rollcall.mockups import samples

STATE_URLS = [
    f"/mockups/pages/{page.slug}/{state.slug}" for page in samples.PAGES for state in page.states
]
COMPONENT_URLS = [f"/mockups/components/{c.slug}" for c in samples.COMPONENTS]
PAGE_URLS = [f"/mockups/pages/{page.slug}" for page in samples.PAGES]
ALL_GALLERY_URLS = ["/mockups", *PAGE_URLS, *STATE_URLS, *COMPONENT_URLS]
BANNER = "Mockup: sample data"
SAMPLE_INVOICE_URL = "/mockups/sample-invoice.pdf"
THEME_SWITCH = "/theme"  # the light/dark switch in the header posts here (tests/test_theme.py)
REPO_DIR = Path(__file__).parent.parent


@pytest.fixture(scope="module")
def gallery(database_url, tmp_path_factory):
    from rollcall.config import load_settings

    settings = load_settings(
        {
            "DATABASE_URL": database_url,
            "SECRET_KEY": "test-secret-" + "x" * 32,
            "SHOP_TIMEZONE": "America/Chicago",
            "DATA_DIR": str(tmp_path_factory.mktemp("data")),
            "MOCKUPS": "on",
        }
    )
    with TestClient(create_app(settings)) as test_client:
        yield test_client


class PageParts(HTMLParser):
    """Collects links, form fields, labels, styles and scripts from a page."""

    def __init__(self):
        super().__init__()
        self.targets = []  # href, src, form action and button formaction values
        self.fields = []  # (tag, id, inside a label?)
        self.label_fors = set()
        self.style_attributes = 0
        self.inline_scripts = 0
        self._label_depth = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for name in ("href", "src", "action", "formaction"):
            if attrs.get(name):
                self.targets.append(attrs[name])
        if "style" in attrs or tag == "style":
            self.style_attributes += 1
        if tag == "script" and not attrs.get("src"):
            self.inline_scripts += 1
        if tag == "label":
            self._label_depth += 1
            if attrs.get("for"):
                self.label_fors.add(attrs["for"])
        typed_in = attrs.get("type") not in ("hidden", "submit", "button", "reset")
        if tag in ("input", "select", "textarea") and typed_in:
            self.fields.append((tag, attrs.get("id"), self._label_depth > 0))

    def handle_endtag(self, tag):
        if tag == "label":
            self._label_depth -= 1

    def unlabeled_fields(self):
        return [
            (tag, field_id)
            for tag, field_id, in_label in self.fields
            if not in_label and field_id not in self.label_fors
        ]


def count_class(html: str, name: str) -> int:
    """How many elements carry the class name (among others)."""
    return sum(name in found.split() for found in re.findall(r'class="([^"]*)"', html))


def parse(html: str) -> PageParts:
    parts = PageParts()
    parts.feed(html)
    return parts


# --- the registry -----------------------------------------------------------------------------


def test_registry_lists_the_frame_and_the_six_planned_pages():
    assert [page.slug for page in samples.PAGES] == [
        "frame",
        "tire-set",
        "customer",
        "search",
        "dashboard",
        "sign-in",
        "admin",
    ]
    assert STATE_URLS, "at least one state to show"
    assert COMPONENT_URLS, "at least one component to show"


def test_slugs_are_unique():
    page_slugs = [page.slug for page in samples.PAGES]
    assert len(page_slugs) == len(set(page_slugs))
    for page in samples.PAGES:
        state_slugs = [state.slug for state in page.states]
        assert len(state_slugs) == len(set(state_slugs)), page.slug
    component_slugs = [c.slug for c in samples.COMPONENTS]
    assert len(component_slugs) == len(set(component_slugs))


# --- the index --------------------------------------------------------------------------------


def test_index_lists_every_state_and_component(gallery):
    response = gallery.get("/mockups")
    assert response.status_code == 200
    targets = parse(response.text).targets
    for url in STATE_URLS + COMPONENT_URLS:
        assert url in targets, url


def test_every_page_is_mocked_up():
    assert all(page.states for page in samples.PAGES)


def test_page_with_states_opens_its_first_state(gallery):
    page = next(page for page in samples.PAGES if page.states)
    response = gallery.get(f"/mockups/pages/{page.slug}", follow_redirects=False)
    assert response.status_code in (302, 307)
    assert response.headers["location"] == f"/mockups/pages/{page.slug}/{page.states[0].slug}"


@pytest.mark.parametrize(
    "path",
    ["/mockups/pages/no-such-page", "/mockups/pages/frame/no-such-state", "/mockups/components/x"],
)
def test_unknown_gallery_address_is_not_found(gallery, path):
    response = gallery.get(path)
    assert response.status_code == 404
    assert "Page not found" in response.text


# --- every page state and component ------------------------------------------------------------


@pytest.mark.parametrize("url", ALL_GALLERY_URLS)
def test_gallery_page_renders_with_the_banner(gallery, url):
    response = gallery.get(url)
    assert response.status_code == 200, url
    assert BANNER in response.text


@pytest.mark.parametrize("url", ALL_GALLERY_URLS)
def test_gallery_page_has_no_dead_links(gallery, url):
    for target in set(parse(gallery.get(url).text).targets) - {THEME_SWITCH}:
        parts = urlsplit(target)
        assert not parts.scheme and not parts.netloc, f"{url} links outside Rollcall: {target}"
        assert parts.path.startswith(("/mockups", "/static/")), (
            f"{url} leaves the gallery: {target}"
        )
        assert gallery.get(target).status_code == 200, f"{url} has a dead link: {target}"


@pytest.mark.parametrize("url", ALL_GALLERY_URLS)
def test_gallery_page_fields_all_have_labels(gallery, url):
    assert parse(gallery.get(url).text).unlabeled_fields() == []


@pytest.mark.parametrize("url", ALL_GALLERY_URLS)
def test_gallery_page_has_no_inline_styles_or_scripts(gallery, url):
    parts = parse(gallery.get(url).text)
    assert parts.style_attributes == 0
    assert parts.inline_scripts == 0


def test_submitting_a_mockup_form_shows_the_resulting_state(gallery):
    url = STATE_URLS[0]
    response = gallery.post(url, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == url


# --- the frame ---------------------------------------------------------------------------------


def test_signed_in_staff_member_is_shown_in_the_header(gallery):
    html = gallery.get("/mockups/pages/frame/staff").text
    assert samples.STAFF.name in html
    assert "Sign out" in html
    assert "Admin" not in html  # only admins see admin settings


def test_admin_sees_admin_settings_in_the_navigation(gallery):
    html = gallery.get("/mockups/pages/frame/admin").text
    assert samples.ADMIN.name in html
    assert "Admin settings" in html


def test_real_pages_have_no_banner_and_no_signed_in_staff(gallery):
    html = gallery.get("/").text
    assert BANNER not in html
    assert "Sign out" not in html


# --- the tire set page (task 2.1) -----------------------------------------------------------

TIRE_SET_STATES = [
    "checked-in",
    "checked-out",
    "new",
    "from-pdf",
    "check-in",
    "staggered",
    "edit",
    "form-errors",
    "save-conflict",
    "archived",
]

# Where each state's links and buttons lead, among the tire set states: the flow the owner
# clicks through. Each state may link to more (the customer page, the invoice).
TIRE_SET_FLOW = {
    "checked-in": {"checked-out", "edit"},
    "checked-out": {"check-in", "archived", "edit"},
    "new": {"checked-in"},
    "from-pdf": {"checked-in"},
    "check-in": {"checked-in", "checked-out"},
    "staggered": {"edit"},
    "edit": {"checked-in"},
    "form-errors": {"checked-in"},
    "save-conflict": {"checked-in", "edit"},
    "archived": {"checked-out"},
}


def tire_set_html(gallery, state: str) -> str:
    response = gallery.get(f"/mockups/pages/tire-set/{state}")
    assert response.status_code == 200
    return response.text


def test_tire_set_has_every_planned_state():
    assert [state.slug for state in samples.find_page("tire-set").states] == TIRE_SET_STATES


def test_tire_set_states_all_use_the_page_data_shape():
    from rollcall.views.tire_set import TireSetPage

    for state in samples.find_page("tire-set").states:
        assert isinstance(state.data()["page"], TireSetPage), state.slug


@pytest.mark.parametrize("state", TIRE_SET_STATES)
def test_tire_set_states_link_to_each_other(gallery, state):
    prefix = "/mockups/pages/tire-set/"
    targets = {
        urlsplit(target).path.removeprefix(prefix)
        for target in parse(tire_set_html(gallery, state)).targets
        if urlsplit(target).path.startswith(prefix)
    }
    assert TIRE_SET_FLOW[state] <= targets


def test_checked_in_set_shows_where_it_is_and_its_history(gallery):
    html = tire_set_html(gallery, "checked-in")
    for text in ("Renata Kowalczyk", "225/60R17", "Bridgestone Alenza", "Rack B3", "48213"):
        assert text in html, text
    assert "11/18/2026" in html  # dates as the shop writes them
    assert count_class(html, "stay") == 4  # the current stay and three past ones


def test_checked_out_set_lists_three_past_stays_and_offers_check_in(gallery):
    html = tire_set_html(gallery, "checked-out")
    assert count_class(html, "stay") == 3
    assert "Check in" in html


@pytest.mark.parametrize("state", TIRE_SET_STATES)
def test_nothing_is_recorded_per_tire(gallery, state):
    """No tread depth, DOT codes or tire positions (plan-rollcall-rewrite/design.md, changed
    2026-11-27): anything about one tire goes in the notes."""
    html = tire_set_html(gallery, state)
    for text in ("Tread", "tread", "DOT", 'name="tires-', "Add tire", ">LF<", "Extra"):
        assert text not in html, text


def test_new_set_asks_for_the_set_and_its_check_in(gallery):
    html = tire_set_html(gallery, "new")
    for name in ("front_size", "rear_size", "brand_model", "notes", "checked_in", "location"):
        assert f'name="{name}"' in html, name


def test_set_from_a_pdf_shows_the_invoice_beside_the_form(gallery):
    parts = parse(tire_set_html(gallery, "from-pdf"))
    assert SAMPLE_INVOICE_URL in parts.targets  # embedded, plus the "Open the invoice" link
    html = tire_set_html(gallery, "from-pdf")
    assert "<iframe" in html
    assert "Open the invoice" in html
    for text in ("JF2EXAMPLE0000001", "48213", "225/60R17", "2019 Subaru Outback"):
        assert text in html, text


def test_check_in_step_asks_for_date_ro_and_location(gallery):
    html = tire_set_html(gallery, "check-in")
    for name in ("checked_in", "ro_number", "location"):
        assert f'name="{name}"' in html, name


def test_staggered_set_shows_both_sizes(gallery):
    html = tire_set_html(gallery, "staggered")
    assert "275/35R21" in html and "315/30R21" in html


def test_form_errors_mark_each_wrong_field_and_keep_its_value(gallery):
    html = tire_set_html(gallery, "form-errors")
    page = samples.find_state(samples.find_page("tire-set"), "form-errors").data()["page"]
    assert page.form.errors
    for name, message in page.form.errors.items():
        assert f'aria-describedby="e-{name}"' in html, name
        assert message in html
    assert 'value="22555"' in html  # the wrong size as typed


def test_save_conflict_names_who_and_when_and_keeps_typed_values(gallery):
    html = tire_set_html(gallery, "save-conflict")
    assert "changed by Marcus Oyelaran" in html
    assert "11/18/2026 2:42 PM" in html
    assert "Customer asked for nitrogen fill on return" in html  # the note being typed


def test_archived_set_can_only_be_restored(gallery):
    html = tire_set_html(gallery, "archived")
    assert "Restore" in html
    assert "Check in" not in html
    assert "Archived" in html


# --- the customer view (task 3.1) ------------------------------------------------------------

CUSTOMER_STATES = [
    "active",
    "checked-out",
    "archived",
    "new",
    "no-sets",
    "duplicate",
    "form-errors",
    "edit",
    "save-conflict",
    "many-sets",
    "long-text",
]

# Where each customer state's links and buttons lead, among the customer states.
CUSTOMER_FLOW = {
    "active": {"checked-out", "edit"},
    "checked-out": {"archived", "edit"},
    "archived": {"checked-out"},
    "new": {"no-sets"},
    "no-sets": {"edit"},
    "duplicate": {"active", "no-sets"},
    "form-errors": {"no-sets"},
    "edit": {"active"},
    "save-conflict": {"active", "edit"},
    "many-sets": {"edit"},
    "long-text": {"edit"},
}


def customer_html(gallery, state: str) -> str:
    response = gallery.get(f"/mockups/pages/customer/{state}")
    assert response.status_code == 200
    return response.text


def targets_under(html: str, prefix: str) -> set[str]:
    return {
        urlsplit(target).path.removeprefix(prefix)
        for target in parse(html).targets
        if urlsplit(target).path.startswith(prefix)
    }


def test_customer_has_every_planned_state():
    assert [state.slug for state in samples.find_page("customer").states] == CUSTOMER_STATES


def test_customer_states_all_use_the_page_data_shape():
    from rollcall.views.customer import CustomerPage

    for state in samples.find_page("customer").states:
        assert isinstance(state.data()["page"], CustomerPage), state.slug
        assert state.template == "pages/customer.html", state.slug


@pytest.mark.parametrize("state", CUSTOMER_STATES)
def test_customer_states_link_to_each_other(gallery, state):
    html = customer_html(gallery, state)
    assert CUSTOMER_FLOW[state] <= targets_under(html, "/mockups/pages/customer/")


def test_customer_shows_details_sets_and_history(gallery):
    html = customer_html(gallery, "active")
    for text in ("Renata Kowalczyk", "(555) 014-2271", "renata.k@example.com", "Wheel locks"):
        assert text in html, text
    for heading in ("In the shop", "Out", "Archived", "History"):
        assert heading in html, heading
    assert count_class(html, "set") == 3
    assert count_class(html, "change") >= 4
    assert "Dana Whitfield" in html  # who made each change
    assert "11/18/2026 9:14 AM" in html  # when, in the shop's time


def test_each_set_links_to_its_page_and_can_be_checked_in_or_out(gallery):
    html = customer_html(gallery, "active")
    tire_sets = targets_under(html, "/mockups/pages/tire-set/")
    assert {"checked-in", "checked-out", "archived", "check-in"} <= tire_sets
    assert "Check out" in html and "Check in" in html


def test_customer_with_a_set_in_the_shop_cannot_be_archived(gallery):
    assert ">Archive<" not in customer_html(gallery, "active")
    assert ">Archive<" in customer_html(gallery, "checked-out")


def test_new_customer_form_asks_for_the_customer_fields(gallery):
    html = customer_html(gallery, "new")
    for name in ("first_name", "last_name", "phones-0", "email", "notes"):
        assert f'name="{name}"' in html, name


def test_customer_without_sets_offers_to_add_one(gallery):
    html = customer_html(gallery, "no-sets")
    assert "No tire sets yet" in html
    assert "new" in targets_under(html, "/mockups/pages/tire-set/")


def test_possible_duplicate_is_suggested_before_saving(gallery):
    html = customer_html(gallery, "duplicate")
    assert "Renata Kowalczyk" in html
    assert 'value="Renata"' in html  # what was typed is kept
    assert "active" in targets_under(html, "/mockups/pages/customer/")


def test_customer_form_errors_mark_each_wrong_field_and_keep_its_value(gallery):
    html = customer_html(gallery, "form-errors")
    page = samples.find_state(samples.find_page("customer"), "form-errors").data()["page"]
    assert page.form.errors
    for name, message in page.form.errors.items():
        assert f'aria-describedby="e-{name}"' in html, name
        assert message in html
    assert 'value="555-01"' in html


def test_customer_save_conflict_names_who_and_when_and_keeps_typed_values(gallery):
    html = customer_html(gallery, "save-conflict")
    assert "changed by Marcus Oyelaran" in html
    assert "11/18/2026 2:42 PM" in html
    assert "Prefers a text the day before pickup" in html


def test_customer_with_many_sets_lists_them_all(gallery):
    html = customer_html(gallery, "many-sets")
    assert count_class(html, "set") >= 7
    assert "In too long" in html


def test_long_names_and_notes_are_shown_in_full(gallery):
    html = customer_html(gallery, "long-text")
    assert "Bartholomew Alexander Vandersloot-Okonkwo" in html
    assert "never a text" in html


def test_archived_customer_can_only_be_restored(gallery):
    html = customer_html(gallery, "archived")
    assert "Restore" in html
    assert "Add tire set" not in html
    assert "Check in" not in html


# --- search (task 3.2) ---------------------------------------------------------------------

SEARCH_STATES = [
    "no-query",
    "size-digits",
    "no-results",
    "many-results",
    "many-results-2",
    "in-shop",
    "too-long",
    "archived",
]
SEARCH_FIELDS = ("name", "phone", "size", "brand", "vehicle", "VIN", "plate", "RO", "location")


def search_html(gallery, state: str) -> str:
    response = gallery.get(f"/mockups/pages/search/{state}")
    assert response.status_code == 200
    return response.text


def search_page(state: str):
    return samples.find_state(samples.find_page("search"), state).data()["page"]


def test_search_has_every_planned_state():
    assert [state.slug for state in samples.find_page("search").states] == SEARCH_STATES


def test_search_states_all_use_the_page_data_shape():
    from rollcall.views.search import SearchPage

    for state in samples.find_page("search").states:
        assert isinstance(state.data()["page"], SearchPage), state.slug
        assert state.template == "pages/search.html", state.slug


def test_navigation_search_opens_the_empty_search(gallery):
    response = gallery.get("/mockups/pages/search", follow_redirects=False)
    assert response.headers["location"] == "/mockups/pages/search/no-query"


@pytest.mark.parametrize("state", SEARCH_STATES)
def test_search_has_one_box_and_the_five_filters(gallery, state):
    html = search_html(gallery, state)
    assert html.count('name="q"') == 1
    assert 'type="search"' in html
    for label in ("All", "In shop", "Out", "Too long", "Archived"):
        assert f">{label}<" in html, label
    assert html.count('aria-current="page"') >= 1  # the chosen filter (and the nav item)
    assert "new" in targets_under(html, "/mockups/pages/customer/")  # New customer


def test_empty_search_says_what_can_be_found(gallery):
    html = search_html(gallery, "no-query")
    for field in SEARCH_FIELDS:
        assert field in html, field
    assert count_class(html, "result") == 0
    assert "No customers match" not in html


def test_size_typed_as_digits_finds_the_size(gallery):
    html = search_html(gallery, "size-digits")
    assert 'value="2256017"' in html  # what was typed stays in the box
    assert html.count("225/60R17") >= 4
    assert "3 customers, 4 sets" in html
    assert count_class(html, "result") == 3
    assert "active" in targets_under(html, "/mockups/pages/customer/")
    assert {"checked-in", "checked-out"} <= targets_under(html, "/mockups/pages/tire-set/")
    assert "Check out" in html and "Check in" in html


def test_no_results_says_so_and_points_to_archived_matches(gallery):
    html = search_html(gallery, "no-results")
    assert "No customers match" in html and "impreza" in html
    assert "archived" in targets_under(html, "/mockups/pages/search/")
    assert count_class(html, "result") == 0


def test_many_results_come_in_pages(gallery):
    first = search_html(gallery, "many-results")
    assert count_class(first, "result") == 20
    assert "1–20 of 38" in first
    assert "many-results-2" in targets_under(first, "/mockups/pages/search/")
    second = search_html(gallery, "many-results-2")
    assert count_class(second, "result") == 18
    assert "21–38 of 38" in second
    assert "many-results" in targets_under(second, "/mockups/pages/search/")


def test_too_long_filter_lists_only_sets_in_too_long(gallery):
    page = search_page("too-long")
    assert page.filter.value == "too_long" and not page.query
    assert all(item.in_too_long for result in page.results for item in result.sets)
    html = search_html(gallery, "too-long")
    assert "6 months" in html
    assert html.count(">In too long<") == page.sets == 5


@pytest.mark.parametrize("state", [s for s in SEARCH_STATES if s != "archived"])
def test_archived_customers_and_sets_are_hidden_by_default(state):
    for result in search_page(state).results:
        assert not result.archived, result.name
        assert all(item.status.value != "archived" for item in result.sets), result.name


def test_archived_filter_shows_archived_customers_and_sets_without_actions(gallery):
    page = search_page("archived")
    assert any(result.archived for result in page.results)
    assert all(item.action is None for result in page.results for item in result.sets)
    html = search_html(gallery, "archived")
    assert "Check in" not in html and "Check out" not in html
    assert 'value="impreza"' in html  # the query is kept when the filter changes


# --- the dashboard (task 3.3) ----------------------------------------------------------------

DASHBOARD_STATES = ["busy", "empty"]
STAT_LABELS = (
    "Sets in the shop",
    "In too long",
    "Checked in",
    "Checked out",
    "Customers",
)


def dashboard_html(gallery, state: str) -> str:
    response = gallery.get(f"/mockups/pages/dashboard/{state}")
    assert response.status_code == 200
    return response.text


def dashboard_page(state: str):
    return samples.find_state(samples.find_page("dashboard"), state).data()["page"]


def test_dashboard_has_every_planned_state():
    assert [state.slug for state in samples.find_page("dashboard").states] == DASHBOARD_STATES


def test_dashboard_states_all_use_the_page_data_shape():
    from rollcall.views.dashboard import DashboardPage

    for state in samples.find_page("dashboard").states:
        assert isinstance(state.data()["page"], DashboardPage), state.slug
        assert state.template == "pages/dashboard.html", state.slug


@pytest.mark.parametrize("state", DASHBOARD_STATES)
def test_dashboard_shows_the_five_numbers_each_with_a_link(gallery, state):
    html = dashboard_html(gallery, state)
    for label in STAT_LABELS:
        assert label in html, label
    assert count_class(html, "rc-stat") == 5
    assert html.count("this week, since Monday 11/16") == 2
    assert "with a set in the shop" in html
    page = dashboard_page(state)
    assert [stat.kind.label for stat in page.stats] == list(STAT_LABELS)
    for stat in page.stats:
        assert f'href="{stat.url}"' in html, stat.kind


def test_shop_wide_numbers_open_the_matching_search(gallery):
    """The search states opened agree with the numbers (sets and customers in, too long)."""
    stats = {stat.kind.value: stat for stat in dashboard_page("busy").stats}
    for kind, search_state in (
        ("in_shop", "in-shop"),
        ("too_long", "too-long"),
        ("customers", "in-shop"),
    ):
        assert urlsplit(stats[kind].url).path == f"/mockups/pages/search/{search_state}", kind
    assert stats["in_shop"].value == search_page("in-shop").sets
    assert stats["customers"].value == search_page("in-shop").customers
    assert stats["too_long"].value == search_page("too-long").sets


def test_weekly_numbers_open_this_weeks_list(gallery):
    page = dashboard_page("busy")
    weekly = [stat for stat in page.stats if stat.kind.value in ("checked_in", "checked_out")]
    assert all(stat.url.endswith("#this-week") for stat in weekly)
    assert sum(stat.value for stat in weekly) == page.this_week_total
    html = dashboard_html(gallery, "busy")
    assert 'id="this-week"' in html
    assert count_class(html, "change") == len(page.this_week) == 12
    assert "12 latest of 27" in html


def test_dashboard_starts_the_common_jobs(gallery):
    html = dashboard_html(gallery, "busy")
    assert 'name="q"' in html  # search
    assert 'type="file"' in html and 'name="invoice"' in html and "multipart/form-data" in html
    assert "from-pdf" in targets_under(html, "/mockups/pages/tire-set/")
    assert "new" in targets_under(html, "/mockups/pages/customer/")
    assert "size-digits" in targets_under(html, "/mockups/pages/search/")


def test_sets_in_too_long_stand_out_only_when_there_are_some(gallery):
    assert count_class(dashboard_html(gallery, "busy"), "rc-stat-alert") == 1
    assert count_class(dashboard_html(gallery, "empty"), "rc-stat-alert") == 0


def test_empty_shop_shows_zeros_and_says_nothing_happened(gallery):
    html = dashboard_html(gallery, "empty")
    assert all(stat.value == 0 for stat in dashboard_page("empty").stats)
    assert "Nothing checked in or out this week" in html
    assert count_class(html, "change") == 0


# --- sign-in (task 3.4) ------------------------------------------------------------------------

SIGN_IN_STATES = [
    "sign-in",
    "signed-out",
    "wrong-password",
    "deactivated",
    "first-admin",
    "first-admin-errors",
    "change-password",
    "change-password-errors",
]


def sign_in_html(gallery, state: str) -> str:
    response = gallery.get(f"/mockups/pages/sign-in/{state}")
    assert response.status_code == 200
    return response.text


def password_values(html: str) -> list[str]:
    """The value attributes of every password field (there should be none)."""
    return re.findall(r'<input[^>]*type="password"[^>]*value="([^"]*)"', html)


def test_sign_in_has_every_planned_state():
    assert [state.slug for state in samples.find_page("sign-in").states] == SIGN_IN_STATES


def test_sign_in_states_all_use_the_page_data_shape():
    from rollcall.views.sign_in import SignInPage

    for state in samples.find_page("sign-in").states:
        page = state.data()["page"]
        assert isinstance(page, SignInPage), state.slug
        assert state.template == "pages/sign_in.html", state.slug
        forms = [page.sign_in, page.setup, page.change_password]
        assert sum(form is not None for form in forms) == 1, state.slug


@pytest.mark.parametrize("state", SIGN_IN_STATES)
def test_no_password_is_ever_shown_back(gallery, state):
    html = sign_in_html(gallery, state)
    assert 'type="password"' in html
    assert all(value == "" for value in password_values(html))


@pytest.mark.parametrize("state", ["sign-in", "signed-out", "wrong-password", "deactivated"])
def test_before_sign_in_there_is_no_navigation_and_no_one_signed_in(gallery, state):
    html = sign_in_html(gallery, state)
    assert "Sign out" not in html
    assert ">Dashboard<" not in html and ">Search<" not in html


def test_sign_in_asks_for_username_and_password(gallery):
    html = sign_in_html(gallery, "sign-in")
    assert 'name="username"' in html and 'autocomplete="username"' in html
    assert 'name="password"' in html and 'autocomplete="current-password"' in html
    assert "busy" in targets_under(html, "/mockups/pages/dashboard/")


def test_sign_out_leads_to_the_signed_out_state(gallery):
    html = gallery.get("/mockups/pages/dashboard/busy").text
    assert "signed-out" in targets_under(html, "/mockups/pages/sign-in/")
    assert "Signed out." in sign_in_html(gallery, "signed-out")


def test_wrong_password_keeps_the_username_and_does_not_say_which_was_wrong(gallery):
    html = sign_in_html(gallery, "wrong-password")
    assert 'value="dana"' in html
    assert "username and password don&#39;t match" in html
    assert 'role="alert"' in html


def test_deactivated_account_is_told_to_ask_an_admin(gallery):
    html = sign_in_html(gallery, "deactivated")
    assert "turned off" in html and "admin" in html


def test_first_admin_setup_asks_for_name_username_and_password_twice(gallery):
    html = sign_in_html(gallery, "first-admin")
    for name in ("name", "username", "password", "password_again"):
        assert f'name="{name}"' in html, name
    assert html.count('autocomplete="new-password"') == 2
    assert "admin" in html
    assert "empty" in targets_under(html, "/mockups/pages/dashboard/")


def test_first_admin_errors_mark_each_field_and_keep_the_name(gallery):
    html = sign_in_html(gallery, "first-admin-errors")
    for name in ("username", "password", "password_again"):
        assert f'aria-describedby="e-{name}"' in html, name
    assert 'value="Marcus Oyelaran"' in html and 'value="marcus o"' in html


@pytest.mark.parametrize("state", ["change-password", "change-password-errors"])
def test_temporary_password_must_be_changed_before_anything_else(gallery, state):
    html = sign_in_html(gallery, state)
    assert "Jordan Pike" in html and "Sign out" in html  # signed in...
    assert ">Dashboard<" not in html and ">Search<" not in html  # ...but nowhere to go yet
    assert html.count('autocomplete="new-password"') == 2
    assert "temporary password" in html


def test_new_password_errors_are_marked(gallery):
    html = sign_in_html(gallery, "change-password-errors")
    for name in ("password", "password_again"):
        assert f'aria-describedby="e-{name}"' in html, name


# --- admin settings (task 3.5) ----------------------------------------------------------------

ADMIN_STATES = [
    "many-staff",
    "one-admin",
    "new-account",
    "account-created",
    "password-reset",
    "form-errors",
    "settings-error",
    "save-conflict",
]


def admin_html(gallery, state: str) -> str:
    response = gallery.get(f"/mockups/pages/admin/{state}")
    assert response.status_code == 200
    return response.text


def admin_page(state: str):
    return samples.find_state(samples.find_page("admin"), state).data()["page"]


def action_labels(account) -> set[str]:
    return {action.label for action in account.actions}


def test_admin_has_every_planned_state():
    assert [state.slug for state in samples.find_page("admin").states] == ADMIN_STATES


def test_admin_states_all_use_the_page_data_shape_and_an_admin_is_signed_in():
    from rollcall.views.admin import AdminPage

    for state in samples.find_page("admin").states:
        assert isinstance(state.data()["page"], AdminPage), state.slug
        assert state.template == "pages/admin.html", state.slug
        assert state.staff.is_admin, state.slug


@pytest.mark.parametrize("state", ADMIN_STATES)
def test_admin_shows_staff_accounts_and_the_too_long_setting(gallery, state):
    html = admin_html(gallery, state)
    assert "Staff accounts" in html
    assert 'name="too_long_months"' in html
    page = admin_page(state)
    assert count_class(html, "account") == len(page.accounts) + len(page.turned_off)


def test_each_account_can_be_reset_promoted_and_turned_off(gallery):
    page = admin_page("many-staff")
    staff = next(a for a in page.accounts if a.name == "Dana Whitfield")
    admin = next(a for a in page.accounts if a.name == "Inês Carvalho")
    assert action_labels(staff) == {"Reset password", "Make admin", "Turn off"}
    assert action_labels(admin) == {"Reset password", "Make staff", "Turn off"}
    assert page.turned_off
    assert all(action_labels(account) == {"Turn on"} for account in page.turned_off)
    html = admin_html(gallery, "many-staff")
    for text in ("Admin", "Turned off", "Temporary password", "Never signed in", "You"):
        assert text in html, text


def test_the_only_admin_cannot_be_made_staff_or_turned_off(gallery):
    page = admin_page("one-admin")
    admins = [a for a in page.accounts if a.is_admin]
    assert len(admins) == 1
    assert not action_labels(admins[0]) & {"Make staff", "Turn off"}
    assert "The only admin" in admin_html(gallery, "one-admin")


def test_no_admin_can_turn_off_their_own_account():
    for state in ADMIN_STATES:
        you = [a for a in admin_page(state).accounts if a.is_you]
        assert len(you) == 1, state
        assert not action_labels(you[0]) & {"Make staff", "Turn off"}, state


def test_new_account_asks_for_name_username_and_admin(gallery):
    html = admin_html(gallery, "new-account")
    for name in ("name", "username", "is_admin"):
        assert f'name="{name}"' in html, name
    assert 'type="password"' not in html  # Rollcall makes up the temporary password
    assert "account-created" in targets_under(html, "/mockups/pages/admin/")


@pytest.mark.parametrize("state", ["account-created", "password-reset"])
def test_temporary_password_is_shown_once_to_the_admin(gallery, state):
    html = admin_html(gallery, state)
    assert "Temporary password" in html or "temporary password" in html
    assert "not shown again" in html


def test_admin_form_errors_mark_each_wrong_field_and_keep_its_value(gallery):
    html = admin_html(gallery, "form-errors")
    for name in ("name", "username"):
        assert f'aria-describedby="e-{name}"' in html, name
    assert 'value="dana"' in html


def test_setting_error_keeps_the_typed_value(gallery):
    html = admin_html(gallery, "settings-error")
    assert 'aria-describedby="e-too_long_months"' in html
    assert 'value="6.5"' in html


def test_setting_save_conflict_names_who_and_when_and_keeps_the_typed_value(gallery):
    html = admin_html(gallery, "save-conflict")
    assert "changed by Inês Carvalho" in html
    assert "11/18/2026 2:42 PM" in html
    assert 'value="8"' in html


def test_staff_who_are_not_admins_do_not_see_admin_settings(gallery):
    html = gallery.get("/mockups/pages/dashboard/busy").text
    assert "Admin settings" not in html


# --- the approved design (spec: One approved design; Light and dark mode) ---------------------


def test_tire_set_uses_the_real_page_template():
    """The gallery renders the page template the real route will use (task 2.6)."""
    for state in samples.find_page("tire-set").states:
        assert state.template == "pages/tire_set.html", state.slug


@pytest.mark.parametrize("url", STATE_URLS)
def test_no_switch_between_designs_remains(gallery, url):
    html = gallery.get(url).text
    assert "?design=" not in html
    stylesheets = {t for t in parse(html).targets if t.split("?")[0].endswith(".css")}
    assert {t.split("?")[0] for t in stylesheets} == {
        "/static/vendor/pico-2.1.1.min.css",
        "/static/app.css",
    }


def test_candidate_designs_are_gone():
    from rollcall.web import STATIC_DIR, TEMPLATES_DIR

    assert not (TEMPLATES_DIR / "mockups" / "discovery").exists()
    assert not (STATIC_DIR / "mockups").exists()


def test_gallery_pages_have_the_light_dark_switch_returning_to_the_same_state(gallery):
    html = gallery.get("/mockups/pages/tire-set/edit?from=test").text
    assert 'action="/theme"' in html
    assert 'name="next" value="/mockups/pages/tire-set/edit?from=test"' in html


def test_approved_design_is_drawn_in_the_chosen_mode(gallery):
    gallery.cookies.clear()
    try:
        gallery.post("/theme", data={"mode": "dark", "next": "/"}, follow_redirects=False)
        html = gallery.get("/mockups/pages/tire-set/checked-in").text
        assert re.search(r'<html[^>]*data-theme="dark"', html)
    finally:
        gallery.cookies.clear()


# --- the sample invoice (spec: Sample PDF beside the form) -------------------------------------


def test_sample_invoice_is_served_as_a_pdf(gallery):
    response = gallery.get(SAMPLE_INVOICE_URL)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF-")


def test_sample_invoice_may_be_shown_inside_rollcall_pages_only(gallery):
    """frame-ancestors 'self' on the PDF; the rest of the policy is unchanged."""
    policy = gallery.get(SAMPLE_INVOICE_URL).headers["content-security-policy"]
    assert policy == (
        "default-src 'self'; frame-ancestors 'self'; base-uri 'self'; form-action 'self'"
    )


@pytest.mark.parametrize("url", ["/", "/mockups", STATE_URLS[0], "/static/app.css", "/x"])
def test_everything_else_still_refuses_to_be_framed(gallery, url):
    policy = gallery.get(url).headers["content-security-policy"]
    assert "frame-ancestors 'none'" in policy


def test_committed_sample_invoice_is_what_the_script_makes():
    """The PDF in the repo is the script's output, so it holds only the script's invented data."""
    script = runpy.run_path(str(REPO_DIR / "scripts" / "make_sample_invoice.py"))
    assert script["build"]() == script["OUTPUT"].read_bytes()


def test_sample_invoice_has_the_labels_the_prefill_reads():
    """Laid out like a Protractor invoice (v1-lessons.md), with invented values."""
    script = runpy.run_path(str(REPO_DIR / "scripts" / "make_sample_invoice.py"))
    text = "\n".join(script["lines_text"]())
    assert text.startswith("Invoice\n")
    for label in ("Bill To", "Description", "VIN", "Invoice #", "Work Order #", "Invoice Date"):
        assert label in text, label
    assert "Seasonal Tire Storage" in text
    assert "Notes__" in text


# --- switched off --------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "path", ["/mockups", "/mockups/", "/mockups/pages/tire-set/checked-in", SAMPLE_INVOICE_URL]
)
def test_gallery_is_not_found_when_switched_off(client, path):
    response = client.get(path)
    assert response.status_code == 404
    assert "Page not found" in response.text


def test_gallery_setting_is_off_in_the_default_test_settings(settings):
    assert dataclasses.replace(settings).mockups is False
