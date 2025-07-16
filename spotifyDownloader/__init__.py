"""Init file for the spotifyDownloader package."""

from config.config import (
    DOWNLOAD_DIR,
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
    CACHE_DIR,
)
from core.locale import get_text
from core.utils import delete_message, send_message
from typing import List, Tuple
from pathlib import Path
import json
import requests
import re
from spotifyDownloader.artist import Artist
from spotifyDownloader.song import Song
import telebot
from loguru import logger
from spotdl.utils.config import DEFAULT_CONFIG, DOWNLOADER_OPTIONS
from spotdl.download.downloader import Downloader
from spotdl.utils.spotify import SpotifyClient, SpotifyError
from spotdl.utils.m3u import create_m3u_content
from spotdl.utils.search import (
    get_all_user_playlists,
    get_user_saved_albums,
    get_all_saved_playlists,
)
from spotdl.utils.formatter import create_file_name
from spotdl.types.song import SongList
from spotdl.types.playlist import Playlist
from spotdl.types.album import Album
from spotdl.types.saved import Saved

SYNC_JSON_PATH = f"{CACHE_DIR}/sync.spotdl"


class SpotifyDownloader:
    """
    A class responsible for downloading Spotify content using SpotDL.
    Handles initialization, output path formatting, and download operations.
    """

    def __init__(self) -> None:
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
    def _is_spotify_playlist(query: str) -> bool:
        """
        Checks if the given query is a Spotify playlist URL.
        Args:
            query (str): The Spotify URL or query to check.
        Returns:
            bool: True if it's a playlist, False otherwise.
        """
        return "open.spotify.com" in query and "playlist" in query

    @staticmethod
    def _is_spotify_album(query: str) -> bool:
        """
        Checks if the given query is a Spotify album URL.
        Args:
            query (str): The Spotify URL or query to check.
        Returns:
            bool: True if it's an album, False otherwise.
        """
        return "open.spotify.com" in query and "album" in query

    @staticmethod
    def _is_spotify_artist(query: str) -> bool:
        """
        Checks if the given query is a Spotify artist URL.
        Args:
            query (str): The Spotify URL or query to check.
        Returns:
            bool: True if it's an artist, False otherwise.
        """
        return "open.spotify.com" in query and "artist" in query

    @staticmethod
    def _is_spotify_track(query: str) -> bool:
        """
        Checks if the given query is a Spotify track URL.
        Args:
            query (str): The Spotify URL or query to check.
        Returns:
            bool: True if it's a track, False otherwise.
        """
        return "open.spotify.com" in query and "track" in query

    @staticmethod
    def _is_spotify_saved(query: str) -> bool:
        """
        Checks if the given query is a Spotify saved tracks URL.
        Args:
            query (str): The Spotify URL or query to check.
        Returns:
            bool: True if it's a saved tracks, False otherwise.
        """
        return "saved" == query

    @staticmethod
    def _is_spotify_saved_playlists(query: str) -> bool:
        """
        Checks if the given query is a Spotify saved playlists URL.
        Args:
            query (str): The Spotify URL or query to check.
        Returns:
            bool: True if it's a saved playlist, False otherwise.
        """
        return "all-saved-playlists" == query

    @staticmethod
    def _is_spotify_saved_albums(query: str) -> bool:
        """
        Checks if the given query is a Spotify saved albums URL.
        Args:
            query (str): The Spotify URL or query to check.
        Returns:
            bool: True if it's a saved album, False otherwise.
        """
        return "all-user-saved-albums" == query

    @staticmethod
    def _is_spotify_user_playlists(query: str) -> bool:
        """
        Checks if the given query is a Spotify user playlists URL.
        Args:
            query (str): The Spotify URL or query to check.
        Returns:
            bool: True if it's a user playlists, False otherwise.
        """
        return "all-user-playlists" == query

    @staticmethod
    def _is_spotify_user_followed_artists(query: str) -> bool:
        """
        Checks if the given query is a Spotify user followed artists URL.
        Args:
            query (str): The Spotify URL or query to check.
        Returns:
            bool: True if it's a user followed artists, False otherwise.
        """
        return "all-user-followed-artists" == query

    def _get_output_pattern(self, query: str) -> str:
        """
        Returns an output pattern based on the Spotify item type.
        """
        if (
            self._is_spotify_saved_albums(query)
            or self._is_spotify_user_followed_artists(query)
            or self._is_spotify_track(query)
            or self._is_spotify_artist(query)
            or self._is_spotify_album(query)
        ):
            return "{album-artist}/{album}/{artists} - {title}.{output-ext}"
        elif (
            self._is_spotify_user_playlists(query)
            or self._is_spotify_saved_playlists(query)
            or self._is_spotify_playlist(query)
            or self._is_spotify_saved(query)
        ):
            return "Playlists/{list-name}/{artists} - {title}.{output-ext}"
        else:
            return "{artists} - {title}.{output-ext}"

    def _create_downloader(self) -> Downloader:
        """
        Creates a SpotDL Downloader instance with the given output pattern.
        """
        settings = DOWNLOADER_OPTIONS.copy()
        return Downloader(settings=settings, loop=None)

    def _close_downloader(self, downloader: Downloader) -> None:
        """
        Closes the downloader's progress handler to avoid file descriptor leaks.
        """
        if hasattr(downloader, "progress_handler"):
            try:
                downloader.progress_handler.close()
            except Exception as e:
                logger.error(f"Error closing progress handler: {e}")

    def _read_json_file(self, path: Path) -> dict:
        """
        Safely reads a JSON file and returns its content as a dict. Logs and returns empty dict on error.
        Args:
            path (Path): Path to the JSON file.
        Returns:
            dict: Parsed JSON content or empty dict if error.
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading JSON file {path}: {e}")
            return {}

    def _write_json_file(self, path: Path, data: dict) -> bool:
        """
        Safely writes a dict to a JSON file. Logs errors.
        Args:
            path (Path): Path to the JSON file.
            data (dict): Data to write.
        Returns:
            bool: True if write succeeded, False otherwise.
        """
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logger.info(f"JSON file written: {path}")
            return True
        except Exception as e:
            logger.error(f"Error writing JSON file {path}: {e}")
            return False

    def _update_sync_file(self, query_dict: dict) -> None:
        """
        Update the sync file by removing any existing entry for the query and adding the new one.
        Args:
            query_dict (dict): The query dictionary to add/update in the sync file.
        """
        all_queries = []
        sync_path = Path(SYNC_JSON_PATH)
        if sync_path.exists():
            data = self._read_json_file(sync_path)
            all_queries = data.get("queries", [])
        # Remove any existing entry for this query
        all_queries = [q for q in all_queries if q.get("query") != query_dict["query"]]
        # Add the updated query
        all_queries.append(query_dict)
        self._write_json_file(sync_path, {"queries": all_queries})

    def _gen_m3u_files(self, songs: List[Song], query: str) -> None:
        """
        Generate M3U files for the downloaded songs.
        Args:
            songs (List[Song]): List of Song objects to generate M3U files for.
            query (str): The Spotify query string.
        Raises:
            ValueError: If songs list is empty.
        """
        if not songs:
            logger.warning("No songs provided for M3U generation.")
            return
        playlists = {}
        if not isinstance(query, str) or not query:
            logger.warning("Query for M3U generation must be a non-empty string.")
            return
        if self._is_spotify_user_playlists(query) or self._is_spotify_saved_playlists(
            query
        ):
            for song in songs:
                if not hasattr(song, "list_name") or not song.list_name:
                    continue
                playlists.setdefault(song.list_name, []).append(song)
        elif self._is_spotify_playlist(query) or self._is_spotify_saved(query):
            if songs and hasattr(songs[0], "list_name") and songs[0].list_name:
                list_name = songs[0].list_name
                playlists[list_name] = songs
        else:
            return
        for list_name, playlist_songs in playlists.items():
            if not list_name or not playlist_songs:
                logger.warning(
                    f"Skipping M3U for empty playlist or list_name: {list_name}"
                )
                continue
            m3u_content = create_m3u_content(
                song_list=playlist_songs,
                template="{artists} - {title}.{output-ext}",
                file_extension=DOWNLOADER_OPTIONS["format"],
                restrict=DOWNLOADER_OPTIONS["restrict"],
                short=False,
                detect_formats=DOWNLOADER_OPTIONS["detect_formats"],
            )
            file_path = Path(f"{DOWNLOAD_DIR}/Playlists/{list_name}/{list_name}.m3u8")
            try:
                with open(file_path, "w", encoding="utf-8") as m3u_file:
                    m3u_file.write(m3u_content)
                logger.info(f"M3U file generated: {file_path}")
            except Exception as e:
                logger.error(f"Error writing M3U file {file_path}: {e}")

    @staticmethod
    def _get_largest_image(images: list) -> str | None:
        """Returns the URL of the largest image or None if not available."""
        if not images:
            return None
        try:
            return max(
                images, key=lambda i: (i.get("width") or 0) * (i.get("height") or 0)
            ).get("url")
        except Exception as e:
            logger.warning(f"Error selecting largest image: {e}")
            return None

    def _download_images(self, images_to_download: List[dict]) -> None:
        """
        Downloads images from the provided list of image URLs.
        Args:
            images (list): List of dictionaries containing 'image_url' and 'list_name'.
        """
        for item in images_to_download:
            list_name = item["list_name"]
            image_url = item["image_url"]
            if not image_url:
                logger.warning(f"No image URL for {list_name}, skipping.")
                continue
            image_path = Path(f"{DOWNLOAD_DIR}/{list_name}/cover.jpg")
            image_dir = image_path.parent
            if not image_dir.exists():
                image_dir.mkdir(parents=True, exist_ok=True)
            if image_path.exists():
                logger.info(f"Image already exists, skipping download: {image_path}")
                continue
            try:
                response = requests.get(image_url, timeout=10)
                response.raise_for_status()
                with open(image_path, "wb") as f:
                    f.write(response.content)
                logger.info(f"Image saved: {image_path}")
            except Exception as e:
                logger.error(f"Error saving image for {list_name}: {e}")

    def __normalize_query_url(self, query: str) -> str:
        """
        Normalizes the Spotify query URL by removing any /intl-xxx/ segments.
        Args:
            query (str): The Spotify URL or query to normalize.
        Returns:
            str: The normalized query URL.
        """
        return re.sub(r"\/intl-\w+\/", "/", query)

    def _populate_songs_from_lists(
        self, songs: List[Song], lists: List[SongList]
    ) -> List[Song]:
        """
        Populates and returns a list of Song objects from the provided SongList objects.
        Args:
            lists (List[SongList]): List of SongList objects.
        Returns:
            List[Song]: List of Song objects.
        """
        for song_list in lists:
            logger.info(
                f"Found {len(song_list.urls)} songs in {song_list.name} ({song_list.__class__.__name__})"
            )
            for index, song in enumerate(song_list.songs):
                song_data = self._build_song_data(song, song_list)
                songs.append(Song.from_dict(song_data))

    def _handle_track(
        self, query: str, songs: List[Song], images_to_download: List[dict]
    ) -> bool:
        """
        Handles Spotify track queries. Adds the track to songs and its image to images_to_download.
        Args:
            query (str): Spotify query or URL.
            songs (List[Song]): List of Song objects.
            images_to_download (List[dict]): List of dicts with 'list_name' and 'image_url'.
        Returns:
            bool: True if added successfully, False otherwise.
        """
        song = Song.from_url(url=query)
        if not song:
            logger.warning(f"Track not found for query: {query}")
            return False
        songs.append(song)
        image_url = self._get_largest_image(song.artist.get("images", []))
        if image_url:
            images_to_download.append(
                {
                    "list_name": song.artist["name"],
                    "image_url": image_url,
                }
            )
        return True

    def _handle_playlist(
        self, query: str, lists: List[SongList], images_to_download: List[dict]
    ) -> bool:
        """
        Handles Spotify playlist queries. Adds the playlist to lists and its image to images_to_download.
        Args:
            query (str): Spotify query or URL.
            lists (List[SongList]): List of SongList objects.
            images_to_download (List[dict]): List of dicts with 'list_name' and 'image_url'.
        Returns:
            bool: True if added successfully, False otherwise.
        """
        playlist = Playlist.from_url(query, fetch_songs=False)
        lists.append(playlist)
        images_to_download.append(
            {
                "list_name": f"Playlists/{playlist.name}",
                "image_url": playlist.cover_url,
            }
        )
        return True

    def _handle_album(
        self, query: str, lists: List[SongList], images_to_download: List[dict]
    ) -> bool:
        """
        Handles Spotify album queries. Adds the album to lists and the artist's image to images_to_download.
        Args:
            query (str): Spotify query or URL.
            lists (List[SongList]): List of SongList objects.
            images_to_download (List[dict]): List of dicts with 'list_name' and 'image_url'.
        Returns:
            bool: True if added successfully, False otherwise.
        """
        album = Album.from_url(query, fetch_songs=False)
        lists.append(album)
        artist_id = album.artist["id"]
        artist = Artist.from_url(artist_id, fetch_songs=False)
        if not artist:
            logger.warning(f"Artist not found for album: {album.name}")
            return False
        image_url = self._get_largest_image(artist.images)
        if image_url:
            images_to_download.append(
                {
                    "list_name": artist.name,
                    "image_url": image_url,
                }
            )
        return True

    def _handle_artist(
        self, query: str, lists: List[SongList], images_to_download: List[dict]
    ) -> bool:
        """
        Handles Spotify artist queries. Adds the artist to lists and its image to images_to_download.
        Args:
            query (str): Spotify query or URL.
            lists (List[SongList]): List of SongList objects.
            images_to_download (List[dict]): List of dicts with 'list_name' and 'image_url'.
        Returns:
            bool: True if added successfully, False otherwise.
        """
        artist = Artist.from_url(query, fetch_songs=False)
        lists.append(artist)
        image_url = self._get_largest_image(artist.images)
        if image_url:
            images_to_download.append(
                {
                    "list_name": artist.name,
                    "image_url": image_url,
                }
            )
        return True

    def _handle_user_playlists(
        self, lists: List[SongList], images_to_download: List[dict]
    ) -> bool:
        """
        Handles user playlists queries. Adds all playlists to lists and their images to images_to_download.
        Args:
            lists (List[SongList]): List of SongList objects.
            images_to_download (List[dict]): List of dicts with 'list_name' and 'image_url'.
        Returns:
            bool: True if added successfully, False otherwise.
        """
        user_playlists = get_all_user_playlists()
        lists.extend(user_playlists)
        for playlist in user_playlists:
            images_to_download.append(
                {
                    "list_name": f"Playlists/{playlist.name}",
                    "image_url": playlist.cover_url,
                }
            )
        return True

    def _handle_saved_playlists(
        self, lists: List[SongList], images_to_download: List[dict]
    ) -> bool:
        """
        Handles saved playlists queries. Adds all saved playlists to lists and their images to images_to_download.
        Args:
            lists (List[SongList]): List of SongList objects.
            images_to_download (List[dict]): List of dicts with 'list_name' and 'image_url'.
        Returns:
            bool: True if added successfully, False otherwise.
        """
        saved_playlists = get_all_saved_playlists()
        lists.extend(saved_playlists)
        for playlist in saved_playlists:
            images_to_download.append(
                {
                    "list_name": f"Playlists/{playlist.name}",
                    "image_url": playlist.cover_url,
                }
            )
        return True

    def _handle_saved_albums(
        self, lists: List[SongList], images_to_download: List[dict]
    ) -> bool:
        """
        Handles saved albums queries. Adds artist images for all saved albums to images_to_download.
        Args:
            images_to_download (List[dict]): List of dicts with 'list_name' and 'image_url'.
        Returns:
            bool: True if added successfully, False otherwise.
        """
        saved_albums = get_user_saved_albums()
        lists.extend(saved_albums)
        for album in saved_albums:
            artist_id = album.artist["id"]
            if not artist_id:
                continue
            artist = Artist.from_url(artist_id, fetch_songs=False)
            if not artist:
                logger.warning(f"Artist not found for album: {album.name}")
                continue
            image_url = self._get_largest_image(artist.images)
            if image_url:
                images_to_download.append(
                    {
                        "list_name": artist.name,
                        "image_url": image_url,
                    }
                )
        return True

    def _handle_user_followed_artists(
        self, lists: List[SongList], images_to_download: List[dict]
    ) -> bool:
        """
        Handles user followed artists queries. Adds images for all followed artists to images_to_download.
        Args:
            images_to_download (List[dict]): List of dicts with 'list_name' and 'image_url'.
        Returns:
            bool: True if added successfully, False otherwise.
        """
        followed_artists = self._get_user_followed_artists()
        lists.extend(followed_artists)
        for artist in followed_artists:
            image_url = self._get_largest_image(artist.images)
            if image_url:
                images_to_download.append(
                    {
                        "list_name": artist.name,
                        "image_url": image_url,
                    }
                )
        return True

    def _handle_saved(self, query: str, lists: List[SongList]) -> bool:
        """
        Handles saved tracks queries. Adds the saved tracks to lists.
        """
        lists.append(Saved.from_url(query, fetch_songs=False))
        return True

    def _get_dispatch_dict(
        self, songs: List[Song], lists: List[SongList], images_to_download: list
    ):
        """
        Returns the dispatch dictionary for Spotify query types.
        Each entry maps a query type to a tuple of (checker function, handler function).
        Args:
            songs (List[Song]): List to populate with Song objects.
            lists (List[SongList]): List to populate with SongList objects.
            images_to_download (list): List to populate with image download info.
        Returns:
            dict: Dispatch dictionary for query handling.
        """
        return {
            "track": (
                self._is_spotify_track,
                lambda q: self._handle_track(q, songs, images_to_download),
            ),
            "playlist": (
                self._is_spotify_playlist,
                lambda q: self._handle_playlist(q, lists, images_to_download),
            ),
            "album": (
                self._is_spotify_album,
                lambda q: self._handle_album(q, lists, images_to_download),
            ),
            "artist": (
                self._is_spotify_artist,
                lambda q: self._handle_artist(q, lists, images_to_download),
            ),
            "user_playlists": (
                self._is_spotify_user_playlists,
                lambda q: self._handle_user_playlists(lists, images_to_download),
            ),
            "saved_playlists": (
                self._is_spotify_saved_playlists,
                lambda q: self._handle_saved_playlists(lists, images_to_download),
            ),
            "saved_albums": (
                self._is_spotify_saved_albums,
                lambda q: self._handle_saved_albums(lists, images_to_download),
            ),
            "user_followed_artists": (
                self._is_spotify_user_followed_artists,
                lambda q: self._handle_user_followed_artists(lists, images_to_download),
            ),
            "saved": (self._is_spotify_saved, lambda q: self._handle_saved(q, lists)),
        }

    def _get_user_followed_artists() -> List[Artist]:
        """
        Get all user playlists

        ### Returns
        - List of all user playlists
        """
        spotify_client = SpotifyClient()
        if spotify_client.user_auth is False:  # type: ignore
            raise SpotifyError("You must be logged in to use this function")

        user_followed_response = spotify_client.current_user_followed_artists()
        if user_followed_response is None:
            raise SpotifyError("Couldn't get user followed artists")

        user_followed_response = user_followed_response["artists"]
        user_followed = user_followed_response["items"]

        # Fetch all artists
        while user_followed_response and user_followed_response["next"]:
            response = spotify_client.next(user_followed_response)
            if response is None:
                break

            user_followed_response = response["artists"]
            user_followed.extend(user_followed_response["items"])

        return [
            Artist.from_url(
                followed_artist["external_urls"]["spotify"], fetch_songs=False
            )
            for followed_artist in user_followed
        ]

    def _search_and_download(
        self, downloader: Downloader, query: str, output: str
    ) -> bool:
        """
        Searches for Spotify content based on the query and downloads it using a modular dispatch dictionary.
        Args:
            downloader (Downloader): SpotDL Downloader instance.
            query (str): Spotify URL or query to process.
            output (str): Output path pattern for downloads.
        Returns:
            bool: True if download succeeded, False otherwise.
        """
        songs: List[Song] = []
        lists: List[SongList] = []
        images_to_download = []

        logger.info(f"Processing query: {query}")
        query = self.__normalize_query_url(query)

        dispatch = self._get_dispatch_dict(songs, lists, images_to_download)

        handled = False
        try:
            for key, (check_fn, handler_fn) in dispatch.items():
                if check_fn(query):
                    handled = handler_fn(query)
                    break
            if not handled:
                logger.warning(f"Unsupported query type for image saving: {query}")
                return False

            self._populate_songs_from_lists(songs, lists)

            # Filter songs by album type if specified
            original_length = len(songs)
            album_type = DOWNLOADER_OPTIONS["album_type"]
            if album_type:
                songs = [song for song in songs if song.album_type == album_type]
                logger.info(
                    f"Skipped {(original_length - len(songs))} songs for Album Type {album_type}"
                )

            logger.debug(f"Found {len(songs)} songs in {len(lists)} lists")
            if not songs:
                logger.error("No songs to download.")
                return False

            self._download_images(images_to_download)
            downloader.download_multiple_songs(songs)
            self._update_sync_file(
                {
                    "type": "sync",
                    "query": query,
                    "songs": [song.json for song in songs],
                    "output": output,
                }
            )
            self._gen_m3u_files(songs=songs, query=query)
        except Exception as e:
            logger.error(f"Download error for query '{query}': {str(e)}")
            return False
        return True

    def _send_status_message(self, bot: telebot.TeleBot, text: str) -> int | None:
        """
        Sends a status message to the user and returns the message_id (or None if failed).
        Args:
            bot (telebot.TeleBot): The Telegram bot instance.
            text (str): The message to send.
        Returns:
            int | None: The message_id if sent, otherwise None.
        """
        msg = send_message(bot=bot, message=text)
        return msg.message_id if msg else None

    def _delete_status_message(
        self, bot: telebot.TeleBot, message_id: int | None
    ) -> None:
        """
        Deletes a status message if the message_id is valid.
        Args:
            bot (telebot.TeleBot): The Telegram bot instance.
            message_id (int | None): The message id to delete.
        """
        if message_id:
            delete_message(bot=bot, message_id=message_id)

    def _get_song_file_path(
        self, song: Song, output: str, fmt: str, restrict: bool
    ) -> Path:
        """
        Returns the Path of a song file according to the configuration.
        Args:
            song (Song): The song object.
            output (str): Output pattern.
            fmt (str): File format.
            restrict (bool): Restrict flag.
        Returns:
            Path: The path to the song file.
        """
        return Path(create_file_name(song, output, fmt, restrict))

    def _remove_file(self, file: Path) -> None:
        """
        Safely remove a file and its .lrc if configured.
        """
        if file.exists():
            logger.info(f"Deleting {file}")
            try:
                file.unlink()
            except (PermissionError, OSError) as exc:
                logger.error(f"Could not remove file: {file}, error: {exc}")
        else:
            logger.info(f"{file} does not exist.")

    def _remove_lrc(self, file: Path, remove_lrc: bool) -> None:
        """
        Remove the .lrc file associated with a song file if configured.
        """
        if remove_lrc:
            lrc_file = file.with_suffix(".lrc")
            if lrc_file.exists():
                logger.info(f"Deleting lrc {lrc_file}")
                try:
                    lrc_file.unlink()
                except (PermissionError, OSError) as exc:
                    logger.error(f"Could not remove lrc file: {lrc_file}, error: {exc}")
            else:
                logger.info(f"{lrc_file} does not exist.")

    def _rename_file(self, old_path: Path, new_path: Path) -> None:
        """
        Safely rename a file, removing the destination if it exists.
        """
        if old_path.exists():
            logger.info(f"Renaming '{old_path}' to '{new_path}'")
            if new_path.exists():
                old_path.unlink()
                return
            try:
                old_path.rename(new_path)
            except (PermissionError, OSError) as exc:
                logger.error(f"Could not rename file: {old_path}, error: {exc}")
        else:
            logger.info(f"{old_path} does not exist.")

    def _rename_lrc(self, old_path: Path, new_path: Path, remove_lrc: bool) -> None:
        """
        Rename the .lrc file associated with a song file if configured.
        """
        if remove_lrc:
            lrc_file = old_path.with_suffix(".lrc")
            new_lrc_file = new_path.with_suffix(".lrc")
            if lrc_file.exists():
                logger.info(f"Renaming lrc '{lrc_file}' to '{new_lrc_file}'")
                try:
                    lrc_file.rename(new_lrc_file)
                except (PermissionError, OSError) as exc:
                    logger.error(f"Could not rename lrc file: {lrc_file}, error: {exc}")
            else:
                logger.info(f"{lrc_file} does not exist.")

    def _build_song_data(self, song: Song, song_list: SongList) -> dict:
        """
        Builds the metadata dictionary for a song according to its list and configuration.
        Args:
            song (Song): The original song object.
            song_list (SongList): The list to which the song belongs.
        Returns:
            dict: Metadata dictionary for Song.from_dict.
        """
        song_data = song.json.copy()
        song_data["list_name"] = song_list.name
        song_data["list_url"] = song_list.url
        song_data["list_position"] = song.list_position
        song_data["list_length"] = song_list.length
        if DOWNLOADER_OPTIONS["playlist_numbering"]:
            song_data["track_number"] = song_data["list_position"]
            song_data["tracks_count"] = song_data["list_length"]
            song_data["album_name"] = song_data["list_name"]
            song_data["disc_number"] = 1
            song_data["disc_count"] = 1
            if isinstance(song_list, Playlist):
                song_data["album_artist"] = song_list.author_name
                song_data["cover_url"] = song_list.cover_url
        if DOWNLOADER_OPTIONS["playlist_retain_track_cover"]:
            song_data["track_number"] = song_data["list_position"]
            song_data["tracks_count"] = song_data["list_length"]
            song_data["album_name"] = song_data["list_name"]
            song_data["disc_number"] = 1
            song_data["disc_count"] = 1
            song_data["cover_url"] = song_data["cover_url"]
            if isinstance(song_list, Playlist):
                song_data["album_artist"] = song_list.author_name
        return song_data

    def download(self, bot: telebot.TeleBot, query: str) -> bool:
        """
        Downloads the content for the given Spotify query.
        Sends messages to the user via the Telegram bot.

        Args:
            bot: The Telegram bot instance.
            query: The Spotify URL or query to download.

        Returns:
            bool: True if download succeeded, False otherwise.
        """
        message_id = self._send_status_message(bot, get_text("download_in_progress"))
        output_pattern = self._get_output_pattern(query=query)
        downloader = None
        try:
            downloader = self._create_downloader()
            downloader.settings["output"] = f"{DOWNLOAD_DIR}/{output_pattern}"
            logger.info(f"Output pattern set to: {downloader.settings['output']}")

            success = self._search_and_download(
                downloader=downloader, query=query, output=downloader.settings["output"]
            )
            if not success:
                logger.error(f"Failed to download songs for query: {query}")
                send_message(bot=bot, message=get_text("error_download_failed"))
                return False

            send_message(bot=bot, message=get_text("download_finished"))
            return True
        except Exception as e:
            logger.error(f"Download error for query '{query}': {str(e)}")
            send_message(bot=bot, message=get_text("error_download_failed"))
            return False
        finally:
            self._close_downloader(downloader)
            self._delete_status_message(bot, message_id)

    def sync(self, bot: telebot.TeleBot) -> None:
        """
        Sync function.
        Downloads new songs and removes those no longer present in the playlists/albums/etc.

        Args:
            bot (telebot.TeleBot): The Telegram bot instance. Must not be None.
        """
        message_id = self._send_status_message(bot, get_text("sync_in_progress"))
        sync_json_path = Path(SYNC_JSON_PATH)
        if not sync_json_path.exists():
            logger.error(f"Sync file not found: {sync_json_path}")
            send_message(bot=bot, message=get_text("error_sync_file_not_found"))
            self._delete_status_message(bot, message_id)
            return
        sync_queries = self._read_json_file(sync_json_path)
        if not sync_queries or "queries" not in sync_queries:
            logger.error(f"Invalid or empty sync file: {sync_json_path}")
            send_message(bot=bot, message=get_text("error_sync_file_invalid"))
            self._delete_status_message(bot, message_id)
            return
        for query in sync_queries.get("queries", []):
            downloader = self._create_downloader()
            try:
                downloader.settings["output"] = query["output"]
                songs = self._search(query["query"])

                old_files = []
                for entry in query["songs"]:
                    file_name = self._get_song_file_path(
                        Song.from_dict(entry),
                        downloader.settings["output"],
                        downloader.settings["format"],
                        downloader.settings["restrict"],
                    )
                    old_files.append((file_name, entry["url"]))

                new_urls = [song.url for song in songs]

                if not downloader.settings.get("sync_without_deleting", False):
                    to_rename: List[Tuple[Path, Path]] = []
                    to_delete = []
                    for path, url in old_files:
                        if url not in new_urls:
                            to_delete.append(path)
                        else:
                            new_song = songs[new_urls.index(url)]
                            new_path = self._get_song_file_path(
                                Song.from_dict(new_song.json),
                                downloader.settings["output"],
                                downloader.settings["format"],
                                downloader.settings["restrict"],
                            )
                            if path != new_path:
                                to_rename.append((path, new_path))

                    for old_path, new_path in to_rename:
                        self._rename_file(old_path, new_path)
                        self._rename_lrc(
                            old_path,
                            new_path,
                            downloader.settings.get("sync_remove_lrc", False),
                        )

                    for file in to_delete:
                        self._remove_file(file)
                        self._remove_lrc(
                            file, downloader.settings.get("sync_remove_lrc", False)
                        )

                    if len(to_delete) == 0:
                        logger.info("Nothing to delete...")
                    else:
                        logger.info(f"{len(to_delete)} old songs were deleted.")

                success = self._search_and_download(
                    downloader=downloader, query=query["query"], output=query["output"]
                )
                if not success:
                    logger.error(
                        f"Failed to download songs for query: {query['query']}"
                    )
                    send_message(bot=bot, message=get_text("error_download_failed"))
                    continue
            finally:
                self._close_downloader(downloader)

        self._delete_status_message(bot, message_id)
        send_message(bot=bot, message=get_text("sync_finished"))
