from config.settings import CONTAINER_NAME, TELEGRAM_TOKEN
from core.downloader import download_from_url, download_liked_songs
from core.spotify_auth import get_valid_token
from utils import debug, delete_message, get_text, error, send_message
import telebot
import os
import re
import time

VERSION = "0.0.1"

downloadId = None

# Instanciamos el bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

def is_valid_url(url):
	match = re.match(r"https://open\.spotify\.com/([a-zA-Z0-9]+)", url)
	return bool(match)

def download(message):
	url = message.text.strip()
	
	if not is_valid_url(url):
		send_message(message=get_text("rejected_url"))
		return

	x = send_message(message=get_text("downloading"))
	result = download_from_url(url=url)
	delete_message(x.message_id)
	if result:
		send_message(message=result)

@bot.message_handler(commands=['start'])
def start(message):
	send_message(message=get_text("menu"))

@bot.message_handler(commands=['authorize'])
def authorize(message):
	get_valid_token(message)

@bot.message_handler(commands=['download'])
def download_command(message):
	send_message(message=get_text("download_url"))
	bot.register_next_step_handler(message, download)

@bot.message_handler(commands=['download_liked_songs'])
def download_liked_songs_command(message):
	x = send_message(message=get_text("downloading"))
	result = download_liked_songs()
	delete_message(x.message_id)
	if result:
		send_message(message=result)

@bot.message_handler(commands=['cancel'])
def cancel_command(message):
	global downloadId
	if downloadId is not None:
		try:
			os.kill(downloadId, 9)
		except Exception as e:
			error(get_text("error_cancel_download", downloadId, e))
		downloadId = None
	else:
		send_message(message=get_text("no_download_in_progress"))

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

if __name__ == '__main__':
	debug(get_text("debug_starting_bot", VERSION))

	bot.set_my_commands([
		telebot.types.BotCommand("/start", get_text("menu_start")),
		telebot.types.BotCommand("/download", get_text("menu_download")),
		telebot.types.BotCommand("/download_liked_songs", get_text("menu_download_liked_songs")),
		telebot.types.BotCommand("/cancel", get_text("menu_cancel")),
		telebot.types.BotCommand("/version", get_text("menu_version")),
		telebot.types.BotCommand("/donate", get_text("menu_donate")),
	])

	starting_message = f"🎙️ *{CONTAINER_NAME}\n{get_text('active')}*"
	starting_message += f"\n_📝 v{VERSION}_"
	send_message(message=starting_message)
	
	bot.infinity_polling(timeout=60)