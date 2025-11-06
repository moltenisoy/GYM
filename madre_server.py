# madre_server.py
#
# Define la lógica del servidor API usando FastAPI.
# Esta API será consumida por las Aplicaciones Hijas.
# Importa la base de datos SQLite desde 'madre_db'.

from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

# Importar la base de datos
import madre_db
from shared.logger import setup_logger
from shared.constants import APP_VERSION, APP_FEATURES, SYNC_REQUIRED_HOURS

# Initialize logger
logger = setup_logger(__name__, log_file="madre_server.log")

# Crear la instancia de la aplicación FastAPI
app = FastAPI(title="Servidor API de la Aplicación Madre", version=APP_VERSION)

logger.info(f"FastAPI application initialized - Version {APP_VERSION}")

# --- Modelos de Datos (Pydantic) ---
class AuthRequest(BaseModel):
    username: str = Field(..., min_length=1, description="Nombre de usuario")
    password: str = Field(..., min_length=1, description="Contraseña del usuario")

class UserUpdateRequest(BaseModel):
    username: str
    permiso_acceso: bool

# --- Endpoints de la API ---

@app.post("/autorizar", summary="Autoriza el inicio de sesión de una Aplicación Hija")
async def autorizar_usuario(auth_request: AuthRequest):
    """
    Endpoint de autenticación con contraseña.
    Verifica credenciales y valida que el usuario tenga permiso de acceso.
    
    Args:
        auth_request: Objeto con username y password
    
    Returns:
        Dict con status, usuario, nombre_completo, equipo, last_sync
    
    Raises:
        HTTPException: 401 si credenciales inválidas, 403 si acceso denegado
    """
    logger.info(f"Intento de autorización para usuario: {auth_request.username}")
    
    # Autenticar usuario
    success, user_data = madre_db.authenticate_user(
        auth_request.username, 
        auth_request.password
    )
    
    if not success or not user_data:
        logger.warning(f"Credenciales inválidas para usuario: {auth_request.username}")
        raise HTTPException(status_code=401, detail="Credenciales inválidas.")
    
    # Verificar permiso de acceso
    if not user_data.get('permiso_acceso'):
        logger.warning(f"Acceso denegado para usuario: {auth_request.username}")
        raise HTTPException(status_code=403, detail="Permiso de acceso denegado por el administrador.")
    
    # Actualizar última sincronización
    madre_db.update_user_sync(auth_request.username)
    
    logger.info(f"Autorización exitosa para usuario: {auth_request.username}")
    
    # Retornar información del usuario
    return {
        "status": "aprobado",
        "usuario": auth_request.username,
        "nombre_completo": user_data.get('nombre_completo'),
        "equipo": user_data.get('equipo'),
        "last_sync": datetime.now().isoformat()
    }

@app.get("/validar_sync", summary="Valida si el usuario necesita sincronizar")
async def validar_sync(
    usuario: str = Query(..., description="Nombre de usuario")
):
    """
    Valida si el usuario ha sincronizado en las últimas horas configuradas.
    Si no, debe bloquearse el acceso en la app Hija.
    
    Args:
        usuario: Nombre de usuario a validar
    
    Returns:
        Dict con requiere_sync, bloqueado, mensaje, horas_desde_sync
    
    Raises:
        HTTPException: 404 si usuario no encontrado
    """
    logger.debug(f"Validando estado de sincronización para usuario: {usuario}")
    
    user = madre_db.get_user(usuario)
    if not user:
        logger.warning(f"Usuario no encontrado en validación de sync: {usuario}")
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    
    last_sync_str = user.get('last_sync')
    if not last_sync_str:
        logger.info(f"Primera sincronización requerida para: {usuario}")
        return {
            "requiere_sync": True,
            "bloqueado": True,
            "mensaje": "Primera sincronización requerida"
        }
    
    try:
        last_sync = datetime.fromisoformat(last_sync_str)
        tiempo_desde_sync = datetime.now() - last_sync
        horas_desde_sync = tiempo_desde_sync.total_seconds() / 3600
        
        if horas_desde_sync > SYNC_REQUIRED_HOURS:
            logger.warning(f"Sincronización requerida para {usuario}: {horas_desde_sync:.1f} horas desde última sync")
            return {
                "requiere_sync": True,
                "bloqueado": True,
                "mensaje": f"Sincronización requerida. Última sync: {horas_desde_sync:.1f} horas atrás",
                "horas_desde_sync": horas_desde_sync
            }
        else:
            logger.debug(f"Sincronización actual para {usuario}: {horas_desde_sync:.1f} horas")
            return {
                "requiere_sync": False,
                "bloqueado": False,
                "mensaje": "Sincronización actual",
                "horas_desde_sync": horas_desde_sync
            }
    except Exception as e:
        logger.error(f"Error validando sincronización para {usuario}: {e}", exc_info=True)
        return {
            "requiere_sync": True,
            "bloqueado": True,
            "mensaje": "Error al validar sincronización"
        }

@app.get("/sincronizar_datos", summary="Proporciona datos de sincronización completos a una Hija")
async def obtener_datos_sync(
    usuario: str = Query(..., description="El nombre de usuario de la Hija que solicita los datos")
):
    """
    Endpoint de sincronización completa.
    Devuelve todos los datos del usuario: perfil, cronograma, galería, etc.
    """
    user = madre_db.get_user(usuario)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario solicitante desconocido.")
    
    user_id = user['id']
    
    # Obtener foto de perfil
    profile_photo = madre_db.get_user_profile_photo(user_id)
    
    # Obtener cronograma actual
    training_schedule = madre_db.get_training_schedule(user_id)
    
    # Obtener galería de fotos
    photo_gallery = madre_db.get_photo_gallery(user_id)
    
    # Obtener datos de sincronización global
    sync_data = madre_db.get_sync_data()
    
    # Actualizar última sincronización
    madre_db.update_user_sync(usuario)
    
    return {
        "status": "sincronizacion_exitosa",
        "timestamp": datetime.now().isoformat(),
        "usuario": {
            "username": user['username'],
            "nombre_completo": user['nombre_completo'],
            "email": user['email'],
            "telefono": user['telefono'],
            "equipo": user['equipo'],
            "fecha_registro": user['fecha_registro']
        },
        "profile_photo": profile_photo,
        "training_schedule": training_schedule,
        "photo_gallery": photo_gallery,
        "sync_content": sync_data
    }

@app.post("/actualizar_permiso", summary="Actualiza el permiso de acceso de un usuario")
async def actualizar_permiso(request: UserUpdateRequest):
    """
    Endpoint para que la app Madre actualice permisos de usuarios.
    """
    success = madre_db.update_user_permission(request.username, request.permiso_acceso)
    if not success:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    
    return {
        "status": "actualizado",
        "usuario": request.username,
        "permiso_acceso": request.permiso_acceso
    }

@app.post("/sincronizar_masiva", summary="Fuerza sincronización para múltiples usuarios")
async def sincronizar_masiva(usernames: list[str]):
    """
    Endpoint para sincronización masiva.
    Marca la hora de sincronización para múltiples usuarios.
    """
    resultados = []
    for username in usernames:
        success = madre_db.update_user_sync(username)
        resultados.append({
            "usuario": username,
            "actualizado": success
        })
    
    return {
        "status": "sincronizacion_masiva_completada",
        "total": len(usernames),
        "resultados": resultados
    }

@app.get("/usuarios", summary="Obtiene lista de todos los usuarios")
async def obtener_usuarios():
    """
    Endpoint para obtener la lista completa de usuarios.
    Usado por la app Madre para gestión.
    """
    usuarios = madre_db.get_all_users()
    # Remover password_hash de la respuesta
    for user in usuarios:
        user.pop('password_hash', None)
    
    return {
        "total": len(usuarios),
        "usuarios": usuarios
    }

# ============================================================================
# ENDPOINTS DE MENSAJERÍA
# ============================================================================

class MessageRequest(BaseModel):
    from_user: str
    to_user: str
    subject: str
    body: str
    parent_message_id: Optional[int] = None

class ChatMessageRequest(BaseModel):
    from_user: str
    to_user: str
    message: str

@app.post("/enviar_mensaje", summary="Enviar mensaje")
async def enviar_mensaje(request: MessageRequest):
    """Endpoint para enviar un mensaje."""
    message_id = madre_db.send_message(
        request.from_user,
        request.to_user,
        request.subject,
        request.body,
        request.parent_message_id
    )
    
    if message_id:
        return {
            "status": "mensaje_enviado",
            "message_id": message_id,
            "timestamp": datetime.now().isoformat()
        }
    else:
        raise HTTPException(status_code=500, detail="Error al enviar mensaje")

@app.get("/obtener_mensajes", summary="Obtener mensajes del usuario")
async def obtener_mensajes(
    usuario: str = Query(..., description="Nombre de usuario"),
    solo_no_leidos: bool = Query(False, description="Solo mensajes no leídos")
):
    """Endpoint para obtener mensajes de un usuario."""
    messages = madre_db.get_user_messages(usuario, include_read=not solo_no_leidos)
    unread_count = madre_db.count_unread_messages(usuario)
    
    return {
        "status": "ok",
        "total_mensajes": len(messages),
        "mensajes_no_leidos": unread_count,
        "mensajes": messages
    }

@app.get("/obtener_mensaje/{message_id}", summary="Obtener mensaje específico")
async def obtener_mensaje(message_id: int):
    """Endpoint para obtener un mensaje específico con adjuntos."""
    message = madre_db.get_message_by_id(message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    
    attachments = madre_db.get_message_attachments(message_id)
    message['attachments'] = attachments
    
    return {
        "status": "ok",
        "mensaje": message
    }

@app.post("/marcar_leido/{message_id}", summary="Marcar mensaje como leído")
async def marcar_leido(message_id: int):
    """Endpoint para marcar un mensaje como leído."""
    success = madre_db.mark_message_read(message_id)
    if success:
        return {"status": "marcado_leido", "message_id": message_id}
    else:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")

@app.delete("/eliminar_mensaje/{message_id}", summary="Eliminar mensaje")
async def eliminar_mensaje(message_id: int):
    """Endpoint para eliminar un mensaje."""
    success = madre_db.delete_message(message_id)
    if success:
        return {"status": "mensaje_eliminado", "message_id": message_id}
    else:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")

@app.get("/contar_no_leidos", summary="Contar mensajes no leídos")
async def contar_no_leidos(usuario: str = Query(..., description="Nombre de usuario")):
    """Endpoint para contar mensajes no leídos."""
    count = madre_db.count_unread_messages(usuario)
    return {
        "status": "ok",
        "usuario": usuario,
        "mensajes_no_leidos": count
    }

# ============================================================================
# ENDPOINTS DE CHAT EN VIVO
# ============================================================================

@app.post("/enviar_chat", summary="Enviar mensaje de chat en vivo")
async def enviar_chat(request: ChatMessageRequest):
    """Endpoint para enviar un mensaje de chat en vivo."""
    chat_id = madre_db.send_chat_message(
        request.from_user,
        request.to_user,
        request.message
    )
    
    if chat_id:
        return {
            "status": "chat_enviado",
            "chat_id": chat_id,
            "timestamp": datetime.now().isoformat()
        }
    else:
        raise HTTPException(status_code=500, detail="Error al enviar chat")

@app.get("/obtener_chat", summary="Obtener historial de chat")
async def obtener_chat(
    user1: str = Query(..., description="Usuario 1"),
    user2: str = Query(..., description="Usuario 2"),
    limit: int = Query(50, description="Límite de mensajes")
):
    """Endpoint para obtener historial de chat entre dos usuarios."""
    messages = madre_db.get_chat_history(user1, user2, limit)
    return {
        "status": "ok",
        "total_mensajes": len(messages),
        "mensajes": messages
    }

@app.post("/marcar_chat_leido", summary="Marcar mensajes de chat como leídos")
async def marcar_chat_leido(
    from_user: str = Query(..., description="Usuario remitente"),
    to_user: str = Query(..., description="Usuario destinatario")
):
    """Endpoint para marcar mensajes de chat como leídos."""
    madre_db.mark_chat_messages_read(from_user, to_user)
    return {"status": "chat_marcado_leido"}

@app.get("/contar_chat_no_leidos", summary="Contar mensajes de chat no leídos")
async def contar_chat_no_leidos(usuario: str = Query(..., description="Nombre de usuario")):
    """Endpoint para contar mensajes de chat no leídos."""
    count = madre_db.count_unread_chat_messages(usuario)
    return {
        "status": "ok",
        "usuario": usuario,
        "chat_no_leidos": count
    }

# ============================================================================
# ENDPOINTS DE MULTI-MADRE
# ============================================================================

@app.post("/registrar_servidor_madre", summary="Registrar otro servidor Madre")
async def registrar_servidor_madre(
    server_name: str = Query(..., description="Nombre del servidor"),
    server_url: str = Query(..., description="URL del servidor"),
    sync_token: str = Query("", description="Token de sincronización")
):
    """Endpoint para registrar otro servidor Madre para sincronización."""
    success = madre_db.add_madre_server(server_name, server_url, sync_token)
    if success:
        return {
            "status": "servidor_registrado",
            "server_name": server_name
        }
    else:
        raise HTTPException(status_code=400, detail="Servidor ya registrado")

@app.get("/obtener_servidores_madre", summary="Obtener servidores Madre registrados")
async def obtener_servidores_madre():
    """Endpoint para obtener todos los servidores Madre registrados."""
    servers = madre_db.get_all_madre_servers()
    return {
        "status": "ok",
        "total": len(servers),
        "servidores": servers
    }

@app.get("/health", summary="Health check endpoint")
async def health_check():
    """
    Health check endpoint para verificar el estado del servidor.
    Verifica conectividad con la base de datos.
    
    Returns:
        Dict con status, version, database_status
    """
    try:
        # Verificar conectividad de base de datos
        users_count = len(madre_db.get_all_users())
        db_status = "healthy"
        logger.debug("Health check: Database connection OK")
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        logger.error(f"Health check: Database error - {e}")
    
    return {
        "status": "online",
        "version": APP_VERSION,
        "database_status": db_status
    }


@app.get("/", summary="Endpoint raíz de estado")
async def root():
    """
    Endpoint simple para verificar que el servidor está en línea.
    
    Returns:
        Dict con mensaje, version, features
    """
    logger.debug("Root endpoint accessed")
    return {
        "mensaje": "Servidor de la Aplicación Madre está en línea.",
        "version": APP_VERSION,
        "features": APP_FEATURES
    }
