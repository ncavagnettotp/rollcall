"""The search page's data: everything the page shows, including every link.

One box matches customer name, phone, tire size (by digits, so 225/60R17 and 2256017 both
match), brand, vehicle, VIN, plate, RO number and location. One filter at a time narrows it:
all (the default, archived hidden), in shop, out, too long, archived. Results are customers,
each with their matching tire sets (plan-rollcall-rewrite/design.md, Decisions: search (Q10),
"too long" (Q6), archive (Q4)). The dashboard's numbers link here with a filter chosen.

Nothing typed and the default filter means nothing has been searched yet: the page asks for a
search instead of listing every customer.
"""

from dataclasses import dataclass
from enum import StrEnum

from rollcall.views.customer import SetSummary
from rollcall.views.shared import Action, Link, Message


class Filter(StrEnum):
    ALL = "all"
    IN_SHOP = "in_shop"
    OUT = "out"
    TOO_LONG = "too_long"
    ARCHIVED = "archived"

    @property
    def label(self) -> str:
        return {
            "all": "All",
            "in_shop": "In shop",
            "out": "Out",
            "too_long": "Too long",
            "archived": "Archived",
        }[self.value]


@dataclass(frozen=True)
class FilterLink:
    """One filter, linking to the same search with that filter (and the typed query) chosen."""

    filter: Filter
    url: str
    current: bool


@dataclass(frozen=True)
class SearchResult:
    """A customer who matches, with the tire sets that match."""

    name: str
    url: str
    phones: tuple[str, ...]
    archived: bool
    matched: str | None  # what matched when it is not the name or phone, e.g. "VIN JF2…"
    sets: tuple[SetSummary, ...]
    more_sets: int = 0  # the customer's other sets, not shown here (on their page)


@dataclass(frozen=True)
class Paging:
    first: int  # the first and last result shown, counting from 1
    last: int
    previous_url: str | None
    next_url: str | None


@dataclass(frozen=True)
class SearchPage:
    title: str
    action_url: str  # the search form's target (it sends q and filter)
    query: str  # as typed
    filter: Filter
    filters: tuple[FilterLink, ...]
    note: str | None  # what the filter means, e.g. how long "too long" is
    searched: bool  # False: nothing typed, default filter; the page asks for a search
    customers: int  # how many customers match in all (not only on this page)
    sets: int  # how many of their sets match
    results: tuple[SearchResult, ...]
    paging: Paging | None  # None when every result fits on one page
    archived_match: Link | None  # no results here, but archived customers match
    actions: tuple[Action, ...]  # New customer
    messages: tuple[Message, ...] = ()
