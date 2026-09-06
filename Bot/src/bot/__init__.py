import asyncio
import logging

# logging
import sys

import dotenv

from .discord_logger_handler import DiscordHandler
from .plant_bot import plant_bot
from .test_logging_server import logging_server

# setup logging
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Setup Logger
log_format = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
_console_handler = logging.StreamHandler(sys.stdout)
_console_handler.setFormatter(log_format)

root_logger.addHandler(_console_handler)


# Load envs
dotenv.load_dotenv()


# Commands


def main() -> None:
    bot = plant_bot()

    wildbush: int = 704773768035172726
    discord_handler = DiscordHandler(bot, wildbush)
    discord_handler.setLevel(logging.ERROR)
    root_logger.addHandler(discord_handler)

    bot.run(log_handler=None)


def test_server() -> None:
    server = logging_server()
    asyncio.run(server.run())
