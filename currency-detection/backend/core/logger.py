"""
Structured logging using loguru.
"""
import sys
import os
from loguru import logger

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE_PATH", "outputs/logs/app.log")

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logger.remove()
logger.add(sys.stderr, level=LOG_LEVEL, colorize=True,
           format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan> - {message}")
logger.add(LOG_FILE, level=LOG_LEVEL, rotation="10 MB", retention="7 days",
           format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} - {message}")

__all__ = ["logger"]
