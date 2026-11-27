"""The tire set page's data: everything the page shows, including every link.

One page covers a set's details and history, its form (new set or edit) and the check-in step.
Which parts are shown follows from which values are present: `form` set means the form is
shown, `check_in` set means the check-in step is shown; the details and history may be shown
beside either, as the design chooses.

Form values are text exactly as typed (so a wrong value can be shown back with its error);
details are display-ready values. Dates are `date` (shown with the `shop_date` filter), moments
are UTC `datetime` (shown with `shop_time`).

Fields follow plan-rollcall-rewrite/design.md, Decisions: set fields (Q3), stays, archive (Q4),
vehicle as text and storage location (Q9), what a PDF fills (Q7). Nothing is recorded per tire
(no positions, DOT codes or tread depth; changed 2026-11-27): that goes in the notes.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum

from rollcall.views.shared import Action, Conflict, Link, Message


class Status(StrEnum):
    IN_SHOP = "in_shop"
    OUT = "out"
    ARCHIVED = "archived"

    @property
    def label(self) -> str:
        return {"in_shop": "In shop", "out": "Out", "archived": "Archived"}[self.value]


class Choice(StrEnum):
    """Lug nuts, center caps, centering rings, TPMS sensors. Unknown is never shown as no."""

    UNKNOWN = "unknown"
    YES = "yes"
    NO = "no"

    @property
    def label(self) -> str:
        return {"unknown": "Unknown", "yes": "Yes", "no": "No"}[self.value]


class Season(StrEnum):
    SUMMER = "summer"
    WINTER = "winter"
    ALL_SEASON = "all_season"

    @property
    def label(self) -> str:
        return {"summer": "Summer", "winter": "Winter", "all_season": "All-season"}[self.value]


# --- shared pieces ----------------------------------------------------------------------------


@dataclass(frozen=True)
class CustomerSummary:
    name: str
    phones: tuple[str, ...]
    url: str


# --- the set's details and history --------------------------------------------------------------


@dataclass(frozen=True)
class Accessories:
    lug_nuts: Choice
    center_caps: Choice
    centering_rings: Choice
    tpms_sensors: Choice

    def items(self) -> tuple[tuple[str, Choice], ...]:
        return (
            ("Lug nuts", self.lug_nuts),
            ("Center caps", self.center_caps),
            ("Centering rings", self.centering_rings),
            ("TPMS sensors", self.tpms_sensors),
        )


@dataclass(frozen=True)
class TireSetDetails:
    sizes: tuple[str, ...]  # one size, or front then rear for a staggered set
    brand_model: str
    on_wheels: bool
    wheel_description: str | None
    season: Season | None
    accessories: Accessories
    vehicle: str | None
    vin: str | None
    plate: str | None
    notes: str | None

    @property
    def staggered(self) -> bool:
        return len(self.sizes) > 1


@dataclass(frozen=True)
class Stay:
    """One visit: checked in, and checked out unless it is the current stay."""

    checked_in: date
    ro_number: str | None
    location: str | None
    checked_out: date | None
    invoice: Link | None  # the PDF attached to this stay


# --- forms --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class CheckInInput:
    checked_in: str  # yyyy-mm-dd, as a date field sends it
    ro_number: str = ""
    location: str = ""


@dataclass(frozen=True)
class TireSetInput:
    front_size: str = ""
    rear_size: str = ""
    brand_model: str = ""
    on_wheels: str = ""  # "wheels", "tires" or "" (not chosen yet)
    wheel_description: str = ""
    season: str = ""  # a Season value or ""
    lug_nuts: str = Choice.UNKNOWN.value
    center_caps: str = Choice.UNKNOWN.value
    centering_rings: str = Choice.UNKNOWN.value
    tpms_sensors: str = Choice.UNKNOWN.value
    vehicle: str = ""
    vin: str = ""
    plate: str = ""
    notes: str = ""


@dataclass(frozen=True)
class CustomerInput:
    """Customer values read from a PDF, for a set whose customer is not chosen yet."""

    first_name: str
    last_name: str
    phone: str
    email: str


@dataclass(frozen=True)
class CustomerMatch:
    """An existing customer the PDF's customer may be (chosen with a radio button)."""

    id: str
    name: str
    phones: tuple[str, ...]


@dataclass(frozen=True)
class Invoice:
    """The PDF a form was filled from, shown beside the form."""

    filename: str
    url: str
    invoice_number: str


@dataclass(frozen=True)
class TireSetForm:
    heading: str
    action_url: str
    cancel_url: str
    submit_label: str
    values: TireSetInput
    check_in: CheckInInput | None  # a new set is checked in as it is created
    errors: Mapping[str, str] = field(default_factory=dict)  # field name -> message
    conflict: Conflict | None = None
    invoice: Invoice | None = None
    new_customer: CustomerInput | None = None  # from a PDF: the customer as the PDF names them
    customer_matches: tuple[CustomerMatch, ...] = ()


@dataclass(frozen=True)
class CheckInForm:
    """Check a checked-out set back in: date, RO and storage location."""

    action_url: str
    cancel_url: str
    values: CheckInInput
    errors: Mapping[str, str] = field(default_factory=dict)


# --- the page -----------------------------------------------------------------------------------


@dataclass(frozen=True)
class TireSetPage:
    title: str
    customer: CustomerSummary
    status: Status | None  # None for a set not saved yet
    in_too_long: bool  # the current stay is older than the shop's threshold
    archived_on: date | None  # set only while archived
    details: TireSetDetails | None  # None for a set not saved yet
    current_stay: Stay | None
    past_stays: tuple[Stay, ...]  # newest first
    actions: tuple[Action, ...]
    messages: tuple[Message, ...] = ()
    form: TireSetForm | None = None
    check_in: CheckInForm | None = None
