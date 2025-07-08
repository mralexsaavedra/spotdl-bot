"""Init file for the spotifyDownloader package."""

import json
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
from loguru import logger
from spotdl.utils.config import DEFAULT_CONFIG, DOWNLOADER_OPTIONS
from spotdl.download.downloader import Downloader
from spotdl.utils.spotify import SpotifyClient
from spotdl.utils.search import get_simple_songs
from spotdl.types.song import Song
from spotdl.utils.formatter import create_file_name
import telebot

SYNC_JSON_PATH = f"{CACHE_DIR}/sync.spotdl"


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

    def _get_save_path(self, query: str, song: Song) -> str | None:
        """
        Returns the save path for the downloaded content based on the song info.
        """
        if "album" in query or query == "all-user-saved-albums":
            album_artist = song.album_artist or song.artist
            album = song.album_name or "Unknown Album"
            return f"{DOWNLOAD_DIR}/{album_artist}/{album}/{album_artist}-{album}.sync.spotdl"
        elif (
            "playlist" in query
            or query == "all-user-playlists"
            or query == "all-saved-playlists"
        ):
            list_name = song.list_name or "Unknown Playlist"
            return f"{DOWNLOAD_DIR}/Playlists/{list_name}/{list_name}.sync.spotdl"
        elif "artist" in query:
            artist_name = song.artist or "Unknown Artist"
            return f"{DOWNLOAD_DIR}/{artist_name}/{artist_name}.sync.spotdl"
        elif query == "saved":
            return f"{DOWNLOAD_DIR}/Liked Songs/saved-songs.sync.spotdl"
        else:
            # For other types, we can return None or a default path
            logger.warning(
                f"Unsupported query type for save path: {query}. Returning None."
            )
            return None

    def _create_downloader(self) -> Downloader:
        """
        Creates a SpotDL Downloader instance with the given output pattern.
        """
        settings = DOWNLOADER_OPTIONS.copy()
        return Downloader(settings=settings, loop=None)

    def _get_simple_songs(self, query) -> List[Song]:
        """
        Wrapper for get_simple_songs with default downloader options.
        Accepts either a string or list as query.
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

    def download(self, bot: telebot.TeleBot, query: str) -> bool:
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
            downloader = self._create_downloader()
            downloader.settings["output"] = f"{DOWNLOAD_DIR}/{output_pattern}"

            songs = self._get_simple_songs(query)
            logger.info(f"Found {len(songs)} songs for query: {query}")

            if not songs:
                logger.info(f"No songs found for the given query: {query}")
                if message_id:
                    delete_message(bot=bot, message_id=message_id)
                send_message(bot=bot, message=get_text("error_download_failed"))
                return False

            # Add the save path and output to sync.json
            queries = []
            if Path(SYNC_JSON_PATH).exists():
                with open(SYNC_JSON_PATH, "r", encoding="utf-8") as sync_file:
                    try:
                        data = json.load(sync_file)
                        queries = data.get("queries", [])
                    except Exception:
                        queries = []
            # Only add the query if it does not already exist in sync.json
            if not any(q.get("query") == query for q in queries):
                queries.append(
                    {
                        "type": "sync",
                        "query": query,
                        "songs": [song.json for song in songs],
                        "output": downloader.settings["output"],
                    }
                )
            with open(SYNC_JSON_PATH, "w", encoding="utf-8") as sync_file:
                json.dump(
                    {"queries": queries},
                    sync_file,
                    indent=4,
                    ensure_ascii=False,
                )

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

    def _remove_file(self, file: Path) -> None:
        """
        Safely remove a file and its .lrc if configured.
        """
        if file.exists():
            logger.info(f"Deleting {file}")
            try:
                file.unlink()
            except (PermissionError, OSError) as exc:
                logger.debug(f"Could not remove file: {file}, error: {exc}")
        else:
            logger.debug(f"{file} does not exist.")

    def _remove_lrc(self, file: Path, remove_lrc: bool) -> None:
        """
        Remove the .lrc file associated with a song file if configured.
        """
        if remove_lrc:
            lrc_file = file.with_suffix(".lrc")
            if lrc_file.exists():
                logger.debug(f"Deleting lrc {lrc_file}")
                try:
                    lrc_file.unlink()
                except (PermissionError, OSError) as exc:
                    logger.debug(f"Could not remove lrc file: {lrc_file}, error: {exc}")
            else:
                logger.debug(f"{lrc_file} does not exist.")

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
                logger.debug(f"Could not rename file: {old_path}, error: {exc}")
        else:
            logger.debug(f"{old_path} does not exist.")

    def _rename_lrc(self, old_path: Path, new_path: Path, remove_lrc: bool) -> None:
        """
        Rename the .lrc file associated with a song file if configured.
        """
        if remove_lrc:
            lrc_file = old_path.with_suffix(".lrc")
            new_lrc_file = new_path.with_suffix(".lrc")
            if lrc_file.exists():
                logger.debug(f"Renaming lrc '{lrc_file}' to '{new_lrc_file}'")
                try:
                    lrc_file.rename(new_lrc_file)
                except (PermissionError, OSError) as exc:
                    logger.debug(f"Could not rename lrc file: {lrc_file}, error: {exc}")
            else:
                logger.debug(f"{lrc_file} does not exist.")

    def sync(self, bot: telebot.TeleBot) -> None:
        """
        Sync function.
        Downloads new songs and removes those no longer present in the playlists/albums/etc.

        Args:
            bot (telebot.TeleBot): The Telegram bot instance. Must not be None.
        """
        msg = send_message(bot=bot, message=get_text("sync_in_progress"))
        sync_message_id = msg.message_id if msg else None
        sync_json_path = Path(SYNC_JSON_PATH)
        if not sync_json_path.exists():
            logger.error(f"Sync file not found: {sync_json_path}")
            send_message(bot=bot, message=get_text("error_sync_file_not_found"))
            if sync_message_id:
                delete_message(bot=bot, message_id=sync_message_id)
            return

        try:
            with open(sync_json_path, "r", encoding="utf-8") as sync_file:
                sync_queries = json.load(sync_file)
        except Exception as e:
            logger.error(f"Error reading sync file: {e}")
            send_message(bot=bot, message=get_text("error_sync_file_invalid"))
            if sync_message_id:
                delete_message(bot=bot, message_id=sync_message_id)
            return

        downloader = None
        for query in sync_queries.get("queries", []):
            downloader = self._create_downloader()
            downloader.settings["output"] = query["output"]

            songs = self._get_simple_songs(query["query"])

            # Get the names and URLs of previously downloaded songs from the sync file
            old_files = []
            for entry in query["songs"]:
                file_name = create_file_name(
                    Song.from_dict(entry),
                    downloader.settings["output"],
                    downloader.settings["format"],
                    downloader.settings["restrict"],
                )
                old_files.append((Path(file_name), entry["url"]))

            new_urls = [song.url for song in songs]

            # Delete all song files whose URL is no longer part of the latest playlist
            if not downloader.settings.get("sync_without_deleting", False):
                to_rename: List[Tuple[Path, Path]] = []
                to_delete = []
                for path, url in old_files:
                    if url not in new_urls:
                        to_delete.append(path)
                    else:
                        new_song = songs[new_urls.index(url)]
                        new_path = Path(
                            create_file_name(
                                Song.from_dict(new_song.json),
                                downloader.settings["output"],
                                downloader.settings["format"],
                                downloader.settings["restrict"],
                            )
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

            # Download new/updated songs
            try:
                downloader.download_multiple_songs(songs)
            except Exception as e:
                logger.error(f"Error downloading songs: {e}")
                continue
            finally:
                if downloader and hasattr(downloader, "progress_handler"):
                    try:
                        downloader.progress_handler.close()
                    except Exception as close_err:
                        logger.error(f"Error closing progress handler: {close_err}")

            # Write the new sync file only after successful download
            try:
                # Read all queries, remove the old entry for this query, and add the new one
                all_queries = []
                if Path(SYNC_JSON_PATH).exists():
                    with open(SYNC_JSON_PATH, "r", encoding="utf-8") as f:
                        try:
                            data = json.load(f)
                            all_queries = data.get("queries", [])
                        except Exception:
                            all_queries = []
                # Remove any existing entry for this query
                all_queries = [
                    q for q in all_queries if q.get("query") != query["query"]
                ]
                # Add the updated query
                all_queries.append(
                    {
                        "type": "sync",
                        "query": query["query"],
                        "songs": [song.json for song in songs],
                        "output": query["output"],
                    }
                )
                with open(SYNC_JSON_PATH, "w", encoding="utf-8") as save_file:
                    json.dump(
                        {"queries": all_queries},
                        save_file,
                        indent=4,
                        ensure_ascii=False,
                    )
            except Exception as e:
                logger.error(f"Error writing sync file {SYNC_JSON_PATH}: {e}")

        if sync_message_id:
            delete_message(bot=bot, message_id=sync_message_id)
        send_message(bot=bot, message=get_text("sync_finished"))
