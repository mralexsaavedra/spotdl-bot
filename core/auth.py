from config.config import TELEGRAM_TOKEN
from spotifyDownloader.oauth2 import SpotifyOAuth
import telebot

bot: telebot.TeleBot = telebot.TeleBot(TELEGRAM_TOKEN)

auth_manager = SpotifyOAuth()
auth_manager.get_access_token(bot=bot)
