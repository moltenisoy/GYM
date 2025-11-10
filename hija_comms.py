
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

logger = setup_logger(__name__, log_file="hija_comms.log")

settings = get_hija_settings()

if os.path.isabs(settings.LOCAL_DATA_DIR):
    LOCAL_DATA_DIR = settings.LOCAL_DATA_DIR
else:
    LOCAL_DATA_DIR = os.path.join(os.path.dirname(__file__), settings.LOCAL_DATA_DIR)
CREDENTIALS_FILE = os.path.join(LOCAL_DATA_DIR, CREDENTIALS_FILENAME)

logger.info("Communication module initialized - Madre URL: %s", settings.MADRE_BASE_URL)


class APICommunicator:
    """
    Gestiona todas las peticiones HTTP a la API del Sistema de Gestión del Gimnasio.
    Incluye retry logic con exponential backoff, timeouts configurables,
    detección de conexión, y manejo robusto de errores de red.
    """

    def __init__(self, base_url: Optional[str] = None):
        """
        Inicializa el comunicador API con características mejoradas de resiliencia.

        Args:
            base_url: URL base del servidor Madre (default: from settings)
        """
        self.base_url = base_url or settings.MADRE_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

        self.is_connected = False
        self.last_successful_request = None
        self.consecutive_failures = 0

        os.makedirs(LOCAL_DATA_DIR, exist_ok=True)
        logger.info("APICommunicator initialized with base_url: %s", self.base_url)

        self._check_connectivity()

    def _check_connectivity(self) -> bool:
        """
        Verifica la conectividad con el servidor madre.
        Intenta alcanzar el endpoint de health para validar conexión.

        Returns:
            bool: True si hay conectividad, False en caso contrario
        """
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=settings.HTTP_TIMEOUT_SHORT
            )
            if response.status_code == 200:
                self.is_connected = True
                self.consecutive_failures = 0
                logger.info("Conectividad con servidor madre: OK")
                return True
        except Exception as e:
            self.is_connected = False
            logger.warning("No se pudo establecer conexión con servidor madre: %s", e)

        return False

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
                logger.debug("Request attempt %d/%d: %s %s", attempt + 1, max_retries, method, url)

                if method.upper() == 'GET':
                    response = self.session.get(url, timeout=timeout, **kwargs)
                elif method.upper() == 'POST':
                    response = self.session.post(url, timeout=timeout, **kwargs)
                elif method.upper() == 'DELETE':
                    response = self.session.delete(url, timeout=timeout, **kwargs)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                response.raise_for_status()
                logger.debug("Request successful: %s %s", method, url)

                self.is_connected = True
                self.last_successful_request = datetime.now()
                self.consecutive_failures = 0

                return response

            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                last_exception = e
                self.consecutive_failures += 1
                self.is_connected = False

                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(
                        "Request failed (attempt %d/%d): %s. Retrying in %.2fs...",
                        attempt + 1, max_retries, e, wait_time
                    )
                    time.sleep(wait_time)

                    if self.consecutive_failures >= 2:
                        logger.info("Intentando reestablecer conexión...")
                        self._check_connectivity()
                else:
                    logger.error("Request failed after %d attempts: %s", max_retries, e)
                    raise

            except requests.exceptions.HTTPError as e:
                logger.error("HTTP error: %s", e)

                if e.response.status_code >= 500 and attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(
                        "Server error %d, retrying in %.2fs...",
                        e.response.status_code, wait_time
                    )
                    time.sleep(wait_time)
                    continue

                raise

        raise last_exception

    def get_connection_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado actual de la conexión con el servidor.

        Returns:
            Dict con información del estado de conexión
        """
        return {
            'connected': self.is_connected,
            'last_successful_request': self.last_successful_request.isoformat() if self.last_successful_request else None,
            'consecutive_failures': self.consecutive_failures,
            'server_url': self.base_url
        }

    def force_reconnect(self) -> bool:
        """
        Fuerza un intento de reconexión con el servidor.

        Returns:
            bool: True si la reconexión fue exitosa
        """
        logger.info("Forzando reconexión con servidor madre...")
        self.consecutive_failures = 0
        return self._check_connectivity()

    def save_credentials(self, username: str, password: str) -> bool:
        """Guarda las credenciales localmente (cifradas básicamente)."""
        try:
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
            logger.error("Error guardando credenciales: %s", e)
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

        logger.info("Attempting login for user: %s", username)

        try:
            response = self._retry_request(
                'POST',
                url,
                json=payload,
                timeout=settings.HTTP_TIMEOUT_SHORT,
                max_retries=2
            )

            data = response.json()
            if data.get("status") == STATUS_APPROVED:
                self.save_credentials(username, password)
                logger.info("Login successful for user: %s", username)
                return True, data
            else:
                logger.warning("Unexpected API response for user: %s", username)
                return False, "Respuesta de API desconocida."

        except requests.exceptions.HTTPError as e:
            try:
                error_detail = e.response.json().get("detail", "Error de servidor")
                logger.error("Login HTTP error for %s: %s", username, error_detail)
                return False, f"Error: {error_detail}"
            except json.JSONDecodeError:
                logger.error("Login HTTP error for %s: %d", username, e.response.status_code)
                return False, f"Error HTTP {e.response.status_code}"

        except requests.exceptions.ConnectionError as e:
            logger.error("Connection error during login for %s: %s", username, e)
            return False, ERROR_CONNECTION

        except requests.exceptions.Timeout as e:
            logger.error("Timeout during login for %s: %s", username, e)
            return False, ERROR_TIMEOUT

        except Exception as e:
            logger.error("Unexpected error during login for %s: %s", username, e, exc_info=True)
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

        logger.info("Fetching sync data for user: %s", username)

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
                logger.info("Sync data fetched successfully for user: %s", username)
                return True, data
            else:
                logger.warning("Invalid sync response for user: %s", username)
                return False, {"error": "Respuesta de sincronización inválida."}

        except requests.exceptions.HTTPError as e:
            try:
                error_detail = e.response.json().get("detail", "Error de servidor")
                logger.error("Sync HTTP error for %s: %s", username, error_detail)
                return False, {"error": f"Error: {error_detail}"}
            except json.JSONDecodeError:
                logger.error("Sync HTTP error for %s: %d", username, e.response.status_code)
                return False, {"error": f"Error HTTP {e.response.status_code}"}

        except requests.exceptions.ConnectionError as e:
            logger.error("Connection error during sync for %s: %s", username, e)
            return False, {"error": ERROR_CONNECTION}

        except requests.exceptions.Timeout as e:
            logger.error("Timeout during sync for %s: %s", username, e)
            return False, {"error": ERROR_TIMEOUT}

        except Exception as e:
            logger.error("Unexpected error during sync for %s: %s", username, e, exc_info=True)
            return False, {"error": f"Error inesperado: {e}"}


    def send_message(self, to_user: str, subject: str, body: str,
                     parent_message_id: Optional[int] = None) -> Tuple[bool, dict]:
        """Envía un mensaje."""
        url = f"{self.base_url}/enviar_mensaje"

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


    def send_chat_message(self, to_user: str, message: str) -> Tuple[bool, dict]:
        """Envía un mensaje de chat en vivo."""
        url = f"{self.base_url}/enviar_chat"

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
