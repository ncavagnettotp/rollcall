"""Sample data for the tire set page's gallery states. Every name and number is invented.

The main story follows Renata Kowalczyk's summer set, the one on the sample invoice
(scripts/make_sample_invoice.py): out since April, checked in again on 11/18/2026 with RO 48213.
"Today" in the gallery is 11/18/2026.

Links point at the gallery state that shows the result, so the owner can click through:
checked out -> check in -> checked in -> check out -> checked out -> archive -> archived -> restore.
"""

from dataclasses import replace
from datetime import UTC, date, datetime

from rollcall.mockups.urls import SAMPLE_INVOICE_URL, page_url
from rollcall.views.tire_set import (
    Accessories,
    Action,
    CheckInForm,
    CheckInInput,
    Choice,
    Conflict,
    CustomerInput,
    CustomerMatch,
    CustomerSummary,
    Invoice,
    Link,
    Message,
    Season,
    Status,
    Stay,
    Tire,
    TireInput,
    TireSetDetails,
    TireSetForm,
    TireSetInput,
    TireSetPage,
    TreadReading,
)

TODAY = date(2026, 11, 18)
FOUR = ("LF", "RF", "LR", "RR")


def state(slug: str) -> str:
    return page_url("tire-set", slug)


CUSTOMER_URL = page_url("customer")
RENATA = CustomerSummary("Renata Kowalczyk", ("(555) 014-2271",), CUSTOMER_URL)


def treads(*values: int | None, positions=FOUR) -> tuple[TreadReading, ...]:
    return tuple(TreadReading(p, v) for p, v in zip(positions, values, strict=True))


def invoice_link(number: str) -> Link:
    return Link(f"Invoice {number}", SAMPLE_INVOICE_URL)


# --- Renata's summer set --------------------------------------------------------------------

ALENZA_DOT = ("2321", "2321", "2421", "2421")


def alenza_details(tread: tuple[int | None, ...]) -> TireSetDetails:
    return TireSetDetails(
        sizes=("225/60R17",),
        brand_model="Bridgestone Alenza",
        on_wheels=True,
        wheel_description="OEM alloys",
        season=Season.SUMMER,
        accessories=Accessories(Choice.YES, Choice.UNKNOWN, Choice.NO, Choice.YES),
        vehicle="2019 Subaru Outback",
        vin="JF2EXAMPLE0000001",
        plate="IL SMPL 123",
        notes="Wheel locks in the trunk, key in the glovebox.",
        tires=tuple(Tire(p, d, t) for p, d, t in zip(FOUR, ALENZA_DOT, tread, strict=True)),
    )


PAST_STAYS = (
    Stay(date(2025, 11, 14), "46872", "Rack B3", treads(7, 7, 6, 6), date(2026, 4, 20), None),
    Stay(date(2024, 11, 12), "45120", "Rack A1", treads(8, 8, 8, 7), date(2025, 4, 8), None),
    Stay(date(2023, 11, 20), "43391", None, treads(9, 9, 9, 9), date(2024, 4, 15), None),
)
CURRENT_STAY = Stay(TODAY, "48213", "Rack B3", treads(6, 6, 5, 5), None, invoice_link("900123"))

EDIT_ACTION = Action("Edit", state("edit"), kind="secondary")


def checked_in() -> dict:
    return {
        "page": TireSetPage(
            title="225/60R17 Bridgestone Alenza",
            customer=RENATA,
            status=Status.IN_SHOP,
            in_too_long=False,
            archived_on=None,
            details=alenza_details((6, 6, 5, 5)),
            current_stay=CURRENT_STAY,
            past_stays=PAST_STAYS,
            actions=(Action("Check out", state("checked-out"), post=True), EDIT_ACTION),
            messages=(Message("Checked in. Rack B3, RO 48213."),),
        )
    }


def checked_out() -> dict:
    return {
        "page": TireSetPage(
            title="225/60R17 Bridgestone Alenza",
            customer=RENATA,
            status=Status.OUT,
            in_too_long=False,
            archived_on=None,
            details=alenza_details((7, 7, 6, 6)),
            current_stay=None,
            past_stays=PAST_STAYS,
            actions=(
                Action("Check in", state("check-in")),
                EDIT_ACTION,
                Action("Archive", state("archived"), post=True, kind="quiet"),
            ),
        )
    }


def check_in() -> dict:
    page = checked_out()["page"]
    form = CheckInForm(
        action_url=state("checked-in"),
        cancel_url=state("checked-out"),
        values=CheckInInput(TODAY.isoformat()),
        tires=tuple(TireInput(p, d) for p, d in zip(FOUR, ALENZA_DOT, strict=True)),
    )
    return {"page": replace(page, actions=(), check_in=form)}


def archived() -> dict:
    old_set = TireSetDetails(
        sizes=("205/60R16",),
        brand_model="Nokian Hakkapeliitta R5",
        on_wheels=True,
        wheel_description="Black steel wheels",
        season=Season.WINTER,
        accessories=Accessories(Choice.UNKNOWN, Choice.NO, Choice.NO, Choice.NO),
        vehicle="2014 Subaru Impreza",
        vin=None,
        plate=None,
        notes="Customer sold the Impreza; keeping the record for history.",
        tires=tuple(Tire(p, "4417", t) for p, t in zip(FOUR, (4, 4, 3, 3), strict=True)),
    )
    stays = (
        Stay(date(2025, 4, 2), "46010", "Rack D2", treads(4, 4, 3, 3), date(2025, 11, 10), None),
        Stay(date(2024, 4, 9), "44312", "Rack D2", treads(6, 6, 5, 5), date(2024, 11, 4), None),
    )
    return {
        "page": TireSetPage(
            title="205/60R16 Nokian Hakkapeliitta R5",
            customer=RENATA,
            status=Status.ARCHIVED,
            in_too_long=False,
            archived_on=date(2026, 4, 30),
            details=old_set,
            current_stay=None,
            past_stays=stays,
            actions=(Action("Restore", state("checked-out"), post=True, kind="secondary"),),
        )
    }


# --- forms ----------------------------------------------------------------------------------


def _form(**changes) -> TireSetForm:
    base = TireSetForm(
        heading="New tire set",
        action_url=state("checked-in"),
        cancel_url=CUSTOMER_URL,
        add_tire_url=state("new"),
        submit_label="Save and check in",
        values=TireSetInput(),
        check_in=CheckInInput(TODAY.isoformat()),
    )
    return replace(base, **changes)


def _new_page(form: TireSetForm, title: str = "New tire set") -> TireSetPage:
    return TireSetPage(
        title=title,
        customer=RENATA,
        status=None,
        in_too_long=False,
        archived_on=None,
        details=None,
        current_stay=None,
        past_stays=(),
        actions=(),
        form=form,
    )


def new_set() -> dict:
    return {"page": _new_page(_form())}


ALENZA_INPUT = TireSetInput(
    front_size="225/60R17",
    brand_model="Bridgestone Alenza",
    on_wheels="wheels",
    wheel_description="OEM alloys",
    season="summer",
    lug_nuts="yes",
    center_caps="unknown",
    centering_rings="no",
    tpms_sensors="yes",
    vehicle="2019 Subaru Outback",
    vin="JF2EXAMPLE0000001",
    plate="IL SMPL 123",
    notes="Wheel locks in the trunk, key in the glovebox.",
    tires=tuple(TireInput(p, d) for p, d in zip(FOUR, ALENZA_DOT, strict=True)),
)


def from_pdf() -> dict:
    # A PDF never fills DOT codes, tread or location, so those stay empty.
    values = replace(ALENZA_INPUT, notes="", tires=tuple(TireInput(p) for p in FOUR))
    form = _form(
        heading="New tire set from an invoice",
        add_tire_url=state("from-pdf"),
        values=values,
        check_in=CheckInInput("2026-11-18", ro_number="48213"),
        invoice=Invoice("invoice-900123.pdf", SAMPLE_INVOICE_URL, "900123"),
        new_customer=CustomerInput("Renata", "Kowalczyk", "(555) 014-2271", "renata.k@example.com"),
        customer_matches=(CustomerMatch("c-1042", "Renata Kowalczyk", ("(555) 014-2271",)),),
    )
    page = _new_page(form, title="New tire set from an invoice")
    messages = (Message("Read from invoice 900123. Check every value before saving."),)
    return {"page": replace(page, messages=messages)}


def form_errors() -> dict:
    values = replace(
        ALENZA_INPUT,
        front_size="22555",
        tires=(
            TireInput("LF", "2321", "6"),
            TireInput("RF", "321", "6"),
            TireInput("LR", "2421", "25"),
            TireInput("RR", "2421", "5"),
        ),
    )
    errors = {
        "front_size": "Enter a full size, e.g. 225/60R17 or 35x12.50R20.",
        "tires-1-dot": "Use four digits: week and year, e.g. 2321.",
        "tires-2-tread": "Tread is a whole number of 32nds from 0 to 20.",
    }
    form = _form(
        add_tire_url=state("form-errors"),
        values=values,
        check_in=CheckInInput("2026-11-18", "48213", "Rack B3"),
        errors=errors,
    )
    page = _new_page(form)
    messages = (Message("Three values need fixing before the set can be saved.", "error"),)
    return {"page": replace(page, messages=messages)}


def _edit_page(form: TireSetForm, messages=()) -> TireSetPage:
    page = checked_in()["page"]
    return replace(page, actions=(), messages=messages, form=form)


def _edit_form(**changes) -> TireSetForm:
    edit_values = {
        "heading": "Edit tire set",
        "cancel_url": state("checked-in"),
        "add_tire_url": state("edit"),
        "submit_label": "Save",
        "values": ALENZA_INPUT,
        "check_in": None,
    }
    return _form(**(edit_values | changes))


def edit() -> dict:
    return {"page": _edit_page(_edit_form())}


def save_conflict() -> dict:
    typed = replace(
        ALENZA_INPUT,
        notes="Wheel locks in the trunk, key in the glovebox. "
        "Customer asked for nitrogen fill on return.",
    )
    form = _edit_form(
        add_tire_url=state("save-conflict"),
        values=typed,
        conflict=Conflict(
            "Marcus Oyelaran", datetime(2026, 11, 18, 20, 42, tzinfo=UTC), state("edit")
        ),
    )
    return {"page": _edit_page(form)}


# --- staggered, five tires, long text -------------------------------------------------------


def staggered() -> dict:
    positions = ("LF", "RF", "LR", "RR", "Extra")
    details = TireSetDetails(
        sizes=("275/35R21", "315/30R21"),
        brand_model="Pirelli P Zero PZ4 Elect Run Flat NCS (Porsche N0 approved)",
        on_wheels=True,
        wheel_description=(
            "21-inch Mission E Design wheels in satin Aurum, painted calipers side facing out, "
            "each wheel wrapped in its own bag"
        ),
        season=Season.SUMMER,
        accessories=Accessories(Choice.YES, Choice.YES, Choice.UNKNOWN, Choice.YES),
        vehicle="2022 Porsche Taycan 4S Cross Turismo Performance Battery Plus",
        vin="WP0EXAMPLE0000002",
        plate="IL VANDRSLT",
        notes=(
            "Customer prefers a call to Jonathan (assistant) before pickup, never a text. "
            "Spare is the same size as the rear and was never mounted; the LR has a plugged "
            "puncture from 2025 noted on RO 46511. Torque to 160 Nm by hand, no impact guns "
            "on these wheels under any circumstances."
        ),
        tires=tuple(
            Tire(p, d, t)
            for p, d, t in zip(
                positions,
                ("1822", "1822", "2022", "2022", "2022"),
                (7, 7, 5, 6, 10),
                strict=True,
            )
        ),
    )
    stay = Stay(
        date(2026, 3, 2),
        "47205",
        "Mezzanine overflow rack, far left bay behind the alignment machine, top shelf",
        treads(7, 7, 5, 6, 10, positions=positions),
        None,
        invoice_link("897310"),
    )
    customer = CustomerSummary(
        "Bartholomew Alexander Vandersloot-Okonkwo",
        ("(555) 019-8830", "(555) 012-4471"),
        CUSTOMER_URL,
    )
    return {
        "page": TireSetPage(
            title="275/35R21 and 315/30R21 Pirelli P Zero PZ4 Elect Run Flat NCS",
            customer=customer,
            status=Status.IN_SHOP,
            in_too_long=True,
            archived_on=None,
            details=details,
            current_stay=stay,
            past_stays=(),
            actions=(Action("Check out", state("checked-out"), post=True), EDIT_ACTION),
        )
    }
