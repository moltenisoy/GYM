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
