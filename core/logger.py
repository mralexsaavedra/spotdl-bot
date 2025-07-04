from config.config import LOG_DIR, LOG_LEVEL
from loguru import logger
import os
import sys

os.makedirs(LOG_DIR, exist_ok=True)

# Clear existing loguru handlers
logger.remove()

# Console logging with colors
logger.add(
    sink=sys.stdout,
    level=LOG_LEVEL,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
)

# General file logging
logger.add(
    sink=f"{LOG_DIR}/app.log",
    rotation="5 MB",
    retention="7 days",
    level=LOG_LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
)

# spotdl-specific log file
logger.add(
    sink=f"{LOG_DIR}/spotdl.log",
    rotation="5 MB",
    retention="7 days",
    level=LOG_LEVEL,
    filter=lambda record: "spotdl" in record["name"],
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
)
