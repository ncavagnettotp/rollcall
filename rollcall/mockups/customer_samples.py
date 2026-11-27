"""Sample data for the customer view's gallery states. Every name and number is invented.

Renata Kowalczyk continues the tire set page's story: on 11/18/2026 her summer set (Bridgestone
Alenza) was checked in and her winter set (Michelin X-Ice Snow) went home; her old Nokian set is
archived. "Today" in the gallery is 11/18/2026; times are UTC and shown in the shop's zone.

Links point at the gallery state that shows the result:
active -> check out -> checked-out -> archive -> archived -> restore -> checked-out;
new -> save -> no-sets; edit -> save -> active.
"""

from dataclasses import replace
from datetime import UTC, date, datetime

from rollcall.mockups.urls import page_url
from rollcall.views.customer import (
    Change,
    CustomerDetails,
    CustomerForm,
    CustomerInput,
    CustomerPage,
    PossibleDuplicate,
    SetSummary,
)
from rollcall.views.shared import Action, Conflict, Link, Message
from rollcall.views.tire_set import Status


def state(slug: str) -> str:
    return page_url("customer", slug)


def tire_set(slug: str) -> str:
    return page_url("tire-set", slug)


def at(year: int, month: int, day: int, hour: int, minute: int) -> datetime:
    """A moment in UTC (the shop is six hours behind in November, five in summer)."""
    return datetime(year, month, day, hour, minute, tzinfo=UTC)


TODAY = date(2026, 11, 18)
DANA = "Dana Whitfield"
MARCUS = "Marcus Oyelaran"
SEARCH_URL = page_url("search")
EDIT = Action("Edit", state("edit"), kind="secondary")


def add_set(url: str = tire_set("new")) -> Action:
    return Action("Add tire set", url)


def check_out(url: str) -> Action:
    return Action("Check out", url, post=True, kind="secondary")


def check_in(url: str) -> Action:
    return Action("Check in", url, kind="secondary")


# --- Renata ---------------------------------------------------------------------------------

RENATA = CustomerDetails(
    phones=("(555) 014-2271",),
    email="renata.k@example.com",
    notes="Wheel locks in the trunk, key in the glovebox.",
)
ALENZA = "225/60R17 Bridgestone Alenza"
X_ICE = "225/60R17 Michelin X-Ice Snow"
NOKIAN = "205/60R16 Nokian Hakkapeliitta R5"
VEHICLE = "2019 Subaru Outback"

ALENZA_IN = SetSummary(
    ALENZA,
    tire_set("checked-in"),
    Status.IN_SHOP,
    in_too_long=False,
    location="Rack B3",
    since=date(2026, 11, 18),
    ro_number="48213",
    vehicle=VEHICLE,
    action=check_out(state("checked-out")),
)
ALENZA_OUT = replace(
    ALENZA_IN,
    url=tire_set("checked-out"),
    status=Status.OUT,
    location=None,
    ro_number=None,
    action=check_in(tire_set("check-in")),
)
X_ICE_OUT = SetSummary(
    X_ICE,
    tire_set("checked-out"),
    Status.OUT,
    in_too_long=False,
    location=None,
    since=date(2026, 11, 18),
    ro_number=None,
    vehicle=VEHICLE,
    action=check_in(tire_set("check-in")),
)
NOKIAN_ARCHIVED = SetSummary(
    NOKIAN,
    tire_set("archived"),
    Status.ARCHIVED,
    in_too_long=False,
    location=None,
    since=date(2026, 4, 30),
    ro_number=None,
    vehicle="2014 Subaru Impreza",
    action=None,
)

RENATA_HISTORY = (
    Change(
        at(2026, 11, 18, 15, 14),
        DANA,
        "Checked in at Rack B3, RO 48213",
        Link(ALENZA, tire_set("checked-in")),
    ),
    Change(at(2026, 11, 18, 15, 12), DANA, "Checked out", Link(X_ICE, tire_set("checked-out"))),
    Change(at(2026, 4, 30, 19, 5), MARCUS, "Archived the set", Link(NOKIAN, tire_set("archived"))),
    Change(at(2026, 4, 20, 14, 40), DANA, "Checked out", Link(ALENZA, tire_set("checked-out"))),
    Change(
        at(2026, 4, 20, 14, 38),
        DANA,
        "Checked in at Rack C1, RO 47390",
        Link(X_ICE, tire_set("checked-out")),
    ),
    Change(at(2026, 3, 2, 16, 21), MARCUS, "Changed the phone to (555) 014-2271"),
)


def _renata(**changes) -> CustomerPage:
    page = CustomerPage(
        title="Renata Kowalczyk",
        archived_on=None,
        details=RENATA,
        in_shop=(ALENZA_IN,),
        out=(X_ICE_OUT,),
        archived_sets=(NOKIAN_ARCHIVED,),
        history=RENATA_HISTORY,
        actions=(add_set(), EDIT),
        add_set_url=tire_set("new"),
    )
    return replace(page, **changes)


def active() -> dict:
    return {"page": _renata()}


CHECKED_OUT_HISTORY = (
    Change(at(2026, 11, 18, 17, 30), DANA, "Checked out", Link(ALENZA, tire_set("checked-out"))),
    *RENATA_HISTORY,
)


def checked_out() -> dict:
    return {
        "page": _renata(
            in_shop=(),
            out=(ALENZA_OUT, X_ICE_OUT),
            history=CHECKED_OUT_HISTORY,
            actions=(
                add_set(),
                EDIT,
                Action("Archive", state("archived"), post=True, kind="quiet"),
            ),
            messages=(Message(f"Checked out {ALENZA}."),),
        )
    }


def archived() -> dict:
    no_action = (replace(ALENZA_OUT, action=None), replace(X_ICE_OUT, action=None))
    return {
        "page": _renata(
            archived_on=TODAY,
            in_shop=(),
            out=no_action,
            history=(
                Change(at(2026, 11, 18, 17, 34), MARCUS, "Archived the customer"),
                *CHECKED_OUT_HISTORY,
            ),
            actions=(Action("Restore", state("checked-out"), post=True, kind="secondary"),),
            add_set_url=None,
        )
    }


# --- a new customer ---------------------------------------------------------------------------


def _new_form(**changes) -> CustomerForm:
    form = CustomerForm(
        heading="New customer",
        action_url=state("no-sets"),
        cancel_url=SEARCH_URL,
        submit_label="Save customer",
        values=CustomerInput(),
    )
    return replace(form, **changes)


def _form_page(form: CustomerForm, title: str, messages=()) -> CustomerPage:
    return CustomerPage(
        title=title,
        archived_on=None,
        details=None,
        in_shop=(),
        out=(),
        archived_sets=(),
        history=(),
        actions=(),
        add_set_url=None,
        messages=messages,
        form=form,
    )


def new() -> dict:
    return {"page": _form_page(_new_form(), "New customer")}


def no_sets() -> dict:
    return {
        "page": CustomerPage(
            title="Marisol Tanaka-Brooks",
            archived_on=None,
            details=CustomerDetails(("(555) 016-3390",), "marisol.tb@example.com", None),
            in_shop=(),
            out=(),
            archived_sets=(),
            history=(Change(at(2026, 11, 18, 16, 2), DANA, "Added the customer"),),
            actions=(add_set(), EDIT),
            add_set_url=tire_set("new"),
            messages=(Message("Customer added. Add their first tire set."),),
        )
    }


def duplicate() -> dict:
    typed = CustomerInput("Renata", "Kowalczyk", ("(555) 014-2271",), "", "")
    form = _new_form(
        values=typed,
        submit_label="Save as a new customer",
        duplicates=(PossibleDuplicate("Renata Kowalczyk", ("(555) 014-2271",), state("active")),),
    )
    return {"page": _form_page(form, "New customer")}


def form_errors() -> dict:
    typed = CustomerInput("Marisol", "", ("555-01",), "marisol.tb@", "")
    errors = {
        "last_name": "Enter a last name.",
        "phones-0": "Enter a full phone number, e.g. (555) 014-2271.",
        "email": "Check the email address: a name, @ and a domain, e.g. name@example.com.",
    }
    messages = (Message("Three values need fixing before the customer can be saved.", "error"),)
    return {"page": _form_page(_new_form(values=typed, errors=errors), "New customer", messages)}


# --- editing Renata ---------------------------------------------------------------------------

RENATA_INPUT = CustomerInput(
    "Renata", "Kowalczyk", RENATA.phones, "renata.k@example.com", RENATA.notes or ""
)


def _edit_form(**changes) -> CustomerForm:
    form = CustomerForm(
        heading="Edit customer",
        action_url=state("active"),
        cancel_url=state("active"),
        submit_label="Save",
        values=RENATA_INPUT,
    )
    return replace(form, **changes)


def edit() -> dict:
    return {"page": _form_page(_edit_form(), "Renata Kowalczyk")}


def save_conflict() -> dict:
    typed = replace(
        RENATA_INPUT,
        notes="Wheel locks in the trunk, key in the glovebox. "
        "Prefers a text the day before pickup.",
    )
    conflict = Conflict(MARCUS, at(2026, 11, 18, 20, 42), state("edit"))
    return {"page": _form_page(_edit_form(values=typed, conflict=conflict), "Renata Kowalczyk")}


# --- many sets ------------------------------------------------------------------------------


def many_sets() -> dict:
    def summary(title, slug, status, since, vehicle, location=None, ro=None, too_long=False):
        action = {
            Status.IN_SHOP: check_out(state("many-sets")),
            Status.OUT: check_in(tire_set("check-in")),
            Status.ARCHIVED: None,
        }[status]
        return SetSummary(
            title, tire_set(slug), status, too_long, location, since, ro, vehicle, action
        )

    in_shop = (
        summary(
            "235/65R18 Michelin CrossClimate 2",
            "checked-in",
            Status.IN_SHOP,
            date(2026, 11, 10),
            "2021 Honda Pilot",
            "Rack A4",
            "48102",
        ),
        summary(
            "215/55R17 Continental WinterContact SI",
            "checked-in",
            Status.IN_SHOP,
            date(2026, 10, 28),
            "2018 Toyota Camry",
            "Rack A5",
            "47988",
        ),
        summary(
            "265/70R17 BFGoodrich All-Terrain T/A KO2",
            "staggered",
            Status.IN_SHOP,
            date(2026, 3, 3),
            "2016 Ford F-150",
            "Yard shed 2",
            "47160",
            too_long=True,
        ),
    )
    out = (
        summary(
            "235/65R18 Bridgestone Blizzak DM-V2",
            "checked-out",
            Status.OUT,
            date(2026, 11, 10),
            "2021 Honda Pilot",
        ),
        summary(
            "215/55R17 Michelin Defender2",
            "checked-out",
            Status.OUT,
            date(2026, 10, 28),
            "2018 Toyota Camry",
        ),
        summary(
            "195/65R15 Hankook Winter i*cept",
            "checked-out",
            Status.OUT,
            date(2026, 4, 2),
            "2012 Toyota Prius",
        ),
        summary(
            "265/70R17 General Grabber X3",
            "checked-out",
            Status.OUT,
            date(2026, 3, 3),
            "2016 Ford F-150",
        ),
    )
    archived_sets = (
        summary(
            "205/55R16 Goodyear Assurance",
            "archived",
            Status.ARCHIVED,
            date(2025, 6, 9),
            "2009 Honda Civic",
        ),
    )
    return {
        "page": CustomerPage(
            title="Thandiwe Abernathy-Reyes",
            archived_on=None,
            details=CustomerDetails(
                ("(555) 017-6402", "(555) 011-9283"),
                "thandiwe.ar@example.com",
                "Family account: four vehicles. Ask which car before checking a set out.",
            ),
            in_shop=in_shop,
            out=out,
            archived_sets=archived_sets,
            history=(
                Change(
                    at(2026, 11, 10, 18, 3),
                    DANA,
                    "Checked in at Rack A4, RO 48102",
                    Link(in_shop[0].title, in_shop[0].url),
                ),
                Change(
                    at(2026, 11, 10, 18, 1), DANA, "Checked out", Link(out[0].title, out[0].url)
                ),
                Change(
                    at(2026, 10, 28, 15, 47),
                    MARCUS,
                    "Checked in at Rack A5, RO 47988",
                    Link(in_shop[1].title, in_shop[1].url),
                ),
            ),
            actions=(add_set(), EDIT),
            add_set_url=tire_set("new"),
        )
    }


# --- long text --------------------------------------------------------------------------------


def long_text() -> dict:
    pirelli = SetSummary(
        "275/35R21 and 315/30R21 Pirelli P Zero PZ4 Elect Run Flat NCS",
        tire_set("staggered"),
        Status.IN_SHOP,
        in_too_long=True,
        location="Mezzanine overflow rack, far left bay behind the alignment machine, top shelf",
        since=date(2026, 3, 2),
        ro_number="47205",
        vehicle="2022 Porsche Taycan 4S Cross Turismo Performance Battery Plus",
        action=check_out(state("long-text")),
    )
    return {
        "page": CustomerPage(
            title="Bartholomew Alexander Vandersloot-Okonkwo",
            archived_on=None,
            details=CustomerDetails(
                ("(555) 019-8830", "(555) 012-4471", "(555) 018-0057"),
                "bartholomew.vandersloot-okonkwo.office@family-holdings.example.com",
                "Prefers a call to Jonathan (assistant) before pickup, never a text. The second "
                "number is the house in the summer, the third the office; leave no voicemail at "
                "the office. Pays on pickup only, by card, and wants the old invoice reprinted "
                "every time. The Taycan's wheels must never touch the impact gun.",
            ),
            in_shop=(pirelli,),
            out=(),
            archived_sets=(),
            history=(
                Change(
                    at(2026, 3, 2, 21, 55),
                    MARCUS,
                    f"Checked in at {pirelli.location}, RO 47205",
                    Link(pirelli.title, pirelli.url),
                ),
            ),
            actions=(add_set(), EDIT),
            add_set_url=tire_set("new"),
        )
    }
