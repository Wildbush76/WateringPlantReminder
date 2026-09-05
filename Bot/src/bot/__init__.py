import asyncio

import dotenv

from . import globals as globals
from .plant_bot import plant_bot
from .test_logging_server import logging_server

# Load envs
dotenv.load_dotenv(".env")


# Commands


def main() -> None:
    bot = plant_bot()
    bot.run()


def test_server() -> None:
    server = logging_server()
    asyncio.run(server.run())
