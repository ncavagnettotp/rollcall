"""The registry of everything the mockup gallery shows, with its invented sample data.

Every page lists its named states; each state names its template and builds the page data from
rollcall/views/. The gallery index, the gallery routes and tests/test_mockups.py all read this
registry, so a state added here is shown and checked automatically.

All names, phone numbers, VINs, plates and RO numbers here are invented. Never copy anything
from a real invoice.
"""

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field

from rollcall.mockups import tire_set_samples as tire_set
from rollcall.mockups.urls import INDEX_URL, component_url, page_url
from rollcall.views.frame import SignedInStaff
from rollcall.web import NavItem

# --- who is signed in, and the navigation they see ----------------------------------------------

STAFF = SignedInStaff(name="Dana Whitfield", is_admin=False, sign_out_url=page_url("sign-in"))
ADMIN = SignedInStaff(name="Marcus Oyelaran", is_admin=True, sign_out_url=page_url("sign-in"))


def navigation(staff: SignedInStaff | None) -> list[NavItem]:
    """The planned navigation: what a signed-in staff member (or admin) will see."""
    if staff is None:
        return []
    items = [NavItem("Dashboard", page_url("dashboard")), NavItem("Search", page_url("search"))]
    if staff.is_admin:
        items.append(NavItem("Admin settings", page_url("admin")))
    return items


# --- the registry ------------------------------------------------------------------------------


@dataclass(frozen=True)
class Banner:
    """The "Mockup: sample data" banner at the top of every gallery page."""

    title: str
    index_url: str = INDEX_URL
    home_url: str = INDEX_URL


@dataclass(frozen=True)
class State:
    slug: str
    title: str
    description: str
    template: str
    data: Callable[[], Mapping[str, object]] = dict  # the template's values, built on request
    staff: SignedInStaff | None = STAFF  # who is signed in; None for pages before sign-in


@dataclass(frozen=True)
class Page:
    slug: str
    title: str
    states: tuple[State, ...] = field(default_factory=tuple)

    @property
    def url(self) -> str:
        return page_url(self.slug)

    def state_url(self, state: State) -> str:
        return page_url(self.slug, state.slug)


@dataclass(frozen=True)
class Component:
    slug: str
    title: str
    description: str
    template: str  # a gallery template showing the component's variations

    @property
    def url(self) -> str:
        return component_url(self.slug)


TIRE_SET_TEMPLATE = "pages/tire_set.html"


def _frame_note() -> Mapping[str, object]:
    return {"note": "Every page sits in this frame. The page's own content goes here."}


PAGES: tuple[Page, ...] = (
    Page(
        "frame",
        "Page frame",
        (
            State(
                "staff",
                "Signed in as staff",
                "The header a staff member sees: navigation, their name, sign out.",
                "mockups/frame.html",
                _frame_note,
            ),
            State(
                "admin",
                "Signed in as an admin",
                "Admins also see Admin settings in the navigation.",
                "mockups/frame.html",
                _frame_note,
                staff=ADMIN,
            ),
        ),
    ),
    Page(
        "tire-set",
        "Tire set",
        tuple(
            State(slug, title, description, TIRE_SET_TEMPLATE, data)
            for slug, title, description, data in (
                (
                    "checked-in",
                    "Checked in",
                    "In the shop: where it is, this stay's RO and tread, and three past stays.",
                    tire_set.checked_in,
                ),
                (
                    "checked-out",
                    "Checked out",
                    "Back with the customer, with three past stays. Can be checked in or archived.",
                    tire_set.checked_out,
                ),
                (
                    "new",
                    "New set",
                    "Adding a set to a customer: four empty tire rows, checked in as it is saved.",
                    tire_set.new_set,
                ),
                (
                    "from-pdf",
                    "Filled from a PDF",
                    "The form filled from an invoice, with the invoice beside it.",
                    tire_set.from_pdf,
                ),
                (
                    "check-in",
                    "Check-in step",
                    "Checking a set back in: date, RO, storage location and tread per tire.",
                    tire_set.check_in,
                ),
                (
                    "staggered",
                    "Staggered, five tires, long text",
                    "Two sizes, a spare, very long names and notes, in the shop too long.",
                    tire_set.staggered,
                ),
                (
                    "edit",
                    "Edit",
                    "Changing a saved set's details.",
                    tire_set.edit,
                ),
                (
                    "form-errors",
                    "Form errors",
                    "Saved with three mistakes: each marked, with its message and typed value.",
                    tire_set.form_errors,
                ),
                (
                    "save-conflict",
                    "Save conflict",
                    "Someone else saved the set meanwhile; the typed values are kept.",
                    tire_set.save_conflict,
                ),
                (
                    "archived",
                    "Archived",
                    "Hidden from search, history kept; it can be restored.",
                    tire_set.archived,
                ),
            )
        ),
    ),
    Page("customer", "Customer"),
    Page("search", "Search"),
    Page("dashboard", "Dashboard"),
    Page("sign-in", "Sign in"),
    Page("admin", "Admin settings"),
)

COMPONENTS: tuple[Component, ...] = (
    Component(
        "field",
        "Form field",
        "A labeled field, with a hint, required, and with an error.",
        "mockups/components/field.html",
    ),
    Component(
        "button",
        "Button",
        "The button kinds: primary, secondary, quiet and link.",
        "mockups/components/button.html",
    ),
    Component(
        "table",
        "Table",
        "A table with rows, and with none.",
        "mockups/components/table.html",
    ),
)


def find_page(slug: str) -> Page | None:
    return next((page for page in PAGES if page.slug == slug), None)


def find_state(page: Page, slug: str) -> State | None:
    return next((state for state in page.states if state.slug == slug), None)


def find_component(slug: str) -> Component | None:
    return next((component for component in COMPONENTS if component.slug == slug), None)
