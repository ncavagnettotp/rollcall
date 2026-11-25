# Rollcall app image. Built by compose.yaml; see openspec/specs/platform for what it must do.

FROM python:3.13.18-slim AS build
COPY --from=ghcr.io/astral-sh/uv:0.13.8 /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
WORKDIR /app
# Dependencies first, so code changes do not reinstall them.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY rollcall ./rollcall
RUN uv sync --frozen --no-dev --no-editable

FROM python:3.13.18-slim
RUN useradd --system --uid 10001 --no-create-home rollcall \
    && mkdir /data && chown rollcall:rollcall /data
COPY --from=build /app/.venv /app/.venv
ENV PATH=/app/.venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    WEB_CONCURRENCY=2
USER rollcall
WORKDIR /app
EXPOSE 8000
CMD ["python", "-m", "rollcall"]
