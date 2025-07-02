from utils import get_text, error, send_message
import requests
import os
import json
import time
import base64
import urllib.parse
import sys

SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.environ.get("SPOTIFY_REDIRECT_URI")
SCOPES="playlist-read-private user-follow-read user-library-read"
TOKEN_PATH = '/root/.spotdl/.spotipy'

if SPOTIFY_CLIENT_ID is None or SPOTIFY_CLIENT_ID == '':
	error(get_text("error_bot_spotify_client_id"))
	sys.exit(1)
if SPOTIFY_CLIENT_SECRET is None or SPOTIFY_CLIENT_SECRET == '':
	error(get_text("error_bot_spotify_client_secret"))
	sys.exit(1)
if SPOTIFY_REDIRECT_URI is None or SPOTIFY_REDIRECT_URI == '':
	error(get_text("error_bot_spotify_client_secret"))
	sys.exit(1)

def save_token(token_data):
  token_data['expires_at'] = int(time.time()) + token_data['expires_in']
  os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
  with open(TOKEN_PATH, 'w') as f:
    json.dump(token_data, f)

def load_token():
  if os.path.exists(TOKEN_PATH):
    with open(TOKEN_PATH, 'r') as f:
      return json.load(f)
  return None

def refresh_token(refresh_token):
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
    new_token['refresh_token'] = refresh_token  # mantener el mismo si no se devuelve uno nuevo
    save_token(new_token)
    return new_token
  else:
    raise Exception(f"❌ Error al refrescar el token: {r.text}")
  
def get_new_token(message):
  code = message.text.strip()
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
    save_token(token)
  else:
    raise Exception(f"❌ Error al obtener token: {r.text}")
   

def authorize(message):
  params = {
    'client_id': SPOTIFY_CLIENT_ID,
    'response_type': 'code',
    'redirect_uri': SPOTIFY_REDIRECT_URI,
    'scope': SCOPES
  }
  auth_url = f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"
  send_message(message=get_text("authorize", auth_url))
  time.sleep(5)
  send_message(message=get_text("redirect_url"))
  bot.register_next_step_handler(message, get_new_token)

def get_valid_token(message):
  token = load_token()
  if token:
    if int(time.time()) < token.get('expires_at', 0):
      print("✅ Token válido cargado desde archivo")
      return token
    else:
      print("⏰ Token expirado")
      return refresh_token(token['refresh_token'])
  else:
    return authorize(message)
