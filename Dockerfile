FROM python:3.13-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN useradd -m app
WORKDIR /app
RUN chown app /app
COPY . /app



USER app

ENV UV_NO_DEV=1
RUN uv sync --locked





#start the bot
CMD ["uv","run","bot"]