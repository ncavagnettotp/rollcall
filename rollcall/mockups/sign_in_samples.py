"""Sample data for the sign-in pages' gallery states. Every name is invented.

Signing in leads to the dashboard; setting up the first admin leads to the empty dashboard of a
fresh install; signing out from any gallery page leads to the signed-out state.
"""

from dataclasses import replace

from rollcall.mockups.urls import page_url
from rollcall.views.shared import Message
from rollcall.views.sign_in import (
    PasswordForm,
    SetupForm,
    SetupInput,
    SignInForm,
    SignInPage,
)

DASHBOARD = page_url("dashboard", "busy")
WRONG = "That username and password don't match. Check both and try again."
TOO_SHORT = "Use at least 12 characters; this one has 8."


def state(slug: str) -> str:
    return page_url("sign-in", slug)


def _sign_in(**values) -> SignInPage:
    return SignInPage("Sign in", sign_in=SignInForm(DASHBOARD, **values))


def sign_in() -> dict:
    return {"page": _sign_in()}


def signed_out() -> dict:
    return {"page": SignInPage("Sign in", (Message("Signed out."),), SignInForm(DASHBOARD))}


def wrong_password() -> dict:
    return {"page": _sign_in(username="dana", error=Message(WRONG, "error"))}


def deactivated() -> dict:
    return {
        "page": _sign_in(
            username="kpike",
            error=Message(
                "This account is turned off, so it can't sign in. An admin can turn it back on "
                "in Admin settings.",
                "error",
            ),
        )
    }


def first_admin() -> dict:
    return {"page": SignInPage("Set up Rollcall", setup=SetupForm(page_url("dashboard", "empty")))}


def first_admin_errors() -> dict:
    form = SetupForm(
        state("first-admin-errors"),
        SetupInput("Marcus Oyelaran", "marcus o"),
        {
            "username": "Use letters, digits, dots and dashes only, no spaces: e.g. marcus.o",
            "password": TOO_SHORT,
            "password_again": "The two passwords are different.",
        },
    )
    messages = (Message("Three values need fixing before Rollcall can be set up.", "error"),)
    return {"page": SignInPage("Set up Rollcall", messages, setup=form)}


def _change(**values) -> PasswordForm:
    form = PasswordForm(DASHBOARD, "Jordan Pike", page_url("sign-in", "signed-out"))
    return replace(form, **values)


def change_password() -> dict:
    return {"page": SignInPage("Choose a new password", change_password=_change())}


def change_password_errors() -> dict:
    form = _change(
        action_url=state("change-password-errors"),
        errors={
            "password": TOO_SHORT,
            "password_again": "The two passwords are different.",
        },
    )
    return {"page": SignInPage("Choose a new password", change_password=form)}
