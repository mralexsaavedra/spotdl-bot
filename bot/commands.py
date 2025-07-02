from config.settings import VERSION
from core.downloader import  download, download_liked_songs
from core.spotify_auth import get_valid_token
from core.locale import delete_message, get_text, send_message
import telebot
import time

def register_commands(bot):
  @bot.message_handler(commands=['start'])
  def start_command(message):
    send_message(message=get_text("menu"))

  @bot.message_handler(commands=['authorize'])
  def authorize_command(message):
    get_valid_token(message)

  @bot.message_handler(commands=['download'])
  def download_command(message):
    send_message(message=get_text("download_url"))
    bot.register_next_step_handler(message, download)

  @bot.message_handler(commands=['download_liked_songs'])
  def download_liked_songs_command(message):
    download_liked_songs()

  @bot.message_handler(commands=['version'])
  def version_command(message):
    x = send_message(message=get_text("version", VERSION))
    time.sleep(15)
    delete_message(x.message_id)

  @bot.message_handler(commands=['donate'])
  def donate_command(message):
    x = send_message(message=get_text("donate"))
    time.sleep(45)
    delete_message(x.message_id)

  @bot.message_handler(func=lambda message: message.text.startswith("https://open.spotify.com/"))
  def process_direct_url(message):
    download(message)

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