from utils import error, get_text, send_message
import subprocess

DOWNLOAD_DIR = "/music"

def download_from_url(url):
  try:
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
  
    p = subprocess.Popen(["spotdl", "download", url, "--output", f'{DOWNLOAD_DIR}/{output}'])
    
    global downloadId
    downloadId = p.pid
    p.wait()
    
    if p.returncode == 0:
      send_message(message=get_text("download_completed"))
    else:
      send_message(message=get_text("download_cancelled"))
    
    downloadId = None
    return None
  except Exception as e:
    error(get_text("error_download_with_error", url, e))
    return get_text("error_download", url)

def download_liked_songs():
  try:
    output = DOWNLOAD_DIR + "/Liked Songs/{artists} - {title}.{output-ext}" 
    p = subprocess.Popen(["spotdl", "download", "saved", "--output", output, "--user-auth"])
    global downloadId
    downloadId = p.pid
    p.wait()
    if p.returncode == 0:
      send_message(message=get_text("liked_songs_download_completed"))
    else:
      send_message(message=get_text("download_cancelled"))
    downloadId = None
    return None
  except Exception as e:
    error(get_text("liked_songs_error_download_with_error", e))
    return get_text("liked_songs_error_download")