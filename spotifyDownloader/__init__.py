"""Init file for the spotifyDownloader package."""

import json
import os
import requests
from config.config import (
    DOWNLOAD_DIR,
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
    CACHE_DIR,
)
from core.locale import get_text
from core.utils import delete_message, send_message
from typing import List, Tuple, Union
from pathlib import Path
from loguru import logger
from spotdl.utils.config import DEFAULT_CONFIG, DOWNLOADER_OPTIONS
from spotdl.download.downloader import Downloader
from spotdl.utils.spotify import SpotifyClient
from spotdl.utils.search import get_simple_songs
from spotdl.types.song import Song
from spotdl.utils.m3u import create_m3u_content
from spotdl.utils.formatter import create_file_name
import telebot
from spotdl.types.playlist import Playlist

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
    def get_output_pattern(query: str) -> str:
        """
        Returns an output pattern based on the Spotify item type.
        """
        if (
            "all-user-saved-albums" == query
            or "all-user-followed-artists" == query
            or "track" in query
            or "artist" in query
            or "album" in query
        ):
            return "{album-artist}/{album}/{artists} - {title}.{output-ext}"
        elif (
            query == "all-user-playlists"
            or query == "all-saved-playlists"
            or "playlist" in query
        ):
            return "Playlists/{list-name}/{artists} - {title}.{output-ext}"
        elif query == "saved":
            return "Playlists/Saved tracks/{artists} - {title}.{output-ext}"
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

    def _search(self, query: Union[str, List[str]]) -> List[Song]:
        """
        Wrapper for get_simple_songs with default downloader options.
        Args:
            query (str | List[str]): Spotify query or list of queries.
        Returns:
            List[Song]: List of found Song objects.
        """
        if not isinstance(query, list):
            query = [query]
        return get_simple_songs(
            query=query,
            use_ytm_data=DOWNLOADER_OPTIONS["ytm_data"],
            playlist_numbering=DOWNLOADER_OPTIONS["playlist_numbering"],
            album_type=DOWNLOADER_OPTIONS["album_type"],
            playlist_retain_track_cover=DOWNLOADER_OPTIONS[
                "playlist_retain_track_cover"
            ],
        )

    def _download_songs(
        self, downloader: Downloader, songs: List[Song], query: str
    ) -> bool:
        """
        Attempt to download songs. Returns True if successful, False otherwise.
        Ensures progress handler is closed to avoid file descriptor leaks.
        """
        try:
            downloader.download_multiple_songs(songs)
        except Exception as e:
            logger.error(f"Download error for query '{query}': {str(e)}")
            return False
        return True

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
        """
        playlists = {}
        if query == "all-user-playlists" or query in "all-saved-playlists":
            for song in songs:
                if not song.list_name:
                    continue
                playlists.setdefault(song.list_name, []).append(song)
        elif "playlist" in query or "saved" in query:
            if songs:
                list_name = songs[0].list_name
                playlists[list_name] = songs
        else:
            return

        for list_name, playlist_songs in playlists.items():
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

    def _save_image(self, songs: List[Song], query: str) -> None:
        """
        Downloads and saves the artist's image in their folder.
        """
        images_to_download = []
        if (
            query == "all-user-playlists"
            or query == "all-saved-playlists"
            or "playlist" in query
        ):
            playlists = {}
            for song in songs:
                if not song.list_name:
                    continue
                playlists.setdefault(song.list_name, song)
            for list_name, song in playlists.items():
                try:
                    playlist = Playlist.from_url(song.list_url, fetch_songs=False)
                    image_url = playlist.cover_url
                    if image_url:
                        images_to_download.append(
                            {
                                "list_name": f"Playlists/{playlist.name}",
                                "image_url": image_url,
                            }
                        )
                except Exception as e:
                    logger.error(f"Error fetching playlist info for {list_name}: {e}")
        elif (
            query == "all-user-saved-albums"
            or query == "all-user-followed-artists"
            or "track" in query
            or "album" in query
            or "artist" in query
        ):
            artists = {}
            for song in songs:
                _song = Song.from_url(song.url)
                artist_id = _song.artist_id
                if not artist_id:
                    continue
                artists.setdefault(artist_id, song)
            spotify_client = SpotifyClient()
            for artist_id, song in artists.items():
                try:
                    artist = spotify_client.artist(artist_id)
                    images_to_download.append(
                        {
                            "list_name": artist.get("name"),
                            "image_url": max(
                                artist.get("images", []),
                                key=lambda i: i["width"] * i["height"],
                            )["url"],
                        }
                    )
                except Exception as e:
                    logger.error(f"Error fetching artist image for {artist_id}: {e}")
        else:
            return

        for item in images_to_download:
            list_name = item["list_name"]
            image_url = item["image_url"]
            image_path = Path(f"{DOWNLOAD_DIR}/{list_name}/cover.jpg")
            try:
                response = requests.get(image_url, timeout=10)
                response.raise_for_status()
                with open(image_path, "wb") as f:
                    f.write(response.content)
                logger.info(f"Image saved: {image_path}")
            except Exception as e:
                logger.error(f"Error saving image for {list_name}: {e}")

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
        output_pattern = self.get_output_pattern(query=query)
        downloader = None
        try:
            downloader = self._create_downloader()
            downloader.settings["output"] = f"{DOWNLOAD_DIR}/{output_pattern}"
            logger.info(f"Output pattern set to: {downloader.settings['output']}")

            songs = self._search(query)
            logger.info(f"Found {len(songs)} songs for query: {query}")

            if not songs:
                logger.info(f"No songs found for the given query: {query}")
                self._delete_status_message(bot, message_id)
                send_message(bot=bot, message=get_text("error_download_failed"))
                return False

            success = self._download_songs(downloader, songs, query)
            if not success:
                logger.error(f"Failed to download songs for query: {query}")
                send_message(bot=bot, message=get_text("error_download_failed"))
                return False

            self._save_image(songs=songs, query=query)
            self._update_sync_file(
                {
                    "type": "sync",
                    "query": query,
                    "songs": [song.json for song in songs],
                    "output": downloader.settings["output"],
                }
            )
            self._gen_m3u_files(songs=songs, query=query)

            send_message(bot=bot, message=get_text("download_finished"))
            return True
        except Exception as e:
            logger.error(f"Download error for query '{query}': {str(e)}")
            send_message(bot=bot, message=get_text("error_download_failed"))
            return False
        finally:
            self._close_downloader(downloader)
            self._delete_status_message(bot, message_id)

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

                success = self._download_songs(downloader, songs, query["query"])
                if not success:
                    logger.error(
                        f"Failed to download songs for query: {query['query']}"
                    )
                    send_message(bot=bot, message=get_text("error_download_failed"))
                    continue

                self._save_image(songs=songs, query=query["query"])
                self._update_sync_file(
                    {
                        "type": "sync",
                        "query": query["query"],
                        "songs": [song.json for song in songs],
                        "output": query["output"],
                    }
                )
                self._gen_m3u_files(songs=songs, query=query["query"])
            finally:
                self._close_downloader(downloader)

        self._delete_status_message(bot, message_id)
        send_message(bot=bot, message=get_text("sync_finished"))
