from config.settings import TELEGRAM_TOKEN, VERSION
from bot.commands import register_commands
from locale.locale import get_text
from core.logger import setup_logger
from core.utils import send_message
import telebot

logger = setup_logger(__name__)

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def run_bot():
  logger.debug(get_text("log_bot_start", VERSION))

  register_commands(bot)

  starting_message = (
    f"{get_text("bot_started_title")}\n"
    f"{get_text("status_active")}\n"
    f"{get_text('bot_version_label', VERSION)}\n\n"
    f"{get_text('bot_description')}"
)


  send_message(bot, message=starting_message)

  bot.infinity_polling()