import asyncio

import dotenv

from . import globals as globals
from .test_logging_server import logging_server

# Load envs
dotenv.load_dotenv(".env")


# Commands


def main() -> None:
    print("Hello from bot!")


def test_server() -> None:
    server = logging_server()
    asyncio.run(server.run())
