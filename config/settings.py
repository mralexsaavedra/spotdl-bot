from core.locale import get_text
from core.logger import setup_logger
import os
import sys

logger = setup_logger(__name__)

VERSION = "0.0.1"
TOKEN_PATH = '/cache/token.json'
CONTAINER_NAME = os.environ.get("CONTAINER_NAME")

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_GROUP = os.environ.get("TELEGRAM_GROUP")
TELEGRAM_ADMIN = os.environ.get("TELEGRAM_ADMIN")

SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.environ.get("SPOTIFY_REDIRECT_URI")

if CONTAINER_NAME is None or CONTAINER_NAME == '':
	logger.error(get_text("error_bot_container_name"))
	sys.exit(1)
if TELEGRAM_TOKEN is None or TELEGRAM_TOKEN == '':
	logger.error(get_text("error_bot_token"))
	sys.exit(1)
if TELEGRAM_ADMIN is None or TELEGRAM_ADMIN == '':
	logger.error(get_text("error_bot_telegram_admin"))
	sys.exit(1)
if TELEGRAM_GROUP is None or TELEGRAM_GROUP == '':
	if len(str(TELEGRAM_ADMIN).split(',')) > 1:
		logger.error(get_text("error_multiple_admin_only_with_group"))
		sys.exit(1)
	TELEGRAM_GROUP = TELEGRAM_ADMIN
if SPOTIFY_CLIENT_ID is None or SPOTIFY_CLIENT_ID == '':
	logger.error(get_text("error_bot_spotify_client_id"))
	sys.exit(1)
if SPOTIFY_CLIENT_SECRET is None or SPOTIFY_CLIENT_SECRET == '':
	logger.error(get_text("error_bot_spotify_client_secret"))
	sys.exit(1)
if SPOTIFY_REDIRECT_URI is None or SPOTIFY_REDIRECT_URI == '':
	logger.error(get_text("error_bot_spotify_redirect_uri"))
	sys.exit(1)