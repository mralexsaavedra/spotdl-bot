import time
from spotifyDownloader import SpotifyDownloader
from config.config import VERSION
from core.spotify_auth import auth
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
        auth(bot, message)

    @bot.message_handler(commands=["download"])
    def download_command(message):
        """Requests a Spotify URL to download."""
        send_message(bot, message=get_text("download_prompt_url"))

    # --- Downloads ---
    @bot.message_handler(commands=["downloadliked"])
    def download_liked_command(message):
        """Downloads songs marked as favorites."""
        spotdl.download_all_user_songs(bot=bot)

    @bot.message_handler(commands=["downloadalbums"])
    def download_albums_command(message):
        """Downloads albums saved by the user."""
        spotdl.download_all_user_albums(bot=bot)

    @bot.message_handler(commands=["downloadplaylists"])
    def download_playlists_command(message):
        """Downloads playlists saved by the user."""
        spotdl.download_all_user_playlists(bot=bot)

    # --- Utilities ---
    @bot.message_handler(commands=["version"])
    def version_command(message):
        """Shows the current version of the bot."""
        x = send_message(bot, message=get_text("bot_version_info", VERSION))
        time.sleep(15)
        delete_message(bot, message_id=x.message_id)

    @bot.message_handler(commands=["donate"])
    def donate_command(message):
        """Shows a message to support with a donation."""
        x = send_message(bot, message=get_text("donation_message"))
        time.sleep(45)
        delete_message(bot, message_id=x.message_id)

    # --- Direct URLs ---
    @bot.message_handler(func=lambda message: is_spotify_url(message.text))
    def process_direct_url(message):
        """Processes a Spotify URL directly."""
        url = message.text.strip()
        spotdl.download(bot=bot, query=url)

    # --- Fallback ---
    @bot.message_handler(func=lambda message: True)
    def echo_all(message):
        """Shows an error if the command is not recognized."""
        bot.reply_to(message, get_text("error_unknown_command"))

    # --- Commands visible in Telegram ---
    bot.set_my_commands(
        [
            telebot.types.BotCommand("/start", get_text("menu_option_start")),
            telebot.types.BotCommand("/authorize", get_text("menu_option_authorize")),
            telebot.types.BotCommand("/download", get_text("menu_option_download_url")),
            telebot.types.BotCommand(
                "/downloadliked", get_text("menu_option_download_liked")
            ),
            telebot.types.BotCommand(
                "/downloadalbums", get_text("menu_option_download_albums")
            ),
            telebot.types.BotCommand(
                "/downloadplaylists", get_text("menu_option_download_playlists")
            ),
            telebot.types.BotCommand("/version", get_text("menu_option_version")),
            telebot.types.BotCommand("/donate", get_text("menu_option_donate")),
        ]
    )
