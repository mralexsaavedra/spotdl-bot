import re
import telebot
from config.config import CALL_PATTERNS, TELEGRAM_GROUP
from loguru import logger


def is_spotify_url(url: str) -> bool:
    """
    Check if the given URL is a valid Spotify link.

    Args:
        url (str): The URL to validate.

    Returns:
        bool: True if it's a Spotify URL, False otherwise.
    """
    pattern = r"^https:\/\/open\.spotify\.com\/(?:intl-[a-z]{2}\/)?(track|album|playlist|artist)\/[a-zA-Z0-9]+(?:\?.*)?$"
    return bool(re.match(pattern, url))


def send_message(
    bot: telebot.TeleBot,
    chat_id: int = TELEGRAM_GROUP,
    message: str | None = None,
    reply_markup=None,
    parse_mode: str = "markdown",
    disable_web_page_preview: bool = True,
) -> object | None:
    """
    Sends a message to a Telegram chat.

    Args:
        bot (telebot.TeleBot): The bot instance.
        chat_id (int): The chat ID to send the message to.
        message (str | None): The message content.
        reply_markup: Optional reply markup.
        parse_mode (str): Text parse mode.
        disable_web_page_preview (bool): Disable link previews.

    Returns:
        The sent message object or None.
    """
    if not message:
        return None

    try:
        return bot.send_message(
            chat_id,
            message,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            disable_web_page_preview=disable_web_page_preview,
        )
    except Exception as e:
        logger.error(f"Error sending message to {chat_id}: {e}")
        raise


def delete_message(bot: telebot.TeleBot, message_id: int) -> None:
    """
    Deletes a message in a Telegram chat.

    Args:
        bot (telebot.TeleBot): The bot instance.
        message_id (int): The ID of the message to delete.
    """
    try:
        bot.delete_message(TELEGRAM_GROUP, message_id)
    except Exception as e:
        logger.warning(f"Failed to delete message {message_id}: {e}")


def parse_call_data(call_data):
    parts = call_data.split("|")
    comando = parts[0]
    args = parts[1:]

    if comando not in CALL_PATTERNS:
        raise ValueError(f"COMMAND NOT IN PATTERN: {comando}")

    expected_keys = CALL_PATTERNS[comando]

    if len(args) != len(expected_keys):
        raise ValueError(
            f"INCORRECT LENGTH CALLBACK DATA FOR '{comando}': IT WAS EXPECTED {len(expected_keys)}"
        )

    parsed = {"comando": comando}
    parsed.update(dict(zip(expected_keys, args)))
    return parsed
