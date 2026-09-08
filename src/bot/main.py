import logging

# logging
import sys

import dotenv

from .discord_bot.discord_logger_handler import DiscordHandler
from .discord_bot.plant_bot import plant_bot


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
