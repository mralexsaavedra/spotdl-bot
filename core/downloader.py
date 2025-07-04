from config.config import (
    DOWNLOAD_DIR,
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
    CACHE_DIR,
)
from core.logger import setup_logger
from core.utils import delete_message, is_spotify_url, send_message
from core.locale import get_text
from spotdl import Spotdl
from spotdl.utils.config import DEFAULT_CONFIG, DOWNLOADER_OPTIONS
from spotdl.utils.search import get_simple_songs
import time

MAX_RETRIES = 5
WAIT_TIME = 30  # Tiempo de espera en segundos para reintentos

logger = setup_logger(__name__)


def is_rate_limit_error(e):
    message = str(e).lower()
    return "429" in message or "rate limit" in message or "too many requests" in message


def run_spotdl():
    retries = 0
    url = "https://open.spotify.com/intl-es/track/2zQvtkghOHiBG48Bj0oFR9?si=0645845c6cab417f"

    while retries < MAX_RETRIES:
        try:
            settings = DOWNLOADER_OPTIONS.copy()
            settings["output"] = DOWNLOAD_DIR

            spotdl = Spotdl(
                client_id=SPOTIFY_CLIENT_ID,
                client_secret=SPOTIFY_CLIENT_SECRET,
                user_auth=False,
                cache_path=CACHE_DIR,
                no_cache=DEFAULT_CONFIG["no_cache"],
                headless=DEFAULT_CONFIG["headless"],
                downloader_settings=settings,
            )

            logger.info("Starting Spotify download...")

            if isinstance(url, str):
                query = [url]
            elif isinstance(url, list):
                query = url
            else:
                raise ValueError("URL must be a string or a list of URLs.")

            songs = get_simple_songs(
                query,
                use_ytm_data=settings["ytm_data"],
                playlist_numbering=settings["playlist_numbering"],
                albums_to_ignore=settings["ignore_albums"],
                album_type=settings["album_type"],
                playlist_retain_track_cover=settings["playlist_retain_track_cover"],
            )

            spotdl.download_songs(songs)

            logger.info("Spotify download finished successfully.")
            return "success"

        except Exception as e:
            if is_rate_limit_error(e):
                retries += 1
                logger.warning(
                    f"⚠️ Rate limit detected. Retrying in {WAIT_TIME}s... (Attempt {retries}/{MAX_RETRIES})"
                )
                time.sleep(WAIT_TIME)
                continue

            logger.error(f"❌ Download error: {str(e)}")
            return "error"

    logger.error("❌ Max retries reached. Please try again later.")
    return "rate_limited"


def run_spotdl_command(bot, command, output=DOWNLOAD_DIR):
    retries = 0
    message_id = None

    while retries < MAX_RETRIES:
        try:
            settings = DOWNLOADER_OPTIONS.copy()
            settings["output"] = output

            spotdl = Spotdl(
                client_id=SPOTIFY_CLIENT_ID,
                client_secret=SPOTIFY_CLIENT_SECRET,
                user_auth=True,
                cache_path=CACHE_DIR,
                no_cache=DEFAULT_CONFIG["no_cache"],
                headless=DEFAULT_CONFIG["headless"],
                downloader_settings=settings,
            )

            logger.info("Starting download...")
            msg = send_message(bot, message=get_text("download_in_progress"))
            message_id = msg.message_id

            if isinstance(command, str):
                spotdl.download([command])
            elif isinstance(command, list):
                spotdl.download(command)
            else:
                raise ValueError("Command must be a string or a list of URLs.")

            delete_message(bot, message_id=message_id)
            send_message(bot, message=get_text("download_finished"))
            return "success"

        except Exception as e:
            if is_rate_limit_error(e):
                retries += 1
                logger.warning(
                    f"⚠️ Rate limit detected. Retrying in {WAIT_TIME}s... (Attempt {retries}/{MAX_RETRIES})"
                )
                time.sleep(WAIT_TIME)
                continue

            logger.error(f"❌ Download error: {str(e)}")
            if message_id:
                delete_message(bot, message_id=message_id)
            send_message(bot, message=get_text("error_download_failed"))
            return "error"

    if message_id:
        delete_message(bot, message_id=message_id)
    send_message(bot, message=get_text("error_rate_limited"))
    logger.error("❌ Max retries reached. Please try again later.")
    return "rate_limited"


def download(bot, message):
    url = message.text.strip()
    logger.info(f"Downloading from Spotify URL: {url}")

    if not is_spotify_url(url):
        logger.error(f"Invalid Spotify URL: {url}")
        send_message(bot, message=get_text("error_invalid_spotify_url"))
        return

    if "track" in url:
        output = "{artist}/{artists} - {title}.{output-ext}"
    elif "album" in url:
        output = "{album-artist}/{album}/{artists} - {title}.{output-ext}"
    elif "playlist" in url:
        output = "Playlists/{list-name}/{artists} - {title}.{output-ext}"
    elif "artist" in url:
        output = "{artist}/{artists} - {title}.{output-ext}"
    else:
        output = "{artists} - {title}.{output-ext}"

    command = [
        "spotdl",
        "download",
        url,
        "--output",
        f"{DOWNLOAD_DIR}/{output}",
        "--client-id",
        SPOTIFY_CLIENT_ID,
        "--client-secret",
        SPOTIFY_CLIENT_SECRET,
        "--cache-path",
        CACHE_DIR,
    ]
    run_spotdl_command(bot, url, output)


def download_liked(bot):
    logger.info("Downloading liked songs")
    output = "Liked Songs/{artists} - {title}.{output-ext}"
    command = [
        "spotdl",
        "download",
        "saved",
        "--user-auth",
        "--output",
        f"{DOWNLOAD_DIR}/{output}",
        "--client-id",
        SPOTIFY_CLIENT_ID,
        "--client-secret",
        SPOTIFY_CLIENT_SECRET,
        "--cache-path",
        CACHE_DIR,
    ]
    run_spotdl_command(bot, "all-user-saved-songs", output)


def download_albums(bot):
    logger.info("Downloading saved albums")
    output = "{album-artist}/{album}/{artists} - {title}.{output-ext}"
    command = [
        "spotdl",
        "download",
        "all-user-saved-albums",
        "--user-auth",
        "--output",
        f"{DOWNLOAD_DIR}/{output}",
        "--client-id",
        SPOTIFY_CLIENT_ID,
        "--client-secret",
        SPOTIFY_CLIENT_SECRET,
        "--cache-path",
        CACHE_DIR,
    ]
    run_spotdl_command(bot, "all-user-saved-albums", output)


def download_playlists(bot):
    logger.info("Downloading playlists")
    output = "Playlists/{list-name}/{artists} - {title}.{output-ext}"
    command = [
        "spotdl",
        "download",
        "all-user-playlists",
        "--user-auth",
        "--output",
        f"{DOWNLOAD_DIR}/{output}",
        "--client-id",
        SPOTIFY_CLIENT_ID,
        "--client-secret",
        SPOTIFY_CLIENT_SECRET,
        "--cache-path",
        CACHE_DIR,
    ]
    run_spotdl_command(bot, "all-user-playlists", output)
