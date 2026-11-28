"""Rollcall serves every asset itself (spec: Works without the internet)."""

import hashlib
from pathlib import Path

import pytest

VENDOR = Path(__file__).parent.parent / "rollcall" / "static" / "vendor"


def vendored_files():
    """(file name, version, sha256) for each line of VENDORED.txt."""
    entries = []
    for line in (VENDOR / "VENDORED.txt").read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            name, version, sha256, *_source = line.split()
            entries.append((name, version, sha256))
    return entries


def test_htmx_and_pico_are_both_recorded():
    names = [name for name, _, _ in vendored_files()]
    assert any(name.startswith("htmx-2.") for name in names)
    assert any(name.startswith("pico-2.") for name in names)


@pytest.mark.parametrize(("name", "version", "sha256"), vendored_files())
def test_vendored_file_matches_its_recorded_checksum(name, version, sha256):
    content = (VENDOR / name).read_bytes()
    assert hashlib.sha256(content).hexdigest() == sha256
    assert version in name


def test_every_vendored_file_is_recorded():
    recorded = {name for name, _, _ in vendored_files()}
    on_disk = {path.name for path in VENDOR.iterdir() if path.name != "VENDORED.txt"}
    assert on_disk == recorded


@pytest.mark.parametrize(
    ("path", "content_type"),
    [
        ("/static/app.css", "text/css"),
        ("/static/app.js", "text/javascript"),
        ("/static/vendor/htmx-2.0.11.min.js", "text/javascript"),
        ("/static/vendor/pico-2.1.1.min.css", "text/css"),
    ],
)
def test_assets_are_served_with_the_right_type(client, path, content_type):
    response = client.get(path)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith(content_type)


STATIC = VENDOR.parent
APP_CSS = (STATIC / "app.css").read_text()


def pico_data_icons() -> set[str]:
    """Pico's icon variables that are data: images (blocked by the content security policy)."""
    import re

    pico = next(VENDOR.glob("pico-*.css")).read_text()
    return set(re.findall(r"--pico-icon-([a-z]+):url\(\"data:", pico))


def test_rollcall_uses_no_data_images():
    import re

    assert not re.search(r"url\(\s*[\"']?data:", APP_CSS)


def test_every_pico_icon_is_replaced_by_a_file_or_left_out():
    """Each of Pico's data: icons points at Rollcall's own file, or is switched off."""
    icons = pico_data_icons()
    assert {"checkbox", "chevron", "date", "invalid"} <= icons
    for name in icons:
        # From the site root: a url in a variable is read against Pico's stylesheet, not ours.
        as_file = f'--pico-icon-{name}: url("/static/pico-icons/{name}.svg");' in APP_CSS
        left_out = f"--pico-icon-{name}: none;" in APP_CSS
        assert as_file or left_out, name
        if as_file:
            assert (STATIC / "pico-icons" / f"{name}.svg").is_file(), name


def test_pico_icon_files_are_served_as_svg(client):
    response = client.get("/static/pico-icons/checkbox.svg")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/svg+xml")


def test_pages_name_rollcalls_own_tab_icon(client):
    """Without it the browser asks for /favicon.ico on every page and gets "not found"."""
    assert '<link rel="icon" href="/static/favicon.svg"' in client.get("/").text
    response = client.get("/static/favicon.svg")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/svg+xml")
