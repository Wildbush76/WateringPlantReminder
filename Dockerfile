FROM python:3.13-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN useradd app
WORKDIR /app
COPY . .

ENV UV_NO_DEV=1
RUN uv sync --locked


USER app


#start the bot
CMD ["uv","run","bot"]