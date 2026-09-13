FROM python:3.13-slim-trixie AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --locked --no-editable --no-install-project

COPY README.md src ./
RUN uv sync --no-dev --locked --no-editable

#Part 2
FROM python:3.13-slim-trixie AS runtime
COPY --from=builder --chown=root:root /app/.venv /app/.venv
VOLUME /var/lib/plant_bot

RUN chmod -R o=rx /app

RUN useradd -m app
USER app

ENV PYTHONPATH=/app/.venv/lib/python3.13/site-packages
CMD ["python", "-m", "bot"]