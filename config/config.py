from core.logger import setup_logger
from dotenv import load_dotenv
import os
import sys

VERSION = "0.1.0"
TOKEN_PATH = '/cache/token.json'
LOCALE_DIR = "./locale"
DOWNLOAD_DIR = "/music"

logger = setup_logger(__name__)
if not os.getenv("RUNNING_IN_DOCKER"):
	load_dotenv()
	LOCALE_DIR = "/app/locale"

LANGUAGE = os.getenv("LANGUAGE")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_GROUP = os.getenv("TELEGRAM_GROUP")
TELEGRAM_ADMIN = os.getenv("TELEGRAM_ADMIN")

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

if TELEGRAM_TOKEN is None or TELEGRAM_TOKEN == '':
	logger.warning("Missing bot token in the TELEGRAM_TOKEN variable.")
	sys.exit(1)
if TELEGRAM_ADMIN is None or TELEGRAM_ADMIN == '':
	logger.warning("Missing admin user chatId in the TELEGRAM_ADMIN variable.")
	sys.exit(1)
if TELEGRAM_GROUP is None or TELEGRAM_GROUP == '':
	if len(str(TELEGRAM_ADMIN).split(',')) > 1:
		logger.warning("You can only specify multiple admins if the bot is used in a group (using the TELEGRAM_GROUP variable).")
		sys.exit(1)
	TELEGRAM_GROUP = TELEGRAM_ADMIN
if SPOTIFY_CLIENT_ID is None or SPOTIFY_CLIENT_ID == '':
	logger.warning("Missing Spotify clientId in the SPOTIFY_CLIENT_ID variable.")
	sys.exit(1)
if SPOTIFY_CLIENT_SECRET is None or SPOTIFY_CLIENT_SECRET == '':
	logger.warning("Missing Spotify clientSecret in the SPOTIFY_CLIENT_SECRET variable.")
	sys.exit(1)
if SPOTIFY_REDIRECT_URI is None or SPOTIFY_REDIRECT_URI == '':
	logger.warning("Missing Spotify redirectUri in the SPOTIFY_REDIRECT_URI variable.")
	sys.exit(1)