"""
Init module for spotifyDownloader. This module contains the main entry point for spotifyDownloader.
And SpotifyDownloader class
"""

from config.config import (
    DOWNLOAD_DIR,
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
    CACHE_DIR,
)

from typing import List

from spotdl._version import __version__
from spotdl.download.downloader import Downloader
from spotdl.utils.spotify import SpotifyClient
from spotdl.utils.search import get_simple_songs
from spotdl.utils.config import DEFAULT_CONFIG, DOWNLOADER_OPTIONS


class SpotifyDownloader:
    """
    SpotifyDownloader simplifies the process of downloading songs from Spotify using spotDL.
    """

    def __init__(self) -> None:
        """
        Initialize the SpotifyDownloader by setting up Spotify client and downloader.
        """
        self._initialize_spotify_client()
        self.downloader = self._initialize_downloader()

    def _initialize_spotify_client(self) -> None:
        """
        Initialize the Spotify client with provided credentials.
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
        Create and return a configured Downloader instance.
        """
        downloader_settings = DOWNLOADER_OPTIONS.copy()
        downloader_settings["output"] = DOWNLOAD_DIR
        return Downloader(settings=downloader_settings, loop=None)

    def download(self, query: List[str]) -> None:
        """
        Search for songs using the provided query list and download them to disk.

        Args:
            query (List[str]): List of Spotify URLs or search queries.
        """
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
        self.downloader.download_multiple_songs(songs)
