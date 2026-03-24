import logging
import os
from datetime import datetime

# Create logs directory
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, f"sentinel_{datetime.now().strftime('%Y%m%d')}.log")


def get_logger(name="SentinelAI"):
    """
    Returns a configured logger instance
    """

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Prevent duplicate logs
    if logger.hasHandlers():
        return logger

    # -----------------------------
    # FORMAT
    # -----------------------------
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    # -----------------------------
    # FILE HANDLER
    # -----------------------------
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # -----------------------------
    # CONSOLE HANDLER
    # -----------------------------
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # -----------------------------
    # ADD HANDLERS
    # -----------------------------
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Global logger instance
logger = get_logger()

