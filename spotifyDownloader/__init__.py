"""
spotifyDownloader module

Contains the main SpotifyDownloader class that simplifies
downloading songs, albums, and playlists from Spotify
using the spotDL library.
"""

from typing import List, Optional, Union
import telebot

from config.config import (
    DOWNLOAD_DIR,
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
    CACHE_DIR,
)
from core.locale import get_text
from core.logger import setup_logger
from core.utils import delete_message, send_message
from spotdl.download.downloader import Downloader
from spotdl.utils.spotify import SpotifyClient
from spotdl.utils.search import get_simple_songs
from spotdl.utils.config import DEFAULT_CONFIG, DOWNLOADER_OPTIONS

logger = setup_logger(__name__)


class SpotifyDownloader:
    """
    Encapsulates the logic for downloading music from Spotify
    using spotDL, managing configuration and authentication.
    """

    def __init__(self) -> None:
        """
        Initializes the Spotify client and downloader with default settings.
        """
        self._initialize_spotify_client()
        self.downloader = self._initialize_downloader()

    def _initialize_spotify_client(self) -> None:
        """
        Initializes the Spotify client configuration with credentials.
        """
        SpotifyClient.init(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            user_auth=False,
            cache_path=CACHE_DIR,
            no_cache=DEFAULT_CONFIG["no_cache"],
            headless=DEFAULT_CONFIG["headless"],
        )

    def _initialize_downloader(self) -> Downloader:
        """
        Creates and returns a configured Downloader instance.
        """
        settings = DOWNLOADER_OPTIONS.copy()
        settings["output"] = DOWNLOAD_DIR
        return Downloader(settings=settings, loop=None)

    def download(
        self,
        bot: telebot.TeleBot,
        query: Union[str, List[str]],
        output: Optional[str] = None,
    ) -> None:
        """
        Downloads songs, albums, or playlists from a URL or list of URLs.

        Args:
            bot (telebot.TeleBot): Telegram bot instance to send messages.
            query (Union[str, List[str]]): URL(s) or search terms to download.
            output (Optional[str]): Optional pattern for output directory/filename.
                                    If not specified, it is inferred based on content type.
        """
        if isinstance(query, str):
            query = [query]

        # If output pattern not specified, infer based on the content type in the URL
        if output is None:
            url = query[0] if query else ""
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

        self.downloader.settings["output"] = f"{DOWNLOAD_DIR}/{output}"

        songs = get_simple_songs(
            query,
            use_ytm_data=self.downloader.settings["ytm_data"],
            playlist_numbering=self.downloader.settings["playlist_numbering"],
            albums_to_ignore=self.downloader.settings["ignore_albums"],
            album_type=self.downloader.settings["album_type"],
            playlist_retain_track_cover=self.downloader.settings[
                "playlist_retain_track_cover"
            ],
        )

        logger.info("Starting download...")
        msg = send_message(bot, message=get_text("download_in_progress"))
        message_id = msg.message_id

        self.downloader.download_multiple_songs(songs)

        logger.info("Download finished successfully.")
        delete_message(bot, message_id=message_id)
        send_message(bot, message=get_text("download_finished"))

    def download_liked(self, bot: telebot.TeleBot) -> None:
        """
        Downloads all songs liked by the user.
        """
        output = "Liked Songs/{artists} - {title}.{output-ext}"
        self.download(bot=bot, query="all-user-saved-songs", output=output)

    def download_albums(self, bot: telebot.TeleBot) -> None:
        """
        Downloads all albums saved in the user's library.
        """
        output = "{album-artist}/{album}/{artists} - {title}.{output-ext}"
        self.download(bot=bot, query="all-user-saved-albums", output=output)

    def download_playlists(self, bot: telebot.TeleBot) -> None:
        """
        Downloads all playlists saved in the user's library.
        """
        output = "Playlists/{list-name}/{artists} - {title}.{output-ext}"
        self.download(bot=bot, query="all-user-playlists", output=output)
