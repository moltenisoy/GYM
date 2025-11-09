from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

import madre_db
from shared.logger import setup_logger
from shared.constants import APP_VERSION, APP_FEATURES, SYNC_REQUIRED_HOURS

logger = setup_logger(__name__, log_file="madre_server.log")

app = FastAPI(title="API del Sistema de Gestión del Gimnasio", version=APP_VERSION)

logger.info(f"FastAPI application initialized - Version {APP_VERSION}")

try:
    from madre_server_extended_api import get_extended_api_router
    from madre_server_extended_api2 import get_extended_api_router2

    app.include_router(get_extended_api_router())
    app.include_router(get_extended_api_router2())
    logger.info("Extended API routers included successfully (Features 1-16)")
except Exception as e:
    logger.error(f"Error including extended API routers: {e}", exc_info=True)

class AuthRequest(BaseModel):
    username: str = Field(..., min_length=1, description="Nombre de usuario")
    password: str = Field(..., min_length=1, description="Contraseña del usuario")

class UserUpdateRequest(BaseModel):
    username: str
    permiso_acceso: bool

@app.post("/autorizar", summary="Autoriza el inicio de sesión de una Aplicación Hija")
async def autorizar_usuario(auth_request: AuthRequest):
    logger.info(f"Intento de autorización para usuario: {auth_request.username}")

    success, user_data = madre_db.authenticate_user(
        auth_request.username,
        auth_request.password
    )

    if not success or not user_data:
        logger.warning(f"Credenciales inválidas para usuario: {auth_request.username}")
        raise HTTPException(status_code=401, detail="Credenciales inválidas.")

    if not user_data.get('permiso_acceso'):
        logger.warning(f"Acceso denegado para usuario: {auth_request.username}")
        raise HTTPException(status_code=403, detail="Permiso de acceso denegado por el administrador.")

    madre_db.update_user_sync(auth_request.username)

    logger.info(f"Autorización exitosa para usuario: {auth_request.username}")

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
    user = madre_db.get_user(usuario)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario solicitante desconocido.")

    user_id = user['id']

    profile_photo = madre_db.get_user_profile_photo(user_id)

    training_schedule = madre_db.get_training_schedule(user_id)

    photo_gallery = madre_db.get_photo_gallery(user_id)

    sync_data = madre_db.get_sync_data()

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
    usuarios = madre_db.get_all_users()
    for user in usuarios:
        user.pop('password_hash', None)

    return {
        "total": len(usuarios),
        "usuarios": usuarios
    }

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
    success = madre_db.mark_message_read(message_id)
    if success:
        return {"status": "marcado_leido", "message_id": message_id}
    else:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")

@app.delete("/eliminar_mensaje/{message_id}", summary="Eliminar mensaje")
async def eliminar_mensaje(message_id: int):
    success = madre_db.delete_message(message_id)
    if success:
        return {"status": "mensaje_eliminado", "message_id": message_id}
    else:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")

@app.get("/contar_no_leidos", summary="Contar mensajes no leídos")
async def contar_no_leidos(usuario: str = Query(..., description="Nombre de usuario")):
    count = madre_db.count_unread_messages(usuario)
    return {
        "status": "ok",
        "usuario": usuario,
        "mensajes_no_leidos": count
    }

@app.post("/enviar_chat", summary="Enviar mensaje de chat en vivo")
async def enviar_chat(request: ChatMessageRequest):
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
    madre_db.mark_chat_messages_read(from_user, to_user)
    return {"status": "chat_marcado_leido"}

@app.get("/contar_chat_no_leidos", summary="Contar mensajes de chat no leídos")
async def contar_chat_no_leidos(usuario: str = Query(..., description="Nombre de usuario")):
    count = madre_db.count_unread_chat_messages(usuario)
    return {
        "status": "ok",
        "usuario": usuario,
        "chat_no_leidos": count
    }

@app.post("/registrar_servidor_madre", summary="Registrar otro servidor Madre")
async def registrar_servidor_madre(
    server_name: str = Query(..., description="Nombre del servidor"),
    server_url: str = Query(..., description="URL del servidor"),
    sync_token: str = Query("", description="Token de sincronización")
):
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
    servers = madre_db.get_all_madre_servers()
    return {
        "status": "ok",
        "total": len(servers),
        "servidores": servers
    }

@app.get("/health", summary="Health check endpoint")
async def health_check():
    try:
        _ = len(madre_db.get_all_users())
        db_status = "healthy"
        logger.debug("Health check: Database connection OK")
    except Exception as e:
        db_status = "unhealthy"
        logger.error(f"Health check: Database error - {e}", exc_info=True)

    return {
        "status": "online",
        "version": APP_VERSION,
        "database_status": db_status
    }

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
    try:
        classes = madre_db.get_all_classes(active_only)
        return {"status": "success", "clases": classes}
    except Exception as e:
        logger.error(f"Error getting classes: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al obtener clases")

@app.get("/clases/horarios", summary="Obtiene horarios de clases")
async def get_schedules(class_id: Optional[int] = None):
    try:
        schedules = madre_db.get_class_schedules(class_id)
        return {"status": "success", "horarios": schedules}
    except Exception as e:
        logger.error(f"Error getting schedules: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al obtener horarios")

@app.post("/clases/reservar", summary="Reserva una clase (One-Click)")
async def book_class(booking: ClassBookingRequest):
    try:
        user = madre_db.get_user(booking.username)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        success, message = madre_db.book_class(
            user['id'], booking.schedule_id, booking.fecha_clase
        )

        if not success and "llena" in message:
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

class EquipmentReservationRequest(BaseModel):
    username: str
    equipment_id: int
    fecha_reserva: str
    hora_inicio: str
    hora_fin: str

@app.get("/equipos", summary="Obtiene equipos y zonas disponibles")
async def get_equipment():
    try:
        equipment = madre_db.get_all_equipment_zones()
        return {"status": "success", "equipos": equipment}
    except Exception as e:
        logger.error(f"Error getting equipment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al obtener equipos")

@app.post("/equipos/reservar", summary="Reserva equipo o zona")
async def reserve_equipment(reservation: EquipmentReservationRequest):
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
    try:
        exercises = madre_db.get_all_exercises()
        return {"status": "success", "ejercicios": exercises}
    except Exception as e:
        logger.error(f"Error getting exercises: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al obtener ejercicios")

@app.post("/workout/log", summary="Registra serie de ejercicio (Quick Log)")
async def log_workout(log: WorkoutLogRequest):
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

@app.post("/checkin/generate-token", summary="Genera token de check-in QR/NFC")
async def generate_checkin_token(username: str, token_type: str = "qr"):
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

@app.get("/notificaciones", summary="Obtiene notificaciones del usuario")
async def get_notifications(username: str, unread_only: bool = False):
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

@app.post("/utilidades/calculadora-discos", summary="Calcula discos para barra")
async def calculate_plates(target_weight: float, bar_weight: float = 20.0):
    try:
        from shared.workout_utils import calculate_plates as calc_plates
        result = calc_plates(target_weight, bar_weight)
        return {"status": "success", "resultado": result}
    except Exception as e:
        logger.error(f"Error calculating plates: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al calcular discos")

@app.get("/", summary="Endpoint raíz de estado")
async def root():
    logger.debug("Root endpoint accessed")
    return {
        "mensaje": "Servidor de la Aplicación Madre está en línea.",
        "version": APP_VERSION,
        "features": APP_FEATURES
    }
