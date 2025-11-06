"""
Centralized logging configuration for the GYM system.
Provides structured logging with file rotation and console output.
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
    Set up a logger with file rotation and optional console output.

    Args:
        name: Name of the logger (usually module name)
        log_file: Optional log file name (without path). If None, uses {name}.log
        level: Logging level (default: INFO)
        console_output: Whether to also output to console (default: True)

    Returns:
        Configured logger instance

    Example:
        >>> logger = setup_logger(__name__)
        >>> logger.info("Application started")
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(__file__), '..', LOG_DIR_NAME)
    os.makedirs(log_dir, exist_ok=True)

    # Determine log file path
    if log_file is None:
        log_file = f"{name}.log"
    log_path = os.path.join(log_dir, log_file)

    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=LOG_FILE_MAX_BYTES,
        backupCount=LOG_FILE_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler (optional)
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get an existing logger by name, or create a new one if it doesn't exist.

    Args:
        name: Name of the logger

    Returns:
        Logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.debug("Debug message")
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger
