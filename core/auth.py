from config.config import (
    CACHE_DIR,
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
    SPOTIFY_REDIRECT_URI,
)
from spotdl.utils.config import DEFAULT_CONFIG
from spotipy.cache_handler import CacheFileHandler, MemoryCacheHandler
from spotipy.oauth2 import SpotifyOAuth, SpotifyOauthError
from loguru import logger
import sys
from core.locale import get_text

if not all([SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI]):
    logger.error(get_text("auth_missing_env"))
    sys.exit(1)

logger.info(get_text("auth_init_client_id", SPOTIFY_CLIENT_ID))
logger.info(get_text("auth_cache_dir", CACHE_DIR, DEFAULT_CONFIG["no_cache"]))

cache_handler = (
    CacheFileHandler(f"{CACHE_DIR}/.spotipy")
    if not DEFAULT_CONFIG["no_cache"]
    else MemoryCacheHandler()
)

try:
    auth_manager = SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope="playlist-read-private user-follow-read user-library-read",
        open_browser=False,
        cache_handler=cache_handler,
    )
    logger.info(get_text("auth_instructions"))
    token_info = auth_manager.get_access_token(as_dict=False)
    if token_info:
        logger.success(get_text("auth_success"))
    else:
        logger.error(get_text("auth_failure"))
        sys.exit(1)
except SpotifyOauthError as e:
    logger.error(get_text("auth_oauth_error", e))
    sys.exit(1)
except Exception as e:
    logger.error(get_text("auth_unexpected_error", e))
    sys.exit(1)
