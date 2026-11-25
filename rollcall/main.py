"""The Rollcall application: settings, startup checks, database, pages.

Run with: uvicorn rollcall.main:create_app --factory
"""

import logging
import os
import sys
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from rollcall import health, web
from rollcall.config import ConfigError, Settings, load_settings
from rollcall.db import create_pool
from rollcall.migrate import apply_migrations
from rollcall.mockups import routes as mockup_routes
from rollcall.pages import start, theme

log = logging.getLogger("rollcall")


class StartupError(Exception):
    """Something the app needs before serving pages is missing."""


def ensure_data_dir(path: Path) -> None:
    """Create the data folder if needed and prove the app can write to it."""
    try:
        path.mkdir(parents=True, exist_ok=True)
        # A uniquely named file per check, so workers starting together never collide.
        with tempfile.NamedTemporaryFile(dir=path, prefix=".write-test-"):
            pass
    except OSError as error:
        raise StartupError(f"DATA_DIR {path} is not a writable folder ({error.strerror})") from None


def create_app(settings: Settings | None = None) -> FastAPI:
    if settings is None:
        try:
            settings = load_settings(os.environ)
        except ConfigError as error:
            sys.exit(str(error))  # prints the problems and exits with status 1

    logging.basicConfig(
        level=settings.log_level, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        ensure_data_dir(settings.data_dir)
        pool = create_pool(settings.database_url, settings.db_pool_size)
        try:
            with pool.connection() as conn:
                applied = apply_migrations(conn)
            if applied:
                log.info("Applied migrations: %s", ", ".join(f"{v:04d}" for v in applied))
            app.state.pool = pool
            yield
        finally:
            pool.close()

    app = FastAPI(
        title="Rollcall", lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None
    )
    app.state.settings = settings
    app.state.templates = web.make_templates(settings.shop_timezone, nav_items=[start.NAV_ITEM])
    app.add_exception_handler(StarletteHTTPException, web.http_error)
    app.add_middleware(web.CatchErrors)  # inner: turns crashes into the error page
    app.add_middleware(web.SecurityHeaders)  # outer: headers on every response, errors too
    app.mount("/static", StaticFiles(directory=web.STATIC_DIR), name="static")
    app.include_router(health.router)
    app.include_router(start.router)
    app.include_router(theme.router)
    if settings.mockups:
        app.include_router(mockup_routes.router)
    return app
