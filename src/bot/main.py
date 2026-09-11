import logging

# logging
import sys

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
    _setup_logger()

    bot = plant_bot()

    # Load the token
    with open("/run/secrets/plant_token") as file:
        token = file.read()

    bot.run(token=token, log_handler=None)
