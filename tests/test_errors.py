"""Friendly error pages; details only in the server log (spec: Safe error handling)."""

import logging
import re

import pytest
from fastapi.testclient import TestClient

from rollcall.main import create_app

CODE = re.compile(r"E-[A-Z0-9]{6}")
SECRET_DETAIL = "secret detail: SELECT password FROM staff /srv/rollcall/app.py"
HTMX = {"HX-Request": "true"}


@pytest.fixture
def failing_client(settings):
    """An app with one extra route that always fails with an unhandled error."""
    app = create_app(settings)

    @app.get("/explode")
    def explode():
        raise RuntimeError(SECRET_DETAIL)

    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


# --- page not found ------------------------------------------------------------------------


def test_unknown_address_shows_page_not_found_in_the_frame(client):
    response = client.get("/no-such-page")
    assert response.status_code == 404
    assert response.headers["content-type"].startswith("text/html")
    assert "Page not found" in response.text
    assert 'id="messages"' in response.text  # inside the normal frame
    assert '<a href="/"' in response.text  # a way back


def test_wrong_method_gets_a_friendly_page_too(client):
    response = client.delete("/")
    assert response.status_code == 405
    assert 'id="messages"' in response.text
    assert "Traceback" not in response.text


# --- unexpected failures -------------------------------------------------------------------


def test_unexpected_failure_shows_a_reference_code_and_no_details(failing_client):
    response = failing_client.get("/explode")
    assert response.status_code == 500
    assert "Something went wrong" in response.text
    assert CODE.search(response.text)
    for leak in ("secret detail", "RuntimeError", "Traceback", "SELECT", ".py", "/srv/"):
        assert leak not in response.text, leak


def test_the_log_has_the_full_error_under_the_same_code(failing_client, caplog):
    caplog.set_level(logging.ERROR)
    response = failing_client.get("/explode")
    code = CODE.search(response.text).group()

    [record] = [r for r in caplog.records if code in r.getMessage()]
    assert "/explode" in record.getMessage()
    assert record.exc_info is not None
    assert SECRET_DETAIL in str(record.exc_info[1])


def test_each_failure_gets_its_own_code(failing_client):
    first = CODE.search(failing_client.get("/explode").text).group()
    second = CODE.search(failing_client.get("/explode").text).group()
    assert first != second


# --- failures during htmx partial updates -----------------------------------------------------


def test_htmx_failure_returns_a_message_fragment_for_the_message_area(failing_client):
    response = failing_client.get("/explode", headers=HTMX)
    assert response.status_code == 500
    assert "<html" not in response.text  # a fragment, not a whole page
    assert CODE.search(response.text)
    assert "secret detail" not in response.text
    assert response.headers["hx-retarget"] == "#messages"
    assert response.headers["hx-reswap"] == "innerHTML"


def test_htmx_not_found_is_also_a_fragment(client):
    response = client.get("/no-such-page", headers=HTMX)
    assert response.status_code == 404
    assert "<html" not in response.text
    assert "Page not found" in response.text
    assert response.headers["hx-retarget"] == "#messages"


def test_the_browser_script_shows_htmx_error_responses():
    """htmx 2 drops 4xx/5xx responses by default; app.js must let them swap into #messages."""
    from rollcall.web import STATIC_DIR

    script = (STATIC_DIR / "app.js").read_text()
    assert "htmx:beforeSwap" in script
    assert "shouldSwap" in script


def test_error_pages_carry_the_security_headers(failing_client):
    response = failing_client.get("/explode")
    assert response.status_code == 500
    assert "default-src 'self'" in response.headers["content-security-policy"]
    assert response.headers["x-content-type-options"] == "nosniff"
