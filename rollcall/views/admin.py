"""The admin settings page's data: staff accounts and the shop's settings. Admins only.

Accounts follow plan-rollcall-rewrite/design.md, Decisions: account creation (an admin makes an
account; Rollcall makes up its temporary password, shown to the admin once, and the person
chooses their own at the first sign-in), admin powers (make an account an admin, or staff again),
deactivation ("turned off": can't sign in, history stays; the last admin can't be made staff or
turned off), sign-in (a forgotten password is replaced with a new temporary one). The one shop
setting is how long a stay may last before it is "in too long" (Q6, 6 months by default).
"""

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime

from rollcall.views.shared import Action, Conflict, Message


@dataclass(frozen=True)
class StaffAccount:
    name: str
    username: str
    is_admin: bool
    active: bool  # False: turned off, can't sign in
    must_change_password: bool  # still on a temporary password
    last_signed_in: datetime | None  # UTC; None: never signed in
    is_you: bool  # the admin looking at the page
    actions: tuple[Action, ...]  # reset password, make admin / staff, turn off / on
    note: str | None = None  # why an action is missing, e.g. the only admin


@dataclass(frozen=True)
class AccountInput:
    name: str = ""
    username: str = ""
    is_admin: bool = False


@dataclass(frozen=True)
class AccountForm:
    """A new staff account. Rollcall makes up the temporary password when it is saved."""

    action_url: str
    cancel_url: str
    values: AccountInput = AccountInput()
    errors: Mapping[str, str] = field(default_factory=dict)  # field name -> message


@dataclass(frozen=True)
class SettingsForm:
    action_url: str
    too_long_months: str  # as typed
    errors: Mapping[str, str] = field(default_factory=dict)
    conflict: Conflict | None = None


@dataclass(frozen=True)
class AdminPage:
    title: str
    accounts: tuple[StaffAccount, ...]  # active accounts: admins first, then by name
    turned_off: tuple[StaffAccount, ...]  # by name
    settings: SettingsForm
    actions: tuple[Action, ...]  # New staff account
    account_form: AccountForm | None = None
    messages: tuple[Message, ...] = ()
