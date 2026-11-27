"""The customer view's data: everything the page shows, including every link.

One page covers a customer's details, their tire sets (in the shop, out, archived) with check in
and check out on each, the history of changes, and the customer form (new customer or edit).
`form` set means the form is shown instead of the details.

Fields follow plan-rollcall-rewrite/design.md, Decisions: customer fields (Q8: first and last name,
one or more phones, email, notes; no address), archive (Q4: only when no set is checked in;
hidden from search, restorable), "too long" (Q6), every change attributed and kept.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date, datetime

from rollcall.views.shared import Action, Conflict, Link, Message
from rollcall.views.tire_set import Status


@dataclass(frozen=True)
class CustomerDetails:
    phones: tuple[str, ...]
    email: str | None
    notes: str | None


@dataclass(frozen=True)
class SetSummary:
    """One tire set in the customer's list (also used later by search results)."""

    title: str  # size(s) and brand, as on the tire set page
    url: str
    status: Status
    in_too_long: bool
    location: str | None  # where it is, while in the shop
    since: date  # checked in (in the shop), checked out (out) or archived on (archived)
    ro_number: str | None  # the current stay's, while in the shop
    vehicle: str | None
    action: Action | None  # check in or check out; none while archived


@dataclass(frozen=True)
class Change:
    """One line of history: when, who, what."""

    at: datetime  # UTC
    by: str
    text: str
    link: Link | None = None  # the tire set it was about


@dataclass(frozen=True)
class CustomerInput:
    """The customer form's values, as typed. Phones: phones-<row>, counting from 0; the form
    always shows one empty phone field more, so another number can be added without a button."""

    first_name: str = ""
    last_name: str = ""
    phones: tuple[str, ...] = ()
    email: str = ""
    notes: str = ""


@dataclass(frozen=True)
class PossibleDuplicate:
    """An existing customer with a similar name or the same phone (never merged by itself)."""

    name: str
    phones: tuple[str, ...]
    url: str


@dataclass(frozen=True)
class CustomerForm:
    heading: str
    action_url: str
    cancel_url: str
    submit_label: str
    values: CustomerInput
    errors: Mapping[str, str] = field(default_factory=dict)  # field name -> message
    conflict: Conflict | None = None
    duplicates: tuple[PossibleDuplicate, ...] = ()


@dataclass(frozen=True)
class CustomerPage:
    title: str  # the customer's name, or "New customer"
    archived_on: date | None
    details: CustomerDetails | None  # None for a customer not saved yet
    in_shop: tuple[SetSummary, ...]
    out: tuple[SetSummary, ...]
    archived_sets: tuple[SetSummary, ...]
    history: tuple[Change, ...]  # newest first
    actions: tuple[Action, ...]
    add_set_url: str | None  # None while archived
    messages: tuple[Message, ...] = ()
    form: CustomerForm | None = None
