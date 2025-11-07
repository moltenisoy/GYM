# madre_server_extended_api.py
#
# Extended API endpoints for features 1-16 from SUGERENCIAS_FUNCIONALIDADES.md
# This module contains FastAPI routers for all new functionalities

from fastapi import APIRouter, Query, HTTPException, Body, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Import extended database functions
from madre_db_extended import (
    log_exercise_session, get_exercise_history, update_exercise_progress,
    add_exercise_video, get_exercise_videos, add_custom_video_for_user, get_user_custom_videos
)
from madre_db_extended_features import (
    create_training_plan, add_workout_to_plan, mark_workout_completed,
    get_user_training_plan, get_plan_workouts, add_exercise_substitute, get_exercise_substitutes,
    add_body_measurement, get_body_measurements, add_progress_photo, get_progress_photos,
    create_nutrition_plan, add_recipe, assign_meal_to_plan, get_user_nutrition_plan,
    get_plan_meals, log_water_intake, get_water_intake, add_food_substitute, get_food_substitutes,
    log_food_entry, get_food_diary, get_daily_nutrition_totals, add_food_to_database, search_food_database,
    update_user_statistics, get_user_statistics, update_user_streak, get_user_streak
)
from madre_db_extended_features2 import (
    create_achievement, award_achievement, get_user_achievements, get_all_achievements,
    get_user_level, update_user_level, create_challenge, enroll_user_in_challenge,
    update_challenge_progress, get_active_challenges,
    create_support_ticket, add_ticket_response, update_ticket_status,
    get_user_tickets, get_ticket_responses, add_faq_item, get_faq_items,
    add_knowledge_base_article, search_knowledge_base,
    add_trainer_feedback, get_user_feedback, add_technique_correction,
    get_technique_corrections, add_improvement_suggestion, get_improvement_suggestions,
    set_trainer_availability, get_trainer_availability, create_session_booking,
    cancel_session_booking, get_user_bookings, add_to_waitlist,
    create_group_class_type, schedule_group_class, enroll_in_group_class,
    cancel_group_class_enrollment, get_available_group_classes, get_user_group_class_enrollments,
    create_user_goal, update_goal_progress, get_user_goals, add_goal_milestone,
    create_transformation_program, enroll_user_in_transformation, add_transformation_evaluation,
    get_user_transformation, get_transformation_evaluations,
    create_user_reminder, get_user_reminders, update_reminder_enabled,
    log_reminder_sent, get_reminder_history
)
import madre_db
from shared.logger import setup_logger

logger = setup_logger(__name__, log_file="madre_server_extended_api.log")


# ============================================================================
# DEPENDENCY: User Validation Helper
# ============================================================================

async def get_user_from_username(username: str) -> Dict[str, Any]:
    """Dependency to get and validate user from username."""
    user = madre_db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


# ============================================================================
# FEATURE 1: Real-time Exercise Tracking
# ============================================================================

router_exercise_tracking = APIRouter(prefix="/api/v1/exercise-tracking", tags=["Exercise Tracking"])


class ExerciseSessionRequest(BaseModel):
    username: str
    exercise_name: str
    sets: int = Field(ge=0)
    reps: int = Field(ge=0)
    weight: float = Field(ge=0)
    duration_seconds: int = Field(ge=0)
    notes: Optional[str] = ""


@router_exercise_tracking.post("/log-session")
async def log_session(request: ExerciseSessionRequest):
    """Registra una sesión de ejercicio."""
    user = await get_user_from_username(request.username)
    
    session_id = log_exercise_session(
        user['id'], request.exercise_name, request.sets, request.reps,
        request.weight, request.duration_seconds, request.notes
    )
    
    # Update progress tracking
    total_volume = request.sets * request.reps * request.weight
    update_exercise_progress(user['id'], request.exercise_name, request.weight, total_volume)
    
    # Update user statistics
    update_user_statistics(user['id'], workouts_completed=1, active_minutes=request.duration_seconds // 60)
    update_user_streak(user['id'])
    
    return {"status": "success", "session_id": session_id}


@router_exercise_tracking.get("/history")
async def get_history(username: str = Query(...), exercise_name: Optional[str] = None, limit: int = 50):
    """Obtiene el historial de ejercicios."""
    user = madre_db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    history = get_exercise_history(user['id'], exercise_name, limit)
    return {"status": "success", "history": history}


# ============================================================================
# FEATURE 2: Exercise Videos Library
# ============================================================================

router_exercise_videos = APIRouter(prefix="/api/v1/exercise-videos", tags=["Exercise Videos"])


class ExerciseVideoRequest(BaseModel):
    exercise_name: str
    video_path: str
    description: Optional[str] = ""
    difficulty_level: str = "intermediate"
    muscle_group: Optional[str] = ""
    equipment_needed: Optional[str] = ""
    duration_seconds: int = 0
    trainer_name: Optional[str] = ""


@router_exercise_videos.post("/add")
async def add_video(request: ExerciseVideoRequest):
    """Añade un video de ejercicio a la biblioteca."""
    video_id = add_exercise_video(
        request.exercise_name, request.video_path, request.description,
        request.difficulty_level, request.muscle_group, request.equipment_needed,
        request.duration_seconds, request.trainer_name
    )
    
    if video_id is None:
        raise HTTPException(status_code=409, detail="El video ya existe")
    
    return {"status": "success", "video_id": video_id}


@router_exercise_videos.get("/list")
async def list_videos(muscle_group: Optional[str] = None, difficulty: Optional[str] = None):
    """Lista videos de ejercicios."""
    videos = get_exercise_videos(muscle_group, difficulty)
    return {"status": "success", "videos": videos}


@router_exercise_videos.post("/add-custom")
async def add_custom_video(
    username: str = Body(...),
    video_path: str = Body(...),
    title: str = Body(...),
    description: str = Body(""),
    uploaded_by: str = Body("")
):
    """Añade un video personalizado para un usuario."""
    user = madre_db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    video_id = add_custom_video_for_user(user['id'], video_path, title, description, uploaded_by)
    return {"status": "success", "video_id": video_id}


@router_exercise_videos.get("/custom")
async def get_custom_videos(username: str = Query(...)):
    """Obtiene videos personalizados de un usuario."""
    user = madre_db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    videos = get_user_custom_videos(user['id'])
    return {"status": "success", "videos": videos}


# ============================================================================
# FEATURE 3: Interactive Training Plans
# ============================================================================

router_training_plans = APIRouter(prefix="/api/v1/training-plans", tags=["Training Plans"])


class TrainingPlanRequest(BaseModel):
    username: str
    plan_name: str
    start_date: str
    end_date: Optional[str] = None
    goal: Optional[str] = ""


class WorkoutRequest(BaseModel):
    plan_id: int
    scheduled_date: str
    workout_name: str
    exercises: List[Dict[str, Any]]
    duration_minutes: int = 60


@router_training_plans.post("/create")
async def create_plan(request: TrainingPlanRequest):
    """Crea un plan de entrenamiento."""
    user = madre_db.get_user(request.username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    plan_id = create_training_plan(user['id'], request.plan_name, request.start_date, request.end_date, request.goal)
    return {"status": "success", "plan_id": plan_id}


@router_training_plans.post("/add-workout")
async def add_workout(request: WorkoutRequest):
    """Añade un entrenamiento al plan."""
    workout_id = add_workout_to_plan(
        request.plan_id, request.scheduled_date, request.workout_name,
        request.exercises, request.duration_minutes
    )
    return {"status": "success", "workout_id": workout_id}


@router_training_plans.post("/complete-workout")
async def complete_workout(workout_id: int = Body(...)):
    """Marca un entrenamiento como completado."""
    success = mark_workout_completed(workout_id)
    if not success:
        raise HTTPException(status_code=404, detail="Entrenamiento no encontrado")
    return {"status": "success"}


@router_training_plans.get("/get-plan")
async def get_plan(username: str = Query(...)):
    """Obtiene el plan de entrenamiento activo del usuario."""
    user = madre_db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    plan = get_user_training_plan(user['id'])
    if not plan:
        return {"status": "success", "plan": None}
    
    # Get workouts for the plan
    workouts = get_plan_workouts(plan['id'])
    plan['workouts'] = workouts
    
    return {"status": "success", "plan": plan}


@router_training_plans.get("/substitutes")
async def get_substitutes(exercise_name: str = Query(...)):
    """Obtiene sustitutos para un ejercicio."""
    substitutes = get_exercise_substitutes(exercise_name)
    return {"status": "success", "substitutes": substitutes}


# ============================================================================
# FEATURE 4: Body Measurements Tracking
# ============================================================================

router_body_measurements = APIRouter(prefix="/api/v1/body-measurements", tags=["Body Measurements"])


class BodyMeasurementRequest(BaseModel):
    username: str
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    chest_cm: Optional[float] = None
    waist_cm: Optional[float] = None
    hips_cm: Optional[float] = None
    left_arm_cm: Optional[float] = None
    right_arm_cm: Optional[float] = None
    left_thigh_cm: Optional[float] = None
    right_thigh_cm: Optional[float] = None
    body_fat_percentage: Optional[float] = None
    muscle_mass_kg: Optional[float] = None
    notes: Optional[str] = ""


@router_body_measurements.post("/add")
async def add_measurement(request: BodyMeasurementRequest):
    """Añade mediciones corporales."""
    user = madre_db.get_user(request.username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    measurement_id = add_body_measurement(
        user['id'], request.weight_kg, request.height_cm, request.chest_cm,
        request.waist_cm, request.hips_cm, request.left_arm_cm, request.right_arm_cm,
        request.left_thigh_cm, request.right_thigh_cm, request.body_fat_percentage,
        request.muscle_mass_kg, request.notes
    )
    
    return {"status": "success", "measurement_id": measurement_id}


@router_body_measurements.get("/history")
async def get_measurements(username: str = Query(...), limit: int = 50):
    """Obtiene el historial de mediciones."""
    user = madre_db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    measurements = get_body_measurements(user['id'], limit)
    return {"status": "success", "measurements": measurements}


@router_body_measurements.post("/add-photo")
async def add_photo(
    username: str = Body(...),
    photo_type: str = Body(...),
    photo_path: str = Body(...),
    measurement_id: Optional[int] = None
):
    """Añade una foto de progreso."""
    user = madre_db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    photo_id = add_progress_photo(user['id'], photo_type, photo_path, measurement_id)
    return {"status": "success", "photo_id": photo_id}


@router_body_measurements.get("/photos")
async def get_photos(username: str = Query(...), photo_type: Optional[str] = None):
    """Obtiene fotos de progreso."""
    user = madre_db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    photos = get_progress_photos(user['id'], photo_type)
    return {"status": "success", "photos": photos}


# ============================================================================
# FEATURE 5: Personalized Nutrition Plans
# ============================================================================

router_nutrition = APIRouter(prefix="/api/v1/nutrition", tags=["Nutrition"])


class NutritionPlanRequest(BaseModel):
    username: str
    plan_name: str
    daily_calories: int
    protein_grams: int
    carbs_grams: int
    fats_grams: int
    start_date: str
    end_date: Optional[str] = None
    created_by: str = ""
    notes: Optional[str] = ""


@router_nutrition.post("/create-plan")
async def create_plan_nutrition(request: NutritionPlanRequest):
    """Crea un plan nutricional."""
    user = madre_db.get_user(request.username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    plan_id = create_nutrition_plan(
        user['id'], request.plan_name, request.daily_calories, request.protein_grams,
        request.carbs_grams, request.fats_grams, request.start_date, request.end_date,
        request.created_by, request.notes
    )
    
    return {"status": "success", "plan_id": plan_id}


@router_nutrition.get("/get-plan")
async def get_plan_nutrition(username: str = Query(...)):
    """Obtiene el plan nutricional del usuario."""
    user = madre_db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    plan = get_user_nutrition_plan(user['id'])
    if not plan:
        return {"status": "success", "plan": None}
    
    # Get meals for the plan
    meals = get_plan_meals(plan['id'])
    plan['meals'] = meals
    
    return {"status": "success", "plan": plan}


@router_nutrition.post("/log-water")
async def log_water(username: str = Body(...), water_ml: int = Body(...), date: Optional[str] = None):
    """Registra ingesta de agua."""
    user = madre_db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    log_water_intake(user['id'], water_ml, date)
    return {"status": "success"}


@router_nutrition.get("/get-water")
async def get_water(username: str = Query(...), date: Optional[str] = None):
    """Obtiene la ingesta de agua."""
    user = madre_db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    water_ml = get_water_intake(user['id'], date)
    return {"status": "success", "water_ml": water_ml}


# ============================================================================
# FEATURE 6: Food Diary
# ============================================================================

router_food_diary = APIRouter(prefix="/api/v1/food-diary", tags=["Food Diary"])


class FoodEntryRequest(BaseModel):
    username: str
    meal_type: str
    food_name: str
    quantity: float
    unit: str
    calories: int = 0
    protein: float = 0
    carbs: float = 0
    fats: float = 0
    photo_path: Optional[str] = None
    notes: Optional[str] = ""
    meal_date: Optional[str] = None
    meal_time: Optional[str] = None


@router_food_diary.post("/log-food")
async def log_food(request: FoodEntryRequest):
    """Registra una entrada en el diario alimenticio."""
    user = madre_db.get_user(request.username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    entry_id = log_food_entry(
        user['id'], request.meal_type, request.food_name, request.quantity, request.unit,
        request.calories, request.protein, request.carbs, request.fats,
        request.photo_path, request.notes, request.meal_date, request.meal_time
    )
    
    return {"status": "success", "entry_id": entry_id}


@router_food_diary.get("/get-diary")
async def get_diary(
    username: str = Query(...),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Obtiene entradas del diario alimenticio."""
    user = madre_db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    entries = get_food_diary(user['id'], start_date, end_date)
    return {"status": "success", "entries": entries}


@router_food_diary.get("/daily-totals")
async def daily_totals(username: str = Query(...), date: Optional[str] = None):
    """Obtiene los totales nutricionales del día."""
    user = madre_db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    totals = get_daily_nutrition_totals(user['id'], date)
    return {"status": "success", "totals": totals}


@router_food_diary.get("/search-food")
async def search_food(search_term: str = Query(...)):
    """Busca alimentos en la base de datos."""
    results = search_food_database(search_term)
    return {"status": "success", "results": results}


# ============================================================================
# FEATURE 7: Personal Dashboard & Statistics
# ============================================================================

router_dashboard = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard & Statistics"])


@router_dashboard.get("/statistics")
async def get_statistics(
    username: str = Query(...),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Obtiene las estadísticas del usuario."""
    user = madre_db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    stats = get_user_statistics(user['id'], start_date, end_date)
    return {"status": "success", "statistics": stats}


@router_dashboard.get("/streak")
async def get_streak(username: str = Query(...)):
    """Obtiene la racha del usuario."""
    user = madre_db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    streak = get_user_streak(user['id'])
    return {"status": "success", "streak": streak}


# ============================================================================
# FEATURE 8: Achievements & Gamification
# ============================================================================

router_gamification = APIRouter(prefix="/api/v1/gamification", tags=["Gamification"])


@router_gamification.get("/achievements")
async def get_achievements(username: str = Query(...)):
    """Obtiene los logros del usuario."""
    user = madre_db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    achievements = get_user_achievements(user['id'])
    return {"status": "success", "achievements": achievements}


@router_gamification.get("/all-achievements")
async def list_all_achievements():
    """Lista todos los logros disponibles."""
    achievements = get_all_achievements()
    return {"status": "success", "achievements": achievements}


@router_gamification.get("/level")
async def get_level(username: str = Query(...)):
    """Obtiene el nivel del usuario."""
    user = madre_db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    level = get_user_level(user['id'])
    return {"status": "success", "level": level}


@router_gamification.get("/challenges")
async def get_challenges(username: str = Query(...)):
    """Obtiene los desafíos activos del usuario."""
    user = madre_db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    challenges = get_active_challenges(user['id'])
    return {"status": "success", "challenges": challenges}


@router_gamification.post("/enroll-challenge")
async def enroll_challenge(username: str = Body(...), challenge_id: int = Body(...)):
    """Inscribe al usuario en un desafío."""
    user = madre_db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    success = enroll_user_in_challenge(user['id'], challenge_id)
    if not success:
        raise HTTPException(status_code=409, detail="Ya inscrito en el desafío")
    
    return {"status": "success"}


# Create main router that includes all sub-routers
def get_extended_api_router():
    """Returns the main API router with all extended endpoints."""
    main_router = APIRouter()
    
    main_router.include_router(router_exercise_tracking)
    main_router.include_router(router_exercise_videos)
    main_router.include_router(router_training_plans)
    main_router.include_router(router_body_measurements)
    main_router.include_router(router_nutrition)
    main_router.include_router(router_food_diary)
    main_router.include_router(router_dashboard)
    main_router.include_router(router_gamification)
    
    logger.info("Extended API router created with all feature endpoints")
    return main_router
