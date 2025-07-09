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
from typing import List, Tuple
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
        if not identifier in [
            "track",
            "artist",
            "album",
            "all-user-saved-albums",
        ]:
            return "{album-artist}/{album}/{artists} - {title}.{output-ext}"
        elif (
            "playlist" in identifier
            or identifier == "all-user-playlists"
            or identifier == "all-saved-playlists"
        ):
            return "Playlists/{list-name}/{artists} - {title}.{output-ext}"
        elif identifier == "saved":
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

    def _download_songs(self, downloader, songs, bot, query) -> bool:
        """
        Attempt to download songs. Returns True if successful, False otherwise.
        Ensures progress handler is closed to avoid file descriptor leaks.
        """
        logger.debug("Starting download_multiple_songs")
        try:
            downloader.download_multiple_songs(songs)
        except Exception as e:
            logger.error(f"Download error for query '{query}': {str(e)}")
            send_message(bot=bot, message=get_text("error_download_failed"))
            return False
        logger.debug("Finished download_multiple_songs")
        return True

    def _update_sync_file(self, query_dict: dict) -> None:
        """
        Update the sync file by removing any existing entry for the query and adding the new one.
        Args:
            query_dict (dict): The query dictionary to add/update in the sync file.
        """
        all_queries = []

        if Path(SYNC_JSON_PATH).exists():
            with open(SYNC_JSON_PATH, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    all_queries = data.get("queries", [])
                except Exception:
                    all_queries = []

        # Remove any existing entry for this query
        all_queries = [q for q in all_queries if q.get("query") != query_dict["query"]]

        # Add the updated query
        all_queries.append(query_dict)

        with open(SYNC_JSON_PATH, "w", encoding="utf-8") as save_file:
            json.dump(
                {"queries": all_queries},
                save_file,
                indent=4,
                ensure_ascii=False,
            )
        logger.info(f"Sync file updated: {SYNC_JSON_PATH}")

    def _gen_m3u_files(self, songs: List[Song], query: str) -> None:
        """
        Generate M3U files for the downloaded songs.
        Args:
            songs (List[Song]): List of Song objects to generate M3U files for.
            query (str): The Spotify query string.
        """
        list_name = songs[0].list_name

        if not list_name:
            return

        if not "playlist" in query or query in [
            "all-user-playlists",
            "all-saved-playlists",
            "saved",
        ]:
            return  # No M3U generation for other types

        m3u_content = create_m3u_content(
            song_list=songs,
            template="{artists} - {title}.{output-ext}",
            file_extension=DOWNLOADER_OPTIONS["format"],
            restrict=DOWNLOADER_OPTIONS["restrict"],
            short=False,
            detect_formats=DOWNLOADER_OPTIONS["detect_formats"],
        )

        file_path = Path(f"{DOWNLOAD_DIR}/Playlists/{list_name}/{list_name}.m3u8")
        with open(file_path, "w", encoding="utf-8") as m3u_file:
            m3u_file.write(m3u_content)
        logger.info(f"M3U file generated: {file_path}")

    def _save_image(self, song: Song, query: str) -> None:
        """
        Downloads and saves the artist's image in their folder.
        """
        if "track" in query or "album" in query or "artist" in query:
            spotify_client = SpotifyClient()

            artist = spotify_client.artist(song.artist_id)
            list_name = artist.get("name")
            image_url = (
                max(artist.get("images"), key=lambda i: i["width"] * i["height"])["url"]
                if (len(artist.get("images", [])) > 0)
                else None
            )
        elif "playlist" in query:
            playlist = Playlist.from_url(query, fetch_songs=False)
            list_name = f"Playlists/{playlist.name}"
            image_url = playlist.cover_url
        else:
            return

        if not image_url:
            logger.info(f"No valid image URL found for {list_name}")
            return

        image_path = Path(f"{DOWNLOAD_DIR}/{list_name}/cover.jpg")
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            with open(image_path, "wb") as f:
                f.write(response.content)
            logger.info(f"Image saved: {image_path}")
        except Exception as e:
            logger.error(f"Error downloading artist image: {e}")

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

            # success = self._download_songs(downloader, songs, bot, query)
            # if not success:
            #     logger.error(f"Failed to download songs for query: {query}")
            #     send_message(bot=bot, message=get_text("error_download_failed"))
            #     return False

            try:
                self._save_image(song=songs[0], query=query)
            except Exception as e:
                logger.error(f"Error saving image: {e}")

            # try:
            #     self._update_sync_file(
            #         {
            #             "type": "sync",
            #             "query": query,
            #             "songs": [song.json for song in songs],
            #             "output": downloader.settings["output"],
            #         }
            #     )
            # except Exception as e:
            #     logger.error(f"Error writing sync file {SYNC_JSON_PATH}: {e}")

            # try:
            #     self._gen_m3u_files(songs=songs, query=query)
            # except Exception as e:
            #     logger.error(f"Error generating M3U files: {e}")

            send_message(bot=bot, message=get_text("download_finished"))
            return True
        except Exception as e:
            logger.error(f"Download error for query '{query}': {str(e)}")
            send_message(bot=bot, message=get_text("error_download_failed"))
            return False
        finally:
            self._close_downloader(downloader)
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
        message_id = msg.message_id if msg else None
        sync_json_path = Path(SYNC_JSON_PATH)
        if not sync_json_path.exists():
            logger.error(f"Sync file not found: {sync_json_path}")
            send_message(bot=bot, message=get_text("error_sync_file_not_found"))
            if message_id:
                delete_message(bot=bot, message_id=message_id)
            return

        try:
            with open(sync_json_path, "r", encoding="utf-8") as sync_file:
                sync_queries = json.load(sync_file)
        except Exception as e:
            logger.error(f"Error reading sync file: {e}")
            send_message(bot=bot, message=get_text("error_sync_file_invalid"))
            if message_id:
                delete_message(bot=bot, message_id=message_id)
            return

        for query in sync_queries.get("queries", []):
            downloader = self._create_downloader()
            try:
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
                success = self._download_songs(downloader, songs, bot, query["query"])
                if not success:
                    logger.error(
                        f"Failed to download songs for query: {query['query']}"
                    )
                    send_message(bot=bot, message=get_text("error_download_failed"))
                    continue  # Skip sync update for this query

                try:
                    self._save_image(song=songs[0], query=query["query"])
                except Exception as e:
                    logger.error(f"Error saving image: {e}")

                # Write the new sync file only after successful download
                try:
                    self._update_sync_file(
                        {
                            "type": "sync",
                            "query": query["query"],
                            "songs": [song.json for song in songs],
                            "output": query["output"],
                        }
                    )
                except Exception as e:
                    logger.error(f"Error writing sync file {SYNC_JSON_PATH}: {e}")

                try:
                    self._gen_m3u_files(songs=songs, query=query["query"])
                except Exception as e:
                    logger.error(f"Error generating M3U files: {e}")
            finally:
                self._close_downloader(downloader)

        if message_id:
            delete_message(bot=bot, message_id=message_id)
        send_message(bot=bot, message=get_text("sync_finished"))
