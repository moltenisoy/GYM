"""
Configuración centralizada de logging para el sistema GYM.
Proporciona logging estructurado con rotación de archivos y salida a consola.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional
from shared.constants import (
    LOG_FORMAT,
    LOG_DATE_FORMAT,
    LOG_FILE_MAX_BYTES,
    LOG_FILE_BACKUP_COUNT,
    LOG_DIR_NAME
)


def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: int = logging.INFO,
    console_output: bool = True
) -> logging.Logger:
    """
    Configura un logger con rotación de archivos y salida opcional a consola.

    Args:
        name: Nombre del logger (usualmente nombre del módulo)
        log_file: Nombre opcional del archivo de log (sin ruta). Si es None, usa {name}.log
        level: Nivel de logging (por defecto: INFO)
        console_output: Si también debe mostrar salida en consola (por defecto: True)

    Returns:
        Instancia de logger configurada

    Ejemplo:
        >>> logger = setup_logger(__name__)
        >>> logger.info("Aplicación iniciada")
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger

    log_dir = os.path.join(os.path.dirname(__file__), '..', LOG_DIR_NAME)
    os.makedirs(log_dir, exist_ok=True)

    if log_file is None:
        log_file = f"{name}.log"
    log_path = os.path.join(log_dir, log_file)

    formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=LOG_FILE_MAX_BYTES,
        backupCount=LOG_FILE_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger existente por nombre, o crea uno nuevo si no existe.

    Args:
        name: Nombre del logger

    Returns:
        Instancia de logger

    Ejemplo:
        >>> logger = get_logger(__name__)
        >>> logger.debug("Mensaje de depuración")
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger
