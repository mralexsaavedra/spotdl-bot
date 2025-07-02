from core.utils import is_spotify_url
from core.locale import get_text
import subprocess

DOWNLOAD_DIR = "/music"

def download(bot, message):
  try:
    url = message.text.strip()
	
    if not is_spotify_url(url):
      bot.send_message(message.chat.id, get_text("not_spotify_url"))
      return
          
    if "track" in url:
      output = "{artist}/{artists} - {title}.{output-ext}"
    elif "album" in url:
      output = "{album-artist}/{album}/{artists} - {title}.{output-ext}"
    elif "playlist" in url:
      output = "Playlists/{list-name}/{artists} - {title}.{output-ext}"
    elif "artist" in url:
      output = "{artist}/{artists} - {title}.{output-ext}"
    else:
      output = "{artists} - {title}.{output-ext}"

    x = bot.send_message(message.chat.id, get_text("downloading"))
  
    subprocess.run(["spotdl", "download", url, "--output", f'{DOWNLOAD_DIR}/{output}'])

    bot.delete_message(x.message_id)
    bot.send_message(message.chat.id, get_text("download_completed"))
  except Exception as e:
    bot.send_message(message.chat.id, get_text("error_download"))

def download_liked_songs(bot, message):
  try:
    x = bot.send_message(message.chat.id, get_text("downloading"))
    
    output = "Liked Songs/{artists} - {title}.{output-ext}" 
    
    subprocess.run(["spotdl", "download", "saved", "--user-auth", "--output", f'{DOWNLOAD_DIR}/{output}'])
    
    bot.delete_message(x.message_id)
    bot.send_message(message.chat.id, get_text("download_completed"))
  except Exception as e:
    bot.send_message(message.chat.id, get_text("error_download"))