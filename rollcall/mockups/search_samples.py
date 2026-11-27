"""Sample data for the search page's gallery states. Every name and number is invented.

"Today" in the gallery is 11/18/2026; "too long" is the default threshold, 6 months, so a set
checked in before 5/18/2026 is in too long. Customers and sets link to the customer and tire set
states that show them best (Renata's own, or the closest one).

The gallery has one state per situation, so a filter or page link opens the state nearest to
it: the filters lead to the too-long and archived states, or back to the size search.
"""

from dataclasses import replace
from datetime import date

from rollcall.mockups import customer_samples as customer
from rollcall.mockups.urls import page_url
from rollcall.views.customer import SetSummary
from rollcall.views.search import (
    Filter,
    FilterLink,
    Paging,
    SearchPage,
    SearchResult,
)
from rollcall.views.shared import Action, Link
from rollcall.views.tire_set import Status

PER_PAGE = 20
TOO_LONG_NOTE = "In the shop longer than 6 months (set in Admin settings). Longest first."


def state(slug: str) -> str:
    return page_url("search", slug)


def customer_page(slug: str) -> str:
    return page_url("customer", slug)


def tire_set(slug: str) -> str:
    return page_url("tire-set", slug)


NEW_CUSTOMER = Action("New customer", customer_page("new"))
SEARCH_TARGET = state("size-digits")  # where typing a search leads in the gallery

# Which state each filter opens in the gallery.
FILTER_STATES = {
    Filter.ALL: "size-digits",
    Filter.IN_SHOP: "size-digits",
    Filter.OUT: "size-digits",
    Filter.TOO_LONG: "too-long",
    Filter.ARCHIVED: "archived",
}


def filters(current: Filter, query: str = "") -> tuple[FilterLink, ...]:
    """The five filters; each keeps what was typed (the gallery ignores the query string)."""
    links = []
    for choice in Filter:
        url = state(FILTER_STATES[choice])
        if query or choice is not Filter.ALL:
            url += f"?q={query}&filter={choice.value}"
        if choice is Filter.ALL and not query:
            url = state("no-query")
        links.append(FilterLink(choice, url, choice is current))
    return tuple(links)


def _page(**values) -> SearchPage:
    base = {
        "title": "Search",
        "action_url": SEARCH_TARGET,
        "query": "",
        "filter": Filter.ALL,
        "filters": filters(Filter.ALL),
        "note": None,
        "searched": True,
        "customers": 0,
        "sets": 0,
        "results": (),
        "paging": None,
        "archived_match": None,
        "actions": (NEW_CUSTOMER,),
    }
    return SearchPage(**(base | values))


def check_out(here: str) -> Action:
    """Checking a set out from the results comes back to the same search."""
    return Action("Check out", state(here), post=True, kind="secondary")


def in_shop(title, slug, since, location, ro, vehicle, here, too_long=False) -> SetSummary:
    return SetSummary(
        title,
        tire_set(slug),
        Status.IN_SHOP,
        too_long,
        location,
        since,
        ro,
        vehicle,
        check_out(here),
    )


def out(title, slug, since, vehicle) -> SetSummary:
    check_in = Action("Check in", tire_set("check-in"), kind="secondary")
    return SetSummary(
        title, tire_set(slug), Status.OUT, False, None, since, None, vehicle, check_in
    )


def archived_set(title, since, vehicle) -> SetSummary:
    return SetSummary(
        title, tire_set("archived"), Status.ARCHIVED, False, None, since, None, vehicle, None
    )


# --- nothing searched yet -------------------------------------------------------------------


def no_query() -> dict:
    return {"page": _page(filters=filters(Filter.ALL), searched=False)}


# --- a size typed as digits -------------------------------------------------------------------

SIZE_QUERY = "2256017"
SIZE_MATCH = "size 225/60R17"


def size_digits() -> dict:
    here = "size-digits"
    renata = SearchResult(
        "Renata Kowalczyk",
        customer_page("active"),
        customer.RENATA.phones,
        archived=False,
        matched=SIZE_MATCH,
        sets=(replace(customer.ALENZA_IN, action=check_out(here)), customer.X_ICE_OUT),
        more_sets=0,
    )
    results = (
        renata,
        SearchResult(
            "Graham Whitlock",
            customer_page("active"),
            ("(555) 013-5508",),
            archived=False,
            matched=SIZE_MATCH,
            sets=(
                in_shop(
                    "225/60R17 Michelin Defender LTX M/S",
                    "checked-in",
                    date(2026, 10, 2),
                    "Rack C2",
                    "47801",
                    "2018 Chevrolet Equinox",
                    here,
                ),
            ),
            more_sets=1,
        ),
        SearchResult(
            "Lucía Ferreira-Dunn",
            customer_page("active"),
            ("(555) 018-0417", "(555) 010-2265"),
            archived=False,
            matched=SIZE_MATCH,
            sets=(
                out(
                    "225/60R17 Goodyear Assurance WeatherReady",
                    "checked-out",
                    date(2026, 4, 14),
                    "2020 Toyota RAV4",
                ),
            ),
        ),
    )
    return {
        "page": _page(
            query=SIZE_QUERY,
            filters=filters(Filter.ALL, SIZE_QUERY),
            customers=3,
            sets=4,
            results=results,
        )
    }


# --- nothing found ----------------------------------------------------------------------------

ARCHIVED_QUERY = "impreza"


def no_results() -> dict:
    return {
        "page": _page(
            query=ARCHIVED_QUERY,
            filters=filters(Filter.ALL, ARCHIVED_QUERY),
            archived_match=Link(
                "Show 2 archived matches",
                state("archived") + f"?q={ARCHIVED_QUERY}&filter=archived",
            ),
        )
    }


# --- many results, two pages ------------------------------------------------------------------

MANY_QUERY = "toyota"
MANY_TOTAL = 38
FIRST_NAMES = (
    "Amara", "Benedikt", "Carmen", "Dmitri", "Esther", "Farid", "Greta", "Hiroshi", "Ingrid",
    "Jamal", "Katarina", "Leonel", "Mireille", "Nnamdi", "Oksana", "Pedro", "Quinn", "Rosalind",
    "Sefa", "Tobias",
)  # fmt: skip
LAST_NAMES = (
    "Abernethy", "Baptiste", "Castellanos", "Dimitrov", "Eriksen", "Fairweather", "Gallagher",
    "Haddad", "Ivanova", "Jablonski", "Kariuki", "Lindqvist", "Moreau", "Nakamura", "Olawale",
    "Petrakis", "Quintero", "Rasmussen", "Szabo", "Thorvaldsen",
)  # fmt: skip
TOYOTA_SETS = (
    ("215/55R17 Michelin CrossClimate 2", "Camry"),
    ("225/65R17 Bridgestone Blizzak DM-V2", "RAV4"),
    ("195/65R15 Nokian WR G4", "Prius"),
    ("245/60R18 Continental TerrainContact H/T", "Highlander"),
    ("265/70R17 Falken Wildpeak A/T3W", "Tacoma"),
)


def _toyota_customer(number: int, here: str) -> SearchResult:
    """The number-th customer (counting from 0) with a Toyota, half in the shop, half out."""
    name = f"{FIRST_NAMES[number % 20]} {LAST_NAMES[(number * 7 + number // 20) % 20]}"
    title, model = TOYOTA_SETS[number % 5]
    vehicle = f"{2012 + number % 13} Toyota {model}"
    since = date(2026, 10 - number % 6, 1 + number % 28)
    if number % 2:
        tire_set_ = out(title, "checked-out", since, vehicle)
    else:
        rack = f"Rack {'ABCDE'[number % 5]}{1 + number % 6}"
        tire_set_ = in_shop(
            title, "checked-in", since, rack, str(47000 + number * 37), vehicle, here
        )
    phone = f"(555) 01{number % 10}-{1000 + number * 211 % 9000:04d}"
    return SearchResult(name, customer_page("active"), (phone,), False, None, (tire_set_,))


def _many(page_number: int) -> SearchPage:
    here = "many-results" if page_number == 1 else "many-results-2"
    first = (page_number - 1) * PER_PAGE + 1
    last = min(page_number * PER_PAGE, MANY_TOTAL)
    paging = Paging(
        first,
        last,
        previous_url=state("many-results") + f"?q={MANY_QUERY}" if page_number > 1 else None,
        next_url=state("many-results-2") + f"?q={MANY_QUERY}&page=2" if last < MANY_TOTAL else None,
    )
    return _page(
        query=MANY_QUERY,
        filters=filters(Filter.ALL, MANY_QUERY),
        customers=MANY_TOTAL,
        sets=MANY_TOTAL,
        results=tuple(_toyota_customer(n, here) for n in range(first - 1, last)),
        paging=paging,
    )


def many_results() -> dict:
    return {"page": _many(1)}


def many_results_2() -> dict:
    return {"page": _many(2)}


# --- in too long, from the dashboard ----------------------------------------------------------


def too_long() -> dict:
    here = "too-long"
    results = (
        SearchResult(
            "Priya Raghunathan",
            customer_page("active"),
            ("(555) 015-7734",),
            archived=False,
            matched=None,
            sets=(
                in_shop(
                    "245/45R18 Nokian WR G4",
                    "staggered",
                    date(2026, 1, 12),
                    "Rack D1",
                    "46980",
                    "2017 Audi A4",
                    here,
                    too_long=True,
                ),
                in_shop(
                    "245/45R18 Michelin Pilot Sport 4S",
                    "staggered",
                    date(2026, 1, 12),
                    "Rack D1",
                    "46980",
                    "2017 Audi A4",
                    here,
                    too_long=True,
                ),
            ),
        ),
        SearchResult(
            "Bartholomew Alexander Vandersloot-Okonkwo",
            customer_page("long-text"),
            ("(555) 019-8830", "(555) 012-4471", "(555) 010-5512"),
            archived=False,
            matched=None,
            sets=(
                in_shop(
                    "275/35R21 and 315/30R21 Pirelli P Zero PZ4 Elect Run Flat NCS",
                    "staggered",
                    date(2026, 3, 2),
                    "Mezzanine overflow rack, far left bay behind the alignment machine, top shelf",
                    "47205",
                    "2022 Porsche Taycan 4S Cross Turismo Performance Battery Plus",
                    here,
                    too_long=True,
                ),
            ),
        ),
        SearchResult(
            "Thandiwe Abernathy-Reyes",
            customer_page("many-sets"),
            ("(555) 017-6402", "(555) 011-9283"),
            archived=False,
            matched=None,
            sets=(
                in_shop(
                    "265/70R17 BFGoodrich All-Terrain T/A KO2",
                    "staggered",
                    date(2026, 3, 3),
                    "Yard shed 2",
                    "47160",
                    "2016 Ford F-150",
                    here,
                    too_long=True,
                ),
            ),
            more_sets=7,
        ),
        SearchResult(
            "Walter Ng",
            customer_page("active"),
            ("(555) 012-0090",),
            archived=False,
            matched=None,
            sets=(
                in_shop(
                    "205/55R16 Hankook Kinergy GT",
                    "staggered",
                    date(2026, 4, 30),
                    "Rack A2",
                    "47512",
                    "2015 Volkswagen Golf",
                    here,
                    too_long=True,
                ),
            ),
            more_sets=1,
        ),
    )
    return {
        "page": _page(
            filter=Filter.TOO_LONG,
            filters=filters(Filter.TOO_LONG),
            note=TOO_LONG_NOTE,
            customers=4,
            sets=5,
            results=results,
        )
    }


# --- archived ---------------------------------------------------------------------------------


def archived() -> dict:
    results = (
        SearchResult(
            "Renata Kowalczyk",
            customer_page("active"),
            customer.RENATA.phones,
            archived=False,
            matched=None,
            sets=(customer.NOKIAN_ARCHIVED,),
            more_sets=2,
        ),
        SearchResult(
            "Desmond Hollingsworth",
            customer_page("archived"),
            ("(555) 016-2047",),
            archived=True,
            matched=None,
            sets=(
                replace(
                    out(
                        "195/65R15 Firestone Winterforce 2",
                        "checked-out",
                        date(2023, 4, 11),
                        "2011 Subaru Impreza",
                    ),
                    action=None,
                ),
            ),
        ),
    )
    return {
        "page": _page(
            query=ARCHIVED_QUERY,
            filter=Filter.ARCHIVED,
            filters=filters(Filter.ARCHIVED, ARCHIVED_QUERY),
            note="Archived customers and archived tire sets: hidden everywhere else.",
            customers=2,
            sets=2,
            results=results,
        )
    }
