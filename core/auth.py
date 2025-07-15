from config.config import (
    CACHE_DIR,
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
    SPOTIFY_REDIRECT_URI,
)
from spotdl.utils.config import DEFAULT_CONFIG
from spotipy.cache_handler import CacheFileHandler, MemoryCacheHandler
from spotipy.oauth2 import SpotifyOAuth
from loguru import logger

logger.info(f"🔧 Initializing Spotify OAuth with client ID: {SPOTIFY_CLIENT_ID}")
logger.info(
    f"Using cache directory: {CACHE_DIR} with no_cache={DEFAULT_CONFIG['no_cache']}"
)

cache_handler = (
    CacheFileHandler(f"{CACHE_DIR}/.spotipy")
    if not DEFAULT_CONFIG["no_cache"]
    else MemoryCacheHandler()
)

auth_manager = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="playlist-read-private user-follow-read user-library-read",
    open_browser=False,
    cache_handler=cache_handler,
)

token_info = auth_manager.get_access_token()

if token_info:
    logger.info("🔑 Spotify OAuth token acquired successfully.")
else:
    logger.error("❌ Failed to acquire Spotify OAuth token. Check your credentials.")
    raise Exception("Spotify OAuth token acquisition failed.")
