# madre_server.py
#
# Define la lógica del servidor API usando FastAPI para el Sistema de Gestión del Gimnasio.
# Esta API será consumida por las Aplicaciones de los Socios (Aplicaciones Hijas).
# Importa la base de datos SQLite desde 'madre_db'.

from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Importar la base de datos
import madre_db
from shared.logger import setup_logger
from shared.constants import APP_VERSION, APP_FEATURES, SYNC_REQUIRED_HOURS

# Initialize logger
logger = setup_logger(__name__, log_file="madre_server.log")

# Crear la instancia de la aplicación FastAPI
app = FastAPI(title="API del Sistema de Gestión del Gimnasio", version=APP_VERSION)

logger.info(f"FastAPI application initialized - Version {APP_VERSION}")

# Include extended API routers for features 1-16
try:
    from madre_server_extended_api import get_extended_api_router
    from madre_server_extended_api2 import get_extended_api_router2
    
    app.include_router(get_extended_api_router())
    app.include_router(get_extended_api_router2())
    logger.info("Extended API routers included successfully (Features 1-16)")
except Exception as e:
    logger.error(f"Error including extended API routers: {e}", exc_info=True)

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
        _ = len(madre_db.get_all_users())
        db_status = "healthy"
        logger.debug("Health check: Database connection OK")
    except Exception as e:
        # No exponer detalles del error por seguridad
        db_status = "unhealthy"
        logger.error(f"Health check: Database error - {e}", exc_info=True)

    return {
        "status": "online",
        "version": APP_VERSION,
        "database_status": db_status
    }


# ============================================================================
# ENDPOINTS DE CLASES Y RESERVAS
# ============================================================================

class ClassBookingRequest(BaseModel):
    username: str
    schedule_id: int
    fecha_clase: str


class ClassRatingRequest(BaseModel):
    username: str
    class_id: int
    schedule_id: int
    fecha_clase: str
    rating: int = Field(..., ge=1, le=5)
    instructor_rating: Optional[int] = Field(None, ge=1, le=5)
    comentario: Optional[str] = ""


@app.get("/clases", summary="Obtiene todas las clases disponibles")
async def get_classes(active_only: bool = True):
    """Retorna lista de todas las clases."""
    try:
        classes = madre_db.get_all_classes(active_only)
        return {"status": "success", "clases": classes}
    except Exception as e:
        logger.error(f"Error getting classes: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al obtener clases")


@app.get("/clases/horarios", summary="Obtiene horarios de clases")
async def get_schedules(class_id: Optional[int] = None):
    """Retorna horarios de clases disponibles."""
    try:
        schedules = madre_db.get_class_schedules(class_id)
        return {"status": "success", "horarios": schedules}
    except Exception as e:
        logger.error(f"Error getting schedules: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al obtener horarios")


@app.post("/clases/reservar", summary="Reserva una clase (One-Click)")
async def book_class(booking: ClassBookingRequest):
    """One-Click Booking: Reserva una clase con un solo toque."""
    try:
        # Obtener user_id
        user = madre_db.get_user(booking.username)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        success, message = madre_db.book_class(
            user['id'], booking.schedule_id, booking.fecha_clase
        )
        
        if not success and "llena" in message:
            # Agregar a lista de espera automáticamente
            success_wl, msg_wl = madre_db.add_to_waitlist(
                user['id'], booking.schedule_id, booking.fecha_clase
            )
            return {
                "status": "waitlist",
                "message": "Clase llena. Agregado a lista de espera.",
                "waitlist_added": success_wl
            }
        
        if success:
            logger.info(f"Class booked: {booking.username} - Schedule {booking.schedule_id}")
            return {"status": "success", "message": message}
        else:
            return {"status": "error", "message": message}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error booking class: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al reservar clase")


@app.get("/clases/mis-reservas", summary="Obtiene reservas del usuario")
async def get_my_bookings(username: str):
    """Retorna las reservas de clases del usuario."""
    try:
        user = madre_db.get_user(username)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        bookings = madre_db.get_user_bookings(user['id'], datetime.now().date().isoformat())
        return {"status": "success", "reservas": bookings}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting bookings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al obtener reservas")


@app.post("/clases/cancelar", summary="Cancela una reserva")
async def cancel_booking(booking_id: int):
    """Cancela una reserva de clase."""
    try:
        success, message = madre_db.cancel_booking(booking_id)
        if success:
            return {"status": "success", "message": message}
        else:
            return {"status": "error", "message": message}
    except Exception as e:
        logger.error(f"Error cancelling booking: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al cancelar reserva")


@app.post("/clases/calificar", summary="Califica una clase")
async def rate_class(rating: ClassRatingRequest):
    """Califica una clase después de asistir (Quick Rating)."""
    try:
        user = madre_db.get_user(rating.username)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        success, message = madre_db.rate_class(
            user['id'], rating.class_id, rating.schedule_id,
            rating.fecha_clase, rating.rating, rating.instructor_rating,
            rating.comentario
        )
        
        if success:
            return {"status": "success", "message": message}
        else:
            return {"status": "error", "message": message}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rating class: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al calificar clase")


# ============================================================================
# ENDPOINTS DE EQUIPOS Y ZONAS
# ============================================================================

class EquipmentReservationRequest(BaseModel):
    username: str
    equipment_id: int
    fecha_reserva: str
    hora_inicio: str
    hora_fin: str


@app.get("/equipos", summary="Obtiene equipos y zonas disponibles")
async def get_equipment():
    """Retorna lista de equipos y zonas reservables."""
    try:
        equipment = madre_db.get_all_equipment_zones()
        return {"status": "success", "equipos": equipment}
    except Exception as e:
        logger.error(f"Error getting equipment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al obtener equipos")


@app.post("/equipos/reservar", summary="Reserva equipo o zona")
async def reserve_equipment(reservation: EquipmentReservationRequest):
    """Reserva un equipo o zona por franjas horarias."""
    try:
        user = madre_db.get_user(reservation.username)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        success, message = madre_db.reserve_equipment(
            user['id'], reservation.equipment_id, reservation.fecha_reserva,
            reservation.hora_inicio, reservation.hora_fin
        )
        
        if success:
            return {"status": "success", "message": message}
        else:
            return {"status": "error", "message": message}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reserving equipment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al reservar equipo")


# ============================================================================
# ENDPOINTS DE WORKOUT LOGGING
# ============================================================================

class WorkoutLogRequest(BaseModel):
    username: str
    exercise_id: int
    fecha: str
    serie: int
    repeticiones: int
    peso: Optional[float] = None
    descanso_segundos: Optional[int] = None


@app.get("/ejercicios", summary="Obtiene lista de ejercicios")
async def get_exercises():
    """Retorna todos los ejercicios disponibles."""
    try:
        exercises = madre_db.get_all_exercises()
        return {"status": "success", "ejercicios": exercises}
    except Exception as e:
        logger.error(f"Error getting exercises: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al obtener ejercicios")


@app.post("/workout/log", summary="Registra serie de ejercicio (Quick Log)")
async def log_workout(log: WorkoutLogRequest):
    """Quick Log: Registra una serie de ejercicio rápidamente."""
    try:
        user = madre_db.get_user(log.username)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        log_id = madre_db.log_workout(
            user['id'], log.exercise_id, log.fecha, log.serie,
            log.repeticiones, log.peso, log.descanso_segundos
        )
        
        if log_id:
            return {"status": "success", "log_id": log_id, "message": "Serie registrada"}
        else:
            return {"status": "error", "message": "Error al registrar serie"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging workout: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al registrar entrenamiento")


@app.get("/workout/historial", summary="Obtiene historial de ejercicio")
async def get_exercise_history(username: str, exercise_id: int, limit: int = 10):
    """Retorna el historial de un ejercicio para el usuario."""
    try:
        user = madre_db.get_user(username)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        history = madre_db.get_exercise_history(user['id'], exercise_id, limit)
        return {"status": "success", "historial": history}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting exercise history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al obtener historial")


# ============================================================================
# ENDPOINTS DE CHECK-IN Y TOKENS
# ============================================================================

@app.post("/checkin/generate-token", summary="Genera token de check-in QR/NFC")
async def generate_checkin_token(username: str, token_type: str = "qr"):
    """Genera un token único de check-in para acceso digital."""
    try:
        user = madre_db.get_user(username)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        success, token = madre_db.generate_checkin_token(user['id'], token_type)
        
        if success:
            return {"status": "success", "token": token, "token_type": token_type}
        else:
            return {"status": "error", "message": "Error al generar token"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating token: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al generar token")


@app.post("/checkin", summary="Registra check-in de usuario")
async def checkin(username: str, location: str = "entrada"):
    """Registra check-in digital del usuario en el gimnasio."""
    try:
        user = madre_db.get_user(username)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        success, message = madre_db.checkin_user(user['id'], location)
        
        if success:
            return {"status": "success", "message": message}
        else:
            return {"status": "error", "message": message}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking in: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al registrar check-in")


# ============================================================================
# ENDPOINTS DE NOTIFICACIONES
# ============================================================================

@app.get("/notificaciones", summary="Obtiene notificaciones del usuario")
async def get_notifications(username: str, unread_only: bool = False):
    """Retorna notificaciones del usuario."""
    try:
        user = madre_db.get_user(username)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        notifications = madre_db.get_user_notifications(user['id'], unread_only)
        return {"status": "success", "notificaciones": notifications}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting notifications: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al obtener notificaciones")


# ============================================================================
# UTILIDADES
# ============================================================================

@app.post("/utilidades/calculadora-discos", summary="Calcula discos para barra")
async def calculate_plates(target_weight: float, bar_weight: float = 20.0):
    """Calculadora de discos: indica qué discos poner en la barra."""
    try:
        from shared.workout_utils import calculate_plates as calc_plates
        result = calc_plates(target_weight, bar_weight)
        return {"status": "success", "resultado": result}
    except Exception as e:
        logger.error(f"Error calculating plates: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al calcular discos")


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
