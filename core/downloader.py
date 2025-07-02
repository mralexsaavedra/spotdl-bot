from config.settings import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, TOKEN_PATH
from core.utils import delete_message, is_spotify_url, send_message
from core.locale import get_text
import subprocess

DOWNLOAD_DIR = "/music"

def download(bot, message):
  try:
    url = message.text.strip()
	
    if not is_spotify_url(url):
      send_message(bot, message=get_text("error_invalid_spotify_url"))
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

    x = send_message(bot, message=get_text("download_in_progress"))
  
    subprocess.run(["spotdl", "download", url, "--output", f'{DOWNLOAD_DIR}/{output}', "--client-id", SPOTIFY_CLIENT_ID, "--client-secret", SPOTIFY_CLIENT_SECRET, "--cache-path", TOKEN_PATH])

    delete_message(bot, message_id=x.message_id)
    send_message(bot, message=get_text("download_finished"))
  except Exception as e:
    send_message(bot, message=get_text("error_download_failed"))

def download_liked_songs(bot, message):
  try:
    x = send_message(bot, message=get_text("download_in_progress"))
    
    output = "Liked Songs/{artists} - {title}.{output-ext}" 
    
    subprocess.run(["spotdl", "download", "saved", "--user-auth", "--output", f'{DOWNLOAD_DIR}/{output}', "--client-id", SPOTIFY_CLIENT_ID, "--client-secret", SPOTIFY_CLIENT_SECRET, "--cache-path", TOKEN_PATH])
    
    delete_message(bot, message_id=x.message_id)
    send_message(bot, message=get_text("download_finished"))
  except Exception as e:
    send_message(bot, message=get_text("error_download_failed"))