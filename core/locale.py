import sys
import os
import json
from typing import Dict, Any
from config.config import LANGUAGE, LOCALE_DIR
from core.logger import setup_logger

logger = setup_logger(__name__)

SUPPORTED_LANGUAGES = ("es", "en")
DEFAULT_LANGUAGE = "es"
_language = (LANGUAGE or DEFAULT_LANGUAGE).lower()

if _language not in SUPPORTED_LANGUAGES:
    logger.error(
        f"LANGUAGE must be one of {SUPPORTED_LANGUAGES}, but got '{_language}'"
    )
    sys.exit(1)

_locale_cache: Dict[str, Dict[str, Any]] = {}


def load_locale(locale: str) -> Dict[str, Any]:
    """
    Load the locale JSON file for the given locale code.

    Args:
        locale (str): Language code, e.g. 'en', 'es'.

    Returns:
        dict: Dictionary of key-text pairs from locale file.
    """
    path = os.path.join(LOCALE_DIR, f"{locale}.json")
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
            logger.debug(f"Locale '{locale}' loaded successfully from {path}")
            return data
    except FileNotFoundError:
        logger.error(f"Locale file not found: {path}")
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON in locale file {path}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error loading locale '{locale}': {e}")
    return {}


def get_locale(locale: str) -> Dict[str, Any]:
    """
    Get the locale dictionary, loading it if needed.

    Args:
        locale (str): Language code.

    Returns:
        dict: Locale dictionary.
    """
    if locale not in _locale_cache:
        _locale_cache[locale] = load_locale(locale)
    return _locale_cache[locale]


def get_text(key: str, *args, **kwargs) -> str:
    """
    Retrieve the localized text for the given key, formatting with args or kwargs.

    Args:
        key (str): The key to look up in locale.
        *args: Positional format arguments, replacing $1, $2, etc.
        **kwargs: Named format arguments, replacing ${name}.

    Returns:
        str: The localized and formatted string.
    """
    messages = get_locale(_language)
    text = messages.get(key)

    if text is None:
        fallback = get_locale(DEFAULT_LANGUAGE)
        text = fallback.get(key)
        if text:
            logger.warning(
                f"Key '{key}' not found in locale '{_language}', using fallback '{DEFAULT_LANGUAGE}'."
            )
        else:
            error_msg = f"Key '{key}' missing in both '{_language}' and fallback '{DEFAULT_LANGUAGE}' locales."
            logger.error(error_msg)
            return error_msg

    # Replace positional placeholders ($1, $2, ...) with args
    for i, arg in enumerate(args, start=1):
        placeholder = f"${i}"
        text = text.replace(placeholder, str(arg))

    # Replace named placeholders (${name}) with kwargs
    for k, v in kwargs.items():
        placeholder = f"${{{k}}}"
        text = text.replace(placeholder, str(v))

    return text
