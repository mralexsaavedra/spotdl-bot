import logging
import sys
import os
from datetime import datetime


def setup_logger(name=None):
    """
    Configura y devuelve un logger con salida a consola y archivo.

    Usa DEBUG si está en modo desarrollo, INFO en producción.

    Variables de entorno:
      - LOG_LEVEL: Nivel de log (opcional)
      - LOG_DIR: Carpeta donde guardar el archivo de logs (opcional)
    """

    logger = logging.getLogger(name)
    if logger.hasHandlers():
        return logger  # Evita añadir múltiples handlers

    # Nivel de log desde entorno o predeterminado
    log_level_str = os.getenv("LOG_LEVEL", "DEBUG").upper()
    log_level = getattr(logging, log_level_str, logging.DEBUG)
    logger.setLevel(log_level)

    # Formato de los mensajes
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(log_format, datefmt=date_format)

    # Handler de consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler de archivo
    log_dir = os.getenv("LOG_DIR", "./logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(
        log_dir, f"{name or 'app'}_{datetime.now().date()}.log"
    )
    file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.propagate = False

    return logger
