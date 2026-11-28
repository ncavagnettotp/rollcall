"""The registry of everything the mockup gallery shows, with its invented sample data.

Every page lists its named states; each state names its template and builds the page data from
rollcall/views/. The gallery index, the gallery routes and tests/test_mockups.py all read this
registry, so a state added here is shown and checked automatically.

All names, phone numbers, VINs, plates and RO numbers here are invented. Never copy anything
from a real invoice.
"""

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from rollcall.mockups import admin_samples as admin
from rollcall.mockups import customer_samples as customer
from rollcall.mockups import dashboard_samples as dashboard
from rollcall.mockups import search_samples as search
from rollcall.mockups import sign_in_samples as sign_in
from rollcall.mockups import tire_set_samples as tire_set
from rollcall.mockups.urls import INDEX_URL, component_url, page_url
from rollcall.views.frame import SignedInStaff
from rollcall.web import NavItem

# --- who is signed in, and the navigation they see ----------------------------------------------

SIGNED_OUT = page_url("sign-in", "signed-out")
STAFF = SignedInStaff(name="Dana Whitfield", is_admin=False, sign_out_url=SIGNED_OUT)
ADMIN = SignedInStaff(name="Marcus Oyelaran", is_admin=True, sign_out_url=SIGNED_OUT)
JORDAN = SignedInStaff(name="Jordan Pike", is_admin=False, sign_out_url=SIGNED_OUT)


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
    navigation: bool = True  # False: signed in, but nothing else may be opened yet


@dataclass(frozen=True)
class Page:
    slug: str
    title: str
    states: tuple[State, ...]  # at least one; the page opens the first

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
CUSTOMER_TEMPLATE = "pages/customer.html"
SEARCH_TEMPLATE = "pages/search.html"
DASHBOARD_TEMPLATE = "pages/dashboard.html"
SIGN_IN_TEMPLATE = "pages/sign_in.html"
ADMIN_TEMPLATE = "pages/admin.html"


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
                    "In the shop: where it is, this stay's RO, and three past stays.",
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
                    "Adding a set to a customer, checked in as it is saved.",
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
                    "Checking a set back in: date, RO and storage location.",
                    tire_set.check_in,
                ),
                (
                    "staggered",
                    "Staggered, long text",
                    "Two sizes, very long names and notes, in the shop too long.",
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
    Page(
        "customer",
        "Customer",
        tuple(
            State(slug, title, description, CUSTOMER_TEMPLATE, data)
            for slug, title, description, data in (
                (
                    "active",
                    "With sets in and out",
                    "Details, a set in the shop, one out, one archived, and the history.",
                    customer.active,
                ),
                (
                    "checked-out",
                    "All sets out",
                    "Just checked a set out from this page; with nothing in the shop, it can be "
                    "archived.",
                    customer.checked_out,
                ),
                (
                    "archived",
                    "Archived",
                    "Hidden from search with their sets, history kept; it can be restored.",
                    customer.archived,
                ),
                ("new", "New customer", "The empty customer form.", customer.new),
                (
                    "no-sets",
                    "Just added, no sets",
                    "A new customer with no tire sets yet.",
                    customer.no_sets,
                ),
                (
                    "duplicate",
                    "Possible duplicate",
                    "The name and phone typed match an existing customer.",
                    customer.duplicate,
                ),
                (
                    "form-errors",
                    "Form errors",
                    "Saved with three mistakes: each marked, with its message and typed value.",
                    customer.form_errors,
                ),
                ("edit", "Edit", "Changing a customer's details.", customer.edit),
                (
                    "save-conflict",
                    "Save conflict",
                    "Someone else saved the customer meanwhile; the typed values are kept.",
                    customer.save_conflict,
                ),
                (
                    "many-sets",
                    "Many sets",
                    "A family with eight sets: three in the shop (one too long), four out, one "
                    "archived.",
                    customer.many_sets,
                ),
                (
                    "long-text",
                    "Long text",
                    "A very long name, three phones, a long email and long notes.",
                    customer.long_text,
                ),
            )
        ),
    ),
    Page(
        "search",
        "Search",
        tuple(
            State(slug, title, description, SEARCH_TEMPLATE, data)
            for slug, title, description, data in (
                (
                    "no-query",
                    "Nothing typed yet",
                    "The search box, what it can find, and the filters.",
                    search.no_query,
                ),
                (
                    "size-digits",
                    "Size typed as digits",
                    "2256017 finds 225/60R17: three customers, four sets.",
                    search.size_digits,
                ),
                (
                    "no-results",
                    "No results",
                    "Nothing matches, but archived customers or sets do.",
                    search.no_results,
                ),
                (
                    "many-results",
                    "Many results",
                    "38 customers with a Toyota: the first 20, and a link to the next page.",
                    search.many_results,
                ),
                (
                    "many-results-2",
                    "Many results, page 2",
                    "The last 18, and a link back.",
                    search.many_results_2,
                ),
                (
                    "in-shop",
                    "In shop",
                    "From the dashboard: every set in the shop, longest first (page 1 of 6).",
                    search.in_shop_filter,
                ),
                (
                    "too-long",
                    "In too long",
                    "Opened from the dashboard: every set in the shop longer than 6 months.",
                    search.too_long,
                ),
                (
                    "archived",
                    "Archived",
                    "The archived filter: archived customers and archived sets.",
                    search.archived,
                ),
            )
        ),
    ),
    Page(
        "dashboard",
        "Dashboard",
        (
            State(
                "busy",
                "A busy week",
                "The middle of the switch to winter tires: the five numbers, search, the invoice "
                "upload and this week's check-ins and check-outs.",
                DASHBOARD_TEMPLATE,
                dashboard.busy,
            ),
            State(
                "empty",
                "An empty shop",
                "A fresh install: every number is 0 and nothing has happened this week.",
                DASHBOARD_TEMPLATE,
                dashboard.empty,
            ),
        ),
    ),
    Page(
        "sign-in",
        "Sign in",
        (
            *(
                State(slug, title, description, SIGN_IN_TEMPLATE, data, staff=None)
                for slug, title, description, data in (
                    ("sign-in", "Sign in", "Username and password.", sign_in.sign_in),
                    (
                        "signed-out",
                        "Signed out",
                        "Where Sign out leads, from any page.",
                        sign_in.signed_out,
                    ),
                    (
                        "wrong-password",
                        "Wrong password",
                        "The username is kept; the message never says which of the two was wrong.",
                        sign_in.wrong_password,
                    ),
                    (
                        "deactivated",
                        "Deactivated account",
                        "The right password for an account an admin turned off.",
                        sign_in.deactivated,
                    ),
                    (
                        "first-admin",
                        "First admin",
                        "A fresh install with no accounts: the first account is the admin.",
                        sign_in.first_admin,
                    ),
                    (
                        "first-admin-errors",
                        "First admin, errors",
                        "A username with a space, a short password, and two that differ.",
                        sign_in.first_admin_errors,
                    ),
                )
            ),
            *(
                State(
                    slug, title, description, SIGN_IN_TEMPLATE, data, staff=JORDAN, navigation=False
                )
                for slug, title, description, data in (
                    (
                        "change-password",
                        "Temporary password",
                        "Signed in with the temporary password an admin gave: a new one first.",
                        sign_in.change_password,
                    ),
                    (
                        "change-password-errors",
                        "Temporary password, errors",
                        "A new password too short, and two that differ.",
                        sign_in.change_password_errors,
                    ),
                )
            ),
        ),
    ),
    Page(
        "admin",
        "Admin settings",
        tuple(
            State(slug, title, description, ADMIN_TEMPLATE, data, staff=ADMIN)
            for slug, title, description, data in (
                (
                    "many-staff",
                    "Many staff",
                    "Two admins, five staff (one still on a temporary password), one turned off; "
                    "and the too-long setting.",
                    admin.many_staff,
                ),
                (
                    "one-admin",
                    "One admin only",
                    "The only admin can't be made staff or turned off.",
                    admin.one_admin,
                ),
                (
                    "new-account",
                    "New staff account",
                    "Name, username, and whether it is an admin.",
                    admin.new_account,
                ),
                (
                    "account-created",
                    "Account made",
                    "The temporary password Rollcall made up, shown once.",
                    admin.account_created,
                ),
                (
                    "password-reset",
                    "Password reset",
                    "A new temporary password for someone who forgot theirs, shown once.",
                    admin.password_reset,
                ),
                (
                    "form-errors",
                    "Form errors",
                    "No name, and a username already taken.",
                    admin.form_errors,
                ),
                (
                    "settings-error",
                    "Setting error",
                    "Too long set to 6.5 months.",
                    admin.settings_error,
                ),
                (
                    "save-conflict",
                    "Save conflict",
                    "Another admin changed the setting meanwhile; the typed value is kept.",
                    admin.save_conflict,
                ),
            )
        ),
    ),
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
