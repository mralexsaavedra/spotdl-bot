from config.settings import CONTAINER_NAME, TELEGRAM_GROUP, TELEGRAM_TOKEN, VERSION
from bot.commands import register_commands
from core.locale import get_text
from core.logger import setup_logger
import telebot

logger = setup_logger(__name__)

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def run_bot():
  logger.debug(get_text("debug_starting_bot", VERSION))

  register_commands(bot)

  starting_message = f"🫡 *{CONTAINER_NAME}\n{get_text('active')}*"
  starting_message += f"\n_⚙️ v{VERSION}_"
  bot.send_message(TELEGRAM_GROUP, starting_message)

  bot.infinity_polling()