# hija_comms.py
#
# Módulo de Comunicaciones de la Aplicación Hija.
# Encapsula toda la lógica de red usando la biblioteca 'requests'.
# Incluye gestión de credenciales persistentes y validación de sincronización.

import requests
import json
import os
import hashlib
import time
import random
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from config.settings import get_hija_settings
from shared.logger import setup_logger
from shared.constants import (
    ENDPOINT_AUTORIZAR,
    ENDPOINT_SINCRONIZAR_DATOS,
    STATUS_APPROVED,
    STATUS_SYNC_SUCCESS,
    ERROR_CONNECTION,
    ERROR_TIMEOUT,
    CREDENTIALS_FILENAME
)

# Initialize logger
logger = setup_logger(__name__, log_file="hija_comms.log")

# Load configuration
settings = get_hija_settings()

# Directorio para datos locales
if os.path.isabs(settings.LOCAL_DATA_DIR):
    LOCAL_DATA_DIR = settings.LOCAL_DATA_DIR
else:
    LOCAL_DATA_DIR = os.path.join(os.path.dirname(__file__), settings.LOCAL_DATA_DIR)
CREDENTIALS_FILE = os.path.join(LOCAL_DATA_DIR, CREDENTIALS_FILENAME)

logger.info(f"Communication module initialized - Madre URL: {settings.MADRE_BASE_URL}")


class APICommunicator:
    """
    Gestiona todas las peticiones HTTP a la API de la Aplicación Madre.
    Incluye retry logic con exponential backoff y timeouts configurables.
    """

    def __init__(self, base_url: Optional[str] = None):
        """
        Inicializa el comunicador API.

        Args:
            base_url: URL base del servidor Madre (default: from settings)
        """
        self.base_url = base_url or settings.MADRE_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        os.makedirs(LOCAL_DATA_DIR, exist_ok=True)
        logger.info(f"APICommunicator initialized with base_url: {self.base_url}")

    def _retry_request(
        self,
        method: str,
        url: str,
        max_retries: int = 3,
        timeout: int = None,
        **kwargs
    ) -> requests.Response:
        """
        Realiza una petición HTTP con retry logic y exponential backoff.

        Args:
            method: Método HTTP ('GET', 'POST', etc.)
            url: URL completa de la petición
            max_retries: Número máximo de reintentos (default: 3)
            timeout: Timeout en segundos (default: from settings)
            **kwargs: Argumentos adicionales para requests

        Returns:
            requests.Response: Respuesta de la petición

        Raises:
            requests.exceptions.RequestException: Si todos los reintentos fallan
        """
        if timeout is None:
            timeout = settings.HTTP_TIMEOUT_MEDIUM

        last_exception = None

        for attempt in range(max_retries):
            try:
                logger.debug(f"Request attempt {attempt + 1}/{max_retries}: {method} {url}")

                if method.upper() == 'GET':
                    response = self.session.get(url, timeout=timeout, **kwargs)
                elif method.upper() == 'POST':
                    response = self.session.post(url, timeout=timeout, **kwargs)
                elif method.upper() == 'DELETE':
                    response = self.session.delete(url, timeout=timeout, **kwargs)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                response.raise_for_status()
                logger.debug(f"Request successful: {method} {url}")
                return response

            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                last_exception = e
                if attempt < max_retries - 1:
                    # Exponential backoff with jitter (random 0-1 second)
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}/{max_retries}): {e}. "
                        f"Retrying in {wait_time:.2f}s..."
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Request failed after {max_retries} attempts: {e}")
                    raise

            except requests.exceptions.HTTPError as e:
                # Don't retry on HTTP errors (4xx, 5xx)
                logger.error(f"HTTP error: {e}")
                raise

        # Should not reach here, but just in case
        raise last_exception

    def save_credentials(self, username: str, password: str) -> bool:
        """Guarda las credenciales localmente (cifradas básicamente)."""
        try:
            # Simple ofuscación (en producción usar keyring o similar)
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            data = {
                "username": username,
                "password_hash": password_hash,
                "last_login": datetime.now().isoformat()
            }
            with open(CREDENTIALS_FILE, 'w') as f:
                json.dump(data, f)
            return True
        except Exception as e:
            print(f"Error guardando credenciales: {e}")
            return False

    def load_credentials(self) -> Optional[Dict[str, str]]:
        """Carga las credenciales guardadas."""
        try:
            if os.path.exists(CREDENTIALS_FILE):
                with open(CREDENTIALS_FILE, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"Error cargando credenciales: {e}")
            return None

    def clear_credentials(self) -> bool:
        """Elimina las credenciales guardadas."""
        try:
            if os.path.exists(CREDENTIALS_FILE):
                os.remove(CREDENTIALS_FILE)
            return True
        except Exception as e:
            print(f"Error eliminando credenciales: {e}")
            return False

    def verify_stored_password(self, password: str) -> bool:
        """Verifica si una contraseña coincide con la guardada."""
        creds = self.load_credentials()
        if not creds:
            return False
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return password_hash == creds.get('password_hash')

    def attempt_login(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Intenta autenticar al usuario contra el endpoint /autorizar con contraseña.
        Incluye retry logic con exponential backoff.

        Args:
            username: Nombre de usuario
            password: Contraseña del usuario

        Returns:
            Tuple[bool, str]: (éxito, mensaje_o_datos)

        Example:
            >>> success, data = communicator.attempt_login("user1", "pass123")
            >>> if success:
            ...     print(f"Login exitoso: {data['nombre_completo']}")
        """
        url = f"{self.base_url}{ENDPOINT_AUTORIZAR}"
        payload = {"username": username, "password": password}

        logger.info(f"Attempting login for user: {username}")

        try:
            response = self._retry_request(
                'POST',
                url,
                json=payload,
                timeout=settings.HTTP_TIMEOUT_SHORT,
                max_retries=2  # Only 2 retries for login
            )

            data = response.json()
            if data.get("status") == STATUS_APPROVED:
                # Guardar credenciales localmente
                self.save_credentials(username, password)
                logger.info(f"Login successful for user: {username}")
                return True, data
            else:
                logger.warning(f"Unexpected API response for user: {username}")
                return False, "Respuesta de API desconocida."

        except requests.exceptions.HTTPError as e:
            try:
                error_detail = e.response.json().get("detail", "Error de servidor")
                logger.error(f"Login HTTP error for {username}: {error_detail}")
                return False, f"Error: {error_detail}"
            except json.JSONDecodeError:
                logger.error(f"Login HTTP error for {username}: {e.response.status_code}")
                return False, f"Error HTTP {e.response.status_code}"

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error during login for {username}: {e}")
            return False, ERROR_CONNECTION

        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout during login for {username}: {e}")
            return False, ERROR_TIMEOUT

        except Exception as e:
            logger.error(f"Unexpected error during login for {username}: {e}", exc_info=True)
            return False, f"Un error inesperado ha ocurrido: {e}"

    def validate_sync_status(self, username: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Valida si el usuario necesita sincronizar (72 horas).
        Retorna (bool_ok, datos_validacion)
        """
        url = f"{self.base_url}/validar_sync"
        params = {"usuario": username}

        try:
            response = self.session.get(url, params=params, timeout=5)
            response.raise_for_status()

            data = response.json()
            bloqueado = data.get("bloqueado", False)

            if bloqueado:
                return False, data
            else:
                return True, data

        except requests.exceptions.HTTPError as e:
            try:
                error_detail = e.response.json().get("detail", "Error de servidor")
                return False, {"error": error_detail}
            except json.JSONDecodeError:
                return False, {"error": f"Error HTTP {e.response.status_code}"}

        except requests.exceptions.ConnectionError:
            return False, {"error": "Error de conexión"}

        except Exception as e:
            return False, {"error": f"Error: {e}"}

    def fetch_sync_data(self, username: str) -> Tuple[bool, dict]:
        """
        Obtiene los datos de sincronización completos del endpoint /sincronizar_datos.
        Incluye retry logic con exponential backoff para mayor robustez.

        Args:
            username: Nombre de usuario solicitante

        Returns:
            Tuple[bool, dict]: (éxito, datos_o_error_msg)

        Example:
            >>> success, data = communicator.fetch_sync_data("user1")
            >>> if success:
            ...     schedule = data['training_schedule']
        """
        url = f"{self.base_url}{ENDPOINT_SINCRONIZAR_DATOS}"
        params = {"usuario": username}

        logger.info(f"Fetching sync data for user: {username}")

        try:
            response = self._retry_request(
                'GET',
                url,
                params=params,
                timeout=settings.HTTP_TIMEOUT_LONG,
                max_retries=3
            )

            data = response.json()
            if data.get("status") == STATUS_SYNC_SUCCESS:
                logger.info(f"Sync data fetched successfully for user: {username}")
                return True, data
            else:
                logger.warning(f"Invalid sync response for user: {username}")
                return False, {"error": "Respuesta de sincronización inválida."}

        except requests.exceptions.HTTPError as e:
            try:
                error_detail = e.response.json().get("detail", "Error de servidor")
                logger.error(f"Sync HTTP error for {username}: {error_detail}")
                return False, {"error": f"Error: {error_detail}"}
            except json.JSONDecodeError:
                logger.error(f"Sync HTTP error for {username}: {e.response.status_code}")
                return False, {"error": f"Error HTTP {e.response.status_code}"}

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error during sync for {username}: {e}")
            return False, {"error": ERROR_CONNECTION}

        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout during sync for {username}: {e}")
            return False, {"error": ERROR_TIMEOUT}

        except Exception as e:
            logger.error(f"Unexpected error during sync for {username}: {e}", exc_info=True)
            return False, {"error": f"Error inesperado: {e}"}

    # ============================================================================
    # FUNCIONES DE MENSAJERÍA
    # ============================================================================

    def send_message(self, to_user: str, subject: str, body: str,
                     parent_message_id: Optional[int] = None) -> Tuple[bool, dict]:
        """Envía un mensaje."""
        url = f"{self.base_url}/enviar_mensaje"

        # Obtener username actual de credenciales
        creds = self.load_credentials()
        from_user = creds.get('username', 'unknown') if creds else 'unknown'

        payload = {
            "from_user": from_user,
            "to_user": to_user,
            "subject": subject,
            "body": body,
            "parent_message_id": parent_message_id
        }

        try:
            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()

            data = response.json()
            return True, data

        except requests.exceptions.HTTPError as e:
            try:
                error_detail = e.response.json().get("detail", "Error de servidor")
                return False, {"error": f"Error: {error_detail}"}
            except json.JSONDecodeError:
                return False, {"error": f"Error HTTP {e.response.status_code}"}

        except requests.exceptions.ConnectionError:
            return False, {"error": "Error de conexión"}

        except Exception as e:
            return False, {"error": f"Error: {e}"}

    def get_messages(self, solo_no_leidos: bool = False) -> Tuple[bool, dict]:
        """Obtiene los mensajes del usuario."""
        url = f"{self.base_url}/obtener_mensajes"

        # Obtener username actual de credenciales
        creds = self.load_credentials()
        username = creds.get('username', '') if creds else ''

        if not username:
            return False, {"error": "Usuario no identificado"}

        params = {
            "usuario": username,
            "solo_no_leidos": solo_no_leidos
        }

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            return True, data

        except requests.exceptions.HTTPError as e:
            try:
                error_detail = e.response.json().get("detail", "Error de servidor")
                return False, {"error": f"Error: {error_detail}"}
            except json.JSONDecodeError:
                return False, {"error": f"Error HTTP {e.response.status_code}"}

        except requests.exceptions.ConnectionError:
            return False, {"error": "Error de conexión"}

        except Exception as e:
            return False, {"error": f"Error: {e}"}

    def mark_message_read(self, message_id: int) -> Tuple[bool, dict]:
        """Marca un mensaje como leído."""
        url = f"{self.base_url}/marcar_leido/{message_id}"

        try:
            response = self.session.post(url, timeout=5)
            response.raise_for_status()

            data = response.json()
            return True, data

        except Exception as e:
            return False, {"error": f"Error: {e}"}

    def count_unread_messages(self) -> Tuple[bool, int]:
        """Cuenta los mensajes no leídos."""
        url = f"{self.base_url}/contar_no_leidos"

        # Obtener username actual de credenciales
        creds = self.load_credentials()
        username = creds.get('username', '') if creds else ''

        if not username:
            return False, 0

        params = {"usuario": username}

        try:
            response = self.session.get(url, params=params, timeout=5)
            response.raise_for_status()

            data = response.json()
            return True, data.get('mensajes_no_leidos', 0)

        except Exception:
            return False, 0

    # ============================================================================
    # FUNCIONES DE CHAT EN VIVO
    # ============================================================================

    def send_chat_message(self, to_user: str, message: str) -> Tuple[bool, dict]:
        """Envía un mensaje de chat en vivo."""
        url = f"{self.base_url}/enviar_chat"

        # Obtener username actual de credenciales
        creds = self.load_credentials()
        from_user = creds.get('username', 'unknown') if creds else 'unknown'

        payload = {
            "from_user": from_user,
            "to_user": to_user,
            "message": message
        }

        try:
            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()

            data = response.json()
            return True, data

        except Exception as e:
            return False, {"error": f"Error: {e}"}

    def get_chat_history(self, other_user: str, limit: int = 50) -> Tuple[bool, dict]:
        """Obtiene el historial de chat con otro usuario."""
        url = f"{self.base_url}/obtener_chat"

        # Obtener username actual de credenciales
        creds = self.load_credentials()
        username = creds.get('username', '') if creds else ''

        if not username:
            return False, {"error": "Usuario no identificado"}

        params = {
            "user1": username,
            "user2": other_user,
            "limit": limit
        }

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            return True, data

        except Exception as e:
            return False, {"error": f"Error: {e}"}
