"""The dashboard's data: everything the page shows, including every link.

The five numbers (plan-rollcall-rewrite/design.md, Decisions: dashboard (Q6)): sets checked in
now, sets in too long, checked in this week, checked out this week, customers with a set in the
shop. The shop-wide numbers link to the matching search; the two weekly numbers link to the
week's check-ins and check-outs listed on the dashboard itself (search has no date filter). A
week starts on Monday, in the shop's time.

The dashboard is where most work starts, so it also has the search box, the invoice upload
(which opens the tire set form filled from the PDF) and New customer.
"""

from dataclasses import dataclass
from datetime import date
from enum import StrEnum

from rollcall.views.customer import Change
from rollcall.views.shared import Action, Message


class StatKind(StrEnum):
    IN_SHOP = "in_shop"
    TOO_LONG = "too_long"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CUSTOMERS = "customers"

    @property
    def label(self) -> str:
        return {
            "in_shop": "Sets in the shop",
            "too_long": "In too long",
            "checked_in": "Checked in",
            "checked_out": "Checked out",
            "customers": "Customers",
        }[self.value]


@dataclass(frozen=True)
class Stat:
    kind: StatKind
    value: int
    url: str  # the matching search, or the week's list below
    note: str | None = None  # what it counts, under the number: "this week, since Monday 11/16"


@dataclass(frozen=True)
class DashboardPage:
    title: str
    stats: tuple[Stat, ...]  # the five, in the order above
    search_url: str  # the search form's target (it sends q)
    upload_url: str  # the invoice upload form's target (it sends the PDF as "invoice")
    week_start: date  # Monday of this week
    this_week: tuple[Change, ...]  # the latest check-ins and check-outs, newest first
    this_week_total: int  # all of this week's, when only the latest are listed
    actions: tuple[Action, ...]  # New customer
    messages: tuple[Message, ...] = ()
