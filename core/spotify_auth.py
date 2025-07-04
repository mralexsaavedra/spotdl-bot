import base64
import json
import os
import time
import urllib.parse
from typing import Optional, Dict, Any

import requests
import telebot

from config.config import (
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
    SPOTIFY_REDIRECT_URI,
    CACHE_DIR,
)
from core.locale import get_text
from core.logger import setup_logger
from core.utils import send_message

SCOPES = "playlist-read-private user-follow-read user-library-read"

logger = setup_logger(__name__)

TOKEN_PATH = f"{CACHE_DIR}/spotify_token.json"


def save_token(token_data: Dict[str, Any]) -> None:
    """
    Save the Spotify token data to a file, adding the expires_at timestamp.

    Args:
        token_data: The token data dictionary returned from Spotify API.

    Raises:
        Exception: If saving fails.
    """
    try:
        logger.info(f"Saving token to file at {TOKEN_PATH}")
        token_data["expires_at"] = int(time.time()) + token_data.get("expires_in", 0)
        os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
        with open(TOKEN_PATH, "w") as f:
            logger.debug(f"Token data being saved: {token_data}")
            json.dump(token_data, f)
    except Exception as e:
        logger.error(f"Failed to save token: {e}")
        raise Exception(get_text("error_save_token")) from e


def load_token() -> Optional[Dict[str, Any]]:
    """
    Load the Spotify token data from a file, if it exists.

    Returns:
        The token dictionary if available, otherwise None.
    """
    if not os.path.exists(TOKEN_PATH):
        logger.info(f"Token file does not exist at {TOKEN_PATH}")
        return None
    try:
        with open(TOKEN_PATH, "r") as f:
            token = json.load(f)
            logger.debug(f"Token loaded from file: {token}")
            return token
    except Exception as e:
        logger.error(f"Failed to load token: {e}")
        raise Exception(get_text("error_load_token")) from e


def refresh_token(bot: telebot.TeleBot, refresh_token: str) -> None:
    """
    Refresh the Spotify access token using the refresh token.

    Args:
        bot: Telegram bot instance, to send messages.
        refresh_token: The refresh token string.

    Raises:
        Exception: If refresh fails.
    """
    logger.info("Refreshing Spotify token...")
    token_url = "https://accounts.spotify.com/api/token"
    auth_header = base64.b64encode(
        f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()
    ).decode()
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    try:
        response = requests.post(token_url, headers=headers, data=data)
        if response.status_code != 200:
            logger.error(f"Refresh token failed: {response.text}")
            raise Exception(get_text("error_refresh_token"))
        token_data = response.json()
        logger.debug(f"Received new token data: {token_data}")
        # Spotify may or may not return a new refresh_token; keep the old if missing
        if "refresh_token" not in token_data:
            token_data["refresh_token"] = refresh_token
        save_token(token_data)
        send_message(bot, message=get_text("auth_token_refreshed"))
    except Exception as e:
        logger.error(f"Exception during token refresh: {e}")
        raise


def get_new_token(message: Any, bot: telebot.TeleBot) -> None:
    """
    Exchange the authorization code received via Telegram message for an access token.

    Args:
        message: Telegram message containing the authorization code.
        bot: Telegram bot instance.

    Raises:
        Exception: If token retrieval fails.
    """
    code = message.text.strip()
    logger.info(f"Received authorization code: {code}")

    token_url = "https://accounts.spotify.com/api/token"
    auth_header = base64.b64encode(
        f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()
    ).decode()
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": SPOTIFY_REDIRECT_URI,
    }
    try:
        response = requests.post(token_url, headers=headers, data=data)
        if response.status_code != 200:
            logger.error(f"Failed to obtain token: {response.text}")
            raise Exception(get_text("error_obtain_token"))
        token_data = response.json()
        logger.debug(f"Token obtained: {token_data}")
        save_token(token_data)
        send_message(bot, message=get_text("auth_success"))
    except Exception as e:
        logger.error(f"Exception during token retrieval: {e}")
        raise


def authorize(bot: telebot.TeleBot, message: Any) -> None:
    """
    Start the Spotify authorization by sending the authorization URL to the user.

    Args:
        bot: Telegram bot instance.
        message: Telegram message triggering authorization.
    """
    logger.info("Starting Spotify authorization process")
    params = {
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "scope": SCOPES,
    }
    auth_url = (
        f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"
    )
    logger.debug(f"Authorization URL: {auth_url}")
    send_message(bot, message=get_text("auth_request", auth_url))
    time.sleep(5)
    send_message(bot, message=get_text("auth_redirect_prompt"))
    bot.register_next_step_handler(message, get_new_token, bot)


def auth(bot: telebot.TeleBot, message: Any) -> None:
    """
    Main entry for Spotify authentication.

    Loads existing token and refreshes if needed, or initiates authorization.

    Args:
        bot: Telegram bot instance.
        message: Telegram message.

    """
    try:
        token = load_token()
        logger.debug(f"Loaded token: {token}")
        if token and token.get("refresh_token"):
            if int(time.time()) >= token.get("expires_at", 0):
                logger.info("Token expired, refreshing...")
                refresh_token(bot, token["refresh_token"])
            else:
                logger.info("Token valid and active")
                send_message(bot, message=get_text("auth_already_done"))
        else:
            logger.info("No valid token found, starting authorization")
            authorize(bot, message)
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        send_message(bot, message=get_text("error_auth_failed"))
