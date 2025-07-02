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
    "🚀 *spotdl-bot*\n"
    f"{get_text('status_active')}\n"
    f"🔧 _v{VERSION}_\n"
  )

  send_message(bot, message=starting_message)

  bot.infinity_polling()