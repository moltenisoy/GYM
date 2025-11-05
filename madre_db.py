# madre_db.py
#
# Este archivo actúa como una base de datos en memoria simple.
# Es importado tanto por 'madre_server.py' como por 'madre_gui.py'.
# Esto permite que tanto el servidor API como la interfaz gráfica de gestión
# lean y escriban desde la misma fuente de verdad.
#
# NOTA SOBRE CONCURRENCIA: En una aplicación de producción, el acceso a estos
# diccionarios desde hilos separados (GUI y Servidor) debería estar
# protegido por un 'threading.Lock' para garantizar la seguridad del hilo
# (thread-safety). Para este prototipo mínimo, confiamos en el
# Global Interpreter Lock (GIL) de Python para operaciones atómicas simples.

# Base de datos de usuarios. La clave es el nombre de usuario.
# El valor es un diccionario que contiene sus datos, incluido el permiso de acceso.
USER_DB = {
    "usuario_alfa": {"permiso_acceso": True, "datos_adicionales": "Equipo A"},
    "usuario_beta": {"permiso_acceso": True, "datos_adicionales": "Equipo B"},
    "usuario_gamma": {"permiso_acceso": False, "datos_adicionales": "Equipo C"},
}

# Base de datos de sincronización. Almacena el contenido que las Hijas
# descargarán cuando soliciten una sincronización.
SYNC_DATA = {
    "contenido": "Este es el contenido inicial desde la Madre.",
    "metadatos_version": "1.0.0"
}
