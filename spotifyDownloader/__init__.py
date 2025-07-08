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

            save_path = self._get_save_path(query=query, song=songs[0])
            if save_path:
                # Create sync file
                with open(save_path, "w", encoding="utf-8") as save_file:
                    json.dump(
                        {
                            "type": "sync",
                            "query": query,
                            "songs": [song.json for song in songs],
                        },
                        save_file,
                        indent=4,
                        ensure_ascii=False,
                    )
                with open(
                    f"{DOWNLOAD_DIR}/sync.json", "w", encoding="utf-8"
                ) as sync_file:
                    json.dump(
                        {
                            "save_path": save_path,
                            "output": downloader.settings["output"],
                        },
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

    def sync(self) -> None:
        """
        Sync function.
        It will download the songs and remove the ones that are no longer
        present in the playlists/albums/etc


        ### Arguments
        - query: list of strings to search for.
        """
        query = ""
        output_pattern = self.get_output_pattern(identifier=query)
        downloader = self._create_downloader(output=output_pattern)

        # Load the sync file
        with open(query[0], "r", encoding="utf-8") as sync_file:
            sync_data = json.load(sync_file)

        # Verify the sync file
        if (
            not isinstance(sync_data, dict)
            or sync_data.get("type") != "sync"
            or sync_data.get("songs") is None
        ):
            raise ValueError("Sync file is not a valid sync file.")

        songs = get_simple_songs(
            query=sync_data["query"],
            use_ytm_data=DOWNLOADER_OPTIONS["ytm_data"],
            playlist_numbering=DOWNLOADER_OPTIONS["playlist_numbering"],
            album_type=DOWNLOADER_OPTIONS["album_type"],
            playlist_retain_track_cover=DOWNLOADER_OPTIONS[
                "playlist_retain_track_cover"
            ],
        )

        # Get the names and URLs of previously downloaded songs from the sync file
        old_files = []
        for entry in sync_data["songs"]:
            file_name = create_file_name(
                Song.from_dict(entry),
                downloader.settings["output"],
                downloader.settings["format"],
                downloader.settings["restrict"],
            )

            old_files.append((file_name, entry["url"]))

        new_urls = [song.url for song in songs]

        # Delete all song files whose URL is no longer part of the latest playlist
        if not downloader.settings["sync_without_deleting"]:
            # Rename songs that have "{list-length}", "{list-position}", "{list-name}",
            # in the output path so that we don't have to download them again,
            # and to avoid mangling the directory structure.
            to_rename: List[Tuple[Path, Path]] = []
            to_delete = []
            for path, url in old_files:
                if url not in new_urls:
                    to_delete.append(path)
                else:
                    new_song = songs[new_urls.index(url)]

                    new_path = create_file_name(
                        Song.from_dict(new_song.json),
                        downloader.settings["output"],
                        downloader.settings["format"],
                        downloader.settings["restrict"],
                    )

                    if path != new_path:
                        to_rename.append((path, new_path))

            # fix later Downloading duplicate songs in the same playlist
            # will trigger a re-download of the song. To fix this we have to copy the song
            # to the new location without removing the old one.
            for old_path, new_path in to_rename:
                if old_path.exists():
                    logger.info("Renaming %s to %s", f"'{old_path}'", f"'{new_path}'")
                    if new_path.exists():
                        old_path.unlink()
                        continue

                    try:
                        old_path.rename(new_path)
                    except (PermissionError, OSError) as exc:
                        logger.debug(
                            "Could not rename temp file: %s, error: %s",
                            old_path,
                            exc,
                        )
                else:
                    logger.debug("%s does not exist.", old_path)

                if downloader.settings["sync_remove_lrc"]:
                    lrc_file = old_path.with_suffix(".lrc")
                    new_lrc_file = new_path.with_suffix(".lrc")
                    if lrc_file.exists():
                        logger.debug(
                            "Renaming lrc %s to %s",
                            f"'{lrc_file}'",
                            f"'{new_lrc_file}'",
                        )
                        try:
                            lrc_file.rename(new_lrc_file)
                        except (PermissionError, OSError) as exc:
                            logger.debug(
                                "Could not rename lrc file: %s, error: %s",
                                lrc_file,
                                exc,
                            )
                    else:
                        logger.debug("%s does not exist.", lrc_file)

            for file in to_delete:
                if file.exists():
                    logger.info("Deleting %s", file)
                    try:
                        file.unlink()
                    except (PermissionError, OSError) as exc:
                        logger.debug(
                            "Could not remove temp file: %s, error: %s", file, exc
                        )
                else:
                    logger.debug("%s does not exist.", file)

                if downloader.settings["sync_remove_lrc"]:
                    lrc_file = file.with_suffix(".lrc")
                    if lrc_file.exists():
                        logger.debug("Deleting lrc %s", lrc_file)
                        try:
                            lrc_file.unlink()
                        except (PermissionError, OSError) as exc:
                            logger.debug(
                                "Could not remove lrc file: %s, error: %s",
                                lrc_file,
                                exc,
                            )
                    else:
                        logger.debug("%s does not exist.", lrc_file)

            if len(to_delete) == 0:
                logger.info("Nothing to delete...")
            else:
                logger.info("%s old songs were deleted.", len(to_delete))

        # Write the new sync file
        with open(query[0], "w", encoding="utf-8") as save_file:
            json.dump(
                {
                    "type": "sync",
                    "query": sync_data["query"],
                    "songs": [song.json for song in songs],
                },
                save_file,
                indent=4,
                ensure_ascii=False,
            )

        downloader.download_multiple_songs(songs)
