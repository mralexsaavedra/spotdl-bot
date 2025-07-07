from config.config import (
    DOWNLOAD_DIR,
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
    CACHE_DIR,
)
from loguru import logger
from typing import List
from spotdl.utils.config import DEFAULT_CONFIG, DOWNLOADER_OPTIONS
from spotdl.download.downloader import Downloader
from spotdl.utils.spotify import SpotifyClient
from spotdl.types.song import Song
from spotdl.utils.search import parse_query


class SpotifyDownloader:
    def __init__(self):
        SpotifyClient.init(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            user_auth=True,
            cache_path=f"{CACHE_DIR}/.spotipy",
            no_cache=DEFAULT_CONFIG["no_cache"],
            headless=DEFAULT_CONFIG["headless"],
        )

    def get_output_pattern(identifier: str) -> str:
        if "track" in identifier:
            return "{artist}/{artists} - {title}.{output-ext}"
        elif "album" in identifier or identifier == "all-user-saved-albums":
            return "{album-artist}/{album}/{artists} - {title}.{output-ext}"
        elif "playlist" in identifier or identifier == "all-user-playlists":
            return "Playlists/{list-name}/{artists} - {title}.{output-ext}"
        elif "artist" in identifier:
            return "{artist}/{artists} - {title}.{output-ext}"
        elif identifier == "saved":
            return "Liked Songs/{artists} - {title}.{output-ext}"
        else:
            return "{artists} - {title}.{output-ext}"

    def search(self, query: List[str]) -> List[Song]:
        """
        Search for songs.

        ### Arguments
        - query: List of search queries

        ### Returns
        - A list of Song objects

        ### Notes
        - query can be a list of song titles, urls, uris
        """

        return parse_query(
            query=query,
            threads=self.downloader.settings["threads"],
            use_ytm_data=self.downloader.settings["ytm_data"],
            playlist_numbering=self.downloader.settings["playlist_numbering"],
            album_type=self.downloader.settings["album_type"],
            playlist_retain_track_cover=self.downloader.settings[
                "playlist_retain_track_cover"
            ],
        )

    def download_songs(self, songs, output):
        downloader_settings = DOWNLOADER_OPTIONS.copy()
        downloader_settings["output"] = f"{DOWNLOAD_DIR}/{output}"
        downloader = Downloader(
            settings=downloader_settings,
            loop=None,
        )

        downloader.download_multiple_songs(songs)

    def download(self, query: List[str]):
        """
        Download songs based on a search query.

        ### Arguments
        - query: List of search queries

        ### Returns
        - None
        """

        songs = self.search(query)
        if not songs:
            logger.info("No songs found for the given query.")
            return

        output = self.get_output_pattern(query)
        self.download_songs(songs=songs, output=output)

    def get_all_user_songs(self):
        """
        Get all songs saved by the user.

        ### Returns
        - A list of Song objects representing the user's saved songs.
        """
        spotify_client = SpotifyClient()

        saved_tracks_response = spotify_client.current_user_saved_tracks()
        if saved_tracks_response is None:
            raise logger.error("Couldn't get saved tracks")

        saved_tracks = saved_tracks_response["items"]

        while saved_tracks_response and saved_tracks_response["next"]:
            response = spotify_client.next(saved_tracks_response)
            if response is None:
                break

            saved_tracks_response = response
            saved_tracks.extend(saved_tracks_response["items"])

        songs = []
        for track in saved_tracks:
            if not isinstance(track, dict) or track.get("track", {}).get("is_local"):
                continue

            track_meta = track["track"]
            album_meta = track_meta["album"]

            release_date = album_meta["release_date"]
            artists = artists = [artist["name"] for artist in track_meta["artists"]]

            song = Song.from_missing_data(
                name=track_meta["name"],
                artists=artists,
                artist=artists[0],
                album_id=album_meta["id"],
                album_name=album_meta["name"],
                album_artist=album_meta["artists"][0]["name"],
                album_type=album_meta["album_type"],
                disc_number=track_meta["disc_number"],
                duration=int(track_meta["duration_ms"] / 1000),
                year=release_date[:4],
                date=release_date,
                track_number=track_meta["track_number"],
                tracks_count=album_meta["total_tracks"],
                song_id=track_meta["id"],
                explicit=track_meta["explicit"],
                url=track_meta["external_urls"]["spotify"],
                isrc=track_meta.get("external_ids", {}).get("isrc"),
                cover_url=(
                    max(album_meta["images"], key=lambda i: i["width"] * i["height"])[
                        "url"
                    ]
                    if album_meta["images"]
                    else None
                ),
            )

            songs.append(song)

    def download_all_user_songs(self):
        songs = self.get_all_user_songs()

        if not songs:
            logger.info("No saved songs found.")
            return

        output = self.get_output_pattern("saved")
        self.download_songs(songs=songs, output=output)
