import threading
from spotifyDownloader import SpotifyDownloader
from config.config import VERSION
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
                get_text("button_saved_song"), callback_data="downloadsavedsongs"
            ),
            InlineKeyboardButton(
                get_text("button_saved_albums"), callback_data="downloadsavedalbums"
            ),
            InlineKeyboardButton(
                get_text("button_saved_playlists"),
                callback_data="downloadsavedplaylists",
            ),
            InlineKeyboardButton(
                get_text("button_user_playlists"), callback_data="downloaduserplaylists"
            ),
            # InlineKeyboardButton(
            #     get_text("button_user_followed_artists"),
            #     callback_data="downloaduserfollowedartists"
            # ),
        )
        send_message(
            bot=bot, message=get_text("download_menu_prompt"), reply_markup=markup
        )

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

    @bot.callback_query_handler(func=lambda mensaje: True)
    def button_controller(call):
        bot.answer_callback_query(call.id)

        data = parse_call_data(call.data)
        comando = data["comando"]
        query = ""

        if comando == "downloadsavedsongs":
            query = "saved"
        elif comando == "downloadsavedalbums":
            query = "all-user-saved-albums"
        elif comando == "downloadsavedplaylists":
            query = "all-saved-playlists"
        elif comando == "downloaduserplaylists":
            query = "all-user-playlists"
        elif comando == "downloaduserfollowedartists":
            query = "all-user-followed-artists"
        else:
            return

        spotdl.download(bot=bot, query=query)

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
