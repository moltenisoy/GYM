"""
Constantes centralizadas para el sistema GYM.
Todos los números mágicos, strings y valores de configuración por defecto están definidos aquí.
"""

# Configuración del Servidor
DEFAULT_HOST_IP = "0.0.0.0"
DEFAULT_HOST_PORT = 8000
DEFAULT_MADRE_BASE_URL = "http://127.0.0.1:8000"

# Configuración de la Base de Datos
DEFAULT_DB_FILENAME = "gym_database.db"

# Tiempos de espera (en segundos)
HTTP_TIMEOUT_SHORT = 5
HTTP_TIMEOUT_MEDIUM = 10
HTTP_TIMEOUT_LONG = 30
HTTP_TIMEOUT_UPLOAD = 60

# Sincronización
SYNC_REQUIRED_HOURS = 72
SYNC_INTERVAL_INITIAL = 300  # 5 minutos
SYNC_INTERVAL_NORMAL = 1800  # 30 minutos

# Mensajes de Estado HTTP
STATUS_APPROVED = "aprobado"
STATUS_SYNC_SUCCESS = "sincronizacion_exitosa"
STATUS_OK = "ok"

# Mensajes de Error
ERROR_CONNECTION = "Error de conexión: No se pudo alcanzar la Aplicación Madre."
ERROR_TIMEOUT = "Error: La petición de conexión ha tardado demasiado."
ERROR_INVALID_CREDENTIALS = "Credenciales inválidas."
ERROR_ACCESS_DENIED = "Permiso de acceso denegado por el administrador."
ERROR_USER_NOT_FOUND = "Usuario no encontrado."
ERROR_SYNC_REQUIRED = "Primera sincronización requerida"
ERROR_UNKNOWN = "Error desconocido"

# Rutas de Archivos
LOCAL_DATA_DIR_NAME = "data"
HIJA_LOCAL_DIR_NAME = "hija_local"
CREDENTIALS_FILENAME = "credentials.json"

# Endpoints de la API
ENDPOINT_AUTORIZAR = "/autorizar"
ENDPOINT_VALIDAR_SYNC = "/validar_sync"
ENDPOINT_SINCRONIZAR_DATOS = "/sincronizar_datos"
ENDPOINT_ACTUALIZAR_PERMISO = "/actualizar_permiso"
ENDPOINT_USUARIOS = "/usuarios"
ENDPOINT_ENVIAR_MENSAJE = "/enviar_mensaje"
ENDPOINT_OBTENER_MENSAJES = "/obtener_mensajes"
ENDPOINT_MARCAR_LEIDO = "/marcar_leido"
ENDPOINT_CONTAR_NO_LEIDOS = "/contar_no_leidos"
ENDPOINT_ENVIAR_CHAT = "/enviar_chat"
ENDPOINT_OBTENER_CHAT = "/obtener_chat"
ENDPOINT_HEALTH = "/health"

# Configuración de Logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_FILE_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
LOG_FILE_BACKUP_COUNT = 5
LOG_DIR_NAME = "logs"

# Metadatos de la Aplicación
APP_VERSION = "3.1.0"
APP_FEATURES = [
    "Autenticación con contraseña",
    "Base de datos SQLite persistente",
    "Validación de sincronización 72h",
    "Sincronización masiva",
    "Gestión completa de usuarios",
    "Sistema de mensajería",
    "Chat en vivo",
    "Soporte multi-madre"
]
