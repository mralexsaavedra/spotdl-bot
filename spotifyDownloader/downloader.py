from config.config import (
    DOWNLOAD_DIR,
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
    CACHE_DIR,
)
from loguru import logger
from core.spotify_auth import load_token
from core.utils import delete_message, get_output_pattern, send_message
from core.locale import get_text
import subprocess
import time

MAX_RETRIES = 5
WAIT_TIME = 30  # Tiempo de espera en segundos para reintentos


def is_rate_limit_error(e):
    message = str(e).lower()
    return "429" in message or "rate limit" in message or "too many requests" in message


def download(bot, query, user_auth=False):
    retries = 0
    message_id = None

    output = get_output_pattern(query)
    command = [
        "spotdl",
        "download",
        query,
        "--output",
        f"{DOWNLOAD_DIR}/{output}",
        "--client-id",
        SPOTIFY_CLIENT_ID,
        "--client-secret",
        SPOTIFY_CLIENT_SECRET,
        "--cache-path",
        f"{CACHE_DIR}/spotify_token.json",
    ]
    if user_auth:
        command.append("--user-auth")
        token = load_token()
        if not token:
            send_message(bot, message=get_text("error_token_required"))
            return

    while retries < MAX_RETRIES:
        try:
            logger.info(f"Running command: {' '.join(command)}")
            msg = send_message(bot, message=get_text("download_in_progress"))
            message_id = msg.message_id

            subprocess.run(
                command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            delete_message(bot, message_id=message_id)
            send_message(bot, message=get_text("download_finished"))
            return "success"

        except Exception as e:
            if is_rate_limit_error(e):
                retries += 1
                logger.warning(
                    f"⚠️ Rate limit detected. Retrying in {WAIT_TIME}s... (Attempt {retries}/{MAX_RETRIES})"
                )
                time.sleep(WAIT_TIME)
                continue

            logger.error(f"❌ Download error: {str(e)}")
            if message_id:
                delete_message(bot, message_id=message_id)
            send_message(bot, message=get_text("error_download_failed"))
            return "error"

    if message_id:
        delete_message(bot, message_id=message_id)
    send_message(bot, message=get_text("error_rate_limited"))
    logger.error("❌ Max retries reached. Please try again later.")
    return "rate_limited"
