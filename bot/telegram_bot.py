from config.settings import TELEGRAM_TOKEN
from bot.commands import register_commands
import telebot

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def run_bot():
  register_commands(bot)
  bot.infinity_polling()