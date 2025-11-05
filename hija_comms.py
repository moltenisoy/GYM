# hija_comms.py
#
# Módulo de Comunicaciones de la Aplicación Hija.
# Encapsula toda la lógica de red usando la biblioteca 'requests'.
# Esto separa la lógica de la API de la lógica de la GUI.

import requests
import json

# --- Configuración de la Conexión ---
# IMPORTANTE: Reemplace '127.0.0.1' con la dirección IP real
# de la máquina donde se ejecuta la Aplicación Madre.
MADRE_BASE_URL = "http://127.0.0.1:8000"


class APICommunicator:
    """
    Gestiona todas las peticiones HTTP a la API de la Aplicación Madre.
    """
    def __init__(self, base_url: str = MADRE_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def attempt_login(self, username: str) -> (bool, str):
        """
        Intenta autenticar al usuario contra el endpoint /autorizar.
        
        Envía un POST con un payload JSON.
        Devuelve una tupla: (bool_exito, mensaje_o_error)
        """
        url = f"{self.base_url}/autorizar"
        payload = {"username": username}
        
        try:
            # Usar 'json=payload' hace que 'requests' automáticamente
            # serialice a JSON y establezca el header 'Content-Type'.
            response = self.session.post(url, json=payload, timeout=5)
            
            # Comprobar si la petición fue exitosa a nivel de HTTP (ej. 200 OK)
            response.raise_for_status()
            
            # Si llegamos aquí, la API respondió con 2xx
            data = response.json()
            if data.get("status") == "aprobado":
                return True, data.get("usuario", "Usuario aprobado")
            else:
                # Caso poco probable si la API está bien diseñada, pero se maneja
                return False, "Respuesta de API desconocida."
                
        except requests.exceptions.HTTPError as e:
            # Manejar errores de la API (ej. 403 Prohibido, 404 No Encontrado)
            try:
                error_detail = e.response.json().get("detail", "Error de servidor")
                return False, f"Error: {error_detail}"
            except json.JSONDecodeError:
                return False, f"Error HTTP {e.response.status_code}"
                
        except requests.exceptions.ConnectionError:
            # Manejar error de conexión (servidor no alcanzable)
            return False, "Error de conexión: No se pudo alcanzar la Aplicación Madre."
            
        except requests.exceptions.Timeout:
            # Manejar tiempo de espera agotado
            return False, "Error: La petición de conexión ha tardado demasiado."
            
        except Exception as e:
            # Manejar cualquier otro error inesperado
            return False, f"Un error inesperado ha ocurrido: {e}"

    def fetch_sync_data(self, username: str) -> (bool, dict):
        """
        Obtiene los datos de sincronización del endpoint /sincronizar_datos.
        
        Envía un GET con el nombre de usuario como parámetro de consulta.
        Devuelve una tupla: (bool_exito, datos_o_error_msg)
        """
        url = f"{self.base_url}/sincronizar_datos"
        # 'params' construye automáticamente la URL query string:
        # .../sincronizar_datos?usuario=nombre_usuario
        params = {"usuario": username}
        
        try:
            response = self.session.get(url, params=params, timeout=5)
            response.raise_for_status()  # Lanza error para 4xx/5xx
            
            data = response.json()
            if data.get("status") == "sincronizacion_exitosa":
                return True, data.get("datos", {})
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
