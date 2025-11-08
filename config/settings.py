"""
Cargador de configuración de ajustes para el sistema GYM.
Carga configuraciones desde variables de entorno con valores por defecto como respaldo.
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
    Obtiene variable de entorno con conversión de tipo y valor por defecto.

    Args:
        key: Nombre de la variable de entorno
        default: Valor por defecto si no se encuentra
        cast_type: Tipo al que convertir el valor (int, bool, str, etc.)

    Returns:
        Valor de la variable de entorno convertido al tipo especificado, o el valor por defecto

    Ejemplo:
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
    """Configuración de ajustes para la aplicación Madre (servidor)."""

    def __init__(self):
        self.HOST: str = get_env('MADRE_HOST', DEFAULT_HOST_IP)
        self.PORT: int = get_env('MADRE_PORT', DEFAULT_HOST_PORT, int)
        self.DB_PATH: str = get_env('DB_PATH', os.path.join(LOCAL_DATA_DIR_NAME, DEFAULT_DB_FILENAME))
        self.LOG_LEVEL: str = get_env('LOG_LEVEL', 'INFO').upper()

    def __repr__(self) -> str:
        return f"MadreSettings(HOST={self.HOST}, PORT={self.PORT}, DB_PATH={self.DB_PATH})"


class HijaSettings:
    """Configuración de ajustes para la aplicación Hija (cliente)."""

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


# Instancias singleton
_madre_settings: Optional[MadreSettings] = None
_hija_settings: Optional[HijaSettings] = None


def get_madre_settings() -> MadreSettings:
    """
    Obtiene la instancia singleton de configuración Madre.

    Returns:
        Instancia de MadreSettings

    Ejemplo:
        >>> settings = get_madre_settings()
        >>> print(settings.HOST, settings.PORT)
    """
    global _madre_settings
    if _madre_settings is None:
        _madre_settings = MadreSettings()
    return _madre_settings


def get_hija_settings() -> HijaSettings:
    """
    Obtiene la instancia singleton de configuración Hija.

    Returns:
        Instancia de HijaSettings

    Ejemplo:
        >>> settings = get_hija_settings()
        >>> print(settings.MADRE_BASE_URL)
    """
    global _hija_settings
    if _hija_settings is None:
        _hija_settings = HijaSettings()
    return _hija_settings


def load_env_file(env_path: str = '.env') -> bool:
    """
    Carga variables de entorno desde un archivo .env.

    Args:
        env_path: Ruta al archivo .env (por defecto: .env en directorio actual)

    Returns:
        True si el archivo se cargó exitosamente, False en caso contrario

    Ejemplo:
        >>> load_env_file('config/.env')
    """
    if not os.path.exists(env_path):
        return False

    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Saltar comentarios y líneas vacías
                if not line or line.startswith('#'):
                    continue

                # Parsear KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    # Remover comillas si están presentes
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    # Solo configurar si no está ya en el entorno
                    if key not in os.environ:
                        os.environ[key] = value

        return True
    except Exception as e:
        print(f"Error cargando archivo .env: {e}")
        return False


# Intentar cargar archivo .env al importar el módulo
load_env_file('.env')
load_env_file('config/.env')
