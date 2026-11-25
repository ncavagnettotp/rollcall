"""Templates, the page frame's navigation, security headers and time display."""

import logging
import mimetypes
import secrets
import string
from dataclasses import dataclass
from datetime import date, datetime
from functools import partial
from http import HTTPStatus
from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi import Request
from fastapi.templating import Jinja2Templates
from jinja2 import StrictUndefined
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.types import ASGIApp, Message, Receive, Scope, Send

PACKAGE_DIR = Path(__file__).parent
TEMPLATES_DIR = PACKAGE_DIR / "templates"
STATIC_DIR = PACKAGE_DIR / "static"

# Vendored files (see static/vendor/VENDORED.txt). Change the version here when updating.
ASSETS = {
    "pico_css": "/static/vendor/pico-2.1.1.min.css",
    "htmx_js": "/static/vendor/htmx-2.0.11.min.js",
    "app_css": "/static/app.css",
    "app_js": "/static/app.js",
}

SECURITY_HEADERS = {
    "content-security-policy": (
        "default-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    ),
    "x-content-type-options": "nosniff",
    "referrer-policy": "same-origin",
}
# A PDF may be shown inside Rollcall's own pages (the invoice beside the tire set form);
# nothing else may be shown inside any page, Rollcall's or another site's.
PDF_SECURITY_HEADERS = SECURITY_HEADERS | {
    "content-security-policy": (
        "default-src 'self'; frame-ancestors 'self'; base-uri 'self'; form-action 'self'"
    ),
}

# Serve JavaScript with its standard type whatever the host's mime.types file says.
mimetypes.add_type("text/javascript", ".js")


@dataclass(frozen=True)
class NavItem:
    label: str
    url: str

    def is_current(self, path: str) -> bool:
        """True on this item's page and on the pages below it (but "/" only on itself)."""
        return path == self.url or (self.url != "/" and path.startswith(self.url.rstrip("/") + "/"))


def format_shop_time(moment: datetime, shop_timezone: ZoneInfo) -> str:
    """Show a stored (UTC) time in the shop's zone, like the shop's invoices: 1/15/2026 12:05 PM."""
    if moment.tzinfo is None:
        raise ValueError("format_shop_time needs a time with a zone; stored times are UTC")
    local = moment.astimezone(shop_timezone)
    hour = local.hour % 12 or 12
    half = "AM" if local.hour < 12 else "PM"
    return f"{local.month}/{local.day}/{local.year} {hour}:{local.minute:02d} {half}"


# The light/dark switch (add-ui-components design.md decision 9): the choice lives in this cookie,
# and the frame writes it on <html> as data-theme. No cookie means "follow the device".
THEME_COOKIE = "rollcall_theme"
THEME_MODES = ("light", "dark")


def theme_of(request: Request) -> str | None:
    """The mode this browser chose, or None to follow the device. Anything else is ignored."""
    value = request.cookies.get(THEME_COOKIE)
    return value if value in THEME_MODES else None


def format_shop_date(day: date) -> str:
    """A calendar date as the shop's invoices write it: 3/2/2026."""
    return f"{day.month}/{day.day}/{day.year}"


def make_templates(shop_timezone: ZoneInfo, nav_items: list[NavItem]) -> Jinja2Templates:
    templates = Jinja2Templates(directory=TEMPLATES_DIR)
    # A value a template shows but the page data lacks is an error naming it, never a blank.
    # Optional values are passed explicitly as None.
    templates.env.undefined = StrictUndefined
    templates.env.filters["shop_time"] = partial(format_shop_time, shop_timezone=shop_timezone)
    templates.env.filters["shop_date"] = format_shop_date
    templates.env.globals["assets"] = ASSETS
    templates.env.globals["theme_of"] = theme_of
    templates.env.globals["nav_items"] = nav_items
    # Optional frame values; a page may pass its own. None means not shown.
    templates.env.globals["signed_in"] = None  # views.frame.SignedInStaff
    templates.env.globals["mockup"] = None  # mockups.samples.Banner, gallery pages only
    return templates


def render(request: Request, template: str, context: dict | None = None, status_code: int = 200):
    """Render a page (or fragment) with the app's templates."""
    templates: Jinja2Templates = request.app.state.templates
    return templates.TemplateResponse(request, template, context or {}, status_code=status_code)


class SecurityHeaders:
    """Adds the security headers to every response, including errors and static files."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_headers(message: Message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                present = {name.lower() for name, _ in headers}
                content_type = dict(headers).get(b"content-type", b"")
                is_pdf = content_type.split(b";")[0].strip().lower() == b"application/pdf"
                chosen = PDF_SECURITY_HEADERS if is_pdf else SECURITY_HEADERS
                for name, value in chosen.items():
                    if name.encode() not in present:
                        headers.append((name.encode(), value.encode()))
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_with_headers)


# --- errors -------------------------------------------------------------------------------

log_errors = logging.getLogger("rollcall.errors")

CODE_ALPHABET = string.ascii_uppercase + string.digits
FRIENDLY = {
    404: ("Page not found", "There is no page at this address."),
    405: ("Not allowed here", "That action is not available on this page."),
}
FRAGMENT_HEADERS = {"HX-Retarget": "#messages", "HX-Reswap": "innerHTML"}


def reference_code() -> str:
    """A short code shown to staff and written to the log, e.g. E-7F3K2Q."""
    return "E-" + "".join(secrets.choice(CODE_ALPHABET) for _ in range(6))


def render_error(
    request: Request,
    status_code: int,
    title: str,
    message: str,
    code: str | None = None,
    headers: dict | None = None,
):
    """The error page in the frame, or for htmx requests a fragment for the message area."""
    context = {"title": title, "message": message, "code": code}
    if request.headers.get("HX-Request") == "true":
        response = render(request, "_error_fragment.html", context, status_code)
        response.headers.update(FRAGMENT_HEADERS)
    else:
        response = render(request, "error.html", context, status_code)
    response.headers.update(headers or {})
    return response


async def http_error(request: Request, error: StarletteHTTPException):
    """Expected errors such as page not found: friendly words, no reference code."""
    status = error.status_code
    title, message = FRIENDLY.get(status, (HTTPStatus(status).phrase, "The request did not work."))
    return render_error(request, status, title, message, headers=getattr(error, "headers", None))


class CatchErrors:
    """Turns any unhandled error into the "Something went wrong" page with a reference code.

    The full error goes only to the log, under the same code. Sits inside SecurityHeaders, so
    error pages get the same headers as every other response.
    """

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        started = False

        async def tracking_send(message: Message):
            nonlocal started
            started = started or message["type"] == "http.response.start"
            await send(message)

        try:
            await self.app(scope, receive, tracking_send)
        except Exception as error:
            code = reference_code()
            log_errors.error(
                "%s unhandled error on %s %s", code, scope["method"], scope["path"], exc_info=error
            )
            if started:
                return  # the response was already under way; nothing more can be sent
            request = Request(scope)
            response = render_error(
                request,
                500,
                "Something went wrong",
                "Rollcall could not finish that. Try again; if it keeps happening, "
                "tell the person who looks after Rollcall and give them this code.",
                code=code,
            )
            await response(scope, receive, send)
