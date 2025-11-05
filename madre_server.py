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

# Crear la instancia de la aplicación FastAPI
app = FastAPI(title="Servidor API de la Aplicación Madre")

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
    """
    # Autenticar usuario
    success, user_data = madre_db.authenticate_user(
        auth_request.username, 
        auth_request.password
    )
    
    if not success or not user_data:
        raise HTTPException(status_code=401, detail="Credenciales inválidas.")
    
    # Verificar permiso de acceso
    if not user_data.get('permiso_acceso'):
        raise HTTPException(status_code=403, detail="Permiso de acceso denegado por el administrador.")
    
    # Actualizar última sincronización
    madre_db.update_user_sync(auth_request.username)
    
    # Retornar información del usuario
    return {
        "status": "aprobado",
        "usuario": auth_request.username,
        "nombre_completo": user_data.get('nombre_completo'),
        "equipo": user_data.get('equipo'),
        "last_sync": datetime.now().isoformat()
    }

@app.get("/validar_sync", summary="Valida si el usuario necesita sincronizar (72 horas)")
async def validar_sync(
    usuario: str = Query(..., description="Nombre de usuario")
):
    """
    Valida si el usuario ha sincronizado en las últimas 72 horas.
    Si no, debe bloquearse el acceso en la app Hija.
    """
    user = madre_db.get_user(usuario)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    
    last_sync_str = user.get('last_sync')
    if not last_sync_str:
        return {
            "requiere_sync": True,
            "bloqueado": True,
            "mensaje": "Primera sincronización requerida"
        }
    
    try:
        last_sync = datetime.fromisoformat(last_sync_str)
        tiempo_desde_sync = datetime.now() - last_sync
        horas_desde_sync = tiempo_desde_sync.total_seconds() / 3600
        
        if horas_desde_sync > 72:
            return {
                "requiere_sync": True,
                "bloqueado": True,
                "mensaje": f"Sincronización requerida. Última sync: {horas_desde_sync:.1f} horas atrás",
                "horas_desde_sync": horas_desde_sync
            }
        else:
            return {
                "requiere_sync": False,
                "bloqueado": False,
                "mensaje": "Sincronización actual",
                "horas_desde_sync": horas_desde_sync
            }
    except:
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

@app.get("/", summary="Endpoint raíz de estado")
async def root():
    """
    Endpoint simple para verificar que el servidor está en línea.
    """
    return {
        "mensaje": "Servidor de la Aplicación Madre está en línea.",
        "version": "2.0.0",
        "features": [
            "Autenticación con contraseña",
            "Base de datos SQLite persistente",
            "Validación de sincronización 72h",
            "Sincronización masiva",
            "Gestión completa de usuarios"
        ]
    }
