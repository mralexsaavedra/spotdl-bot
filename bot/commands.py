import threading
from spotifyDownloader import SpotifyDownloader
from settings.settings import VERSION
from core.locale import get_text
from core.utils import delete_message, is_spotify_url, parse_call_data, send_message
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

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

    # --- Downloads ---
    @bot.message_handler(commands=["download"])
    def download_command(message):
        """Requests a Spotify URL to download."""
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton(
                get_text("button_download_saved_songs"), callback_data="download|saved"
            ),
            InlineKeyboardButton(
                get_text("button_download_saved_albums"),
                callback_data="download|all-user-saved-albums",
            ),
            InlineKeyboardButton(
                get_text("button_download_saved_playlists"),
                callback_data="download|all-saved-playlists",
            ),
            InlineKeyboardButton(
                get_text("button_download_user_playlists"),
                callback_data="download|all-user-playlists",
            ),
            # InlineKeyboardButton(
            #     get_text("button_download_user_followed_artists"),
            #     callback_data="download|all-user-followed-artists"
            # ),
        )
        send_message(
            bot=bot, message=get_text("download_menu_prompt"), reply_markup=markup
        )

    @bot.message_handler(commands=["sync"])
    def sync_command(message):
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton(
                get_text("button_sync_songs"), callback_data="sync|songs"
            ),
            InlineKeyboardButton(
                get_text("button_sync_albums"),
                callback_data="sync|albums",
            ),
            InlineKeyboardButton(
                get_text("button_sync_artists"),
                callback_data="sync|artists",
            ),
            InlineKeyboardButton(
                get_text("button_sync_playlists"),
                callback_data="sync|playlists",
            ),
            InlineKeyboardButton(
                get_text("button_sync_saved_songs"), callback_data="sync|saved"
            ),
            InlineKeyboardButton(
                get_text("button_sync_saved_albums"),
                callback_data="sync|all-user-saved-albums",
            ),
            InlineKeyboardButton(
                get_text("button_sync_saved_playlists"),
                callback_data="sync|all-saved-playlists",
            ),
            InlineKeyboardButton(
                get_text("button_sync_user_playlists"),
                callback_data="sync|all-user-playlists",
            ),
            # InlineKeyboardButton(
            #     get_text("button_sync_user_followed_artists"),
            #     callback_data="sync|all-user-followed-artists"
            # ),
        )
        send_message(bot=bot, message=get_text("sync_menu_prompt"), reply_markup=markup)

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

    @bot.callback_query_handler(func=lambda mensaje: True)
    def button_controller(call):
        bot.answer_callback_query(call.id)

        data = parse_call_data(call.data)
        comando = data["comando"]
        query = data.get("query")

        if comando == "download":
            spotdl.download(bot=bot, query=query)
        elif comando == "sync":
            spotdl.sync(bot=bot, query=query)
        else:
            return

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
            telebot.types.BotCommand("/download", get_text("menu_option_download")),
            telebot.types.BotCommand("/sync", get_text("menu_option_sync")),
            telebot.types.BotCommand("/version", get_text("menu_option_version")),
            telebot.types.BotCommand("/donate", get_text("menu_option_donate")),
        ]
    )
