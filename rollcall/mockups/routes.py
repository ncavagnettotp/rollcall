"""The mockup gallery's addresses. Registered only when MOCKUPS=on (see rollcall/main.py).

Forms in mockups post to the state that shows their result; posting simply opens that state.
Nothing here reads or changes the database.
"""

from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse

from rollcall.mockups import samples
from rollcall.web import render

# Synthetic, made by scripts/make_sample_invoice.py. Real invoices never go in the gallery.
SAMPLE_INVOICE = Path(__file__).parent / "sample-invoice.pdf"

router = APIRouter(prefix=samples.INDEX_URL)


def _frame(title: str, staff=samples.STAFF) -> dict:
    return {
        "mockup": samples.Banner(title),
        "nav_items": samples.navigation(staff),
        "signed_in": staff,
    }


@router.get("")
def index(request: Request):
    context = {"pages": samples.PAGES, "components": samples.COMPONENTS}
    context |= _frame("All mockups")
    return render(request, "mockups/index.html", context)


@router.get("/pages/{page_slug}")
def page(request: Request, page_slug: str):
    found = samples.find_page(page_slug)
    if found is None:
        raise HTTPException(404)
    if found.states:
        return RedirectResponse(samples.page_url(found.slug, found.states[0].slug))
    context = {"page": found} | _frame(found.title)
    return render(request, "mockups/not_yet.html", context)


DESIGN_COOKIE = "mockup_design"


@router.get("/pages/{page_slug}/{state_slug}")
def state(request: Request, page_slug: str, state_slug: str, design: str | None = None):
    found = samples.find_page(page_slug)
    shown = found and samples.find_state(found, state_slug)
    if not shown:
        raise HTTPException(404)
    title = f"{found.title}: {shown.title}"
    context = dict(shown.data()) | _frame(title, shown.staff)
    if not found.designs:
        return render(request, shown.template, context)

    # ?design= picks a design; a cookie remembers it while the owner clicks through.
    if design is not None:
        chosen = samples.find_design(found, design)
        if chosen is None:
            raise HTTPException(404)
    else:
        remembered = request.cookies.get(DESIGN_COOKIE, "")
        chosen = samples.find_design(found, remembered) or found.designs[0]
    switch = tuple(
        samples.DesignChoice(
            d.letter, d.name, f"{request.url.path}?design={d.letter}", d.letter == chosen.letter
        )
        for d in found.designs
    )
    context["mockup"] = samples.Banner(f"{title} · design {chosen.letter.upper()}", designs=switch)
    context["design"] = chosen
    response = render(request, shown.template.format(design=chosen.letter), context)
    response.set_cookie(DESIGN_COOKIE, chosen.letter, path=samples.INDEX_URL, samesite="lax")
    return response


@router.post("/pages/{page_slug}")
@router.post("/pages/{page_slug}/{state_slug}")
def submit(page_slug: str, state_slug: str | None = None):
    """A mockup form was submitted: show the page or state it leads to."""
    return RedirectResponse(samples.page_url(page_slug, state_slug), status_code=303)


@router.get("/components/{component_slug}")
def component(request: Request, component_slug: str):
    found = samples.find_component(component_slug)
    if found is None:
        raise HTTPException(404)
    context = {"component": found} | _frame(f"Component: {found.title}")
    return render(request, found.template, context)


@router.get("/sample-invoice.pdf")
def sample_invoice():
    """The invented invoice shown beside the tire set form's "filled from a PDF" state."""
    return FileResponse(SAMPLE_INVOICE, media_type="application/pdf")
