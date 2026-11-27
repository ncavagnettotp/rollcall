"""Sample data for the dashboard's gallery states. Every name and number is invented.

"Today" in the gallery is Wednesday 11/18/2026, in the middle of the switch to winter tires: this
week started Monday 11/16. The busy shop's numbers agree with the search states they open
(142 sets and 118 customers in the shop, 5 sets in too long).
"""

from datetime import UTC, date, datetime

from rollcall.mockups import customer_samples as customer
from rollcall.mockups import search_samples as search
from rollcall.mockups.urls import page_url
from rollcall.views.customer import Change
from rollcall.views.dashboard import DashboardPage, Stat, StatKind
from rollcall.views.shared import Action, Link

WEEK_START = date(2026, 11, 16)
WEEK_NOTE = "this week, since Monday 11/16"
NEW_CUSTOMER = Action("New customer", page_url("customer", "new"), kind="secondary")
SEARCH_TARGET = page_url("search", "size-digits")
UPLOAD_TARGET = page_url("tire-set", "from-pdf")


def state(slug: str) -> str:
    return page_url("dashboard", slug)


def tire_set(slug: str) -> str:
    return page_url("tire-set", slug)


def at(day: int, hour: int, minute: int) -> datetime:
    """A moment this week, in UTC (the shop is six hours behind)."""
    return datetime(2026, 11, day, hour, minute, tzinfo=UTC)


def stats(here: str, in_shop, too_long, checked_in, checked_out, customers) -> tuple[Stat, ...]:
    week = state(here) + "#this-week"
    return (
        Stat(StatKind.IN_SHOP, in_shop, page_url("search", "in-shop") + "?filter=in_shop"),
        Stat(
            StatKind.TOO_LONG,
            too_long,
            page_url("search", "too-long") + "?filter=too_long",
            "over 6 months",
        ),
        Stat(StatKind.CHECKED_IN, checked_in, week, WEEK_NOTE),
        Stat(StatKind.CHECKED_OUT, checked_out, week, WEEK_NOTE),
        Stat(
            StatKind.CUSTOMERS,
            customers,
            page_url("search", "in-shop") + "?filter=in_shop",
            "with a set in the shop",
        ),
    )


def _checked_in(when, by, name, title, slug, place) -> Change:
    return Change(when, by, f"{name}: checked in at {place}", Link(title, tire_set(slug)))


def _checked_out(when, by, name, title, slug) -> Change:
    return Change(when, by, f"{name}: checked out", Link(title, tire_set(slug)))


DANA, MARCUS = customer.DANA, customer.MARCUS
THIS_WEEK = (
    _checked_in(
        at(18, 21, 5),
        DANA,
        "Graham Whitlock",
        "225/60R17 Michelin Defender LTX M/S",
        "checked-in",
        "Rack C2, RO 48240",
    ),
    _checked_out(
        at(18, 20, 31), MARCUS, "Lucía Ferreira-Dunn", "215/60R16 Nokian WR G4", "checked-out"
    ),
    _checked_in(
        at(18, 19, 48),
        MARCUS,
        "Lucía Ferreira-Dunn",
        "225/60R17 Goodyear Assurance WeatherReady",
        "checked-in",
        "Rack A6, RO 48236",
    ),
    _checked_in(
        at(18, 17, 2),
        DANA,
        "Thandiwe Abernathy-Reyes",
        "235/65R18 Michelin CrossClimate 2",
        "checked-in",
        "Rack A4, RO 48229",
    ),
    _checked_in(
        at(18, 15, 14),
        DANA,
        "Renata Kowalczyk",
        customer.ALENZA,
        "checked-in",
        "Rack B3, RO 48213",
    ),
    _checked_out(at(18, 15, 12), DANA, "Renata Kowalczyk", customer.X_ICE, "checked-out"),
    _checked_in(
        at(17, 22, 40),
        MARCUS,
        "Walter Ng",
        "205/55R16 Michelin Defender2",
        "checked-in",
        "Rack A2, RO 48201",
    ),
    _checked_in(
        at(17, 18, 9),
        DANA,
        "Priya Raghunathan",
        "245/45R18 Bridgestone Turanza QuietTrack",
        "checked-in",
        "Rack D1, RO 48194",
    ),
    _checked_out(
        at(17, 16, 55), DANA, "Priya Raghunathan", "245/45R18 Nokian WR G4", "checked-out"
    ),
    _checked_in(
        at(17, 15, 30),
        MARCUS,
        "Amara Lindqvist",
        "215/55R17 Michelin CrossClimate 2",
        "checked-in",
        "Rack E3, RO 48188",
    ),
    _checked_in(
        at(16, 21, 12),
        DANA,
        "Farid Moreau",
        "265/70R17 Falken Wildpeak A/T3W",
        "checked-in",
        "Yard shed 1, RO 48175",
    ),
    _checked_out(
        at(16, 14, 47), MARCUS, "Esther Szabo", "195/65R15 Hankook Winter i*cept", "checked-out"
    ),
)


def busy() -> dict:
    return {
        "page": DashboardPage(
            title="Dashboard",
            stats=stats("busy", search.IN_SHOP_SETS, 5, 23, 4, search.IN_SHOP_CUSTOMERS),
            search_url=SEARCH_TARGET,
            upload_url=UPLOAD_TARGET,
            week_start=WEEK_START,
            this_week=THIS_WEEK,
            this_week_total=27,
            actions=(NEW_CUSTOMER,),
        )
    }


def empty() -> dict:
    return {
        "page": DashboardPage(
            title="Dashboard",
            stats=stats("empty", 0, 0, 0, 0, 0),
            search_url=SEARCH_TARGET,
            upload_url=UPLOAD_TARGET,
            week_start=WEEK_START,
            this_week=(),
            this_week_total=0,
            actions=(NEW_CUSTOMER,),
        )
    }
