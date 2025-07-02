import logging
import sys

def setup_logger(name=None, level=logging.DEBUG):
	logger = logging.getLogger(name)
	logger.setLevel(level)

	# Formato bonito para consola
	formatter = logging.Formatter(
		'%(asctime)s - %(name)s - %(levelname)s - %(message)s'
	)

	# Handler para consola
	console_handler = logging.StreamHandler(sys.stdout)
	console_handler.setFormatter(formatter)

	# Evitar añadir múltiples handlers si ya existe
	if not logger.hasHandlers():
		logger.addHandler(console_handler)

	return logger
