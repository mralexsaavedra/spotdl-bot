from config.config import (
    DOWNLOAD_DIR,
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
    CACHE_DIR,
)
from typing import List
from core.locale import get_text
from core.utils import delete_message, send_message
from loguru import logger
from spotdl.utils.config import DEFAULT_CONFIG, DOWNLOADER_OPTIONS
from spotdl.download.downloader import Downloader
from spotdl.utils.spotify import SpotifyClient
from spotdl.utils.search import get_simple_songs


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

    def get_output_pattern(self, identifier: str) -> str:
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

    def download(self, bot, query: str):
        msg = send_message(bot=bot, message=get_text("download_in_progress"))
        message_id = msg.message_id

        downloader_settings = DOWNLOADER_OPTIONS.copy()
        output = self.get_output_pattern(identifier=query)
        downloader_settings["output"] = f"{DOWNLOAD_DIR}/{output}"

        try:
            songs = get_simple_songs(
                query=[query],
                use_ytm_data=downloader_settings["ytm_data"],
                playlist_numbering=downloader_settings["playlist_numbering"],
                album_type=downloader_settings["album_type"],
                playlist_retain_track_cover=downloader_settings[
                    "playlist_retain_track_cover"
                ],
            )

            if not songs:
                logger.info("No songs found for the given query.")
                return

            downloader = Downloader(
                settings=downloader_settings,
                loop=None,
            )
            downloader.download_multiple_songs(songs)
            downloader.progress_handler.close()

            delete_message(bot=bot, message_id=message_id)
            send_message(bot=bot, message=get_text("download_finished"))
        except Exception as e:
            logger.error(f"Download error: {str(e)}")
            delete_message(bot=bot, message_id=message_id)
            send_message(bot=bot, message=get_text("error_download_failed"))

        downloader.progress_handler.close()
