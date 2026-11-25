"""The shared page frame, security headers and app startup (spec: Shared page frame, Works
without the internet, One-command start)."""

import json
from datetime import UTC, datetime
from html.parser import HTMLParser
from zoneinfo import ZoneInfo

import psycopg
import pytest

EXPECTED_CSP = "default-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"


class PageParts(HTMLParser):
    """Collects what the frame tests need from a page."""

    def __init__(self):
        super().__init__()
        self.links = []  # every src= and href=
        self.nav_links = []
        self.meta = {}
        self.ids = set()
        self.inline_scripts = 0
        self.style_tags = 0
        self.style_attributes = 0
        self.html_lang = None
        self.header_text = ""
        self.title = ""
        self._in = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self._in.append(tag)
        for name in ("src", "href"):
            if attrs.get(name):
                self.links.append(attrs[name])
        if tag == "a" and "nav" in self._in and attrs.get("href"):
            self.nav_links.append(attrs["href"])
        if tag == "meta" and attrs.get("name"):
            self.meta[attrs["name"]] = attrs.get("content", "")
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "script" and not attrs.get("src"):
            self.inline_scripts += 1
        if tag == "style":
            self.style_tags += 1
        if "style" in attrs:
            self.style_attributes += 1
        if tag == "html":
            self.html_lang = attrs.get("lang")

    def handle_endtag(self, tag):
        if tag in self._in:
            while self._in.pop() != tag:
                pass

    def handle_data(self, data):
        if "header" in self._in:
            self.header_text += data
        if "title" in self._in:
            self.title += data


def parse(html: str) -> PageParts:
    parts = PageParts()
    parts.feed(html)
    return parts


@pytest.fixture
def start_page(client):
    response = client.get("/")
    return response, parse(response.text)


# --- the start page in the frame ------------------------------------------------------------


def test_start_page_is_html(start_page):
    response, _ = start_page
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")


def test_frame_has_header_nav_messages_and_content(start_page):
    response, page = start_page
    assert "Rollcall" in page.header_text
    assert "Rollcall" in page.title
    assert page.nav_links, "the frame has a navigation with at least one link"
    assert "messages" in page.ids
    assert "Rollcall is running" in response.text


def test_frame_uses_vendored_pico_and_htmx(start_page):
    _, page = start_page
    assert "/static/vendor/pico-2.1.1.min.css" in page.links
    assert "/static/vendor/htmx-2.0.11.min.js" in page.links
    assert "/static/app.css" in page.links
    assert "/static/app.js" in page.links


def test_frame_is_set_up_for_phones(start_page):
    _, page = start_page
    assert page.html_lang == "en"
    assert "width=device-width" in page.meta.get("viewport", "")


# --- nothing from the internet ---------------------------------------------------------------


def test_every_link_and_asset_is_local(start_page):
    _, page = start_page
    outside = [link for link in page.links if link.startswith(("http:", "https:", "//"))]
    assert outside == []


def test_every_local_asset_loads(client, start_page):
    _, page = start_page
    for link in page.links:
        if link.startswith("/static/"):
            assert client.get(link).status_code == 200, link


def test_every_nav_link_leads_to_a_page(client, start_page):
    _, page = start_page
    for link in page.nav_links:
        assert client.get(link).status_code == 200, link


def test_no_inline_scripts_or_styles(start_page):
    """The content security policy blocks inline code, so the frame must not need any."""
    _, page = start_page
    assert page.inline_scripts == 0
    assert page.style_tags == 0
    assert page.style_attributes == 0


def test_htmx_indicator_styles_are_turned_off(start_page):
    """htmx would otherwise inject an inline <style>, which the policy blocks."""
    _, page = start_page
    config = json.loads(page.meta["htmx-config"])
    assert config["includeIndicatorStyles"] is False


# --- security headers on every response ----------------------------------------------------


@pytest.mark.parametrize("path", ["/", "/static/app.css", "/no-such-page"])
def test_security_headers_on_every_response(client, path):
    headers = client.get(path).headers
    assert headers["content-security-policy"] == EXPECTED_CSP
    assert headers["x-content-type-options"] == "nosniff"
    assert headers["referrer-policy"] == "same-origin"


# --- startup -------------------------------------------------------------------------------


def test_startup_applies_migrations(client, database_url):
    with psycopg.connect(database_url) as conn:
        assert conn.execute("SELECT to_regclass('schema_migrations')").fetchone()[0]


def test_startup_creates_the_data_directory(client, settings):
    assert settings.data_dir.is_dir()


def test_startup_refuses_an_unwritable_data_directory(settings, tmp_path):
    import dataclasses

    from fastapi.testclient import TestClient

    from rollcall.main import create_app

    blocker = tmp_path / "not-a-folder"
    blocker.write_text("a file where the data folder should be")
    bad = dataclasses.replace(settings, data_dir=blocker / "data")

    with pytest.raises(Exception, match="DATA_DIR"), TestClient(create_app(bad)):
        pass


# --- times are shown in the shop's time zone -------------------------------------------------


def test_shop_time_shows_central_standard_time_in_winter():
    from rollcall.web import format_shop_time

    moment = datetime(2026, 1, 15, 18, 5, tzinfo=UTC)
    assert format_shop_time(moment, ZoneInfo("America/Chicago")) == "1/15/2026 12:05 PM"


def test_shop_time_follows_daylight_saving_in_summer():
    from rollcall.web import format_shop_time

    moment = datetime(2026, 7, 15, 18, 5, tzinfo=UTC)
    assert format_shop_time(moment, ZoneInfo("America/Chicago")) == "7/15/2026 1:05 PM"


def test_shop_time_refuses_times_without_a_zone():
    from rollcall.web import format_shop_time

    with pytest.raises(ValueError):
        format_shop_time(datetime(2026, 1, 15, 18, 5), ZoneInfo("America/Chicago"))
