"""
Configuration settings loader for the GYM system.
Loads settings from environment variables with fallback to defaults.
"""

import os
from typing import Any, Optional
from shared.constants import (
    DEFAULT_HOST_IP,
    DEFAULT_HOST_PORT,
    DEFAULT_MADRE_BASE_URL,
    DEFAULT_DB_FILENAME,
    HTTP_TIMEOUT_SHORT,
    HTTP_TIMEOUT_MEDIUM,
    HTTP_TIMEOUT_LONG,
    SYNC_INTERVAL_INITIAL,
    SYNC_INTERVAL_NORMAL,
    SYNC_REQUIRED_HOURS,
    LOCAL_DATA_DIR_NAME,
    HIJA_LOCAL_DIR_NAME
)


def get_env(key: str, default: Any = None, cast_type: type = str) -> Any:
    """
    Get environment variable with type casting and default value.

    Args:
        key: Environment variable name
        default: Default value if not found
        cast_type: Type to cast the value to (int, bool, str, etc.)

    Returns:
        Environment variable value cast to the specified type, or default

    Example:
        >>> port = get_env('MADRE_PORT', 8000, int)
        >>> debug = get_env('DEBUG', False, bool)
    """
    value = os.getenv(key)

    if value is None:
        return default

    if cast_type == bool:
        return value.lower() in ('true', '1', 'yes', 'on')

    try:
        return cast_type(value)
    except (ValueError, TypeError):
        return default


class MadreSettings:
    """Configuration settings for Madre (server) application."""

    def __init__(self):
        self.HOST: str = get_env('MADRE_HOST', DEFAULT_HOST_IP)
        self.PORT: int = get_env('MADRE_PORT', DEFAULT_HOST_PORT, int)
        self.DB_PATH: str = get_env('DB_PATH', os.path.join(LOCAL_DATA_DIR_NAME, DEFAULT_DB_FILENAME))
        self.LOG_LEVEL: str = get_env('LOG_LEVEL', 'INFO').upper()

    def __repr__(self) -> str:
        return f"MadreSettings(HOST={self.HOST}, PORT={self.PORT}, DB_PATH={self.DB_PATH})"


class HijaSettings:
    """Configuration settings for Hija (client) application."""

    def __init__(self):
        self.MADRE_BASE_URL: str = get_env('MADRE_BASE_URL', DEFAULT_MADRE_BASE_URL)
        self.HTTP_TIMEOUT_SHORT: int = get_env('HTTP_TIMEOUT_SHORT', HTTP_TIMEOUT_SHORT, int)
        self.HTTP_TIMEOUT_MEDIUM: int = get_env('HTTP_TIMEOUT_MEDIUM', HTTP_TIMEOUT_MEDIUM, int)
        self.HTTP_TIMEOUT_LONG: int = get_env('HTTP_TIMEOUT_LONG', HTTP_TIMEOUT_LONG, int)
        self.SYNC_INTERVAL_INITIAL: int = get_env('SYNC_INTERVAL_INITIAL', SYNC_INTERVAL_INITIAL, int)
        self.SYNC_INTERVAL_NORMAL: int = get_env('SYNC_INTERVAL_NORMAL', SYNC_INTERVAL_NORMAL, int)
        self.SYNC_REQUIRED_HOURS: int = get_env('SYNC_REQUIRED_HOURS', SYNC_REQUIRED_HOURS, int)
        self.LOCAL_DATA_DIR: str = get_env('LOCAL_DATA_DIR', os.path.join(LOCAL_DATA_DIR_NAME, HIJA_LOCAL_DIR_NAME))
        self.LOG_LEVEL: str = get_env('LOG_LEVEL', 'INFO').upper()

    def __repr__(self) -> str:
        return f"HijaSettings(MADRE_BASE_URL={self.MADRE_BASE_URL}, LOG_LEVEL={self.LOG_LEVEL})"


# Singleton instances
_madre_settings: Optional[MadreSettings] = None
_hija_settings: Optional[HijaSettings] = None


def get_madre_settings() -> MadreSettings:
    """
    Get Madre settings singleton instance.

    Returns:
        MadreSettings instance

    Example:
        >>> settings = get_madre_settings()
        >>> print(settings.HOST, settings.PORT)
    """
    global _madre_settings
    if _madre_settings is None:
        _madre_settings = MadreSettings()
    return _madre_settings


def get_hija_settings() -> HijaSettings:
    """
    Get Hija settings singleton instance.

    Returns:
        HijaSettings instance

    Example:
        >>> settings = get_hija_settings()
        >>> print(settings.MADRE_BASE_URL)
    """
    global _hija_settings
    if _hija_settings is None:
        _hija_settings = HijaSettings()
    return _hija_settings


def load_env_file(env_path: str = '.env') -> bool:
    """
    Load environment variables from a .env file.

    Args:
        env_path: Path to .env file (default: .env in current directory)

    Returns:
        True if file was loaded successfully, False otherwise

    Example:
        >>> load_env_file('config/.env')
    """
    if not os.path.exists(env_path):
        return False

    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue

                # Parse KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    # Only set if not already in environment
                    if key not in os.environ:
                        os.environ[key] = value

        return True
    except Exception as e:
        print(f"Error loading .env file: {e}")
        return False


# Attempt to load .env file on module import
load_env_file('.env')
load_env_file('config/.env')
