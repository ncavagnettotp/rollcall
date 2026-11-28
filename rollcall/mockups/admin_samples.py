"""Sample data for the admin settings gallery states. Every name and password is invented.

Marcus Oyelaran, an admin, is looking at the page. Kelsey Pike's account is the one the sign-in
mockup shows as deactivated; Jordan Pike's is the one still on a temporary password. Buttons
lead to the state that shows their result.
"""

from dataclasses import replace
from datetime import UTC, datetime

from rollcall.mockups.urls import page_url
from rollcall.views.admin import (
    AccountForm,
    AccountInput,
    AdminPage,
    SettingsForm,
    StaffAccount,
)
from rollcall.views.shared import Action, Conflict, Message

ONLY_ADMIN = (
    "The only admin, so it can't be made staff or turned off. Make another account an admin first."
)
YOURSELF = "Your own account: another admin can make it staff or turn it off."


def state(slug: str) -> str:
    return page_url("admin", slug)


def at(month: int, day: int, hour: int, minute: int) -> datetime:
    return datetime(2026, month, day, hour, minute, tzinfo=UTC)


NEW_ACCOUNT = Action("New staff account", state("new-account"))
SETTINGS = SettingsForm(state("many-staff"), "6")


def reset() -> Action:
    return Action("Reset password", state("password-reset"), post=True, kind="secondary")


def make_admin() -> Action:
    return Action("Make admin", state("many-staff"), post=True, kind="secondary")


def make_staff() -> Action:
    return Action("Make staff", state("many-staff"), post=True, kind="secondary")


def turn_off() -> Action:
    return Action("Turn off", state("many-staff"), post=True, kind="quiet")


def turn_on() -> Action:
    return Action("Turn on", state("many-staff"), post=True, kind="secondary")


def account(name, username, is_admin=False, last=None, *, temporary=False, you=False, active=True):
    if you:
        actions, note = (), YOURSELF
    elif not active:
        actions, note = (turn_on(),), None
    else:
        actions = (reset(), make_staff() if is_admin else make_admin(), turn_off())
        note = None
    return StaffAccount(name, username, is_admin, active, temporary, last, you, actions, note)


MARCUS = account("Marcus Oyelaran", "marcus.o", True, at(11, 18, 14, 2), you=True)
INES = account("Inês Carvalho", "ines", True, at(11, 17, 22, 15))
DANA = account("Dana Whitfield", "dana", last=at(11, 18, 13, 55))
JORDAN = account("Jordan Pike", "jpike", temporary=True)
KOFI = account("Kofi Mensah", "kofi", last=at(11, 18, 12, 40))
SOFIA = account("Sofia Lindgren", "sofia.l", last=at(11, 12, 15, 8))
TOMASZ = account("Tomasz Wiśniewski", "tomasz", last=at(10, 30, 21, 47))
KELSEY = account("Kelsey Pike", "kpike", last=at(4, 29, 18, 20), active=False)

ACCOUNTS = (MARCUS, INES, DANA, JORDAN, KOFI, SOFIA, TOMASZ)


def _page(**values) -> AdminPage:
    base = {
        "title": "Admin settings",
        "accounts": ACCOUNTS,
        "turned_off": (KELSEY,),
        "settings": SETTINGS,
        "actions": (NEW_ACCOUNT,),
    }
    return AdminPage(**(base | values))


def many_staff() -> dict:
    return {"page": _page()}


def one_admin() -> dict:
    only = replace(MARCUS, note=ONLY_ADMIN)
    return {"page": _page(accounts=(only, DANA), turned_off=())}


def _form(**values) -> AccountForm:
    return replace(AccountForm(state("account-created"), state("many-staff")), **values)


def new_account() -> dict:
    return {"page": _page(account_form=_form(), actions=())}


def account_created() -> dict:
    message = Message(
        "Account made for Jordan Pike. Temporary password: cobalt-river-lamp-58. Give it to them "
        "in person; they choose their own when they first sign in. It is not shown again."
    )
    return {"page": _page(messages=(message,))}


def password_reset() -> dict:
    message = Message(
        "New temporary password for Dana Whitfield: maple-orbit-quartz-31. Their old password no "
        "longer works; they choose a new one when they sign in. It is not shown again."
    )
    dana = replace(DANA, must_change_password=True)
    accounts = tuple(dana if a is DANA else a for a in ACCOUNTS)
    return {"page": _page(accounts=accounts, messages=(message,))}


def form_errors() -> dict:
    form = _form(
        action_url=state("form-errors"),
        values=AccountInput("", "dana", False),
        errors={
            "name": "Enter the person's name; it is shown beside every change they make.",
            "username": "dana is already taken (Dana Whitfield). Try dana.w or a different name.",
        },
    )
    messages = (Message("Two values need fixing before the account can be made.", "error"),)
    return {"page": _page(account_form=form, actions=(), messages=messages)}


def settings_error() -> dict:
    settings = SettingsForm(
        state("settings-error"),
        "6.5",
        {"too_long_months": "Enter whole months, from 1 to 36."},
    )
    messages = (Message("The setting was not saved.", "error"),)
    return {"page": _page(settings=settings, messages=messages)}


def save_conflict() -> dict:
    settings = SettingsForm(
        state("many-staff"),
        "8",
        conflict=Conflict("Inês Carvalho", at(11, 18, 20, 42), state("many-staff")),
    )
    return {"page": _page(settings=settings)}
