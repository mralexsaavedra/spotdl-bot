from config.settings import TELEGRAM_GROUP, TELEGRAM_TOKEN
from bot.commands import register_commands
import telebot

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def run_bot():
  register_commands(bot)
  bot.infinity_polling()

def send_message(chat_id=TELEGRAM_GROUP, message=None, reply_markup=None, parse_mode="markdown", disable_web_page_preview=True):
	try:
		return bot.send_message(chat_id, message, parse_mode=parse_mode, reply_markup=reply_markup, disable_web_page_preview=disable_web_page_preview)
	except Exception as e:
		pass

def delete_message(message_id):
	try:
		bot.delete_message(TELEGRAM_GROUP, message_id)
	except:
		pass

def register_next_message(message, func):
  try:
    bot.register_next_step_handler(message, func)
  except Exception as e:
    pass