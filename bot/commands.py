import threading
from spotifyDownloader import SpotifyDownloader
from config.config import VERSION
from spotifyDownloader.auth import SpotifyOAuth
from core.locale import get_text
from core.utils import delete_message, is_spotify_url, send_message
import telebot

spotdl = SpotifyDownloader()


def register_commands(bot: telebot.TeleBot):
    """
    Registers all available commands in the Telegram bot.
    """

    # --- Basic commands ---
    @bot.message_handler(commands=["start"])
    def start_command(message):
        """Shows the main menu."""
        send_message(bot, message=get_text("menu_main"))

    @bot.message_handler(commands=["authorize"])
    def authorize_command(message):
        """Starts the Spotify authorization process."""
        auth_manager = SpotifyOAuth(bot=bot)
        auth_manager.get_access_token(as_dict=False)

    # --- Downloads ---
    @bot.message_handler(commands=["download"])
    def download_command(message):
        """Requests a Spotify URL to download."""
        send_message(bot, message=get_text("download_prompt_url"))

    @bot.message_handler(commands=["downloadsavedsongs"])
    def download_saved_song_command(message):
        """Downloads songs saved by the user."""
        spotdl.download(bot=bot, query="saved")

    @bot.message_handler(commands=["downloadsavedalbums"])
    def download_saved_albums_command(message):
        """Downloads albums saved by the user."""
        spotdl.download(bot=bot, query="all-user-saved-albums")

    @bot.message_handler(commands=["downloaduserplaylists"])
    def download_user_playlists_command(message):
        """Downloads playlists saved by the user."""
        spotdl.download(bot=bot, query="all-user-playlists")

    @bot.message_handler(commands=["downloadsavedplaylists"])
    def download_saved_playlists_command(message):
        """Downloads all saved playlists."""
        spotdl.download(bot=bot, query="all-saved-playlists")

    # @bot.message_handler(commands=["downloaduserfollowedartists"])
    # def download_user_followed_artists_command(message):
    #     """Downloads all playlists from followed artists."""
    #     spotdl.download(bot=bot, query="all-user-followed-artists")

    @bot.message_handler(commands=["sync"])
    def sync_command(message):
        spotdl.sync(bot=bot)

    # --- Utilities ---
    @bot.message_handler(commands=["version"])
    def version_command(message):
        """Shows the current version of the bot."""
        try:
            x = send_message(bot, message=get_text("bot_version_info", VERSION))
            threading.Timer(
                15, delete_message, args=(bot,), kwargs={"message_id": x.message_id}
            ).start()
        except Exception as e:
            bot.reply_to(message, get_text("error_generic"))

    @bot.message_handler(commands=["donate"])
    def donate_command(message):
        """Shows a message to support with a donation."""
        try:
            x = send_message(bot, message=get_text("donation_message"))
            threading.Timer(
                45, delete_message, args=(bot,), kwargs={"message_id": x.message_id}
            ).start()
        except Exception as e:
            bot.reply_to(message, get_text("error_generic"))

    # --- Direct URLs ---
    @bot.message_handler(func=lambda message: is_spotify_url(message.text))
    def process_direct_url(message):
        """Processes a Spotify URL directly."""
        try:
            url = message.text.strip()
            spotdl.download(bot=bot, query=url)
        except Exception as e:
            bot.reply_to(message, get_text("error_generic"))

    # --- Fallback ---
    @bot.message_handler(func=lambda message: True)
    def echo_all(message):
        try:
            bot.reply_to(message, get_text("error_unknown_command"))
        except Exception as e:
            pass

    # --- Commands visible in Telegram ---
    bot.set_my_commands(
        [
            telebot.types.BotCommand("/start", get_text("menu_option_start")),
            telebot.types.BotCommand("/authorize", get_text("menu_option_authorize")),
            telebot.types.BotCommand("/download", get_text("menu_option_download_url")),
            telebot.types.BotCommand(
                "/downloadsavedsongs", get_text("menu_option_download_saved_songs")
            ),
            telebot.types.BotCommand(
                "/downloadsavedalbums", get_text("menu_option_download_saved_albums")
            ),
            telebot.types.BotCommand(
                "/downloadsavedplaylists",
                get_text("menu_option_download_saved_playlists"),
            ),
            telebot.types.BotCommand(
                "/downloaduserplaylists",
                get_text("menu_option_download_user_playlists"),
            ),
            # telebot.types.BotCommand(
            #     "/downloaduserfollowedartists",
            #     get_text("menu_option_download_user_followed_artists"),
            # ),
            telebot.types.BotCommand("/sync", get_text("menu_option_sync")),
            telebot.types.BotCommand("/version", get_text("menu_option_version")),
            telebot.types.BotCommand("/donate", get_text("menu_option_donate")),
        ]
    )
