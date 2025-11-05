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
        
        # Tabla de mensajes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_user TEXT NOT NULL,
                to_user TEXT NOT NULL,
                subject TEXT,
                body TEXT NOT NULL,
                sent_date TEXT NOT NULL,
                read_date TEXT,
                is_read INTEGER DEFAULT 0,
                parent_message_id INTEGER,
                FOREIGN KEY (parent_message_id) REFERENCES messages(id)
            )
        ''')
        
        # Tabla de adjuntos de mensajes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS message_attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                upload_date TEXT NOT NULL,
                FOREIGN KEY (message_id) REFERENCES messages(id)
            )
        ''')
        
        # Tabla de mensajes de chat en vivo
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_user TEXT NOT NULL,
                to_user TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                is_read INTEGER DEFAULT 0
            )
        ''')
        
        # Tabla de servidores madre para sincronización multi-madre
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS madre_servers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_name TEXT UNIQUE NOT NULL,
                server_url TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                last_sync TEXT,
                sync_token TEXT
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

# ============================================================================
# FUNCIONES DE MENSAJERÍA
# ============================================================================

def send_message(from_user: str, to_user: str, subject: str, body: str, 
                 parent_message_id: Optional[int] = None) -> Optional[int]:
    """Envía un mensaje. Retorna el ID del mensaje creado."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sent_date = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO messages (from_user, to_user, subject, body, sent_date, parent_message_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (from_user, to_user, subject, body, sent_date, parent_message_id))
        
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return message_id

def add_message_attachment(message_id: int, filename: str, file_path: str, file_size: int) -> bool:
    """Añade un adjunto a un mensaje."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        upload_date = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO message_attachments (message_id, filename, file_path, file_size, upload_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (message_id, filename, file_path, file_size, upload_date))
        
        conn.commit()
        conn.close()
        return True

def get_user_messages(username: str, include_read: bool = True) -> List[Dict[str, Any]]:
    """Obtiene todos los mensajes de un usuario (recibidos)."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if include_read:
            cursor.execute('''
                SELECT * FROM messages 
                WHERE to_user = ? 
                ORDER BY sent_date DESC
            ''', (username,))
        else:
            cursor.execute('''
                SELECT * FROM messages 
                WHERE to_user = ? AND is_read = 0 
                ORDER BY sent_date DESC
            ''', (username,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

def get_message_by_id(message_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene un mensaje específico."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM messages WHERE id = ?', (message_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None

def mark_message_read(message_id: int) -> bool:
    """Marca un mensaje como leído."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        read_date = datetime.now().isoformat()
        cursor.execute('''
            UPDATE messages SET is_read = 1, read_date = ? WHERE id = ?
        ''', (read_date, message_id))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

def delete_message(message_id: int) -> bool:
    """Elimina un mensaje."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Primero eliminar adjuntos
        cursor.execute('DELETE FROM message_attachments WHERE message_id = ?', (message_id,))
        # Luego eliminar mensaje
        cursor.execute('DELETE FROM messages WHERE id = ?', (message_id,))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

def get_message_attachments(message_id: int) -> List[Dict[str, Any]]:
    """Obtiene los adjuntos de un mensaje."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM message_attachments 
            WHERE message_id = ? 
            ORDER BY upload_date
        ''', (message_id,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

def count_unread_messages(username: str) -> int:
    """Cuenta los mensajes no leídos de un usuario."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as count FROM messages 
            WHERE to_user = ? AND is_read = 0
        ''', (username,))
        
        row = cursor.fetchone()
        conn.close()
        return row['count'] if row else 0

def export_message_to_txt(message_id: int, output_path: str) -> bool:
    """Exporta un mensaje a archivo .txt."""
    message = get_message_by_id(message_id)
    if not message:
        return False
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"De: {message['from_user']}\n")
            f.write(f"Para: {message['to_user']}\n")
            f.write(f"Asunto: {message['subject']}\n")
            f.write(f"Fecha: {message['sent_date']}\n")
            f.write(f"\n{'-'*60}\n\n")
            f.write(message['body'])
            f.write(f"\n\n{'-'*60}\n")
            
            attachments = get_message_attachments(message_id)
            if attachments:
                f.write(f"\nAdjuntos ({len(attachments)}):\n")
                for att in attachments:
                    f.write(f"  - {att['filename']} ({att['file_size']} bytes)\n")
        
        return True
    except Exception as e:
        print(f"Error exportando mensaje: {e}")
        return False

# ============================================================================
# FUNCIONES DE CHAT EN VIVO
# ============================================================================

def send_chat_message(from_user: str, to_user: str, message: str) -> Optional[int]:
    """Envía un mensaje de chat en vivo."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO chat_messages (from_user, to_user, message, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (from_user, to_user, message, timestamp))
        
        chat_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return chat_id

def get_chat_history(user1: str, user2: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Obtiene el historial de chat entre dos usuarios."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM chat_messages 
            WHERE (from_user = ? AND to_user = ?) OR (from_user = ? AND to_user = ?)
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user1, user2, user2, user1, limit))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in reversed(rows)]

def mark_chat_messages_read(from_user: str, to_user: str) -> bool:
    """Marca los mensajes de chat como leídos."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE chat_messages SET is_read = 1 
            WHERE from_user = ? AND to_user = ? AND is_read = 0
        ''', (from_user, to_user))
        
        conn.commit()
        conn.close()
        return True

def count_unread_chat_messages(username: str) -> int:
    """Cuenta los mensajes de chat no leídos para un usuario."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as count FROM chat_messages 
            WHERE to_user = ? AND is_read = 0
        ''', (username,))
        
        row = cursor.fetchone()
        conn.close()
        return row['count'] if row else 0

# ============================================================================
# FUNCIONES DE MULTI-MADRE (SINCRONIZACIÓN ENTRE SERVIDORES)
# ============================================================================

def add_madre_server(server_name: str, server_url: str, sync_token: str = "") -> bool:
    """Añade un servidor Madre para sincronización."""
    with db_lock:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO madre_servers (server_name, server_url, sync_token)
                VALUES (?, ?, ?)
            ''', (server_name, server_url, sync_token))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

def get_all_madre_servers() -> List[Dict[str, Any]]:
    """Obtiene todos los servidores Madre registrados."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM madre_servers WHERE is_active = 1')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

def update_madre_server_sync(server_name: str) -> bool:
    """Actualiza la última sincronización de un servidor Madre."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        last_sync = datetime.now().isoformat()
        cursor.execute('''
            UPDATE madre_servers SET last_sync = ? WHERE server_name = ?
        ''', (last_sync, server_name))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

# Inicializar la base de datos al importar el módulo
init_database()
