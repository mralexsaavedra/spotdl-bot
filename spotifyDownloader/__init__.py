"""
spotifyDownloader module

Contains the main SpotifyDownloader class that simplifies
downloading songs, albums, and playlists from Spotify
using the spotDL library.
"""

import json
from typing import List, Optional, Union
from core.spotify_auth import load_token, refresh_token
import telebot
import asyncio
import threading

from config.config import (
    DOWNLOAD_DIR,
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
    CACHE_DIR,
)
from core.locale import get_text
from loguru import logger
from core.utils import delete_message, get_output_pattern, send_message
from spotdl.download.downloader import Downloader
from spotdl.utils.spotify import SpotifyClient
from spotdl.utils.search import get_simple_songs
from spotdl.utils.config import DEFAULT_CONFIG, DOWNLOADER_OPTIONS
from spotdl.utils.config import DEFAULT_CONFIG, get_config_file


def generate_config():
    """
    Generate the config file if it doesn't exist
    This is done before the argument parser so it doesn't requires `operation`
    and `query` to be passed.
    """

    config_path = get_config_file()
    token = load_token()
    settings = DOWNLOADER_OPTIONS.copy()
    settings["client_id"] = SPOTIFY_CLIENT_ID
    settings["client_secret"] = SPOTIFY_CLIENT_SECRET
    settings["user_auth"] = True
    settings["cache_path"] = f"{CACHE_DIR}/.spotipy"
    settings["no_cache"] = DEFAULT_CONFIG["no_cache"]
    settings["headless"] = DEFAULT_CONFIG["headless"]
    settings["auth_token"] = token["access_token"]
    settings["output"] = DOWNLOAD_DIR

    with open(config_path, "w", encoding="utf-8") as config_file:
        json.dump(settings, config_file, indent=4)

    print(f"Config file generated at {config_path}")

    return None


class SpotifyDownloader:
    """
    Encapsulates the logic for downloading music from Spotify
    using spotDL, managing configuration and authentication.
    """

    def __init__(self) -> None:
        """
        Initializes the Spotify client and downloader with default settings.
        """
        generate_config()
        self._initialize_spotify_client()
        self.downloader = self._initialize_downloader()

    def _initialize_spotify_client(self) -> None:
        """
        Initializes the Spotify client configuration with credentials.
        """
        token = load_token()
        SpotifyClient.init(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            user_auth=True,
            cache_path=f"{CACHE_DIR}/.spotipy",
            no_cache=DEFAULT_CONFIG["no_cache"],
            headless=DEFAULT_CONFIG["headless"],
            auth_token=token["access_token"],
        )

    def _initialize_downloader(self) -> Downloader:
        """
        Creates and returns a configured Downloader instance.
        """
        settings = DOWNLOADER_OPTIONS.copy()
        settings["output"] = DOWNLOAD_DIR
        return Downloader(settings=settings, loop=None)

    def download(
        self, bot: telebot.TeleBot, query: Union[str, List[str]], user_auth=False
    ) -> None:
        """
        Downloads songs, albums, or playlists from a URL or list of URLs.

        Args:
            bot (telebot.TeleBot): Telegram bot instance to send messages.
            query (Union[str, List[str]]): URL(s) or search terms to download.
            output (Optional[str]): Optional pattern for output directory/filename.
                                    If not specified, it is inferred based on content type.
        """
        output = get_output_pattern(query)
        self.downloader.settings["output"] = f"{DOWNLOAD_DIR}/{output}"

        spotify_client = SpotifyClient()
        spotify_client.user_auth = user_auth

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

        print(songs)

        # logger.info("Starting download...")
        # msg = send_message(bot, message=get_text("download_in_progress"))
        # message_id = msg.message_id

        # thread = threading.Thread(target=self._run_download_in_thread, args=(songs,))
        # thread.start()
        # thread.join()

        # logger.info("Download finished successfully.")
        # delete_message(bot, message_id=message_id)
        # send_message(bot, message=get_text("download_finished"))

    def _run_download_in_thread(self, songs):
        loop = self.downloader.loop
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            self.downloader.loop = loop
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.downloader.download_multiple_songs(songs))
