# madre_db.py
#
# Base de datos SQLite para el Sistema de Gestión del Gimnasio.
# Gestiona información de socios, membresías, clases y operaciones del gimnasio.
#
# NOTA SOBRE CONCURRENCIA: Se usa threading.Lock para garantizar
# thread-safety entre la GUI administrativa y el servidor API.

import sqlite3
import threading
import os
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any, List
import json
from config.settings import get_madre_settings
from shared.logger import setup_logger

# Inicializar logger
logger = setup_logger(__name__, log_file="madre_db.log")

# Cargar configuración
settings = get_madre_settings()

# Ruta de la base de datos (from configuration)
DB_PATH = settings.DB_PATH if os.path.isabs(
    settings.DB_PATH) else os.path.join(
        os.path.dirname(__file__),
    settings.DB_PATH)

# Lock para thread-safety
db_lock = threading.Lock()

logger.info(f"Database module initialized - DB Path: {DB_PATH}")


def get_db_connection() -> sqlite3.Connection:
    """
    Crea y retorna una conexión a la base de datos.

    Returns:
        sqlite3.Connection: Conexión a la base de datos con row_factory configurado

    Raises:
        sqlite3.Error: Si hay un error al conectar con la base de datos
    """
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # Permite acceso por nombre de columna
        return conn
    except Exception as e:
        logger.error(f"Error creating database connection: {e}", exc_info=True)
        raise


def init_database() -> None:
    """
    Inicializa la base de datos con las tablas necesarias.
    Crea todas las tablas si no existen.

    Raises:
        sqlite3.Error: Si hay un error al crear las tablas
    """
    logger.info("Initializing database schema...")
    with db_lock:
        try:
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

            # Tabla de clases grupales
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS classes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    descripcion TEXT,
                    instructor TEXT,
                    duracion INTEGER NOT NULL,
                    capacidad_maxima INTEGER NOT NULL,
                    intensidad TEXT,
                    tipo TEXT,
                    created_date TEXT,
                    is_active INTEGER DEFAULT 1
                )
            ''')

            # Tabla de horarios de clases
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS class_schedules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    class_id INTEGER NOT NULL,
                    instructor TEXT,
                    dia_semana TEXT NOT NULL,
                    hora_inicio TEXT NOT NULL,
                    fecha_inicio TEXT NOT NULL,
                    fecha_fin TEXT,
                    recurrente INTEGER DEFAULT 1,
                    sala TEXT,
                    created_date TEXT,
                    FOREIGN KEY (class_id) REFERENCES classes(id)
                )
            ''')

            # Tabla de reservas de clases
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS class_bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    schedule_id INTEGER NOT NULL,
                    fecha_clase TEXT NOT NULL,
                    booking_date TEXT NOT NULL,
                    status TEXT DEFAULT 'confirmed',
                    checked_in INTEGER DEFAULT 0,
                    checkin_date TEXT,
                    cancellation_date TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (schedule_id) REFERENCES class_schedules(id),
                    UNIQUE(user_id, schedule_id, fecha_clase)
                )
            ''')

            # Tabla de lista de espera
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS class_waitlist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    schedule_id INTEGER NOT NULL,
                    fecha_clase TEXT NOT NULL,
                    added_date TEXT NOT NULL,
                    notified_date TEXT,
                    confirmation_deadline TEXT,
                    status TEXT DEFAULT 'waiting',
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (schedule_id) REFERENCES class_schedules(id)
                )
            ''')

            # Tabla de calificaciones de clases
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS class_ratings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    class_id INTEGER NOT NULL,
                    schedule_id INTEGER NOT NULL,
                    fecha_clase TEXT NOT NULL,
                    rating INTEGER NOT NULL,
                    instructor_rating INTEGER,
                    comentario TEXT,
                    rating_date TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (class_id) REFERENCES classes(id),
                    FOREIGN KEY (schedule_id) REFERENCES class_schedules(id)
                )
            ''')

            # Tabla de equipos y zonas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS equipment_zones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    descripcion TEXT,
                    cantidad INTEGER DEFAULT 1,
                    duracion_slot INTEGER DEFAULT 60,
                    reservable INTEGER DEFAULT 1,
                    qr_code TEXT,
                    ubicacion TEXT,
                    created_date TEXT,
                    is_active INTEGER DEFAULT 1
                )
            ''')

            # Tabla de reservas de equipos/zonas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS equipment_reservations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    equipment_id INTEGER NOT NULL,
                    fecha_reserva TEXT NOT NULL,
                    hora_inicio TEXT NOT NULL,
                    hora_fin TEXT NOT NULL,
                    booking_date TEXT NOT NULL,
                    status TEXT DEFAULT 'confirmed',
                    checked_in INTEGER DEFAULT 0,
                    checkin_date TEXT,
                    cancellation_date TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (equipment_id) REFERENCES equipment_zones(id)
                )
            ''')

            # Tabla de ejercicios
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS exercises (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    descripcion TEXT,
                    categoria TEXT,
                    equipo_necesario TEXT,
                    video_url TEXT,
                    instrucciones TEXT,
                    created_date TEXT
                )
            ''')

            # Tabla de logs de entrenamiento
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS workout_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    exercise_id INTEGER NOT NULL,
                    fecha TEXT NOT NULL,
                    serie INTEGER NOT NULL,
                    repeticiones INTEGER NOT NULL,
                    peso REAL,
                    unidad TEXT DEFAULT 'kg',
                    notas TEXT,
                    descanso_segundos INTEGER,
                    log_date TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (exercise_id) REFERENCES exercises(id)
                )
            ''')

            # Tabla de tokens de check-in (QR/NFC)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS checkin_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    token_type TEXT DEFAULT 'qr',
                    generated_date TEXT NOT NULL,
                    expires_date TEXT,
                    is_active INTEGER DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

            # Tabla de historial de check-ins
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS checkin_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    checkin_date TEXT NOT NULL,
                    checkout_date TEXT,
                    checkin_method TEXT DEFAULT 'manual',
                    location TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

            # Tabla de notificaciones
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    tipo TEXT NOT NULL,
                    titulo TEXT NOT NULL,
                    mensaje TEXT NOT NULL,
                    data TEXT,
                    created_date TEXT NOT NULL,
                    read_date TEXT,
                    is_read INTEGER DEFAULT 0,
                    action_url TEXT,
                    expires_date TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

            # Tabla de preferencias de usuario
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    calendar_sync_enabled INTEGER DEFAULT 0,
                    calendar_type TEXT,
                    notification_class_reminder INTEGER DEFAULT 1,
                    notification_waitlist INTEGER DEFAULT 1,
                    notification_class_rating INTEGER DEFAULT 1,
                    reminder_time_minutes INTEGER DEFAULT 60,
                    auto_checkin_enabled INTEGER DEFAULT 0,
                    updated_date TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    UNIQUE(user_id)
                )
            ''')

            conn.commit()
            conn.close()
            logger.info("Database schema initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}", exc_info=True)
            raise


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
                except BaseException:
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
            f.write(f"\n{'-' * 60}\n\n")
            f.write(message['body'])
            f.write(f"\n\n{'-' * 60}\n")

            attachments = get_message_attachments(message_id)
            if attachments:
                f.write(f"\nAdjuntos ({len(attachments)}):\n")
                for att in attachments:
                    f.write(f"  - {att['filename']} ({att['file_size']} bytes)\n")

        return True
    except Exception as e:
        logger.error(f"Error exportando mensaje: {e}", exc_info=True)
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


# ============================================================================
# GESTIÓN DE CLASES Y RESERVAS
# ============================================================================

def create_class(nombre: str, descripcion: str, instructor: str, duracion: int,
                 capacidad_maxima: int, intensidad: str = "media", tipo: str = "grupal") -> Optional[int]:
    """Crea una nueva clase."""
    with db_lock:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            created_date = datetime.now().isoformat()

            cursor.execute('''
                INSERT INTO classes (nombre, descripcion, instructor, duracion,
                                   capacidad_maxima, intensidad, tipo, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (nombre, descripcion, instructor, duracion, capacidad_maxima,
                  intensidad, tipo, created_date))

            conn.commit()
            class_id = cursor.lastrowid
            conn.close()
            logger.info(f"Class created: {nombre} (ID: {class_id})")
            return class_id
        except Exception as e:
            logger.error(f"Error creating class: {e}", exc_info=True)
            return None


def get_all_classes(active_only: bool = True) -> List[Dict[str, Any]]:
    """Obtiene todas las clases."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()

        if active_only:
            cursor.execute('SELECT * FROM classes WHERE is_active = 1 ORDER BY nombre')
        else:
            cursor.execute('SELECT * FROM classes ORDER BY nombre')

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


def get_class(class_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene una clase por ID."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM classes WHERE id = ?', (class_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None


def create_class_schedule(class_id: int, instructor: str, dia_semana: str,
                          hora_inicio: str, fecha_inicio: str, fecha_fin: str = None,
                          recurrente: bool = True, sala: str = "") -> Optional[int]:
    """Crea un horario para una clase."""
    with db_lock:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            created_date = datetime.now().isoformat()

            cursor.execute('''
                INSERT INTO class_schedules (class_id, instructor, dia_semana, hora_inicio,
                                            fecha_inicio, fecha_fin, recurrente, sala, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (class_id, instructor, dia_semana, hora_inicio, fecha_inicio,
                  fecha_fin, 1 if recurrente else 0, sala, created_date))

            conn.commit()
            schedule_id = cursor.lastrowid
            conn.close()
            logger.info(f"Schedule created for class {class_id} (ID: {schedule_id})")
            return schedule_id
        except Exception as e:
            logger.error(f"Error creating schedule: {e}", exc_info=True)
            return None


def get_class_schedules(class_id: int = None) -> List[Dict[str, Any]]:
    """Obtiene horarios de clases."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()

        if class_id:
            cursor.execute('''
                SELECT cs.*, c.nombre as class_nombre, c.capacidad_maxima, c.intensidad, c.tipo
                FROM class_schedules cs
                JOIN classes c ON cs.class_id = c.id
                WHERE cs.class_id = ?
                ORDER BY cs.dia_semana, cs.hora_inicio
            ''', (class_id,))
        else:
            cursor.execute('''
                SELECT cs.*, c.nombre as class_nombre, c.capacidad_maxima, c.intensidad, c.tipo
                FROM class_schedules cs
                JOIN classes c ON cs.class_id = c.id
                WHERE c.is_active = 1
                ORDER BY cs.dia_semana, cs.hora_inicio
            ''')

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


def book_class(user_id: int, schedule_id: int, fecha_clase: str) -> tuple[bool, str]:
    """Reserva una clase para un usuario (One-Click Booking)."""
    with db_lock:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Verificar capacidad
            cursor.execute('''
                SELECT cs.class_id, c.capacidad_maxima,
                       (SELECT COUNT(*) FROM class_bookings
                        WHERE schedule_id = cs.id AND fecha_clase = ? AND status = 'confirmed') as bookings_count
                FROM class_schedules cs
                JOIN classes c ON cs.class_id = c.id
                WHERE cs.id = ?
            ''', (fecha_clase, schedule_id))

            result = cursor.fetchone()
            if not result:
                conn.close()
                return False, "Clase no encontrada"

            capacidad_maxima = result['capacidad_maxima']
            bookings_count = result['bookings_count']

            if bookings_count >= capacidad_maxima:
                conn.close()
                return False, "Clase llena - se agregó a lista de espera"

            # Verificar si ya está reservado
            cursor.execute('''
                SELECT id FROM class_bookings
                WHERE user_id = ? AND schedule_id = ? AND fecha_clase = ?
            ''', (user_id, schedule_id, fecha_clase))

            if cursor.fetchone():
                conn.close()
                return False, "Ya tienes una reserva para esta clase"

            # Crear reserva
            booking_date = datetime.now().isoformat()
            cursor.execute('''
                INSERT INTO class_bookings (user_id, schedule_id, fecha_clase, booking_date, status)
                VALUES (?, ?, ?, ?, 'confirmed')
            ''', (user_id, schedule_id, fecha_clase, booking_date))

            conn.commit()
            conn.close()
            logger.info(f"Class booked: User {user_id}, Schedule {schedule_id}, Date {fecha_clase}")
            return True, "Reserva confirmada exitosamente"
        except sqlite3.IntegrityError:
            return False, "Error: Ya existe una reserva"
        except Exception as e:
            logger.error(f"Error booking class: {e}", exc_info=True)
            return False, "Error al procesar la reserva"


def cancel_booking(booking_id: int) -> tuple[bool, str]:
    """Cancela una reserva de clase."""
    with db_lock:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cancellation_date = datetime.now().isoformat()
            cursor.execute('''
                UPDATE class_bookings
                SET status = 'cancelled', cancellation_date = ?
                WHERE id = ? AND status = 'confirmed'
            ''', (cancellation_date, booking_id))

            conn.commit()
            success = cursor.rowcount > 0

            if success:
                # Obtener información de la reserva para notificar lista de espera
                cursor.execute('''
                    SELECT schedule_id, fecha_clase FROM class_bookings WHERE id = ?
                ''', (booking_id,))
                booking_info = cursor.fetchone()

                if booking_info:
                    # Notificar al primero en lista de espera
                    schedule_id = booking_info['schedule_id']
                    fecha_clase = booking_info['fecha_clase']
                    notify_waitlist(conn, cursor, schedule_id, fecha_clase)

            conn.close()

            if success:
                logger.info(f"Booking cancelled: {booking_id}")
                return True, "Reserva cancelada exitosamente"
            else:
                return False, "No se pudo cancelar la reserva"
        except Exception as e:
            logger.error(f"Error cancelling booking: {e}", exc_info=True)
            return False, "Error al procesar la cancelación"


def notify_waitlist(conn, cursor, schedule_id: int, fecha_clase: str):
    """Notifica al primero en lista de espera cuando se libera un cupo."""
    try:
        # Obtener primero en lista de espera
        cursor.execute('''
            SELECT id, user_id FROM class_waitlist
            WHERE schedule_id = ? AND fecha_clase = ? AND status = 'waiting'
            ORDER BY added_date
            LIMIT 1
        ''', (schedule_id, fecha_clase))

        waitlist_entry = cursor.fetchone()
        if not waitlist_entry:
            return

        waitlist_id = waitlist_entry['id']
        user_id = waitlist_entry['user_id']

        # Crear notificación con temporizador de 10 minutos
        from datetime import timedelta
        expires_date = (datetime.now() + timedelta(minutes=10)).isoformat()

        cursor.execute('''
            INSERT INTO notifications (user_id, tipo, titulo, mensaje, data, created_date, expires_date)
            VALUES (?, 'waitlist_spot_available', 'Cupo Disponible',
                    'Se liberó un cupo en tu clase. Tienes 10 minutos para confirmar.',
                    ?, ?, ?)
        ''', (user_id, json.dumps({'schedule_id': schedule_id, 'fecha_clase': fecha_clase}),
              datetime.now().isoformat(), expires_date))

        # Actualizar lista de espera
        cursor.execute('''
            UPDATE class_waitlist
            SET status = 'notified', notified_date = ?, confirmation_deadline = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), expires_date, waitlist_id))

        conn.commit()
        logger.info(f"Waitlist notification sent to user {user_id}")
    except Exception as e:
        logger.error(f"Error notifying waitlist: {e}", exc_info=True)


def add_to_waitlist(user_id: int, schedule_id: int, fecha_clase: str) -> tuple[bool, str]:
    """Agrega un usuario a la lista de espera."""
    with db_lock:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            added_date = datetime.now().isoformat()
            cursor.execute('''
                INSERT INTO class_waitlist (user_id, schedule_id, fecha_clase, added_date, status)
                VALUES (?, ?, ?, ?, 'waiting')
            ''', (user_id, schedule_id, fecha_clase, added_date))

            conn.commit()
            conn.close()
            logger.info(f"User {user_id} added to waitlist for schedule {schedule_id}")
            return True, "Agregado a lista de espera"
        except Exception as e:
            logger.error(f"Error adding to waitlist: {e}", exc_info=True)
            return False, "Error al agregar a lista de espera"


def get_user_bookings(user_id: int, fecha_desde: str = None) -> List[Dict[str, Any]]:
    """Obtiene las reservas de un usuario."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()

        if fecha_desde:
            cursor.execute('''
                SELECT cb.*, cs.dia_semana, cs.hora_inicio, cs.sala,
                       c.nombre as class_nombre, c.instructor, c.duracion
                FROM class_bookings cb
                JOIN class_schedules cs ON cb.schedule_id = cs.id
                JOIN classes c ON cs.class_id = c.id
                WHERE cb.user_id = ? AND cb.fecha_clase >= ? AND cb.status = 'confirmed'
                ORDER BY cb.fecha_clase, cs.hora_inicio
            ''', (user_id, fecha_desde))
        else:
            cursor.execute('''
                SELECT cb.*, cs.dia_semana, cs.hora_inicio, cs.sala,
                       c.nombre as class_nombre, c.instructor, c.duracion
                FROM class_bookings cb
                JOIN class_schedules cs ON cb.schedule_id = cs.id
                JOIN classes c ON cs.class_id = c.id
                WHERE cb.user_id = ? AND cb.status = 'confirmed'
                ORDER BY cb.fecha_clase, cs.hora_inicio
            ''', (user_id,))

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


def rate_class(user_id: int, class_id: int, schedule_id: int, fecha_clase: str,
               rating: int, instructor_rating: int = None, comentario: str = "") -> tuple[bool, str]:
    """Califica una clase después de asistir."""
    with db_lock:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            rating_date = datetime.now().isoformat()
            cursor.execute('''
                INSERT INTO class_ratings (user_id, class_id, schedule_id, fecha_clase,
                                          rating, instructor_rating, comentario, rating_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, class_id, schedule_id, fecha_clase, rating,
                  instructor_rating, comentario, rating_date))

            conn.commit()
            conn.close()
            logger.info(f"Class rated: User {user_id}, Class {class_id}, Rating {rating}")
            return True, "Calificación enviada exitosamente"
        except Exception as e:
            logger.error(f"Error rating class: {e}", exc_info=True)
            return False, "Error al enviar calificación"


# ============================================================================
# GESTIÓN DE EQUIPOS Y ZONAS
# ============================================================================

def create_equipment_zone(nombre: str, tipo: str, descripcion: str = "",
                          cantidad: int = 1, duracion_slot: int = 60) -> Optional[int]:
    """Crea un equipo o zona reservable."""
    with db_lock:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            created_date = datetime.now().isoformat()

            cursor.execute('''
                INSERT INTO equipment_zones (nombre, tipo, descripcion, cantidad,
                                            duracion_slot, created_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (nombre, tipo, descripcion, cantidad, duracion_slot, created_date))

            conn.commit()
            equipment_id = cursor.lastrowid
            conn.close()
            logger.info(f"Equipment/zone created: {nombre} (ID: {equipment_id})")
            return equipment_id
        except Exception as e:
            logger.error(f"Error creating equipment/zone: {e}", exc_info=True)
            return None


def get_all_equipment_zones(active_only: bool = True) -> List[Dict[str, Any]]:
    """Obtiene todos los equipos y zonas."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()

        if active_only:
            cursor.execute('SELECT * FROM equipment_zones WHERE is_active = 1 AND reservable = 1 ORDER BY nombre')
        else:
            cursor.execute('SELECT * FROM equipment_zones ORDER BY nombre')

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


def reserve_equipment(user_id: int, equipment_id: int, fecha_reserva: str,
                      hora_inicio: str, hora_fin: str) -> tuple[bool, str]:
    """Reserva un equipo o zona."""
    with db_lock:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Verificar disponibilidad
            cursor.execute('''
                SELECT COUNT(*) as count FROM equipment_reservations
                WHERE equipment_id = ? AND fecha_reserva = ? AND status = 'confirmed'
                AND ((hora_inicio < ? AND hora_fin > ?) OR
                     (hora_inicio < ? AND hora_fin > ?) OR
                     (hora_inicio >= ? AND hora_fin <= ?))
            ''', (equipment_id, fecha_reserva, hora_fin, hora_inicio,
                  hora_fin, hora_inicio, hora_inicio, hora_fin))

            result = cursor.fetchone()
            if result['count'] > 0:
                conn.close()
                return False, "Equipo/zona no disponible en ese horario"

            # Crear reserva
            booking_date = datetime.now().isoformat()
            cursor.execute('''
                INSERT INTO equipment_reservations
                (user_id, equipment_id, fecha_reserva, hora_inicio, hora_fin, booking_date, status)
                VALUES (?, ?, ?, ?, ?, ?, 'confirmed')
            ''', (user_id, equipment_id, fecha_reserva, hora_inicio, hora_fin, booking_date))

            conn.commit()
            conn.close()
            logger.info(f"Equipment reserved: User {user_id}, Equipment {equipment_id}")
            return True, "Reserva confirmada exitosamente"
        except Exception as e:
            logger.error(f"Error reserving equipment: {e}", exc_info=True)
            return False, "Error al reservar equipo"


# ============================================================================
# GESTIÓN DE WORKOUT LOGS
# ============================================================================

def create_exercise(nombre: str, descripcion: str = "", categoria: str = "",
                    equipo_necesario: str = "") -> Optional[int]:
    """Crea un ejercicio."""
    with db_lock:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            created_date = datetime.now().isoformat()

            cursor.execute('''
                INSERT INTO exercises (nombre, descripcion, categoria, equipo_necesario, created_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (nombre, descripcion, categoria, equipo_necesario, created_date))

            conn.commit()
            exercise_id = cursor.lastrowid
            conn.close()
            logger.info(f"Exercise created: {nombre} (ID: {exercise_id})")
            return exercise_id
        except Exception as e:
            logger.error(f"Error creating exercise: {e}", exc_info=True)
            return None


def log_workout(user_id: int, exercise_id: int, fecha: str, serie: int,
                repeticiones: int, peso: float = None, descanso_segundos: int = None) -> Optional[int]:
    """Registra una serie de ejercicio (Quick Log)."""
    with db_lock:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            log_date = datetime.now().isoformat()

            cursor.execute('''
                INSERT INTO workout_logs (user_id, exercise_id, fecha, serie, repeticiones,
                                         peso, descanso_segundos, log_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, exercise_id, fecha, serie, repeticiones, peso, descanso_segundos, log_date))

            conn.commit()
            log_id = cursor.lastrowid
            conn.close()
            logger.info(f"Workout logged: User {user_id}, Exercise {exercise_id}")
            return log_id
        except Exception as e:
            logger.error(f"Error logging workout: {e}", exc_info=True)
            return None


def get_exercise_history(user_id: int, exercise_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """Obtiene el historial de un ejercicio."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM workout_logs
            WHERE user_id = ? AND exercise_id = ?
            ORDER BY fecha DESC, serie DESC
            LIMIT ?
        ''', (user_id, exercise_id, limit))

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


def get_all_exercises() -> List[Dict[str, Any]]:
    """Obtiene todos los ejercicios."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM exercises ORDER BY nombre')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


# ============================================================================
# GESTIÓN DE CHECK-IN Y TOKENS
# ============================================================================

def generate_checkin_token(user_id: int, token_type: str = "qr") -> tuple[bool, str]:
    """Genera un token de check-in (QR/NFC)."""
    with db_lock:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Generar token único
            import secrets
            token = secrets.token_urlsafe(32)
            generated_date = datetime.now().isoformat()

            cursor.execute('''
                INSERT INTO checkin_tokens (user_id, token, token_type, generated_date)
                VALUES (?, ?, ?, ?)
            ''', (user_id, token, token_type, generated_date))

            conn.commit()
            conn.close()
            logger.info(f"Check-in token generated for user {user_id}")
            return True, token
        except Exception as e:
            logger.error(f"Error generating check-in token: {e}", exc_info=True)
            return False, ""


def checkin_user(user_id: int, location: str = "entrada") -> tuple[bool, str]:
    """Registra check-in de usuario."""
    with db_lock:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            checkin_date = datetime.now().isoformat()
            cursor.execute('''
                INSERT INTO checkin_history (user_id, checkin_date, location)
                VALUES (?, ?, ?)
            ''', (user_id, checkin_date, location))

            conn.commit()
            conn.close()
            logger.info(f"User {user_id} checked in at {location}")
            return True, "Check-in exitoso"
        except Exception as e:
            logger.error(f"Error checking in user: {e}", exc_info=True)
            return False, "Error al registrar check-in"


# ============================================================================
# GESTIÓN DE NOTIFICACIONES
# ============================================================================

def create_notification(user_id: int, tipo: str, titulo: str, mensaje: str,
                        data: str = "", action_url: str = "", expires_date: str = None) -> Optional[int]:
    """Crea una notificación."""
    with db_lock:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            created_date = datetime.now().isoformat()

            cursor.execute('''
                INSERT INTO notifications (user_id, tipo, titulo, mensaje, data,
                                          created_date, action_url, expires_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, tipo, titulo, mensaje, data, created_date, action_url, expires_date))

            conn.commit()
            notification_id = cursor.lastrowid
            conn.close()
            logger.info(f"Notification created for user {user_id}")
            return notification_id
        except Exception as e:
            logger.error(f"Error creating notification: {e}", exc_info=True)
            return None


def get_user_notifications(user_id: int, unread_only: bool = False) -> List[Dict[str, Any]]:
    """Obtiene notificaciones de un usuario."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()

        if unread_only:
            cursor.execute('''
                SELECT * FROM notifications
                WHERE user_id = ? AND is_read = 0
                ORDER BY created_date DESC
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT * FROM notifications
                WHERE user_id = ?
                ORDER BY created_date DESC
            ''', (user_id,))

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


init_database()
