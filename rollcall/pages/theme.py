"""The light/dark switch in the header of every page (add-ui-components design.md decision 9).

The switch is a small form posting `mode` (light, dark or device) and `next` (the address it was
on). The choice is kept in a cookie for that browser; device forgets it, so the page follows the
device's own setting again. The answer always leads back inside Rollcall.

The form is read here with the standard library: two short fields do not justify a form-parsing
dependency. No CSRF token: a forged post could only change a colour scheme.
"""

from urllib.parse import parse_qs

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from rollcall.web import THEME_COOKIE, THEME_MODES

router = APIRouter()

ONE_YEAR = 365 * 24 * 60 * 60
MAX_FORM_BYTES = 2048


def safe_return(address: str) -> str:
    """The address to go back to: a path inside Rollcall, otherwise the start page."""
    if not address.startswith("/") or address.startswith(("//", "/\\")):
        return "/"
    if "\\" in address or any(ord(c) < 32 or ord(c) == 127 for c in address):
        return "/"
    return address


async def read_form(request: Request) -> dict[str, str]:
    """A small url-encoded form, refused if it is larger than MAX_FORM_BYTES."""
    body = bytearray()
    async for chunk in request.stream():
        body += chunk
        if len(body) > MAX_FORM_BYTES:
            raise HTTPException(400)
    try:
        fields = parse_qs(body.decode("utf-8"), keep_blank_values=True, max_num_fields=10)
    except (UnicodeDecodeError, ValueError):
        raise HTTPException(400) from None
    return {name: values[0] for name, values in fields.items()}


@router.post("/theme")
async def choose_theme(request: Request):
    form = await read_form(request)
    mode = form.get("mode")
    if mode not in (*THEME_MODES, "device"):
        raise HTTPException(400)
    response = RedirectResponse(safe_return(form.get("next", "/")), status_code=303)
    if mode == "device":
        response.delete_cookie(THEME_COOKIE, path="/", httponly=True, samesite="lax")
    else:
        response.set_cookie(
            THEME_COOKIE, mode, max_age=ONE_YEAR, path="/", httponly=True, samesite="lax"
        )
    return response
