from core.logger import setup_logger
import os

logger = setup_logger(__name__)

VERSION = "v0.0.1"
CONTAINER_NAME = os.environ.get("CONTAINER_NAME")
LANGUAGE = os.environ.get("LANGUAGE")

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_GROUP = os.environ.get("TELEGRAM_GROUP")
TELEGRAM_ADMIN = os.environ.get("TELEGRAM_ADMIN")

SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.environ.get("SPOTIFY_REDIRECT_URI")
