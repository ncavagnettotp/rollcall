"""The light/dark switch (spec: Light and dark mode; design.md decision 9 of add-ui-components).

The header of every page has a Light / Dark / Device form posting to /theme. The choice is kept
in a cookie for that browser, and the server writes it into the page as data-theme on <html>, so
the page is drawn in that mode from the first paint without JavaScript.
"""

import re

import pytest

COOKIE = "rollcall_theme"


def post_theme(client, mode, next_url="/"):
    return client.post("/theme", data={"mode": mode, "next": next_url}, follow_redirects=False)


def html_tag(html: str) -> str:
    return re.search(r"<html[^>]*>", html).group(0)


@pytest.fixture(autouse=True)
def fresh_cookies(client):
    client.cookies.clear()
    yield
    client.cookies.clear()


# --- the route --------------------------------------------------------------------------------


@pytest.mark.parametrize("mode", ["light", "dark"])
def test_picking_a_mode_remembers_it_and_returns_to_the_page(client, mode):
    response = post_theme(client, mode)
    assert response.status_code == 303
    assert response.headers["location"] == "/"
    cookie = response.headers["set-cookie"]
    assert cookie.startswith(f"{COOKIE}={mode};")
    for part in ("HttpOnly", "Max-Age=31536000", "Path=/", "SameSite=lax"):
        assert part in cookie, part


def test_device_forgets_the_choice(client):
    post_theme(client, "dark")
    response = post_theme(client, "device")
    assert response.status_code == 303
    cookie = response.headers["set-cookie"]
    assert cookie.startswith(f"{COOKIE}=")
    assert "Max-Age=0" in cookie
    assert COOKIE not in client.cookies


@pytest.mark.parametrize("mode", ["", "purple", "DARK", "auto"])
def test_unknown_modes_are_refused(client, mode):
    response = post_theme(client, mode)
    assert response.status_code == 400
    assert "set-cookie" not in response.headers


def test_missing_mode_is_refused(client):
    response = client.post("/theme", data={"next": "/"}, follow_redirects=False)
    assert response.status_code == 400


def test_oversized_form_is_refused(client):
    response = post_theme(client, "dark", "/" + "x" * 5000)
    assert response.status_code == 400


def test_returns_to_the_same_address_with_its_query(client):
    target = "/mockups/pages/tire-set/edit?design=d"
    assert post_theme(client, "dark", target).headers["location"] == target


@pytest.mark.parametrize(
    "outside",
    [
        "https://evil.example/",
        "//evil.example/x",
        "/\\evil.example",
        "javascript:alert(1)",
        "relative/path",
        "",
        "/ok\r\nX-Injected: 1",
    ],
)
def test_never_returns_outside_rollcall(client, outside):
    response = post_theme(client, "dark", outside)
    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_get_is_not_allowed(client):
    assert client.get("/theme").status_code == 405


# --- the page ---------------------------------------------------------------------------------


def test_page_without_a_choice_follows_the_device(client):
    assert html_tag(client.get("/").text) == '<html lang="en">'


@pytest.mark.parametrize("mode", ["light", "dark"])
def test_page_is_drawn_in_the_chosen_mode(client, mode):
    post_theme(client, mode)
    assert html_tag(client.get("/").text) == f'<html lang="en" data-theme="{mode}">'


def test_unknown_cookie_value_is_ignored(client):
    client.cookies.set(COOKIE, '"><script>')
    assert html_tag(client.get("/").text) == '<html lang="en">'


def test_choice_carries_to_error_pages(client):
    post_theme(client, "dark")
    assert 'data-theme="dark"' in html_tag(client.get("/no-such-page").text)


# --- the switch in the header -----------------------------------------------------------------


def switch_form(html: str) -> str:
    match = re.search(r'<form[^>]*action="/theme".*?</form>', html, re.S)
    assert match, "no light/dark switch on the page"
    return match.group(0)


def test_header_has_the_switch_with_the_current_mode_marked(client):
    form = switch_form(client.get("/").text)
    assert 'method="post"' in form
    for mode in ("light", "dark", "device"):
        assert f'name="mode" value="{mode}"' in form
    assert re.search(r'value="device"[^>]*aria-pressed="true"', form)
    assert form.count('aria-pressed="true"') == 1


def test_switch_marks_the_chosen_mode(client):
    post_theme(client, "dark")
    form = switch_form(client.get("/").text)
    assert re.search(r'value="dark"[^>]*aria-pressed="true"', form)
    assert form.count('aria-pressed="true"') == 1


def test_switch_returns_to_the_page_it_is_on(client):
    form = switch_form(client.get("/?from=test").text)
    assert 'name="next" value="/?from=test"' in form


def test_switch_is_on_error_pages_too(client):
    switch_form(client.get("/no-such-page").text)
