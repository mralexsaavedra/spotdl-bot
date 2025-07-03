from config.settings import VERSION
from core.downloader import  download, download_liked, download_playlists, download_albums
from core.spotify_auth import auth, load_token
from locale.locale import get_text
from core.utils import delete_message, is_spotify_url, send_message
import telebot
import time

def register_commands(bot):
  @bot.message_handler(commands=['start'])
  def start_command(message):
    send_message(bot, message=get_text("menu_main"))

  @bot.message_handler(commands=['authorize'])
  def authorize_command(message):
    auth(bot, message)

  @bot.message_handler(commands=['download'])
  def download_command(message):
    send_message(bot, message=get_text("download_prompt_url"))

  @bot.message_handler(commands=['downloadliked'])
  def download_liked_command(message):
    token = load_token()
    if not token:
      send_message(bot, message=get_text("error_no_valid_token"))
      return
    download_liked(bot)

  @bot.message_handler(commands=['downloadalbums'])
  def download_albums_command(message):
    token = load_token()
    if not token:
      send_message(bot, message=get_text("error_no_valid_token"))
      return
    download_albums(bot)

  @bot.message_handler(commands=['downloadplaylists'])
  def download_playlists_command(message):
    token = load_token()
    if not token:
      send_message(bot, message=get_text("error_no_valid_token"))
      return
    download_playlists(bot)

  @bot.message_handler(commands=['version'])
  def version_command(message):
    x = send_message(bot, message=get_text("bot_version_info", VERSION))
    time.sleep(15)
    delete_message(bot, message_id=x.message_id)

  @bot.message_handler(commands=['donate'])
  def donate_command(message):
    x = send_message(bot, message=get_text("donation_message"))
    time.sleep(45)
    delete_message(bot, message_id=x.message_id)

  @bot.message_handler(func=lambda message: is_spotify_url(message.text))
  def process_direct_url(message):
    download(bot, message)

  @bot.message_handler(func=lambda message: True)
  def echo_all(message):
    bot.reply_to(message, get_text("error_unknown_command"))

  bot.set_my_commands([
		telebot.types.BotCommand("/start", get_text("menu_option_start")),
    telebot.types.BotCommand("/authorize", get_text("menu_option_authorize")),
		telebot.types.BotCommand("/download", get_text("menu_option_download_url")),
		telebot.types.BotCommand("/downloadliked", get_text("menu_option_download_liked")),
    telebot.types.BotCommand("/downloadalbums", get_text("menu_option_download_albums")),
    telebot.types.BotCommand("/downloadplaylists", get_text("menu_option_download_playlists")),
		telebot.types.BotCommand("/version", get_text("menu_option_version")),
		telebot.types.BotCommand("/donate", get_text("menu_option_donate")),
	])