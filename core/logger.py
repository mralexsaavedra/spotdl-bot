from config.config import LOG_DIR, LOG_LEVEL
from loguru import logger
import logging
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
    filter=lambda record: "spotdl"
    not in record["name"].lower(),  # Exclude spotdl logs from app.log
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


# --- Integrate standard logging (spotdl, etc) with loguru ---
class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())


logging.basicConfig(handlers=[InterceptHandler()], level=LOG_LEVEL)
logging.getLogger("spotdl").setLevel(LOG_LEVEL)
