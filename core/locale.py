from config.settings import LANGUAGE
from core.logger import setup_logger
import json

logger = setup_logger(__name__)

def load_locale(locale):
	with open(f"/app/locale/{locale}.json", "r", encoding="utf-8") as file:
		return json.load(file)

def get_text(key, *args):
	messages = load_locale(LANGUAGE.lower())
	if key in messages:
		translated_text = messages[key]
	else:
		messages_en = load_locale("en")
		if key in messages_en:
			logger.warning(f"key ['{key}'] is not in locale {LANGUAGE}")
			translated_text = messages_en[key]
		else:
			logger.error(f"key ['{key}'] is not in locale {LANGUAGE} or EN")
			return f"key ['{key}'] is not in locale {LANGUAGE} or EN"

	for i, arg in enumerate(args, start=1):
		placeholder = f"${i}"
		translated_text = translated_text.replace(placeholder, str(arg))

	return translated_text