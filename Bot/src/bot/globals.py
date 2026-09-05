import logging
import sys

root_logger = logging.getLogger()

# Setup Logger
log_format = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

_console_handler = logging.StreamHandler(sys.stdout)
_console_handler.setFormatter(log_format)

root_logger.addHandler(_console_handler)
