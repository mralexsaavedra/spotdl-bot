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


# App metadata
def get_env(var, default=None):
    value = os.getenv(var, default)
    if value is not None and isinstance(value, str):
        value = value.strip()
    return value or default


VERSION = "0.1.0"

# Directory paths (with defaults for Docker)
DOWNLOAD_DIR = get_env("DOWNLOAD_DIR", "/music")
CACHE_DIR = get_env("CACHE_DIR", "/cache")
LOCALE_DIR = get_env("LOCALE_DIR", "/app/locale")

# Logging configuration
LOG_LEVEL = get_env("LOG_LEVEL", "INFO")
LOG_DIR = get_env("LOG_DIR", "/logs")

# Environment variables
LANGUAGE = get_env("LANGUAGE", "es")
TELEGRAM_TOKEN = get_env("TELEGRAM_TOKEN")
TELEGRAM_GROUP = get_env("TELEGRAM_GROUP")
TELEGRAM_ADMIN = get_env("TELEGRAM_ADMIN")

SPOTIFY_CLIENT_ID = get_env("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = get_env("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = get_env("SPOTIFY_REDIRECT_URI")


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
