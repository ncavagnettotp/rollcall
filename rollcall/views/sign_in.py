"""The sign-in pages' data: signing in, setting up the first admin, and changing a temporary
password. One page shows one of the three forms (whichever is set).

Accounts follow plan-rollcall-rewrite/design.md, Decisions: accounts, first admin (the first
account on a fresh install, made on this page; no other self-signup), account creation (an admin
gives a temporary password, changed at the first sign-in), deactivation (a deactivated account
cannot sign in). Staff sign in with a username, not an email: Rollcall sends no email.

A wrong username and a wrong password get the same message, so the page never tells anyone which
usernames exist. That an account is deactivated is said only after the right password.
Passwords are never sent back to the page. A new password needs at least 12 characters.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field

from rollcall.views.shared import Message


@dataclass(frozen=True)
class SignInForm:
    action_url: str
    username: str = ""  # as typed, kept after a failed sign-in
    error: Message | None = None  # why the sign-in failed, shown in the form


@dataclass(frozen=True)
class SetupInput:
    name: str = ""
    username: str = ""


@dataclass(frozen=True)
class SetupForm:
    """A fresh install has no accounts: the first one made here is an admin."""

    action_url: str
    values: SetupInput = SetupInput()
    errors: Mapping[str, str] = field(default_factory=dict)  # field name -> message


@dataclass(frozen=True)
class PasswordForm:
    """Signed in with a temporary password: a new one is chosen before anything else."""

    action_url: str
    name: str  # who is signed in
    sign_out_url: str
    errors: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class SignInPage:
    title: str
    messages: tuple[Message, ...] = ()
    sign_in: SignInForm | None = None
    setup: SetupForm | None = None
    change_password: PasswordForm | None = None
