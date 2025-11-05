# madre_db.py
#
# Base de datos SQLite real para el sistema Madre-Hija.
# Reemplaza la simulación en memoria con persistencia real.
#
# NOTA SOBRE CONCURRENCIA: Se usa threading.Lock para garantizar 
# thread-safety entre la GUI y el servidor API.

import sqlite3
import threading
import os
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any, List
import json

# Ruta de la base de datos
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'gym_database.db')

# Lock para thread-safety
db_lock = threading.Lock()

def get_db_connection():
    """Crea y retorna una conexión a la base de datos."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Permite acceso por nombre de columna
    return conn

def init_database():
    """Inicializa la base de datos con las tablas necesarias."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                permiso_acceso INTEGER DEFAULT 1,
                nombre_completo TEXT,
                email TEXT,
                telefono TEXT,
                fecha_registro TEXT,
                equipo TEXT,
                last_sync TEXT
            )
        ''')
        
        # Tabla de fotos de perfil
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS profile_photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                photo_path TEXT NOT NULL,
                upload_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Tabla de cronogramas de entrenamiento
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                mes TEXT NOT NULL,
                ano INTEGER NOT NULL,
                schedule_data TEXT NOT NULL,
                created_date TEXT,
                modified_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Tabla de galería de fotos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS photo_gallery (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                photo_path TEXT NOT NULL,
                descripcion TEXT,
                upload_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Tabla de datos de sincronización global
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contenido TEXT NOT NULL,
                metadatos_version TEXT NOT NULL,
                update_date TEXT
            )
        ''')
        
        conn.commit()
        conn.close()

def hash_password(password: str) -> str:
    """Hash de contraseña usando SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    """Verifica una contraseña contra su hash."""
    return hash_password(password) == password_hash

def create_user(username: str, password: str, nombre_completo: str, 
                email: str = "", telefono: str = "", equipo: str = "",
                permiso_acceso: bool = True) -> bool:
    """Crea un nuevo usuario en la base de datos."""
    with db_lock:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            password_hash = hash_password(password)
            fecha_registro = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO users (username, password_hash, permiso_acceso, 
                                 nombre_completo, email, telefono, equipo, fecha_registro)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, password_hash, 1 if permiso_acceso else 0,
                  nombre_completo, email, telefono, equipo, fecha_registro))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

def get_user(username: str) -> Optional[Dict[str, Any]]:
    """Obtiene los datos de un usuario."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None

def get_all_users() -> List[Dict[str, Any]]:
    """Obtiene todos los usuarios."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users ORDER BY username')
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]

def update_user_permission(username: str, permiso_acceso: bool) -> bool:
    """Actualiza el permiso de acceso de un usuario."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET permiso_acceso = ? WHERE username = ?
        ''', (1 if permiso_acceso else 0, username))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

def update_user_sync(username: str) -> bool:
    """Actualiza la última fecha de sincronización del usuario."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        last_sync = datetime.now().isoformat()
        cursor.execute('''
            UPDATE users SET last_sync = ? WHERE username = ?
        ''', (last_sync, username))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

def authenticate_user(username: str, password: str) -> tuple[bool, Optional[Dict[str, Any]]]:
    """Autentica un usuario con contraseña."""
    user = get_user(username)
    if not user:
        return False, None
    
    if verify_password(password, user['password_hash']):
        return True, user
    return False, None

def get_user_profile_photo(user_id: int) -> Optional[str]:
    """Obtiene la ruta de la foto de perfil del usuario."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT photo_path FROM profile_photos 
            WHERE user_id = ? 
            ORDER BY upload_date DESC LIMIT 1
        ''', (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return row['photo_path']
        return None

def set_user_profile_photo(user_id: int, photo_path: str) -> bool:
    """Establece la foto de perfil del usuario."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        upload_date = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO profile_photos (user_id, photo_path, upload_date)
            VALUES (?, ?, ?)
        ''', (user_id, photo_path, upload_date))
        
        conn.commit()
        conn.close()
        return True

def get_training_schedule(user_id: int, mes: str = None, ano: int = None) -> Optional[Dict[str, Any]]:
    """Obtiene el cronograma de entrenamiento del usuario."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if mes and ano:
            cursor.execute('''
                SELECT * FROM training_schedules 
                WHERE user_id = ? AND mes = ? AND ano = ?
                ORDER BY modified_date DESC LIMIT 1
            ''', (user_id, mes, ano))
        else:
            cursor.execute('''
                SELECT * FROM training_schedules 
                WHERE user_id = ? 
                ORDER BY modified_date DESC LIMIT 1
            ''', (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            schedule = dict(row)
            schedule['schedule_data'] = json.loads(schedule['schedule_data'])
            return schedule
        return None

def save_training_schedule(user_id: int, mes: str, ano: int, schedule_data: Dict) -> bool:
    """Guarda o actualiza el cronograma de entrenamiento."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        schedule_json = json.dumps(schedule_data, ensure_ascii=False)
        
        # Verificar si existe
        cursor.execute('''
            SELECT id FROM training_schedules 
            WHERE user_id = ? AND mes = ? AND ano = ?
        ''', (user_id, mes, ano))
        
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute('''
                UPDATE training_schedules 
                SET schedule_data = ?, modified_date = ?
                WHERE id = ?
            ''', (schedule_json, now, existing['id']))
        else:
            cursor.execute('''
                INSERT INTO training_schedules 
                (user_id, mes, ano, schedule_data, created_date, modified_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, mes, ano, schedule_json, now, now))
        
        conn.commit()
        conn.close()
        return True

def get_photo_gallery(user_id: int) -> List[Dict[str, Any]]:
    """Obtiene todas las fotos de la galería del usuario."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM photo_gallery 
            WHERE user_id = ? 
            ORDER BY upload_date DESC
        ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]

def add_photo_to_gallery(user_id: int, photo_path: str, descripcion: str = "") -> bool:
    """Añade una foto a la galería del usuario."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        upload_date = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO photo_gallery (user_id, photo_path, descripcion, upload_date)
            VALUES (?, ?, ?, ?)
        ''', (user_id, photo_path, descripcion, upload_date))
        
        conn.commit()
        conn.close()
        return True

def get_sync_data() -> Dict[str, Any]:
    """Obtiene los datos de sincronización global."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT contenido, metadatos_version FROM sync_data 
            ORDER BY id DESC LIMIT 1
        ''')
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "contenido": row['contenido'],
                "metadatos_version": row['metadatos_version']
            }
        return {
            "contenido": "Contenido inicial del sistema.",
            "metadatos_version": "1.0.0"
        }

def update_sync_data(contenido: str, version: str = None) -> bool:
    """Actualiza los datos de sincronización global."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if version is None:
            # Obtener versión actual e incrementar
            cursor.execute('SELECT metadatos_version FROM sync_data ORDER BY id DESC LIMIT 1')
            row = cursor.fetchone()
            if row:
                try:
                    parts = row['metadatos_version'].split('.')
                    version = f"{parts[0]}.{int(parts[1]) + 1}.0"
                except:
                    version = "1.1.0"
            else:
                version = "1.0.0"
        
        update_date = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO sync_data (contenido, metadatos_version, update_date)
            VALUES (?, ?, ?)
        ''', (contenido, version, update_date))
        
        conn.commit()
        conn.close()
        return True

# Inicializar la base de datos al importar el módulo
init_database()
