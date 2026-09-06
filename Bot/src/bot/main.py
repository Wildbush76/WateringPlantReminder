import asyncio
import logging

# logging
import sys

import dotenv

from .discord_logger_handler import DiscordHandler
from .grapher import create_graph
from .plant_bot import plant_bot
from .test_logging_server import logging_server


def _setup_logger():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    log_format = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    _console_handler = logging.StreamHandler(sys.stdout)
    _console_handler.setFormatter(log_format)

    root_logger.addHandler(_console_handler)


def run_bot() -> None:
    dotenv.load_dotenv()
    _setup_logger()

    bot = plant_bot()

    wildbush: int = 704773768035172726
    discord_handler = DiscordHandler(bot, wildbush)
    discord_handler.setLevel(logging.ERROR)
    logging.getLogger().addHandler(discord_handler)

    bot.run(log_handler=None)


def test_server() -> None:
    _setup_logger()

    server = logging_server()
    asyncio.run(server.run())


def graph_test() -> None:
    _setup_logger()

    async def make_graph():
        await create_graph("data.csv")

    asyncio.run(make_graph())
