# madre_db_extended.py
#
# Extended database schema and functions for features 1-16 from SUGERENCIAS_FUNCIONALIDADES.md
# This module extends madre_db.py with new tables and functions for:
# - Real-time exercise tracking
# - Exercise videos library
# - Interactive training plans
# - Body measurements tracking
# - Personalized nutrition plans
# - Food diary
# - Personal dashboard & statistics
# - Achievements & gamification
# - Q&A system and FAQs
# - Trainer feedback
# - Session booking
# - Group classes
# - Goal setting
# - Transformation programs
# - Reminder system

import sqlite3
import threading
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from madre_db import get_db_connection, db_lock
from shared.logger import setup_logger

logger = setup_logger(__name__, log_file="madre_db_extended.log")


def init_extended_database() -> None:
    """
    Inicializa las tablas extendidas para las funcionalidades 1-16.
    Se ejecuta después de init_database() de madre_db.py
    """
    logger.info("Initializing extended database schema...")
    with db_lock:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # ===================================================================
            # Feature 1: Real-time exercise tracking
            # ===================================================================
            
            # Tabla de ejercicios completados por sesión
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS exercise_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    exercise_name TEXT NOT NULL,
                    sets_completed INTEGER DEFAULT 0,
                    reps_completed INTEGER DEFAULT 0,
                    weight_used REAL DEFAULT 0,
                    duration_seconds INTEGER DEFAULT 0,
                    session_date TEXT NOT NULL,
                    notes TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

            # Historial de progreso por ejercicio
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS exercise_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    exercise_name TEXT NOT NULL,
                    date TEXT NOT NULL,
                    max_weight REAL,
                    total_volume REAL,
                    personal_record INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

            # ===================================================================
            # Feature 2: Exercise videos library
            # ===================================================================
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS exercise_videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    exercise_name TEXT NOT NULL UNIQUE,
                    video_path TEXT NOT NULL,
                    thumbnail_path TEXT,
                    description TEXT,
                    difficulty_level TEXT,
                    muscle_group TEXT,
                    equipment_needed TEXT,
                    duration_seconds INTEGER,
                    upload_date TEXT NOT NULL,
                    trainer_name TEXT
                )
            ''')

            # Videos personalizados por trainer específico
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS custom_videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    video_path TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    upload_date TEXT NOT NULL,
                    uploaded_by TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

            # ===================================================================
            # Feature 3: Interactive training plan
            # ===================================================================
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS training_plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    plan_name TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT,
                    goal TEXT,
                    status TEXT DEFAULT 'active',
                    created_date TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS training_plan_workouts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plan_id INTEGER NOT NULL,
                    scheduled_date TEXT NOT NULL,
                    workout_name TEXT NOT NULL,
                    exercises_json TEXT NOT NULL,
                    duration_minutes INTEGER,
                    completed INTEGER DEFAULT 0,
                    completed_date TEXT,
                    FOREIGN KEY (plan_id) REFERENCES training_plans(id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS workout_exercise_substitutes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_exercise TEXT NOT NULL,
                    substitute_exercise TEXT NOT NULL,
                    reason TEXT
                )
            ''')

            # Notificaciones de entrenamientos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS workout_notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    workout_id INTEGER NOT NULL,
                    notification_type TEXT NOT NULL,
                    notification_time TEXT NOT NULL,
                    sent INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (workout_id) REFERENCES training_plan_workouts(id)
                )
            ''')

            # ===================================================================
            # Feature 4: Body measurements tracking
            # ===================================================================
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS body_measurements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    measurement_date TEXT NOT NULL,
                    weight_kg REAL,
                    height_cm REAL,
                    bmi REAL,
                    chest_cm REAL,
                    waist_cm REAL,
                    hips_cm REAL,
                    left_arm_cm REAL,
                    right_arm_cm REAL,
                    left_thigh_cm REAL,
                    right_thigh_cm REAL,
                    body_fat_percentage REAL,
                    muscle_mass_kg REAL,
                    notes TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS progress_photos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    photo_type TEXT NOT NULL,
                    photo_path TEXT NOT NULL,
                    photo_date TEXT NOT NULL,
                    measurement_id INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (measurement_id) REFERENCES body_measurements(id)
                )
            ''')

            # ===================================================================
            # Feature 5: Personalized nutrition plan
            # ===================================================================
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS nutrition_plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    plan_name TEXT NOT NULL,
                    daily_calories INTEGER,
                    protein_grams INTEGER,
                    carbs_grams INTEGER,
                    fats_grams INTEGER,
                    start_date TEXT NOT NULL,
                    end_date TEXT,
                    created_by TEXT NOT NULL,
                    notes TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS recipes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recipe_name TEXT NOT NULL,
                    meal_type TEXT NOT NULL,
                    ingredients_json TEXT NOT NULL,
                    preparation TEXT NOT NULL,
                    servings INTEGER DEFAULT 1,
                    calories_per_serving INTEGER,
                    protein_per_serving REAL,
                    carbs_per_serving REAL,
                    fats_per_serving REAL,
                    prep_time_minutes INTEGER,
                    cook_time_minutes INTEGER
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS nutrition_plan_meals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plan_id INTEGER NOT NULL,
                    day_of_week TEXT NOT NULL,
                    meal_time TEXT NOT NULL,
                    recipe_id INTEGER,
                    custom_meal_description TEXT,
                    FOREIGN KEY (plan_id) REFERENCES nutrition_plans(id),
                    FOREIGN KEY (recipe_id) REFERENCES recipes(id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS food_substitutes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_food TEXT NOT NULL,
                    substitute_food TEXT NOT NULL,
                    reason TEXT
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS water_intake (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    water_ml INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

            # ===================================================================
            # Feature 6: Food diary
            # ===================================================================
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS food_diary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    meal_date TEXT NOT NULL,
                    meal_time TEXT NOT NULL,
                    meal_type TEXT NOT NULL,
                    food_name TEXT NOT NULL,
                    quantity REAL,
                    unit TEXT,
                    calories INTEGER,
                    protein_grams REAL,
                    carbs_grams REAL,
                    fats_grams REAL,
                    photo_path TEXT,
                    notes TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS food_database (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    food_name TEXT NOT NULL UNIQUE,
                    barcode TEXT,
                    calories_per_100g INTEGER,
                    protein_per_100g REAL,
                    carbs_per_100g REAL,
                    fats_per_100g REAL,
                    serving_size_g REAL,
                    category TEXT
                )
            ''')

            # ===================================================================
            # Feature 7: Personal dashboard statistics
            # ===================================================================
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    stat_date TEXT NOT NULL,
                    workouts_completed INTEGER DEFAULT 0,
                    calories_burned INTEGER DEFAULT 0,
                    active_minutes INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_streaks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    current_streak INTEGER DEFAULT 0,
                    longest_streak INTEGER DEFAULT 0,
                    last_workout_date TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

            # ===================================================================
            # Feature 8: Achievements & gamification
            # ===================================================================
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    achievement_name TEXT NOT NULL UNIQUE,
                    description TEXT NOT NULL,
                    icon_path TEXT,
                    category TEXT NOT NULL,
                    points INTEGER DEFAULT 0,
                    requirement_json TEXT NOT NULL
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    achievement_id INTEGER NOT NULL,
                    earned_date TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (achievement_id) REFERENCES achievements(id),
                    UNIQUE(user_id, achievement_id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_levels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL UNIQUE,
                    current_level TEXT DEFAULT 'principiante',
                    total_points INTEGER DEFAULT 0,
                    level_updated_date TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS challenges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    challenge_name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    challenge_type TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    goal_value INTEGER NOT NULL,
                    reward_points INTEGER DEFAULT 0
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_challenges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    challenge_id INTEGER NOT NULL,
                    current_progress INTEGER DEFAULT 0,
                    completed INTEGER DEFAULT 0,
                    completed_date TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (challenge_id) REFERENCES challenges(id),
                    UNIQUE(user_id, challenge_id)
                )
            ''')

            # ===================================================================
            # Feature 9: Enhanced messaging (already exists in madre_db.py)
            # Feature 10: Q&A system
            # ===================================================================
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS support_tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    ticket_subject TEXT NOT NULL,
                    ticket_body TEXT NOT NULL,
                    status TEXT DEFAULT 'open',
                    priority TEXT DEFAULT 'normal',
                    category TEXT,
                    created_date TEXT NOT NULL,
                    updated_date TEXT,
                    resolved_date TEXT,
                    assigned_to TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ticket_responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket_id INTEGER NOT NULL,
                    responder_username TEXT NOT NULL,
                    response_text TEXT NOT NULL,
                    response_date TEXT NOT NULL,
                    is_internal_note INTEGER DEFAULT 0,
                    FOREIGN KEY (ticket_id) REFERENCES support_tickets(id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS faq_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    category TEXT NOT NULL,
                    display_order INTEGER DEFAULT 0,
                    created_date TEXT NOT NULL,
                    updated_date TEXT
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge_base_articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT NOT NULL,
                    tags_json TEXT,
                    author TEXT NOT NULL,
                    created_date TEXT NOT NULL,
                    updated_date TEXT,
                    view_count INTEGER DEFAULT 0
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quick_responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trigger_keyword TEXT NOT NULL,
                    response_text TEXT NOT NULL,
                    category TEXT
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS response_ratings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    rating INTEGER NOT NULL,
                    feedback TEXT,
                    rating_date TEXT NOT NULL,
                    FOREIGN KEY (ticket_id) REFERENCES support_tickets(id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

            # ===================================================================
            # Feature 11: Trainer feedback
            # ===================================================================
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trainer_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    trainer_username TEXT NOT NULL,
                    workout_session_id INTEGER,
                    feedback_type TEXT NOT NULL,
                    feedback_text TEXT NOT NULL,
                    media_path TEXT,
                    created_date TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (workout_session_id) REFERENCES exercise_sessions(id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS technique_corrections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    exercise_name TEXT NOT NULL,
                    correction_text TEXT NOT NULL,
                    video_path TEXT,
                    annotated_media_path TEXT,
                    trainer_username TEXT NOT NULL,
                    created_date TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS improvement_suggestions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    suggestion_type TEXT NOT NULL,
                    suggestion_text TEXT NOT NULL,
                    priority TEXT DEFAULT 'normal',
                    trainer_username TEXT NOT NULL,
                    created_date TEXT NOT NULL,
                    acknowledged INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

            # ===================================================================
            # Feature 12: Session booking
            # ===================================================================
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trainer_availability (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trainer_username TEXT NOT NULL,
                    day_of_week TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    is_available INTEGER DEFAULT 1
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS session_bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    trainer_username TEXT NOT NULL,
                    booking_date TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    session_type TEXT NOT NULL,
                    status TEXT DEFAULT 'confirmed',
                    notes TEXT,
                    created_date TEXT NOT NULL,
                    canceled_date TEXT,
                    cancellation_reason TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS booking_reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    booking_id INTEGER NOT NULL,
                    reminder_time TEXT NOT NULL,
                    sent INTEGER DEFAULT 0,
                    FOREIGN KEY (booking_id) REFERENCES session_bookings(id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS booking_waitlist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    trainer_username TEXT NOT NULL,
                    requested_date TEXT NOT NULL,
                    requested_time TEXT NOT NULL,
                    added_date TEXT NOT NULL,
                    notified INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

            # ===================================================================
            # Feature 13: Group classes
            # ===================================================================
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS group_class_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    class_name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    duration_minutes INTEGER NOT NULL,
                    intensity_level TEXT NOT NULL,
                    max_capacity INTEGER NOT NULL,
                    instructor_name TEXT
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS group_class_schedule (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    class_type_id INTEGER NOT NULL,
                    class_date TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    instructor_name TEXT NOT NULL,
                    current_enrollment INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'scheduled',
                    FOREIGN KEY (class_type_id) REFERENCES group_class_types(id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS group_class_enrollments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    class_schedule_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    enrollment_date TEXT NOT NULL,
                    attended INTEGER DEFAULT 0,
                    canceled INTEGER DEFAULT 0,
                    canceled_date TEXT,
                    FOREIGN KEY (class_schedule_id) REFERENCES group_class_schedule(id),
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    UNIQUE(class_schedule_id, user_id)
                )
            ''')

            # ===================================================================
            # Feature 14: Goal setting
            # ===================================================================
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    goal_type TEXT NOT NULL,
                    goal_description TEXT NOT NULL,
                    target_value REAL,
                    current_value REAL DEFAULT 0,
                    unit TEXT,
                    timeframe TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    target_date TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    completed_date TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS goal_milestones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    goal_id INTEGER NOT NULL,
                    milestone_value REAL NOT NULL,
                    milestone_date TEXT,
                    achieved INTEGER DEFAULT 0,
                    FOREIGN KEY (goal_id) REFERENCES user_goals(id)
                )
            ''')

            # ===================================================================
            # Feature 15: Transformation programs
            # ===================================================================
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transformation_programs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    program_name TEXT NOT NULL,
                    description TEXT,
                    duration_weeks INTEGER NOT NULL,
                    program_type TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    template_data_json TEXT NOT NULL
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_transformations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    program_id INTEGER NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    completion_percentage INTEGER DEFAULT 0,
                    completed_date TEXT,
                    certificate_issued INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (program_id) REFERENCES transformation_programs(id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transformation_evaluations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transformation_id INTEGER NOT NULL,
                    evaluation_week INTEGER NOT NULL,
                    evaluation_date TEXT NOT NULL,
                    weight_kg REAL,
                    body_fat_percentage REAL,
                    notes TEXT,
                    photo_front TEXT,
                    photo_side TEXT,
                    photo_back TEXT,
                    FOREIGN KEY (transformation_id) REFERENCES user_transformations(id)
                )
            ''')

            # ===================================================================
            # Feature 16: Reminder system
            # ===================================================================
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    reminder_type TEXT NOT NULL,
                    reminder_time TEXT NOT NULL,
                    enabled INTEGER DEFAULT 1,
                    days_of_week TEXT,
                    custom_message TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reminder_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    reminder_type TEXT NOT NULL,
                    sent_date TEXT NOT NULL,
                    delivered INTEGER DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

            conn.commit()
            conn.close()
            logger.info("Extended database schema initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing extended database: {e}", exc_info=True)
            raise


# ============================================================================
# FEATURE 1: Real-time Exercise Tracking
# ============================================================================

def log_exercise_session(user_id: int, exercise_name: str, sets: int, reps: int,
                         weight: float, duration_seconds: int, notes: str = "") -> Optional[int]:
    """Registra una sesión de ejercicio."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        session_date = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO exercise_sessions 
            (user_id, exercise_name, sets_completed, reps_completed, weight_used, 
             duration_seconds, session_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, exercise_name, sets, reps, weight, duration_seconds, session_date, notes))
        
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return session_id


def get_exercise_history(user_id: int, exercise_name: str = None, 
                         limit: int = 50) -> List[Dict[str, Any]]:
    """Obtiene el historial de ejercicios."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if exercise_name:
            cursor.execute('''
                SELECT * FROM exercise_sessions
                WHERE user_id = ? AND exercise_name = ?
                ORDER BY session_date DESC
                LIMIT ?
            ''', (user_id, exercise_name, limit))
        else:
            cursor.execute('''
                SELECT * FROM exercise_sessions
                WHERE user_id = ?
                ORDER BY session_date DESC
                LIMIT ?
            ''', (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


def update_exercise_progress(user_id: int, exercise_name: str, 
                            max_weight: float, total_volume: float) -> bool:
    """Actualiza el progreso de un ejercicio."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        date = datetime.now().date().isoformat()
        
        # Check if it's a personal record
        cursor.execute('''
            SELECT MAX(max_weight) as best FROM exercise_progress
            WHERE user_id = ? AND exercise_name = ?
        ''', (user_id, exercise_name))
        
        row = cursor.fetchone()
        is_pr = row['best'] is None or max_weight > row['best']
        
        cursor.execute('''
            INSERT INTO exercise_progress 
            (user_id, exercise_name, date, max_weight, total_volume, personal_record)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, exercise_name, date, max_weight, total_volume, 1 if is_pr else 0))
        
        conn.commit()
        conn.close()
        return True


# ============================================================================
# FEATURE 2: Exercise Videos Library
# ============================================================================

def add_exercise_video(exercise_name: str, video_path: str, description: str = "",
                       difficulty: str = "intermediate", muscle_group: str = "",
                       equipment: str = "", duration: int = 0, trainer: str = "") -> Optional[int]:
    """Añade un video de ejercicio a la biblioteca."""
    with db_lock:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            upload_date = datetime.now().isoformat()
            cursor.execute('''
                INSERT INTO exercise_videos 
                (exercise_name, video_path, description, difficulty_level, 
                 muscle_group, equipment_needed, duration_seconds, upload_date, trainer_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (exercise_name, video_path, description, difficulty, muscle_group,
                  equipment, duration, upload_date, trainer))
            
            video_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return video_id
        except sqlite3.IntegrityError:
            logger.warning(f"Exercise video already exists: {exercise_name}")
            return None


def get_exercise_videos(muscle_group: str = None, difficulty: str = None) -> List[Dict[str, Any]]:
    """Obtiene videos de ejercicios, opcionalmente filtrados."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM exercise_videos WHERE 1=1'
        params = []
        
        if muscle_group:
            query += ' AND muscle_group = ?'
            params.append(muscle_group)
        
        if difficulty:
            query += ' AND difficulty_level = ?'
            params.append(difficulty)
        
        query += ' ORDER BY exercise_name'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


def add_custom_video_for_user(user_id: int, video_path: str, title: str,
                               description: str = "", uploaded_by: str = "") -> Optional[int]:
    """Añade un video personalizado para un usuario específico."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        upload_date = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO custom_videos 
            (user_id, video_path, title, description, upload_date, uploaded_by)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, video_path, title, description, upload_date, uploaded_by))
        
        video_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return video_id


def get_user_custom_videos(user_id: int) -> List[Dict[str, Any]]:
    """Obtiene los videos personalizados de un usuario."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM custom_videos
            WHERE user_id = ?
            ORDER BY upload_date DESC
        ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


# Initialize extended database when module is imported
init_extended_database()
