# hija_comms.py
#
# Módulo de Comunicaciones de la Aplicación Hija.
# Encapsula toda la lógica de red usando la biblioteca 'requests'.
# Incluye gestión de credenciales persistentes y validación de sincronización.

import requests
import json
import os
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any, Tuple

# --- Configuración de la Conexión ---
# IMPORTANTE: Reemplace '127.0.0.1' con la dirección IP real
# de la máquina donde se ejecuta la Aplicación Madre.
MADRE_BASE_URL = "http://127.0.0.1:8000"

# Directorio para datos locales
LOCAL_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data', 'hija_local')
CREDENTIALS_FILE = os.path.join(LOCAL_DATA_DIR, 'credentials.json')

class APICommunicator:
    """
    Gestiona todas las peticiones HTTP a la API de la Aplicación Madre.
    """
    def __init__(self, base_url: str = MADRE_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        os.makedirs(LOCAL_DATA_DIR, exist_ok=True)
    
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
        
        Envía un POST con username y password.
        Devuelve una tupla: (bool_exito, mensaje_o_datos)
        """
        url = f"{self.base_url}/autorizar"
        payload = {"username": username, "password": password}
        
        try:
            response = self.session.post(url, json=payload, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            if data.get("status") == "aprobado":
                # Guardar credenciales localmente
                self.save_credentials(username, password)
                return True, data
            else:
                return False, "Respuesta de API desconocida."
                
        except requests.exceptions.HTTPError as e:
            try:
                error_detail = e.response.json().get("detail", "Error de servidor")
                return False, f"Error: {error_detail}"
            except json.JSONDecodeError:
                return False, f"Error HTTP {e.response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return False, "Error de conexión: No se pudo alcanzar la Aplicación Madre."
            
        except requests.exceptions.Timeout:
            return False, "Error: La petición de conexión ha tardado demasiado."
            
        except Exception as e:
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
        
        Envía un GET con el nombre de usuario como parámetro de consulta.
        Devuelve una tupla: (bool_exito, datos_o_error_msg)
        """
        url = f"{self.base_url}/sincronizar_datos"
        params = {"usuario": username}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get("status") == "sincronizacion_exitosa":
                # Retornar todos los datos
                return True, data
            else:
                return False, {"error": "Respuesta de sincronización inválida."}
                
        except requests.exceptions.HTTPError as e:
            try:
                error_detail = e.response.json().get("detail", "Error de servidor")
                return False, {"error": f"Error: {error_detail}"}
            except json.JSONDecodeError:
                return False, {"error": f"Error HTTP {e.response.status_code}"}
                
        except requests.exceptions.ConnectionError:
            return False, {"error": "Error de conexión."}
            
        except Exception as e:
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
