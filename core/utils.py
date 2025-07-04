from config.config import TELEGRAM_GROUP
from core.logger import setup_logger
import re

logger = setup_logger(__name__)

def is_spotify_url(url):
  match = re.match(r"https://open\.spotify\.com/([a-zA-Z0-9]+)", url)
  return bool(match)

def send_message(bot, chat_id=TELEGRAM_GROUP, message=None, reply_markup=None, parse_mode="markdown", disable_web_page_preview=True):
  try:
    return bot.send_message(chat_id, message, parse_mode=parse_mode, reply_markup=reply_markup, disable_web_page_preview=disable_web_page_preview)
  except Exception as e:
    logger.error(f"Error sending message to {chat_id}: {e}")
    pass

def delete_message(bot, message_id):
	try:
		bot.delete_message(TELEGRAM_GROUP, message_id)
	except:
		pass