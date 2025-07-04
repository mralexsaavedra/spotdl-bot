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
    SpotifyDownloader class, which simplifies the process of downloading songs from Spotify.
    """

    def __init__(self):
        """
        Initialize the SpotifyDownloader class
        """

        downloader_settings = DOWNLOADER_OPTIONS.copy()
        downloader_settings["output"] = DOWNLOAD_DIR

        # Initialize spotify client
        SpotifyClient.init(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            user_auth=False,
            cache_path=CACHE_DIR,
            no_cache=DEFAULT_CONFIG["no_cache"],
            headless=DEFAULT_CONFIG["headless"],
        )

        # Initialize downloader
        self.downloader = Downloader(
            settings=downloader_settings,
            loop=None,
        )

    def download(self, query: List[str]) -> None:
        """
        Find songs with the provided audio provider and save them to the disk.

        ### Arguments
        - query: list of strings to search for.
        """

        # Parse the query
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

        # Download the songs
        self.downloader.download_multiple_songs(songs)
