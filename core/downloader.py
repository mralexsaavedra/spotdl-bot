from core.utils import is_spotify_url
from core.locale import delete_message, get_text, send_message
import subprocess

DOWNLOAD_DIR = "/music"

def download(message):
  try:
    url = message.text.strip()
	
    if not is_spotify_url(url):
      send_message(message=get_text("rejected_url"))
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

    x = send_message(message=get_text("downloading"))
  
    subprocess.run(["spotdl", "download", url, "--output", f'{DOWNLOAD_DIR}/{output}'])

    delete_message(x.message_id)
    send_message(message=get_text("download_completed"))
  except Exception as e:
    send_message(message=get_text("error_download"))

def download_liked_songs():
  try:
    x = send_message(message=get_text("downloading"))
    
    output = "Liked Songs/{artists} - {title}.{output-ext}" 
    
    subprocess.run(["spotdl", "download", "saved", "--user-auth", "--output", f'{DOWNLOAD_DIR}/{output}'])
    
    delete_message(x.message_id)
    send_message(message=get_text("download_completed"))
  except Exception as e:
    send_message(message=get_text("error_download"))