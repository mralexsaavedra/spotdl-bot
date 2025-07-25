from config.config import TELEGRAM_TOKEN, VERSION
from bot.commands import register_commands
from core.locale import get_text
from core.utils import send_message
from loguru import logger
import telebot


bot: telebot.TeleBot = telebot.TeleBot(TELEGRAM_TOKEN)


def run_bot() -> None:
    """
    Starts the Telegram bot, registers commands, sends a startup message,
    and begins polling for updates.
    """
    logger.info(f"🔧 Starting SpotDL Bot (v{VERSION})")

    register_commands(bot)

    starting_message = (
        f"{get_text('bot_started_title')}\n"
        f"{get_text('bot_status_label')}\n"
        f"{get_text('bot_version_label', VERSION)}\n\n"
        f"{get_text('bot_description')}"
    )

    send_message(bot, message=starting_message)

    try:
        bot.infinity_polling(60)
    except Exception as e:
        logger.error(f"Error during bot polling: {e}")
