import sys
import os
import json
from config.config import LANGUAGE, LOCALE_DIR
from core.logger import setup_logger

logger = setup_logger(__name__)

SUPPORTED_LANGUAGES = ("es", "en")
DEFAULT_LANGUAGE = "es"
_language = LANGUAGE.lower()

if _language not in SUPPORTED_LANGUAGES:
    logger.error("LANGUAGE must be 'es' or 'en'")
    sys.exit(1)

# Locale cache
_locale_cache = {}


def load_locale(locale):
    path = os.path.join(LOCALE_DIR, f"{locale}.json")
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error(f"Locale file not found: {path}")
        return {}


def get_locale(locale):
    if locale not in _locale_cache:
        _locale_cache[locale] = load_locale(locale)
    return _locale_cache[locale]


def get_text(key, *args):
    messages = get_locale(_language)

    if key in messages:
        text = messages[key]
    else:
        fallback = get_locale(DEFAULT_LANGUAGE)
        if key in fallback:
            logger.warning(
                f"Key '{key}' not found in locale '{_language}', using fallback '{DEFAULT_LANGUAGE}'."
            )
            text = fallback[key]
        else:
            error_msg = f"Key '{key}' missing in both '{_language}' and fallback '{DEFAULT_LANGUAGE}' locales."
            logger.error(error_msg)
            return error_msg

    for i, arg in enumerate(args, start=1):
        text = text.replace(f"${i}", str(arg))

    return text
