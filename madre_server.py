# madre_server.py
#
# Define la lógica del servidor API usando FastAPI.
# Esta API será consumida por las Aplicaciones Hijas.
# Importa la base de datos en memoria desde 'madre_db'.

from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any

# Importar la base de datos compartida
import madre_db

# Crear la instancia de la aplicación FastAPI
app = FastAPI(title="Servidor API de la Aplicación Madre")

# --- Modelos de Datos (Pydantic) ---
# Pydantic se usa para la validación de datos de solicitud.
# Define la estructura esperada del JSON en la petición POST de autorización.
class AuthRequest(BaseModel):
    username: str = Field(..., min_length=1, description="Nombre de usuario que intenta iniciar sesión")

# --- Endpoints de la API ---

@app.post("/autorizar", summary="Autoriza el inicio de sesión de una Aplicación Hija")
async def autorizar_usuario(auth_request: AuthRequest):
    """
    Endpoint de autenticación.
    Recibe un nombre de usuario y comprueba si existe en la USER_DB
    y si su 'permiso_acceso' está establecido en True.
    """
    usuario = auth_request.username
    
    if usuario in madre_db.USER_DB:
        if madre_db.USER_DB[usuario].get("permiso_acceso", False):
            # Usuario encontrado y con permiso
            return {"status": "aprobado", "usuario": usuario}
        else:
            # Usuario encontrado pero sin permiso
            raise HTTPException(status_code=403, detail="Permiso de acceso denegado por el administrador.")
    else:
        # Usuario no encontrado
        raise HTTPException(status_code=404, detail="Nombre de usuario no encontrado.")

@app.get("/sincronizar_datos", summary="Proporciona datos de sincronización a una Hija")
async def obtener_datos_sync(
    # Usa 'Query' para hacer el parámetro 'usuario' obligatorio.
    usuario: str = Query(..., description="El nombre de usuario de la Hija que solicita los datos")
):
    """
    Endpoint de sincronización.
    Verifica que el usuario solicitante es válido antes de entregar
    los datos de sincronización.
    """
    if usuario not in madre_db.USER_DB:
        raise HTTPException(status_code=404, detail="Usuario solicitante desconocido.")
        
    # Si el usuario es válido, devuelve el contenido de SYNC_DATA
    return {
        "status": "sincronizacion_exitosa",
        "datos": madre_db.SYNC_DATA
    }

@app.get("/", summary="Endpoint raíz de estado")
async def root():
    """
    Endpoint simple para verificar que el servidor está en línea.
    """
    return {"mensaje": "Servidor de la Aplicación Madre está en línea."}
