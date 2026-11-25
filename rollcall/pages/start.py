"""Temporary start page, so the frame can be seen before real pages exist.

Removed by add-dashboard, which takes over "/".
"""

from datetime import UTC, datetime

from fastapi import APIRouter, Request

from rollcall.web import NavItem, render

router = APIRouter()
NAV_ITEM = NavItem("Home", "/")


@router.get("/")
def start_page(request: Request):
    return render(request, "start.html", {"now": datetime.now(UTC)})
