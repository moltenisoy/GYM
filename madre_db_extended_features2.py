# madre_db_extended_features2.py
#
# Continuation of database functions for features 8-16
# This module contains the CRUD operations for gamification, goals, and reminders

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from madre_db import get_db_connection, db_lock
from shared.logger import setup_logger

logger = setup_logger(__name__, log_file="madre_db_extended_features2.log")


# ============================================================================
# FEATURE 8: Achievements & Gamification
# ============================================================================

def create_achievement(achievement_name: str, description: str, category: str,
                      points: int, requirement: Dict, icon_path: str = None) -> Optional[int]:
    """Crea un logro/achievement."""
    with db_lock:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            requirement_json = json.dumps(requirement, ensure_ascii=False)
            cursor.execute('''
                INSERT INTO achievements 
                (achievement_name, description, icon_path, category, points, requirement_json)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (achievement_name, description, icon_path, category, points, requirement_json))
            
            achievement_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return achievement_id
        except sqlite3.IntegrityError:
            logger.warning(f"Achievement already exists: {achievement_name}")
            return None


def award_achievement(user_id: int, achievement_id: int) -> bool:
    """Otorga un logro a un usuario."""
    with db_lock:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            earned_date = datetime.now().isoformat()
            cursor.execute('''
                INSERT INTO user_achievements (user_id, achievement_id, earned_date)
                VALUES (?, ?, ?)
            ''', (user_id, achievement_id, earned_date))
            
            # Update user points
            cursor.execute('''
                SELECT points FROM achievements WHERE id = ?
            ''', (achievement_id,))
            row = cursor.fetchone()
            
            if row:
                points = row['points']
                cursor.execute('''
                    UPDATE user_levels 
                    SET total_points = total_points + ?
                    WHERE user_id = ?
                ''', (points, user_id))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"User {user_id} already has achievement {achievement_id}")
            return False


def get_user_achievements(user_id: int) -> List[Dict[str, Any]]:
    """Obtiene los logros del usuario."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ua.*, a.achievement_name, a.description, a.icon_path, 
                   a.category, a.points
            FROM user_achievements ua
            JOIN achievements a ON ua.achievement_id = a.id
            WHERE ua.user_id = ?
            ORDER BY ua.earned_date DESC
        ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


def get_all_achievements() -> List[Dict[str, Any]]:
    """Obtiene todos los logros disponibles."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM achievements ORDER BY category, points')
        rows = cursor.fetchall()
        conn.close()
        
        achievements = []
        for row in rows:
            achievement = dict(row)
            achievement['requirement_json'] = json.loads(achievement['requirement_json'])
            achievements.append(achievement)
        
        return achievements


def get_user_level(user_id: int) -> Dict[str, Any]:
    """Obtiene el nivel del usuario."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM user_levels WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        
        if not row:
            # Create initial level
            cursor.execute('''
                INSERT INTO user_levels (user_id, current_level, total_points, level_updated_date)
                VALUES (?, 'principiante', 0, ?)
            ''', (user_id, datetime.now().isoformat()))
            conn.commit()
            
            cursor.execute('SELECT * FROM user_levels WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
        
        conn.close()
        return dict(row) if row else {}


def update_user_level(user_id: int, new_level: str) -> bool:
    """Actualiza el nivel del usuario."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        level_updated_date = datetime.now().isoformat()
        cursor.execute('''
            UPDATE user_levels 
            SET current_level = ?, level_updated_date = ?
            WHERE user_id = ?
        ''', (new_level, level_updated_date, user_id))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success


def create_challenge(challenge_name: str, description: str, challenge_type: str,
                    start_date: str, end_date: str, goal_value: int,
                    reward_points: int = 0) -> Optional[int]:
    """Crea un desafío."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO challenges 
            (challenge_name, description, challenge_type, start_date, end_date, 
             goal_value, reward_points)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (challenge_name, description, challenge_type, start_date, end_date,
              goal_value, reward_points))
        
        challenge_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return challenge_id


def enroll_user_in_challenge(user_id: int, challenge_id: int) -> bool:
    """Inscribe a un usuario en un desafío."""
    with db_lock:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_challenges (user_id, challenge_id, current_progress)
                VALUES (?, ?, 0)
            ''', (user_id, challenge_id))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False


def update_challenge_progress(user_id: int, challenge_id: int, progress_increment: int) -> bool:
    """Actualiza el progreso del usuario en un desafío."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get challenge goal
        cursor.execute('SELECT goal_value, reward_points FROM challenges WHERE id = ?', (challenge_id,))
        challenge = cursor.fetchone()
        
        if not challenge:
            conn.close()
            return False
        
        # Update progress
        cursor.execute('''
            UPDATE user_challenges 
            SET current_progress = current_progress + ?
            WHERE user_id = ? AND challenge_id = ?
        ''', (progress_increment, user_id, challenge_id))
        
        # Check if completed
        cursor.execute('''
            SELECT current_progress FROM user_challenges
            WHERE user_id = ? AND challenge_id = ?
        ''', (user_id, challenge_id))
        
        row = cursor.fetchone()
        
        if row and row['current_progress'] >= challenge['goal_value']:
            # Mark as completed
            completed_date = datetime.now().isoformat()
            cursor.execute('''
                UPDATE user_challenges 
                SET completed = 1, completed_date = ?
                WHERE user_id = ? AND challenge_id = ?
            ''', (completed_date, user_id, challenge_id))
            
            # Award points
            if challenge['reward_points'] > 0:
                cursor.execute('''
                    UPDATE user_levels 
                    SET total_points = total_points + ?
                    WHERE user_id = ?
                ''', (challenge['reward_points'], user_id))
        
        conn.commit()
        conn.close()
        return True


def get_active_challenges(user_id: int = None) -> List[Dict[str, Any]]:
    """Obtiene los desafíos activos."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        if user_id:
            cursor.execute('''
                SELECT c.*, uc.current_progress, uc.completed
                FROM challenges c
                LEFT JOIN user_challenges uc ON c.id = uc.challenge_id AND uc.user_id = ?
                WHERE c.end_date >= ?
                ORDER BY c.end_date
            ''', (user_id, now))
        else:
            cursor.execute('''
                SELECT * FROM challenges
                WHERE end_date >= ?
                ORDER BY end_date
            ''', (now,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


# ============================================================================
# FEATURE 10: Q&A System (Support Tickets & FAQs)
# ============================================================================

def create_support_ticket(user_id: int, subject: str, body: str,
                         category: str = None, priority: str = 'normal') -> Optional[int]:
    """Crea un ticket de soporte."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        created_date = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO support_tickets 
            (user_id, ticket_subject, ticket_body, status, priority, category, created_date, updated_date)
            VALUES (?, ?, ?, 'open', ?, ?, ?, ?)
        ''', (user_id, subject, body, priority, category, created_date, created_date))
        
        ticket_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return ticket_id


def add_ticket_response(ticket_id: int, responder_username: str, response_text: str,
                        is_internal_note: bool = False) -> Optional[int]:
    """Añade una respuesta a un ticket."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        response_date = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO ticket_responses 
            (ticket_id, responder_username, response_text, response_date, is_internal_note)
            VALUES (?, ?, ?, ?, ?)
        ''', (ticket_id, responder_username, response_text, response_date, 1 if is_internal_note else 0))
        
        response_id = cursor.lastrowid
        
        # Update ticket timestamp
        cursor.execute('''
            UPDATE support_tickets SET updated_date = ? WHERE id = ?
        ''', (response_date, ticket_id))
        
        conn.commit()
        conn.close()
        return response_id


def update_ticket_status(ticket_id: int, status: str, assigned_to: str = None) -> bool:
    """Actualiza el estado de un ticket."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        updated_date = datetime.now().isoformat()
        
        if status == 'resolved':
            cursor.execute('''
                UPDATE support_tickets 
                SET status = ?, updated_date = ?, resolved_date = ?, assigned_to = ?
                WHERE id = ?
            ''', (status, updated_date, updated_date, assigned_to, ticket_id))
        else:
            cursor.execute('''
                UPDATE support_tickets 
                SET status = ?, updated_date = ?, assigned_to = ?
                WHERE id = ?
            ''', (status, updated_date, assigned_to, ticket_id))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success


def get_user_tickets(user_id: int, status: str = None) -> List[Dict[str, Any]]:
    """Obtiene los tickets de un usuario."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if status:
            cursor.execute('''
                SELECT * FROM support_tickets
                WHERE user_id = ? AND status = ?
                ORDER BY updated_date DESC
            ''', (user_id, status))
        else:
            cursor.execute('''
                SELECT * FROM support_tickets
                WHERE user_id = ?
                ORDER BY updated_date DESC
            ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


def get_ticket_responses(ticket_id: int, include_internal: bool = False) -> List[Dict[str, Any]]:
    """Obtiene las respuestas de un ticket."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if include_internal:
            cursor.execute('''
                SELECT * FROM ticket_responses
                WHERE ticket_id = ?
                ORDER BY response_date
            ''', (ticket_id,))
        else:
            cursor.execute('''
                SELECT * FROM ticket_responses
                WHERE ticket_id = ? AND is_internal_note = 0
                ORDER BY response_date
            ''', (ticket_id,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


def add_faq_item(question: str, answer: str, category: str, display_order: int = 0) -> Optional[int]:
    """Añade un item a la FAQ."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        created_date = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO faq_items 
            (question, answer, category, display_order, created_date, updated_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (question, answer, category, display_order, created_date, created_date))
        
        faq_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return faq_id


def get_faq_items(category: str = None) -> List[Dict[str, Any]]:
    """Obtiene items de la FAQ."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if category:
            cursor.execute('''
                SELECT * FROM faq_items
                WHERE category = ?
                ORDER BY display_order, id
            ''', (category,))
        else:
            cursor.execute('''
                SELECT * FROM faq_items
                ORDER BY category, display_order, id
            ''')
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


def add_knowledge_base_article(title: str, content: str, category: str,
                               tags: List[str], author: str) -> Optional[int]:
    """Añade un artículo a la base de conocimientos."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        created_date = datetime.now().isoformat()
        tags_json = json.dumps(tags, ensure_ascii=False)
        
        cursor.execute('''
            INSERT INTO knowledge_base_articles 
            (title, content, category, tags_json, author, created_date, updated_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, content, category, tags_json, author, created_date, created_date))
        
        article_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return article_id


def search_knowledge_base(search_term: str, category: str = None) -> List[Dict[str, Any]]:
    """Busca en la base de conocimientos."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if category:
            cursor.execute('''
                SELECT * FROM knowledge_base_articles
                WHERE (title LIKE ? OR content LIKE ?) AND category = ?
                ORDER BY view_count DESC
                LIMIT 20
            ''', (f'%{search_term}%', f'%{search_term}%', category))
        else:
            cursor.execute('''
                SELECT * FROM knowledge_base_articles
                WHERE title LIKE ? OR content LIKE ?
                ORDER BY view_count DESC
                LIMIT 20
            ''', (f'%{search_term}%', f'%{search_term}%'))
        
        rows = cursor.fetchall()
        conn.close()
        
        articles = []
        for row in rows:
            article = dict(row)
            if article.get('tags_json'):
                article['tags_json'] = json.loads(article['tags_json'])
            articles.append(article)
        
        return articles


# ============================================================================
# FEATURE 11: Trainer Feedback
# ============================================================================

def add_trainer_feedback(user_id: int, trainer_username: str, feedback_type: str,
                        feedback_text: str, workout_session_id: int = None,
                        media_path: str = None) -> Optional[int]:
    """Añade feedback del entrenador."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        created_date = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO trainer_feedback 
            (user_id, trainer_username, workout_session_id, feedback_type, 
             feedback_text, media_path, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, trainer_username, workout_session_id, feedback_type,
              feedback_text, media_path, created_date))
        
        feedback_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return feedback_id


def get_user_feedback(user_id: int, feedback_type: str = None, limit: int = 50) -> List[Dict[str, Any]]:
    """Obtiene el feedback del usuario."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if feedback_type:
            cursor.execute('''
                SELECT * FROM trainer_feedback
                WHERE user_id = ? AND feedback_type = ?
                ORDER BY created_date DESC
                LIMIT ?
            ''', (user_id, feedback_type, limit))
        else:
            cursor.execute('''
                SELECT * FROM trainer_feedback
                WHERE user_id = ?
                ORDER BY created_date DESC
                LIMIT ?
            ''', (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


def add_technique_correction(user_id: int, exercise_name: str, correction_text: str,
                            trainer_username: str, video_path: str = None,
                            annotated_media_path: str = None) -> Optional[int]:
    """Añade una corrección de técnica."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        created_date = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO technique_corrections 
            (user_id, exercise_name, correction_text, video_path, 
             annotated_media_path, trainer_username, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, exercise_name, correction_text, video_path,
              annotated_media_path, trainer_username, created_date))
        
        correction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return correction_id


def get_technique_corrections(user_id: int, exercise_name: str = None) -> List[Dict[str, Any]]:
    """Obtiene las correcciones de técnica."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if exercise_name:
            cursor.execute('''
                SELECT * FROM technique_corrections
                WHERE user_id = ? AND exercise_name = ?
                ORDER BY created_date DESC
            ''', (user_id, exercise_name))
        else:
            cursor.execute('''
                SELECT * FROM technique_corrections
                WHERE user_id = ?
                ORDER BY created_date DESC
            ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


def add_improvement_suggestion(user_id: int, suggestion_type: str, suggestion_text: str,
                              trainer_username: str, priority: str = 'normal') -> Optional[int]:
    """Añade una sugerencia de mejora."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        created_date = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO improvement_suggestions 
            (user_id, suggestion_type, suggestion_text, priority, 
             trainer_username, created_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, suggestion_type, suggestion_text, priority,
              trainer_username, created_date))
        
        suggestion_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return suggestion_id


def get_improvement_suggestions(user_id: int, acknowledged: bool = None) -> List[Dict[str, Any]]:
    """Obtiene las sugerencias de mejora."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if acknowledged is not None:
            cursor.execute('''
                SELECT * FROM improvement_suggestions
                WHERE user_id = ? AND acknowledged = ?
                ORDER BY priority DESC, created_date DESC
            ''', (user_id, 1 if acknowledged else 0))
        else:
            cursor.execute('''
                SELECT * FROM improvement_suggestions
                WHERE user_id = ?
                ORDER BY priority DESC, created_date DESC
            ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


# ============================================================================
# FEATURE 12: Session Booking
# ============================================================================

def set_trainer_availability(trainer_username: str, day_of_week: str,
                             start_time: str, end_time: str, is_available: bool = True) -> Optional[int]:
    """Establece la disponibilidad del entrenador."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trainer_availability 
            (trainer_username, day_of_week, start_time, end_time, is_available)
            VALUES (?, ?, ?, ?, ?)
        ''', (trainer_username, day_of_week, start_time, end_time, 1 if is_available else 0))
        
        availability_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return availability_id


def get_trainer_availability(trainer_username: str, day_of_week: str = None) -> List[Dict[str, Any]]:
    """Obtiene la disponibilidad del entrenador."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if day_of_week:
            cursor.execute('''
                SELECT * FROM trainer_availability
                WHERE trainer_username = ? AND day_of_week = ? AND is_available = 1
                ORDER BY start_time
            ''', (trainer_username, day_of_week))
        else:
            cursor.execute('''
                SELECT * FROM trainer_availability
                WHERE trainer_username = ? AND is_available = 1
                ORDER BY day_of_week, start_time
            ''', (trainer_username,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


def create_session_booking(user_id: int, trainer_username: str, booking_date: str,
                          start_time: str, end_time: str, session_type: str,
                          notes: str = "") -> Optional[int]:
    """Crea una reserva de sesión."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        created_date = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO session_bookings 
            (user_id, trainer_username, booking_date, start_time, end_time, 
             session_type, status, notes, created_date)
            VALUES (?, ?, ?, ?, ?, ?, 'confirmed', ?, ?)
        ''', (user_id, trainer_username, booking_date, start_time, end_time,
              session_type, notes, created_date))
        
        booking_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return booking_id


def cancel_session_booking(booking_id: int, reason: str = "") -> bool:
    """Cancela una reserva de sesión."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        canceled_date = datetime.now().isoformat()
        cursor.execute('''
            UPDATE session_bookings 
            SET status = 'canceled', canceled_date = ?, cancellation_reason = ?
            WHERE id = ?
        ''', (canceled_date, reason, booking_id))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success


def get_user_bookings(user_id: int, status: str = None) -> List[Dict[str, Any]]:
    """Obtiene las reservas de un usuario."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if status:
            cursor.execute('''
                SELECT * FROM session_bookings
                WHERE user_id = ? AND status = ?
                ORDER BY booking_date DESC, start_time DESC
            ''', (user_id, status))
        else:
            cursor.execute('''
                SELECT * FROM session_bookings
                WHERE user_id = ?
                ORDER BY booking_date DESC, start_time DESC
            ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


def add_to_waitlist(user_id: int, trainer_username: str, requested_date: str,
                    requested_time: str) -> Optional[int]:
    """Añade un usuario a la lista de espera."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        added_date = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO booking_waitlist 
            (user_id, trainer_username, requested_date, requested_time, added_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, trainer_username, requested_date, requested_time, added_date))
        
        waitlist_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return waitlist_id


# ============================================================================
# FEATURE 13: Group Classes
# ============================================================================

def create_group_class_type(class_name: str, description: str, duration_minutes: int,
                           intensity_level: str, max_capacity: int,
                           instructor_name: str = None) -> Optional[int]:
    """Crea un tipo de clase grupal."""
    with db_lock:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO group_class_types 
                (class_name, description, duration_minutes, intensity_level, 
                 max_capacity, instructor_name)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (class_name, description, duration_minutes, intensity_level,
                  max_capacity, instructor_name))
            
            class_type_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return class_type_id
        except sqlite3.IntegrityError:
            logger.warning(f"Class type already exists: {class_name}")
            return None


def schedule_group_class(class_type_id: int, class_date: str, start_time: str,
                        instructor_name: str) -> Optional[int]:
    """Programa una clase grupal."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO group_class_schedule 
            (class_type_id, class_date, start_time, instructor_name, current_enrollment)
            VALUES (?, ?, ?, ?, 0)
        ''', (class_type_id, class_date, start_time, instructor_name))
        
        schedule_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return schedule_id


def enroll_in_group_class(class_schedule_id: int, user_id: int) -> bool:
    """Inscribe a un usuario en una clase grupal."""
    with db_lock:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check capacity
            cursor.execute('''
                SELECT gcs.current_enrollment, gct.max_capacity
                FROM group_class_schedule gcs
                JOIN group_class_types gct ON gcs.class_type_id = gct.id
                WHERE gcs.id = ?
            ''', (class_schedule_id,))
            
            row = cursor.fetchone()
            if not row or row['current_enrollment'] >= row['max_capacity']:
                conn.close()
                return False
            
            # Enroll user
            enrollment_date = datetime.now().isoformat()
            cursor.execute('''
                INSERT INTO group_class_enrollments 
                (class_schedule_id, user_id, enrollment_date)
                VALUES (?, ?, ?)
            ''', (class_schedule_id, user_id, enrollment_date))
            
            # Update enrollment count
            cursor.execute('''
                UPDATE group_class_schedule 
                SET current_enrollment = current_enrollment + 1
                WHERE id = ?
            ''', (class_schedule_id,))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False


def cancel_group_class_enrollment(class_schedule_id: int, user_id: int) -> bool:
    """Cancela la inscripción de un usuario en una clase grupal."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        canceled_date = datetime.now().isoformat()
        cursor.execute('''
            UPDATE group_class_enrollments 
            SET canceled = 1, canceled_date = ?
            WHERE class_schedule_id = ? AND user_id = ? AND canceled = 0
        ''', (canceled_date, class_schedule_id, user_id))
        
        if cursor.rowcount > 0:
            # Update enrollment count
            cursor.execute('''
                UPDATE group_class_schedule 
                SET current_enrollment = current_enrollment - 1
                WHERE id = ?
            ''', (class_schedule_id,))
            
            conn.commit()
            conn.close()
            return True
        
        conn.close()
        return False


def get_available_group_classes(start_date: str = None) -> List[Dict[str, Any]]:
    """Obtiene las clases grupales disponibles."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if start_date is None:
            start_date = datetime.now().date().isoformat()
        
        cursor.execute('''
            SELECT gcs.*, gct.class_name, gct.description, gct.duration_minutes,
                   gct.intensity_level, gct.max_capacity
            FROM group_class_schedule gcs
            JOIN group_class_types gct ON gcs.class_type_id = gct.id
            WHERE gcs.class_date >= ? AND gcs.status = 'scheduled'
            ORDER BY gcs.class_date, gcs.start_time
        ''', (start_date,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


def get_user_group_class_enrollments(user_id: int) -> List[Dict[str, Any]]:
    """Obtiene las inscripciones a clases grupales de un usuario."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT gce.*, gcs.class_date, gcs.start_time, gct.class_name,
                   gct.duration_minutes, gct.intensity_level, gcs.instructor_name
            FROM group_class_enrollments gce
            JOIN group_class_schedule gcs ON gce.class_schedule_id = gcs.id
            JOIN group_class_types gct ON gcs.class_type_id = gct.id
            WHERE gce.user_id = ? AND gce.canceled = 0
            ORDER BY gcs.class_date DESC, gcs.start_time DESC
        ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


# ============================================================================
# FEATURE 14: Goal Setting
# ============================================================================

def create_user_goal(user_id: int, goal_type: str, goal_description: str,
                    target_value: float, unit: str, timeframe: str,
                    start_date: str, target_date: str) -> Optional[int]:
    """Crea un objetivo para el usuario."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_goals 
            (user_id, goal_type, goal_description, target_value, unit, 
             timeframe, start_date, target_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active')
        ''', (user_id, goal_type, goal_description, target_value, unit,
              timeframe, start_date, target_date))
        
        goal_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return goal_id


def update_goal_progress(goal_id: int, current_value: float) -> bool:
    """Actualiza el progreso de un objetivo."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE user_goals 
            SET current_value = ?
            WHERE id = ?
        ''', (current_value, goal_id))
        
        # Check if goal is completed
        cursor.execute('''
            SELECT target_value, current_value, goal_type FROM user_goals WHERE id = ?
        ''', (goal_id,))
        
        row = cursor.fetchone()
        if row:
            # Check if goal is met (depending on goal type, might be >= or <=)
            if row['current_value'] >= row['target_value']:
                completed_date = datetime.now().isoformat()
                cursor.execute('''
                    UPDATE user_goals 
                    SET status = 'completed', completed_date = ?
                    WHERE id = ?
                ''', (completed_date, goal_id))
        
        conn.commit()
        conn.close()
        return True


def get_user_goals(user_id: int, status: str = None) -> List[Dict[str, Any]]:
    """Obtiene los objetivos del usuario."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if status:
            cursor.execute('''
                SELECT * FROM user_goals
                WHERE user_id = ? AND status = ?
                ORDER BY target_date
            ''', (user_id, status))
        else:
            cursor.execute('''
                SELECT * FROM user_goals
                WHERE user_id = ?
                ORDER BY status, target_date
            ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


def add_goal_milestone(goal_id: int, milestone_value: float) -> Optional[int]:
    """Añade un hito a un objetivo."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO goal_milestones (goal_id, milestone_value)
            VALUES (?, ?)
        ''', (goal_id, milestone_value))
        
        milestone_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return milestone_id


# ============================================================================
# FEATURE 15: Transformation Programs
# ============================================================================

def create_transformation_program(program_name: str, description: str,
                                 duration_weeks: int, program_type: str,
                                 created_by: str, template_data: Dict) -> Optional[int]:
    """Crea un programa de transformación."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        template_json = json.dumps(template_data, ensure_ascii=False)
        cursor.execute('''
            INSERT INTO transformation_programs 
            (program_name, description, duration_weeks, program_type, 
             created_by, template_data_json)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (program_name, description, duration_weeks, program_type,
              created_by, template_json))
        
        program_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return program_id


def enroll_user_in_transformation(user_id: int, program_id: int, start_date: str) -> Optional[int]:
    """Inscribe a un usuario en un programa de transformación."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get program duration
        cursor.execute('SELECT duration_weeks FROM transformation_programs WHERE id = ?', (program_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        # Calculate end date
        start = datetime.fromisoformat(start_date)
        end = start + timedelta(weeks=row['duration_weeks'])
        end_date = end.date().isoformat()
        
        cursor.execute('''
            INSERT INTO user_transformations 
            (user_id, program_id, start_date, end_date, status)
            VALUES (?, ?, ?, ?, 'active')
        ''', (user_id, program_id, start_date, end_date))
        
        transformation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return transformation_id


def add_transformation_evaluation(transformation_id: int, evaluation_week: int,
                                 weight_kg: float = None, body_fat_percentage: float = None,
                                 notes: str = "", photo_front: str = None,
                                 photo_side: str = None, photo_back: str = None) -> Optional[int]:
    """Añade una evaluación al programa de transformación."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        evaluation_date = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO transformation_evaluations 
            (transformation_id, evaluation_week, evaluation_date, weight_kg,
             body_fat_percentage, notes, photo_front, photo_side, photo_back)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (transformation_id, evaluation_week, evaluation_date, weight_kg,
              body_fat_percentage, notes, photo_front, photo_side, photo_back))
        
        evaluation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return evaluation_id


def get_user_transformation(user_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene el programa de transformación activo del usuario."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ut.*, tp.program_name, tp.description, tp.duration_weeks, tp.program_type
            FROM user_transformations ut
            JOIN transformation_programs tp ON ut.program_id = tp.id
            WHERE ut.user_id = ? AND ut.status = 'active'
            ORDER BY ut.start_date DESC
            LIMIT 1
        ''', (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None


def get_transformation_evaluations(transformation_id: int) -> List[Dict[str, Any]]:
    """Obtiene las evaluaciones de un programa de transformación."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM transformation_evaluations
            WHERE transformation_id = ?
            ORDER BY evaluation_week
        ''', (transformation_id,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


# ============================================================================
# FEATURE 16: Reminder System
# ============================================================================

def create_user_reminder(user_id: int, reminder_type: str, reminder_time: str,
                        days_of_week: str = None, custom_message: str = None,
                        enabled: bool = True) -> Optional[int]:
    """Crea un recordatorio para el usuario."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_reminders 
            (user_id, reminder_type, reminder_time, enabled, days_of_week, custom_message)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, reminder_type, reminder_time, 1 if enabled else 0, days_of_week, custom_message))
        
        reminder_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return reminder_id


def get_user_reminders(user_id: int, enabled_only: bool = True) -> List[Dict[str, Any]]:
    """Obtiene los recordatorios del usuario."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if enabled_only:
            cursor.execute('''
                SELECT * FROM user_reminders
                WHERE user_id = ? AND enabled = 1
                ORDER BY reminder_time
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT * FROM user_reminders
                WHERE user_id = ?
                ORDER BY reminder_time
            ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


def update_reminder_enabled(reminder_id: int, enabled: bool) -> bool:
    """Actualiza el estado de un recordatorio."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE user_reminders SET enabled = ? WHERE id = ?
        ''', (1 if enabled else 0, reminder_id))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success


def log_reminder_sent(user_id: int, reminder_type: str, delivered: bool = True) -> Optional[int]:
    """Registra el envío de un recordatorio."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sent_date = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO reminder_history 
            (user_id, reminder_type, sent_date, delivered)
            VALUES (?, ?, ?, ?)
        ''', (user_id, reminder_type, sent_date, 1 if delivered else 0))
        
        history_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return history_id


def get_reminder_history(user_id: int, reminder_type: str = None, limit: int = 50) -> List[Dict[str, Any]]:
    """Obtiene el historial de recordatorios."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if reminder_type:
            cursor.execute('''
                SELECT * FROM reminder_history
                WHERE user_id = ? AND reminder_type = ?
                ORDER BY sent_date DESC
                LIMIT ?
            ''', (user_id, reminder_type, limit))
        else:
            cursor.execute('''
                SELECT * FROM reminder_history
                WHERE user_id = ?
                ORDER BY sent_date DESC
                LIMIT ?
            ''', (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
