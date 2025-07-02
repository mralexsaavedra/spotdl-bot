from logging import error
import os
import sys

from core.locale import get_text

VERSION = "v0.0.1"
CONTAINER_NAME = os.environ.get("CONTAINER_NAME")
LANGUAGE = os.environ.get("LANGUAGE")

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_GROUP = os.environ.get("TELEGRAM_GROUP")
TELEGRAM_ADMIN = os.environ.get("TELEGRAM_ADMIN")

SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.environ.get("SPOTIFY_REDIRECT_URI")

if TELEGRAM_TOKEN is None or TELEGRAM_TOKEN == '':
	error(get_text("error_bot_token"))
	sys.exit(1)
if TELEGRAM_GROUP is None or TELEGRAM_GROUP == '':
	if len(str(TELEGRAM_ADMIN).split(',')) > 1:
		error(get_text("error_multiple_admin_only_with_group"))
		sys.exit(1)
if TELEGRAM_ADMIN is None or TELEGRAM_ADMIN == '':
	error(get_text("error_bot_telegram_admin"))
	sys.exit(1)
	TELEGRAM_GROUP = TELEGRAM_ADMIN
if LANGUAGE.lower() not in ("es"):
	error("LANGUAGE only can be ES")
	sys.exit(1)
if SPOTIFY_CLIENT_ID is None or SPOTIFY_CLIENT_ID == '':
	error(get_text("error_bot_spotify_client_id"))
	sys.exit(1)
if SPOTIFY_CLIENT_SECRET is None or SPOTIFY_CLIENT_SECRET == '':
	error(get_text("error_bot_spotify_client_secret"))
	sys.exit(1)
if SPOTIFY_REDIRECT_URI is None or SPOTIFY_REDIRECT_URI == '':
	error(get_text("error_bot_spotify_redirect_uri"))
	sys.exit(1)
