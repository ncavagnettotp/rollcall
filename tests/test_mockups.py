"""The mockup gallery (spec: Mockup gallery)."""

import pytest


@pytest.mark.parametrize("path", ["/mockups", "/mockups/", "/mockups/pages/tire-set/checked-in"])
def test_gallery_is_not_found_when_switched_off(client, path):
    response = client.get(path)
    assert response.status_code == 404
    assert "Page not found" in response.text
