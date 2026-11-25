"""Addresses inside the mockup gallery."""

INDEX_URL = "/mockups"
SAMPLE_INVOICE_URL = f"{INDEX_URL}/sample-invoice.pdf"


def page_url(page: str, state: str | None = None) -> str:
    return f"{INDEX_URL}/pages/{page}" + (f"/{state}" if state else "")


def component_url(component: str) -> str:
    return f"{INDEX_URL}/components/{component}"
