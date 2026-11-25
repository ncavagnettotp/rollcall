"""GET /health: is the app up and can it reach its database? Used by Docker and by people.

Answers in plain text without sign-in, and never says why the database is unavailable.
"""

import logging

from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse

router = APIRouter()
log = logging.getLogger("rollcall.health")
CHECK_TIMEOUT_SECONDS = 2


@router.get("/health", response_class=PlainTextResponse)
def health(request: Request):
    try:
        with request.app.state.pool.connection(timeout=CHECK_TIMEOUT_SECONDS) as conn:
            conn.execute("SELECT 1")
    except Exception as error:
        log.warning("Health check: database unavailable (%s)", type(error).__name__)
        return PlainTextResponse("database unavailable", status_code=503)
    return PlainTextResponse("ok")
