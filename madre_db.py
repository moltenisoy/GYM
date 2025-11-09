import sqlite3
import threading
import os
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any, List
import json
from config.settings import get_madre_settings
from shared.logger import setup_logger

logger = setup_logger(__name__, log_file="madre_db.log")

settings = get_madre_settings()

DB_PATH = settings.DB_PATH if os.path.isabs(
    settings.DB_PATH) else os.path.join(
        os.path.dirname(__file__),
    settings.DB_PATH)

db_lock = threading.Lock()

logger.info(f"Database module initialized - DB Path: {DB_PATH}")

def get_db_connection() -> sqlite3.Connection:
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f"Error creating database connection: {e}", exc_info=True)
        raise

def init_database() -> None:
    logger.info("Initializing database schema...")
    with db_lock:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

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
                CREATE TABLE IF NOT EXISTS profile_photos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    photo_path TEXT NOT NULL,
                    upload_date TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
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
                CREATE TABLE IF NOT EXISTS photo_gallery (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    photo_path TEXT NOT NULL,
                    descripcion TEXT,
                    upload_date TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
                CREATE TABLE IF NOT EXISTS sync_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contenido TEXT NOT NULL,
                    metadatos_version TEXT NOT NULL,
                    update_date TEXT
                )
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
                CREATE TABLE IF NOT EXISTS message_attachments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id INTEGER NOT NULL,
                    filename TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    upload_date TEXT NOT NULL,
                    FOREIGN KEY (message_id) REFERENCES messages(id)
                )
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_user TEXT NOT NULL,
                    to_user TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    is_read INTEGER DEFAULT 0
                )
                CREATE TABLE IF NOT EXISTS madre_servers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_name TEXT UNIQUE NOT NULL,
                    server_url TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    last_sync TEXT,
                    sync_token TEXT
                )
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
                CREATE TABLE IF NOT EXISTS checkin_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    checkin_date TEXT NOT NULL,
                    checkout_date TEXT,
                    checkin_method TEXT DEFAULT 'manual',
                    location TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
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
                INSERT INTO users (username, password_hash, permiso_acceso,
                                 nombre_completo, email, telefono, equipo, fecha_registro)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

def get_all_users() -> List[Dict[str, Any]]:
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users ORDER BY username')
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

def update_user_permission(username: str, permiso_acceso: bool) -> bool:
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE users SET permiso_acceso = ? WHERE username = ?
            UPDATE users SET last_sync = ? WHERE username = ?
        return True, user
    return False, None

def get_user_profile_photo(user_id: int) -> Optional[str]:
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT photo_path FROM profile_photos
            WHERE user_id = ?
            ORDER BY upload_date DESC LIMIT 1
        return None

def set_user_profile_photo(user_id: int, photo_path: str) -> bool:
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()

        upload_date = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO profile_photos (user_id, photo_path, upload_date)
            VALUES (?, ?, ?)
                SELECT * FROM training_schedules
                WHERE user_id = ? AND mes = ? AND ano = ?
                ORDER BY modified_date DESC LIMIT 1
                SELECT * FROM training_schedules
                WHERE user_id = ?
                ORDER BY modified_date DESC LIMIT 1
            return schedule
        return None

def save_training_schedule(user_id: int, mes: str, ano: int, schedule_data: Dict) -> bool:
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        schedule_json = json.dumps(schedule_data, ensure_ascii=False)

        cursor.execute('''
            SELECT id FROM training_schedules
            WHERE user_id = ? AND mes = ? AND ano = ?
                UPDATE training_schedules
                SET schedule_data = ?, modified_date = ?
                WHERE id = ?
                INSERT INTO training_schedules
                (user_id, mes, ano, schedule_data, created_date, modified_date)
                VALUES (?, ?, ?, ?, ?, ?)
            SELECT * FROM photo_gallery
            WHERE user_id = ?
            ORDER BY upload_date DESC
            INSERT INTO photo_gallery (user_id, photo_path, descripcion, upload_date)
            VALUES (?, ?, ?, ?)
            SELECT contenido, metadatos_version FROM sync_data
            ORDER BY id DESC LIMIT 1
                "metadatos_version": row['metadatos_version']
            }
        return {
            "contenido": "Contenido inicial del sistema.",
            "metadatos_version": "1.0.0"
        }

def update_sync_data(contenido: str, version: str = None) -> bool:
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()

        if version is None:
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
            INSERT INTO messages (from_user, to_user, subject, body, sent_date, parent_message_id)
            VALUES (?, ?, ?, ?, ?, ?)
            INSERT INTO message_attachments (message_id, filename, file_path, file_size, upload_date)
            VALUES (?, ?, ?, ?, ?)
                SELECT * FROM messages
                WHERE to_user = ?
                ORDER BY sent_date DESC
                SELECT * FROM messages
                WHERE to_user = ? AND is_read = 0
                ORDER BY sent_date DESC
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

def mark_message_read(message_id: int) -> bool:
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()

        read_date = datetime.now().isoformat()
        cursor.execute('''
            UPDATE messages SET is_read = 1, read_date = ? WHERE id = ?
        cursor.execute('DELETE FROM messages WHERE id = ?', (message_id,))

        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

def get_message_attachments(message_id: int) -> List[Dict[str, Any]]:
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM message_attachments
            WHERE message_id = ?
            ORDER BY upload_date
            SELECT COUNT(*) as count FROM messages
            WHERE to_user = ? AND is_read = 0

def export_message_to_txt(message_id: int, output_path: str) -> bool:
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

def send_chat_message(from_user: str, to_user: str, message: str) -> Optional[int]:
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()

        timestamp = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO chat_messages (from_user, to_user, message, timestamp)
            VALUES (?, ?, ?, ?)
            SELECT * FROM chat_messages
            WHERE (from_user = ? AND to_user = ?) OR (from_user = ? AND to_user = ?)
            ORDER BY timestamp DESC
            LIMIT ?
            UPDATE chat_messages SET is_read = 1
            WHERE from_user = ? AND to_user = ? AND is_read = 0
            SELECT COUNT(*) as count FROM chat_messages
            WHERE to_user = ? AND is_read = 0

def add_madre_server(server_name: str, server_url: str, sync_token: str = "") -> bool:
    with db_lock:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO madre_servers (server_name, server_url, sync_token)
                VALUES (?, ?, ?)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

def update_madre_server_sync(server_name: str) -> bool:
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()

        last_sync = datetime.now().isoformat()
        cursor.execute('''
            UPDATE madre_servers SET last_sync = ? WHERE server_name = ?
                INSERT INTO classes (nombre, descripcion, instructor, duracion,
                                   capacidad_maxima, intensidad, tipo, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        else:
            cursor.execute('SELECT * FROM classes ORDER BY nombre')

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

def get_class(class_id: int) -> Optional[Dict[str, Any]]:
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
    with db_lock:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            created_date = datetime.now().isoformat()

            cursor.execute('''
                INSERT INTO class_schedules (class_id, instructor, dia_semana, hora_inicio,
                                            fecha_inicio, fecha_fin, recurrente, sala, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                SELECT cs.*, c.nombre as class_nombre, c.capacidad_maxima, c.intensidad, c.tipo
                FROM class_schedules cs
                JOIN classes c ON cs.class_id = c.id
                WHERE cs.class_id = ?
                ORDER BY cs.dia_semana, cs.hora_inicio
                SELECT cs.*, c.nombre as class_nombre, c.capacidad_maxima, c.intensidad, c.tipo
                FROM class_schedules cs
                JOIN classes c ON cs.class_id = c.id
                WHERE c.is_active = 1
                ORDER BY cs.dia_semana, cs.hora_inicio
                SELECT cs.class_id, c.capacidad_maxima,
                       (SELECT COUNT(*) FROM class_bookings
                        WHERE schedule_id = cs.id AND fecha_clase = ? AND status = 'confirmed') as bookings_count
                FROM class_schedules cs
                JOIN classes c ON cs.class_id = c.id
                WHERE cs.id = ?
            bookings_count = result['bookings_count']

            if bookings_count >= capacidad_maxima:
                conn.close()
                return False, "Clase llena - se agregó a lista de espera"

            cursor.execute('''
                SELECT id FROM class_bookings
                WHERE user_id = ? AND schedule_id = ? AND fecha_clase = ?
                INSERT INTO class_bookings (user_id, schedule_id, fecha_clase, booking_date, status)
                VALUES (?, ?, ?, ?, 'confirmed')
                UPDATE class_bookings
                SET status = 'cancelled', cancellation_date = ?
                WHERE id = ? AND status = 'confirmed'
                    SELECT schedule_id, fecha_clase FROM class_bookings WHERE id = ?
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
    try:
        cursor.execute('''
            SELECT id, user_id FROM class_waitlist
            WHERE schedule_id = ? AND fecha_clase = ? AND status = 'waiting'
            ORDER BY added_date
            LIMIT 1
        user_id = waitlist_entry['user_id']

        from datetime import timedelta
        expires_date = (datetime.now() + timedelta(minutes=10)).isoformat()

        cursor.execute('''
            INSERT INTO notifications (user_id, tipo, titulo, mensaje, data, created_date, expires_date)
            VALUES (?, 'waitlist_spot_available', 'Cupo Disponible',
                    'Se liberó un cupo en tu clase. Tienes 10 minutos para confirmar.',
                    ?, ?, ?)
            UPDATE class_waitlist
            SET status = 'notified', notified_date = ?, confirmation_deadline = ?
            WHERE id = ?
                INSERT INTO class_waitlist (user_id, schedule_id, fecha_clase, added_date, status)
                VALUES (?, ?, ?, ?, 'waiting')
                SELECT cb.*, cs.dia_semana, cs.hora_inicio, cs.sala,
                       c.nombre as class_nombre, c.instructor, c.duracion
                FROM class_bookings cb
                JOIN class_schedules cs ON cb.schedule_id = cs.id
                JOIN classes c ON cs.class_id = c.id
                WHERE cb.user_id = ? AND cb.fecha_clase >= ? AND cb.status = 'confirmed'
                ORDER BY cb.fecha_clase, cs.hora_inicio
                SELECT cb.*, cs.dia_semana, cs.hora_inicio, cs.sala,
                       c.nombre as class_nombre, c.instructor, c.duracion
                FROM class_bookings cb
                JOIN class_schedules cs ON cb.schedule_id = cs.id
                JOIN classes c ON cs.class_id = c.id
                WHERE cb.user_id = ? AND cb.status = 'confirmed'
                ORDER BY cb.fecha_clase, cs.hora_inicio
                INSERT INTO class_ratings (user_id, class_id, schedule_id, fecha_clase,
                                          rating, instructor_rating, comentario, rating_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                INSERT INTO equipment_zones (nombre, tipo, descripcion, cantidad,
                                            duracion_slot, created_date)
                VALUES (?, ?, ?, ?, ?, ?)
        else:
            cursor.execute('SELECT * FROM equipment_zones ORDER BY nombre')

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

def reserve_equipment(user_id: int, equipment_id: int, fecha_reserva: str,
                      hora_inicio: str, hora_fin: str) -> tuple[bool, str]:
    with db_lock:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT COUNT(*) as count FROM equipment_reservations
                WHERE equipment_id = ? AND fecha_reserva = ? AND status = 'confirmed'
                AND ((hora_inicio < ? AND hora_fin > ?) OR
                     (hora_inicio < ? AND hora_fin > ?) OR
                     (hora_inicio >= ? AND hora_fin <= ?))
                conn.close()
                return False, "Equipo/zona no disponible en ese horario"

            booking_date = datetime.now().isoformat()
            cursor.execute('''
                INSERT INTO equipment_reservations
                (user_id, equipment_id, fecha_reserva, hora_inicio, hora_fin, booking_date, status)
                VALUES (?, ?, ?, ?, ?, ?, 'confirmed')
                INSERT INTO exercises (nombre, descripcion, categoria, equipo_necesario, created_date)
                VALUES (?, ?, ?, ?, ?)
                INSERT INTO workout_logs (user_id, exercise_id, fecha, serie, repeticiones,
                                         peso, descanso_segundos, log_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            SELECT * FROM workout_logs
            WHERE user_id = ? AND exercise_id = ?
            ORDER BY fecha DESC, serie DESC
            LIMIT ?
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

def generate_checkin_token(user_id: int, token_type: str = "qr") -> tuple[bool, str]:
    with db_lock:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            import secrets
            token = secrets.token_urlsafe(32)
            generated_date = datetime.now().isoformat()

            cursor.execute('''
                INSERT INTO checkin_tokens (user_id, token, token_type, generated_date)
                VALUES (?, ?, ?, ?)
                INSERT INTO checkin_history (user_id, checkin_date, location)
                VALUES (?, ?, ?)
                INSERT INTO notifications (user_id, tipo, titulo, mensaje, data,
                                          created_date, action_url, expires_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                SELECT * FROM notifications
                WHERE user_id = ? AND is_read = 0
                ORDER BY created_date DESC
                SELECT * FROM notifications
                WHERE user_id = ?
                ORDER BY created_date DESC
