from config.settings import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, TOKEN_PATH
from core.locale import get_text
from core.logger import setup_logger
from core.utils import send_message
import requests
import os
import json
import time
import base64
import urllib.parse

SCOPES="playlist-read-private user-follow-read user-library-read"

logger = setup_logger(__name__)

def save_token(token_data):
  logger.debug("Saving token to file")
  token_data['expires_at'] = int(time.time()) + token_data['expires_in']
  os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
  with open(TOKEN_PATH, 'w') as f:
    logger.debug(f"Token data to save: {token_data}")
    json.dump(token_data, f)

def load_token():
  logger.debug("Loading token")
  if os.path.exists(TOKEN_PATH):
    with open(TOKEN_PATH, 'r') as f:
      logger.debug("Loading token from file")
      return json.load(f)
  logger.debug("Token file does not exist")
  return None

def refresh_token(bot, refresh_token):
  logger.debug("Refreshing token")
  token_url = 'https://accounts.spotify.com/api/token'
  auth_header = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
  headers = {
    'Authorization': f'Basic {auth_header}',
    'Content-Type': 'application/x-www-form-urlencoded'
  }
  data = {
    'grant_type': 'refresh_token',
    'refresh_token': refresh_token
  }
  r = requests.post(token_url, headers=headers, data=data)
  if r.status_code == 200:
    new_token = r.json()
    logger.debug(f"New token received: {new_token}")
    new_token['refresh_token'] = refresh_token  # mantener el mismo si no se devuelve uno nuevo
    save_token(new_token)
    send_message(bot, message=get_text("auth_token_refreshed"))
  else:
    raise Exception(f"❌ Error al refrescar el token: {r.text}")
  
def get_new_token(message, bot):
  logger.debug("Received new token code")
  code = message.text.strip()
  logger.debug(f"Authorization code: {code}")
  token_url = 'https://accounts.spotify.com/api/token'
  auth_header = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
  headers = {
    'Authorization': f'Basic {auth_header}',
    'Content-Type': 'application/x-www-form-urlencoded'
  }
  data = {
    'grant_type': 'authorization_code',
    'code': code,
    'redirect_uri': SPOTIFY_REDIRECT_URI
  }

  r = requests.post(token_url, headers=headers, data=data)
  if r.status_code == 200:
    token = r.json()
    logger.debug(f"Token received: {token}")
    save_token(token)
    send_message(bot, message=get_text("auth_success"))
  else:
    raise Exception(f"❌ Error al obtener token: {r.text}")
   

def authorize(bot, message):
  logger.debug("Starting authorization process")
  params = {
    'client_id': SPOTIFY_CLIENT_ID,
    'response_type': 'code',
    'redirect_uri': SPOTIFY_REDIRECT_URI,
    'scope': SCOPES
  }
  auth_url = f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"
  logger.debug(f"Authorization URL: {auth_url}")
  send_message(bot, message=get_text("auth_request", auth_url))
  time.sleep(5)
  send_message(bot, message=get_text("auth_redirect_prompt"))
  bot.register_next_step_handler(message, get_new_token, bot)

def get_valid_token(bot, message):
  token = load_token()
  logger.debug(f"Token loaded: {token}")
  if token:
    if not int(time.time()) < token.get('expires_at', 0):
      refresh_token(bot, refresh_token=token['refresh_token'])
    else:
      logger.debug("Token is valid and not expired")
      send_message(bot, message=get_text("auth_already_done"))
  else:
    authorize(bot, message)
