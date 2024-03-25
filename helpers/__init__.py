import logging

from colorlog import ColoredFormatter

from . import captcha
from . import constants
from . import email
from . import oauth
from . import twitter
from . import utils

logger = logging.getLogger(__name__)

colored_formatter = ColoredFormatter(
    "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    },
)

file_handler = logging.FileHandler("errors.log")
file_handler.setLevel(logging.CRITICAL)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(colored_formatter)
logger.addHandler(console_handler)

logger.setLevel(logging.INFO)
