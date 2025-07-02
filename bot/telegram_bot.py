from config.settings import CONTAINER_NAME, TELEGRAM_GROUP, TELEGRAM_TOKEN, VERSION
from bot.commands import register_commands
from core.locale import get_text
from core.logger import setup_logger
from core.utils import send_message
import telebot

logger = setup_logger(__name__)

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def run_bot():
  logger.debug(get_text("log_bot_start", VERSION))

  register_commands(bot)

  starting_message = (
    f"🚀 *{CONTAINER_NAME}*\n"
    f"{get_text('status_active')}\n"
    f"🔧 Ejecutando la versión _v{VERSION}_\n"
    "🎵 Preparado para gestionar tus descargas desde Spotify."
  )

  send_message(bot, message=starting_message)

  bot.infinity_polling()