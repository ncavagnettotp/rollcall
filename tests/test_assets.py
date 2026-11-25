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
