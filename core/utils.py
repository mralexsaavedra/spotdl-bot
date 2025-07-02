import re

def is_spotify_url(url):
  match = re.match(r"https://open\.spotify\.com/([a-zA-Z0-9]+)", url)
  return bool(match)
