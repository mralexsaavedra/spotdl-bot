import logging
import sys
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


def setup_logger(
    name: str = None,
    level: str = None,
    log_dir: str = None,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
) -> logging.Logger:
    """
    Configure and return a logger with console output and rotating file handler.

    Parameters:
    - name: Logger name (default is root logger).
    - level: Logging level (default read from LOG_LEVEL env or DEBUG).
    - log_dir: Directory to store logs (default ./logs or from LOG_DIR env).
    - max_bytes: Max file size in bytes before rotating (default 10 MB).
    - backup_count: Number of backup files to keep (default 5).

    Environment variables used:
    - LOG_LEVEL
    - LOG_DIR

    Returns:
    - Configured logger with console and rotating file handlers.
    """

    logger = logging.getLogger(name)
    if name is None:
        # Always configure root logger
        for handler in logger.handlers:
            logger.removeHandler(handler)
    elif logger.hasHandlers():
        return logger  # Avoid adding duplicate handlers

    # Determine logging level from parameter or environment or default DEBUG
    level = level or os.getenv("LOG_LEVEL", "DEBUG")
    numeric_level = getattr(logging, level.upper(), logging.DEBUG)
    logger.setLevel(numeric_level)

    # Log format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(log_format, datefmt=date_format)

    # Colored formatter for console
    class ColoredFormatter(logging.Formatter):
        COLORS = {
            "DEBUG": "\033[94m",  # Blue
            "INFO": "\033[92m",  # Green
            "WARNING": "\033[93m",  # Yellow
            "ERROR": "\033[91m",  # Red
            "CRITICAL": "\033[95m",  # Magenta
        }
        RESET = "\033[0m"

        def format(self, record):
            color = self.COLORS.get(record.levelname, self.RESET)
            message = super().format(record)
            return f"{color}{message}{self.RESET}"

    colored_formatter = ColoredFormatter(log_format, datefmt=date_format)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(colored_formatter)
    logger.addHandler(console_handler)

    # File logs directory and rotating file handler
    log_dir = log_dir or os.getenv("LOG_DIR", "./logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"{name or 'app'}_{datetime.now().date()}.log")

    file_handler = RotatingFileHandler(
        log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # logger.propagate = False

    return logger
