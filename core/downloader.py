from config.settings import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, TOKEN_PATH
from core.logger import setup_logger
from core.utils import delete_message, is_spotify_url, send_message
from locale.locale import get_text
import subprocess

DOWNLOAD_DIR = "/music"

logger = setup_logger(__name__)

def download(bot, message):
  try:
    url = message.text.strip()
    logger.debug(f"Downloading from Spotify URL: {url}")
	
    if not is_spotify_url(url):
      logger.error(f"Invalid Spotify URL: {url}")
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

def download_liked(bot):
  try:
    logger.debug("Downloading liked songs")
    x = send_message(bot, message=get_text("download_in_progress"))
    
    output = "Liked Songs/{artists} - {title}.{output-ext}" 

    subprocess.run(["spotdl", "download", "saved", "--user-auth", "--output", f'{DOWNLOAD_DIR}/{output}', "--client-id", SPOTIFY_CLIENT_ID, "--client-secret", SPOTIFY_CLIENT_SECRET, "--cache-path", TOKEN_PATH])
    
    delete_message(bot, message_id=x.message_id)
    send_message(bot, message=get_text("download_finished"))
  except Exception as e:
    send_message(bot, message=get_text("error_download_failed"))

def download_albums(bot):
  try:
    logger.debug("Downloading saved albums")
    x = send_message(bot, message=get_text("download_in_progress"))
    
    output = "{album-artist}/{album}/{artists} - {title}.{output-ext}"
    
    subprocess.run(["spotdl", "download", "all-user-saved-albums", "--user-auth", "--output", f'{DOWNLOAD_DIR}/{output}', "--client-id", SPOTIFY_CLIENT_ID, "--client-secret", SPOTIFY_CLIENT_SECRET, "--cache-path", TOKEN_PATH])
    
    delete_message(bot, message_id=x.message_id)
    send_message(bot, message=get_text("download_finished"))
  except Exception as e:
    send_message(bot, message=get_text("error_download_failed"))

def download_playlists(bot):
  try:
    logger.debug("Downloading playlists")
    x = send_message(bot, message=get_text("download_in_progress"))
    
    output = "Playlists/{list-name}/{artists} - {title}.{output-ext}"
    
    subprocess.run(["spotdl", "download", "all-user-playlists", "--user-auth", "--output", f'{DOWNLOAD_DIR}/{output}', "--client-id", SPOTIFY_CLIENT_ID, "--client-secret", SPOTIFY_CLIENT_SECRET, "--cache-path", TOKEN_PATH])
    
    delete_message(bot, message_id=x.message_id)
    send_message(bot, message=get_text("download_finished"))
  except Exception as e:
    send_message(bot, message=get_text("error_download_failed"))