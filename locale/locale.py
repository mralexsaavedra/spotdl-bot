import sys
from core.logger import setup_logger
import os
import json

LANGUAGE = os.environ.get("LANGUAGE")

logger = setup_logger(__name__)

if LANGUAGE.lower() not in ("es", "en"):
	logger.error("LANGUAGE only can be ES/EN")
	sys.exit(1)

def load_locale(locale):
	with open(f"/app/locale/{locale}.json", "r", encoding="utf-8") as file:
		return json.load(file)

def get_text(key, *args):
	messages = load_locale(LANGUAGE.lower())
	if key in messages:
		translated_text = messages[key]
	else:
		messages_es = load_locale("es")
		if key in messages_es:
			logger.warning(f"key ['{key}'] is not in locale {LANGUAGE}")
			translated_text = messages_es[key]
		else:
			logger.error(f"key ['{key}'] is not in locale {LANGUAGE} or EN")
			return f"key ['{key}'] is not in locale {LANGUAGE} or EN"

	for i, arg in enumerate(args, start=1):
		placeholder = f"${i}"
		translated_text = translated_text.replace(placeholder, str(arg))

	return translated_text