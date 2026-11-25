"""Templates, the page frame's navigation, security headers and time display."""

import mimetypes
from dataclasses import dataclass
from datetime import datetime
from functools import partial
from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi import Request
from fastapi.templating import Jinja2Templates
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

# Serve JavaScript with its standard type whatever the host's mime.types file says.
mimetypes.add_type("text/javascript", ".js")


@dataclass(frozen=True)
class NavItem:
    label: str
    url: str


def format_shop_time(moment: datetime, shop_timezone: ZoneInfo) -> str:
    """Show a stored (UTC) time in the shop's zone, like the shop's invoices: 1/15/2026 12:05 PM."""
    if moment.tzinfo is None:
        raise ValueError("format_shop_time needs a time with a zone; stored times are UTC")
    local = moment.astimezone(shop_timezone)
    hour = local.hour % 12 or 12
    half = "AM" if local.hour < 12 else "PM"
    return f"{local.month}/{local.day}/{local.year} {hour}:{local.minute:02d} {half}"


def make_templates(shop_timezone: ZoneInfo, nav_items: list[NavItem]) -> Jinja2Templates:
    templates = Jinja2Templates(directory=TEMPLATES_DIR)
    templates.env.filters["shop_time"] = partial(format_shop_time, shop_timezone=shop_timezone)
    templates.env.globals["assets"] = ASSETS
    templates.env.globals["nav_items"] = nav_items
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
                for name, value in SECURITY_HEADERS.items():
                    if name.encode() not in present:
                        headers.append((name.encode(), value.encode()))
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_with_headers)
