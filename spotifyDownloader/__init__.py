from config.config import (
    DOWNLOAD_DIR,
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
    CACHE_DIR,
)
from core.locale import get_text
from core.utils import delete_message, send_message, is_spotify_url
from loguru import logger
from spotdl.utils.config import DEFAULT_CONFIG, DOWNLOADER_OPTIONS
from spotdl.download.downloader import Downloader
from spotdl.utils.spotify import SpotifyClient
from spotdl.utils.search import get_simple_songs


class SpotifyDownloader:
    """
    A class responsible for downloading Spotify content using SpotDL.
    Handles initialization, output path formatting, and download operations.
    """

    def __init__(self):
        self._init_spotify_client()

    def _init_spotify_client(self) -> None:
        SpotifyClient.init(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            user_auth=True,
            cache_path=f"{CACHE_DIR}/.spotipy",
            no_cache=DEFAULT_CONFIG["no_cache"],
            headless=DEFAULT_CONFIG["headless"],
        )

    @staticmethod
    def get_output_pattern(identifier: str) -> str:
        """
        Returns an output pattern based on the Spotify item type.
        """
        if "track" in identifier:
            return "{artist}/{artists} - {title}.{output-ext}"
        elif "album" in identifier or identifier == "all-user-saved-albums":
            return "{album-artist}/{album}/{artists} - {title}.{output-ext}"
        elif (
            "playlist" in identifier
            or identifier == "all-user-playlists"
            or identifier == "all-saved-playlists"
        ):
            return "Playlists/{list-name}/{artists} - {title}.{output-ext}"
        elif "artist" in identifier:
            return "{artist}/{artists} - {title}.{output-ext}"
        elif identifier == "saved":
            return "Liked Songs/{artists} - {title}.{output-ext}"
        else:
            return "{artists} - {title}.{output-ext}"

    def _create_downloader(self, output: str) -> Downloader:
        """
        Creates a SpotDL Downloader instance with the given output pattern.
        """
        settings = DOWNLOADER_OPTIONS.copy()
        settings["output"] = f"{DOWNLOAD_DIR}/{output}"
        return Downloader(settings=settings, loop=None)

    def download(self, bot, query: str) -> bool:
        """
        Downloads the content for the given Spotify query.
        Sends messages to the user via the Telegram bot.

        Args:
            bot: The Telegram bot instance.
            query: The Spotify URL or identifier to download.

        Returns:
            bool: True if download succeeded, False otherwise.
        """
        msg = send_message(bot=bot, message=get_text("download_in_progress"))
        message_id = msg.message_id if msg else None

        output_pattern = self.get_output_pattern(identifier=query)
        downloader = None
        try:
            downloader = self._create_downloader(output=output_pattern)
            songs = get_simple_songs(
                query=[query],
                use_ytm_data=DOWNLOADER_OPTIONS["ytm_data"],
                playlist_numbering=DOWNLOADER_OPTIONS["playlist_numbering"],
                album_type=DOWNLOADER_OPTIONS["album_type"],
                playlist_retain_track_cover=DOWNLOADER_OPTIONS[
                    "playlist_retain_track_cover"
                ],
            )

            if not songs:
                logger.info(f"No songs found for the given query: {query}")
                if message_id:
                    delete_message(bot=bot, message_id=message_id)
                send_message(bot=bot, message=get_text("error_download_failed"))
                return False

            downloader.download_multiple_songs(songs)
            send_message(bot=bot, message=get_text("download_finished"))
            return True
        except Exception as e:
            logger.error(f"Download error for query '{query}': {str(e)}")
            send_message(bot=bot, message=get_text("error_download_failed"))
            return False
        finally:
            if downloader and hasattr(downloader, "progress_handler"):
                try:
                    downloader.progress_handler.close()
                except Exception as close_err:
                    logger.error(f"Error closing progress handler: {close_err}")
            if message_id:
                delete_message(bot=bot, message_id=message_id)
