import os
import sys
from dotenv import load_dotenv
from core.logger import setup_logger

# Load environment variables early
if not os.getenv("RUNNING_IN_DOCKER"):
    load_dotenv()

# Logger
logger = setup_logger(__name__)

# App metadata
VERSION = "0.1.0"

# Directory paths
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR")
CACHE_DIR = os.getenv("CACHE_DIR")
LOCALE_DIR = os.getenv("LOCALE_DIR")

# Logging configuration (optional but supported)
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
LOG_DIR = os.getenv("LOG_DIR")

# Environment variables
LANGUAGE = os.getenv("LANGUAGE")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_GROUP = os.getenv("TELEGRAM_GROUP")
TELEGRAM_ADMIN = os.getenv("TELEGRAM_ADMIN")

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")


# Helper for validation
def require_env(var_value, var_name, description):
    if not var_value or not var_value.strip():
        logger.warning(f"Missing {description} in the `{var_name}` variable.")
        sys.exit(1)


# Required checks
require_env(TELEGRAM_TOKEN, "TELEGRAM_TOKEN", "bot token")
require_env(TELEGRAM_ADMIN, "TELEGRAM_ADMIN", "admin user chatId")
require_env(SPOTIFY_CLIENT_ID, "SPOTIFY_CLIENT_ID", "Spotify clientId")
require_env(SPOTIFY_CLIENT_SECRET, "SPOTIFY_CLIENT_SECRET", "Spotify clientSecret")
require_env(SPOTIFY_REDIRECT_URI, "SPOTIFY_REDIRECT_URI", "Spotify redirect URI")

# Handle TELEGRAM_GROUP fallback
if not TELEGRAM_GROUP or not TELEGRAM_GROUP.strip():
    if "," in str(TELEGRAM_ADMIN):
        logger.warning("Multiple admins require a group context (TELEGRAM_GROUP).")
        sys.exit(1)
    TELEGRAM_GROUP = TELEGRAM_ADMIN
