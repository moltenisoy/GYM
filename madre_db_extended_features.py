# madre_db_extended_features.py
#
# Continuation of database functions for features 3-16
# This module contains the CRUD operations for the extended database schema

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from madre_db import get_db_connection, db_lock
from shared.logger import setup_logger

logger = setup_logger(__name__, log_file="madre_db_extended_features.log")


# ============================================================================
# FEATURE 3: Interactive Training Plans
# ============================================================================

def create_training_plan(user_id: int, plan_name: str, start_date: str,
                        end_date: str = None, goal: str = "") -> Optional[int]:
    """Crea un plan de entrenamiento interactivo."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        created_date = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO training_plans 
            (user_id, plan_name, start_date, end_date, goal, created_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, plan_name, start_date, end_date, goal, created_date))
        
        plan_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return plan_id


def add_workout_to_plan(plan_id: int, scheduled_date: str, workout_name: str,
                        exercises: List[Dict], duration_minutes: int = 60) -> Optional[int]:
    """Añade un entrenamiento al plan."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        exercises_json = json.dumps(exercises, ensure_ascii=False)
        cursor.execute('''
            INSERT INTO training_plan_workouts 
            (plan_id, scheduled_date, workout_name, exercises_json, duration_minutes)
            VALUES (?, ?, ?, ?, ?)
        ''', (plan_id, scheduled_date, workout_name, exercises_json, duration_minutes))
        
        workout_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return workout_id


def mark_workout_completed(workout_id: int) -> bool:
    """Marca un entrenamiento como completado."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        completed_date = datetime.now().isoformat()
        cursor.execute('''
            UPDATE training_plan_workouts 
            SET completed = 1, completed_date = ?
            WHERE id = ?
        ''', (completed_date, workout_id))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success


def get_user_training_plan(user_id: int, active_only: bool = True) -> Optional[Dict[str, Any]]:
    """Obtiene el plan de entrenamiento activo del usuario."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if active_only:
            cursor.execute('''
                SELECT * FROM training_plans
                WHERE user_id = ? AND status = 'active'
                ORDER BY created_date DESC
                LIMIT 1
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT * FROM training_plans
                WHERE user_id = ?
                ORDER BY created_date DESC
                LIMIT 1
            ''', (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None


def get_plan_workouts(plan_id: int, include_completed: bool = True) -> List[Dict[str, Any]]:
    """Obtiene los entrenamientos de un plan."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if include_completed:
            cursor.execute('''
                SELECT * FROM training_plan_workouts
                WHERE plan_id = ?
                ORDER BY scheduled_date
            ''', (plan_id,))
        else:
            cursor.execute('''
                SELECT * FROM training_plan_workouts
                WHERE plan_id = ? AND completed = 0
                ORDER BY scheduled_date
            ''', (plan_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        workouts = []
        for row in rows:
            workout = dict(row)
            workout['exercises_json'] = json.loads(workout['exercises_json'])
            workouts.append(workout)
        
        return workouts


def add_exercise_substitute(original_exercise: str, substitute: str, reason: str = "") -> bool:
    """Añade un ejercicio sustituto."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO workout_exercise_substitutes 
            (original_exercise, substitute_exercise, reason)
            VALUES (?, ?, ?)
        ''', (original_exercise, substitute, reason))
        
        conn.commit()
        conn.close()
        return True


def get_exercise_substitutes(exercise_name: str) -> List[Dict[str, Any]]:
    """Obtiene sustitutos para un ejercicio."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM workout_exercise_substitutes
            WHERE original_exercise = ?
        ''', (exercise_name,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


# ============================================================================
# FEATURE 4: Body Measurements Tracking
# ============================================================================

def add_body_measurement(user_id: int, weight_kg: float = None, height_cm: float = None,
                        chest_cm: float = None, waist_cm: float = None, hips_cm: float = None,
                        left_arm_cm: float = None, right_arm_cm: float = None,
                        left_thigh_cm: float = None, right_thigh_cm: float = None,
                        body_fat_percentage: float = None, muscle_mass_kg: float = None,
                        notes: str = "") -> Optional[int]:
    """Añade mediciones corporales."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        measurement_date = datetime.now().isoformat()
        
        # Calculate BMI if weight and height are provided
        bmi = None
        if weight_kg and height_cm:
            height_m = height_cm / 100
            bmi = round(weight_kg / (height_m ** 2), 2)
        
        cursor.execute('''
            INSERT INTO body_measurements 
            (user_id, measurement_date, weight_kg, height_cm, bmi, chest_cm, waist_cm, 
             hips_cm, left_arm_cm, right_arm_cm, left_thigh_cm, right_thigh_cm,
             body_fat_percentage, muscle_mass_kg, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, measurement_date, weight_kg, height_cm, bmi, chest_cm, waist_cm,
              hips_cm, left_arm_cm, right_arm_cm, left_thigh_cm, right_thigh_cm,
              body_fat_percentage, muscle_mass_kg, notes))
        
        measurement_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return measurement_id


def get_body_measurements(user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    """Obtiene el historial de mediciones corporales."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM body_measurements
            WHERE user_id = ?
            ORDER BY measurement_date DESC
            LIMIT ?
        ''', (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


def add_progress_photo(user_id: int, photo_type: str, photo_path: str,
                      measurement_id: int = None) -> Optional[int]:
    """Añade una foto de progreso."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        photo_date = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO progress_photos 
            (user_id, photo_type, photo_path, photo_date, measurement_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, photo_type, photo_path, photo_date, measurement_id))
        
        photo_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return photo_id


def get_progress_photos(user_id: int, photo_type: str = None) -> List[Dict[str, Any]]:
    """Obtiene fotos de progreso."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if photo_type:
            cursor.execute('''
                SELECT * FROM progress_photos
                WHERE user_id = ? AND photo_type = ?
                ORDER BY photo_date DESC
            ''', (user_id, photo_type))
        else:
            cursor.execute('''
                SELECT * FROM progress_photos
                WHERE user_id = ?
                ORDER BY photo_date DESC
            ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


# ============================================================================
# FEATURE 5: Personalized Nutrition Plans
# ============================================================================

def create_nutrition_plan(user_id: int, plan_name: str, daily_calories: int,
                         protein_grams: int, carbs_grams: int, fats_grams: int,
                         start_date: str, end_date: str = None, created_by: str = "",
                         notes: str = "") -> Optional[int]:
    """Crea un plan nutricional personalizado."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO nutrition_plans 
            (user_id, plan_name, daily_calories, protein_grams, carbs_grams, 
             fats_grams, start_date, end_date, created_by, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, plan_name, daily_calories, protein_grams, carbs_grams,
              fats_grams, start_date, end_date, created_by, notes))
        
        plan_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return plan_id


def add_recipe(recipe_name: str, meal_type: str, ingredients: List[Dict],
              preparation: str, servings: int = 1, calories: int = 0,
              protein: float = 0, carbs: float = 0, fats: float = 0,
              prep_time: int = 0, cook_time: int = 0) -> Optional[int]:
    """Añade una receta a la base de datos."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        ingredients_json = json.dumps(ingredients, ensure_ascii=False)
        cursor.execute('''
            INSERT INTO recipes 
            (recipe_name, meal_type, ingredients_json, preparation, servings,
             calories_per_serving, protein_per_serving, carbs_per_serving,
             fats_per_serving, prep_time_minutes, cook_time_minutes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (recipe_name, meal_type, ingredients_json, preparation, servings,
              calories, protein, carbs, fats, prep_time, cook_time))
        
        recipe_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return recipe_id


def assign_meal_to_plan(plan_id: int, day_of_week: str, meal_time: str,
                        recipe_id: int = None, custom_meal: str = "") -> Optional[int]:
    """Asigna una comida a un plan nutricional."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO nutrition_plan_meals 
            (plan_id, day_of_week, meal_time, recipe_id, custom_meal_description)
            VALUES (?, ?, ?, ?, ?)
        ''', (plan_id, day_of_week, meal_time, recipe_id, custom_meal))
        
        meal_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return meal_id


def get_user_nutrition_plan(user_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene el plan nutricional actual del usuario."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM nutrition_plans
            WHERE user_id = ?
            ORDER BY start_date DESC
            LIMIT 1
        ''', (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None


def get_plan_meals(plan_id: int) -> List[Dict[str, Any]]:
    """Obtiene las comidas de un plan nutricional."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT npm.*, r.recipe_name, r.ingredients_json, r.preparation,
                   r.calories_per_serving, r.protein_per_serving, r.carbs_per_serving,
                   r.fats_per_serving
            FROM nutrition_plan_meals npm
            LEFT JOIN recipes r ON npm.recipe_id = r.id
            WHERE npm.plan_id = ?
            ORDER BY npm.day_of_week, npm.meal_time
        ''', (plan_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        meals = []
        for row in rows:
            meal = dict(row)
            if meal.get('ingredients_json'):
                meal['ingredients_json'] = json.loads(meal['ingredients_json'])
            meals.append(meal)
        
        return meals


def log_water_intake(user_id: int, water_ml: int, date: str = None) -> bool:
    """Registra la ingesta de agua."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if date is None:
            date = datetime.now().date().isoformat()
        
        # Check if entry exists for today
        cursor.execute('''
            SELECT id, water_ml FROM water_intake
            WHERE user_id = ? AND date = ?
        ''', (user_id, date))
        
        row = cursor.fetchone()
        
        if row:
            # Update existing entry
            new_amount = row['water_ml'] + water_ml
            cursor.execute('''
                UPDATE water_intake SET water_ml = ?
                WHERE id = ?
            ''', (new_amount, row['id']))
        else:
            # Create new entry
            cursor.execute('''
                INSERT INTO water_intake (user_id, date, water_ml)
                VALUES (?, ?, ?)
            ''', (user_id, date, water_ml))
        
        conn.commit()
        conn.close()
        return True


def get_water_intake(user_id: int, date: str = None) -> int:
    """Obtiene la ingesta de agua de un día."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if date is None:
            date = datetime.now().date().isoformat()
        
        cursor.execute('''
            SELECT water_ml FROM water_intake
            WHERE user_id = ? AND date = ?
        ''', (user_id, date))
        
        row = cursor.fetchone()
        conn.close()
        
        return row['water_ml'] if row else 0


def add_food_substitute(original_food: str, substitute: str, reason: str = "") -> bool:
    """Añade un sustituto de alimento."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO food_substitutes 
            (original_food, substitute_food, reason)
            VALUES (?, ?, ?)
        ''', (original_food, substitute, reason))
        
        conn.commit()
        conn.close()
        return True


def get_food_substitutes(food_name: str) -> List[Dict[str, Any]]:
    """Obtiene sustitutos para un alimento."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM food_substitutes
            WHERE original_food = ?
        ''', (food_name,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


# ============================================================================
# FEATURE 6: Food Diary
# ============================================================================

def log_food_entry(user_id: int, meal_type: str, food_name: str, quantity: float,
                  unit: str, calories: int = 0, protein: float = 0, carbs: float = 0,
                  fats: float = 0, photo_path: str = None, notes: str = "",
                  meal_date: str = None, meal_time: str = None) -> Optional[int]:
    """Registra una entrada en el diario alimenticio."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if meal_date is None:
            meal_date = datetime.now().date().isoformat()
        if meal_time is None:
            meal_time = datetime.now().time().strftime("%H:%M")
        
        cursor.execute('''
            INSERT INTO food_diary 
            (user_id, meal_date, meal_time, meal_type, food_name, quantity, unit,
             calories, protein_grams, carbs_grams, fats_grams, photo_path, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, meal_date, meal_time, meal_type, food_name, quantity, unit,
              calories, protein, carbs, fats, photo_path, notes))
        
        entry_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return entry_id


def get_food_diary(user_id: int, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
    """Obtiene entradas del diario alimenticio."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if start_date and end_date:
            cursor.execute('''
                SELECT * FROM food_diary
                WHERE user_id = ? AND meal_date BETWEEN ? AND ?
                ORDER BY meal_date DESC, meal_time DESC
            ''', (user_id, start_date, end_date))
        elif start_date:
            cursor.execute('''
                SELECT * FROM food_diary
                WHERE user_id = ? AND meal_date >= ?
                ORDER BY meal_date DESC, meal_time DESC
            ''', (user_id, start_date))
        else:
            cursor.execute('''
                SELECT * FROM food_diary
                WHERE user_id = ?
                ORDER BY meal_date DESC, meal_time DESC
                LIMIT 100
            ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


def get_daily_nutrition_totals(user_id: int, date: str = None) -> Dict[str, Any]:
    """Calcula los totales nutricionales del día."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if date is None:
            date = datetime.now().date().isoformat()
        
        cursor.execute('''
            SELECT 
                SUM(calories) as total_calories,
                SUM(protein_grams) as total_protein,
                SUM(carbs_grams) as total_carbs,
                SUM(fats_grams) as total_fats
            FROM food_diary
            WHERE user_id = ? AND meal_date = ?
        ''', (user_id, date))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'date': date,
                'total_calories': row['total_calories'] or 0,
                'total_protein': row['total_protein'] or 0,
                'total_carbs': row['total_carbs'] or 0,
                'total_fats': row['total_fats'] or 0
            }
        
        return {
            'date': date,
            'total_calories': 0,
            'total_protein': 0,
            'total_carbs': 0,
            'total_fats': 0
        }


def add_food_to_database(food_name: str, barcode: str = None,
                        calories_per_100g: int = 0, protein_per_100g: float = 0,
                        carbs_per_100g: float = 0, fats_per_100g: float = 0,
                        serving_size_g: float = 100, category: str = "") -> Optional[int]:
    """Añade un alimento a la base de datos."""
    with db_lock:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO food_database 
                (food_name, barcode, calories_per_100g, protein_per_100g,
                 carbs_per_100g, fats_per_100g, serving_size_g, category)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (food_name, barcode, calories_per_100g, protein_per_100g,
                  carbs_per_100g, fats_per_100g, serving_size_g, category))
            
            food_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return food_id
        except sqlite3.IntegrityError:
            logger.warning(f"Food already exists in database: {food_name}")
            return None


def search_food_database(search_term: str) -> List[Dict[str, Any]]:
    """Busca alimentos en la base de datos."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM food_database
            WHERE food_name LIKE ? OR barcode = ?
            ORDER BY food_name
            LIMIT 50
        ''', (f'%{search_term}%', search_term))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


# ============================================================================
# FEATURE 7: Personal Dashboard Statistics
# ============================================================================

def update_user_statistics(user_id: int, workouts_completed: int = 0,
                          calories_burned: int = 0, active_minutes: int = 0,
                          date: str = None) -> bool:
    """Actualiza las estadísticas diarias del usuario."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if date is None:
            date = datetime.now().date().isoformat()
        
        # Check if entry exists
        cursor.execute('''
            SELECT id FROM user_statistics
            WHERE user_id = ? AND stat_date = ?
        ''', (user_id, date))
        
        row = cursor.fetchone()
        
        if row:
            cursor.execute('''
                UPDATE user_statistics 
                SET workouts_completed = workouts_completed + ?,
                    calories_burned = calories_burned + ?,
                    active_minutes = active_minutes + ?
                WHERE id = ?
            ''', (workouts_completed, calories_burned, active_minutes, row['id']))
        else:
            cursor.execute('''
                INSERT INTO user_statistics 
                (user_id, stat_date, workouts_completed, calories_burned, active_minutes)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, date, workouts_completed, calories_burned, active_minutes))
        
        conn.commit()
        conn.close()
        return True


def get_user_statistics(user_id: int, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
    """Obtiene las estadísticas del usuario."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if start_date and end_date:
            cursor.execute('''
                SELECT * FROM user_statistics
                WHERE user_id = ? AND stat_date BETWEEN ? AND ?
                ORDER BY stat_date DESC
            ''', (user_id, start_date, end_date))
        else:
            cursor.execute('''
                SELECT * FROM user_statistics
                WHERE user_id = ?
                ORDER BY stat_date DESC
                LIMIT 30
            ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


def update_user_streak(user_id: int, workout_date: str = None) -> Dict[str, Any]:
    """Actualiza la racha de entrenamientos del usuario."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if workout_date is None:
            workout_date = datetime.now().date().isoformat()
        
        # Get current streak data
        cursor.execute('''
            SELECT * FROM user_streaks WHERE user_id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        
        if row:
            last_date_str = row['last_workout_date']
            if last_date_str:
                last_date = datetime.fromisoformat(last_date_str).date()
                current_date = datetime.fromisoformat(workout_date).date()
                
                # Check if consecutive day
                if (current_date - last_date).days == 1:
                    # Continue streak
                    new_streak = row['current_streak'] + 1
                    new_longest = max(new_streak, row['longest_streak'])
                elif current_date == last_date:
                    # Same day, don't update
                    conn.close()
                    return dict(row)
                else:
                    # Streak broken, reset to 1
                    new_streak = 1
                    new_longest = row['longest_streak']
            else:
                new_streak = 1
                new_longest = 1
            
            cursor.execute('''
                UPDATE user_streaks 
                SET current_streak = ?, longest_streak = ?, last_workout_date = ?
                WHERE user_id = ?
            ''', (new_streak, new_longest, workout_date, user_id))
        else:
            # Create new streak record
            cursor.execute('''
                INSERT INTO user_streaks 
                (user_id, current_streak, longest_streak, last_workout_date)
                VALUES (?, 1, 1, ?)
            ''', (user_id, workout_date))
        
        conn.commit()
        
        # Get updated data
        cursor.execute('SELECT * FROM user_streaks WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else {}


def get_user_streak(user_id: int) -> Dict[str, Any]:
    """Obtiene la racha actual del usuario."""
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM user_streaks WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        
        return {
            'user_id': user_id,
            'current_streak': 0,
            'longest_streak': 0,
            'last_workout_date': None
        }
