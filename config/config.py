import os
import sys
from dotenv import load_dotenv
from loguru import logger


class ConfigError(Exception):
    """Custom exception for configuration errors."""

    pass


# Load environment variables early
if not os.getenv("RUNNING_IN_DOCKER"):
    load_dotenv()

VERSION = "0.1.1"

# Directory paths (with defaults for Docker)
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "/music")
CACHE_DIR = os.getenv("CACHE_DIR", "/cache")
LOCALE_DIR = os.getenv("LOCALE_DIR", "/locale")

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = os.getenv("LOG_DIR", "/logs")

# Environment variables
LANGUAGE = os.getenv("LANGUAGE", "es")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_GROUP = os.getenv("TELEGRAM_GROUP")
TELEGRAM_ADMIN = os.getenv("TELEGRAM_ADMIN")

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")


def require_env(var_value, var_name, description):
    """
    Validates that a required environment variable is set.
    Raises ConfigError if not set.
    """
    if not var_value or not str(var_value).strip():
        logger.warning(f"Missing {description} in the `{var_name}` variable.")
        raise ConfigError(f"Missing {description} in the `{var_name}` variable.")


# Required checks
try:
    require_env(TELEGRAM_TOKEN, "TELEGRAM_TOKEN", "bot token")
    require_env(TELEGRAM_ADMIN, "TELEGRAM_ADMIN", "admin user chatId")
    require_env(SPOTIFY_CLIENT_ID, "SPOTIFY_CLIENT_ID", "Spotify clientId")
    require_env(SPOTIFY_CLIENT_SECRET, "SPOTIFY_CLIENT_SECRET", "Spotify clientSecret")
    require_env(SPOTIFY_REDIRECT_URI, "SPOTIFY_REDIRECT_URI", "Spotify redirect URI")
except ConfigError as e:
    logger.error(str(e))
    sys.exit(1)


# Handle TELEGRAM_GROUP fallback
def validate_telegram_group():
    global TELEGRAM_GROUP
    if not TELEGRAM_GROUP or not TELEGRAM_GROUP.strip():
        if "," in str(TELEGRAM_ADMIN):
            logger.warning("Multiple admins require a group context (TELEGRAM_GROUP).")
            raise ConfigError(
                "Multiple admins require a group context (TELEGRAM_GROUP)."
            )
        TELEGRAM_GROUP = TELEGRAM_ADMIN


try:
    validate_telegram_group()
except ConfigError as e:
    logger.error(str(e))
    sys.exit(1)


# Optionally, ensure directories exist (for Docker and local dev)
def ensure_dir(path):
    if path and not os.path.exists(path):
        try:
            os.makedirs(path, exist_ok=True)
            logger.info(f"Created directory: {path}")
        except Exception as e:
            logger.warning(f"Could not create directory {path}: {e}")


for d in [DOWNLOAD_DIR, CACHE_DIR, LOCALE_DIR, LOG_DIR]:
    ensure_dir(d)
