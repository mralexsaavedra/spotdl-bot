from config.settings import VERSION
from core.downloader import  download, download_liked_songs
from core.spotify_auth import get_valid_token, load_token
from core.locale import get_text
from core.utils import is_spotify_url
import telebot
import time

def register_commands(bot):
  @bot.message_handler(commands=['start'])
  def start_command(message):
    bot.send_message(chat_id=message.chat.id, message=get_text("menu"))

  @bot.message_handler(commands=['authorize'])
  def authorize_command(message):
    get_valid_token(bot, message)

  @bot.message_handler(commands=['download'])
  def download_command(message):
    bot.send_message(chat_id=message.chat.id, message=get_text("download_url"))

  @bot.message_handler(commands=['download_liked_songs'])
  def download_liked_songs_command(message):
    token = load_token()
    if not token:
      bot.send_message(chat_id=message.chat.id, message=get_text("error_no_token"))
      return
    download_liked_songs(bot, message)

  @bot.message_handler(commands=['version'])
  def version_command(message):
    x = bot.send_message(chat_id=message.chat.id, message=get_text("version", VERSION))
    time.sleep(15)
    bot.delete_message(chat_id=message.chat.id, message=x.message_id)

  @bot.message_handler(commands=['donate'])
  def donate_command(message):
    x = bot.send_message(chat_id=message.chat.id, message=get_text("donate"))
    time.sleep(45)
    bot.delete_message(chat_id=message.chat.id, message=x.message_id)

  @bot.message_handler(func=lambda message: is_spotify_url(message.text))
  def process_direct_url(message):
    download(bot, message)

  @bot.message_handler(func=lambda message: True)
  def echo_all(message):
    bot.reply_to(message, get_text("error_unknown_command"))

  bot.set_my_commands([
		telebot.types.BotCommand("/start", get_text("menu_start")),
    telebot.types.BotCommand("/authorize", get_text("menu_authorize")),
		telebot.types.BotCommand("/download", get_text("menu_download")),
		telebot.types.BotCommand("/download_liked_songs", get_text("menu_download_liked_songs")),
		telebot.types.BotCommand("/version", get_text("menu_version")),
		telebot.types.BotCommand("/donate", get_text("menu_donate")),
	])