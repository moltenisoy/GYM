# madre_server_extended_api2.py
#
# Extended API endpoints for features 10-16 (continuation)

from fastapi import APIRouter, Query, HTTPException, Body
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

# Import extended database functions
from madre_db_extended_features2 import (
    create_support_ticket, add_ticket_response, update_ticket_status,
    get_user_tickets, get_ticket_responses, get_faq_items,
    search_knowledge_base,
    add_trainer_feedback, get_user_feedback, add_technique_correction,
    get_technique_corrections, add_improvement_suggestion, get_improvement_suggestions,
    get_trainer_availability, create_session_booking,
    cancel_session_booking, get_user_bookings,
    get_available_group_classes, get_user_group_class_enrollments,
    enroll_in_group_class, cancel_group_class_enrollment,
    create_user_goal, update_goal_progress, get_user_goals,
    get_user_transformation, get_transformation_evaluations,
    enroll_user_in_transformation, add_transformation_evaluation,
    get_user_reminders, create_user_reminder, update_reminder_enabled,
    get_reminder_history
)
import madre_db
from shared.logger import setup_logger

logger = setup_logger(__name__, log_file="madre_server_extended_api2.log")


# ============================================================================
# FEATURE 10: Q&A System (Support Tickets & FAQs)
# ============================================================================

router_support = APIRouter(prefix="/api/v1/support", tags=["Support & Q&A"])


class SupportTicketRequest(BaseModel):
    username: str
    subject: str
    body: str
    category: Optional[str] = None
    priority: str = "normal"


class TicketResponseRequest(BaseModel):
    ticket_id: int
    responder_username: str
    response_text: str
    is_internal_note: bool = False


@router_support.post("/create-ticket")
async def create_ticket(request: SupportTicketRequest):
    """Crea un ticket de soporte."""
    user = madre_db.get_user(request.username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    ticket_id = create_support_ticket(
        user['id'], request.subject, request.body, request.category, request.priority
    )
    
    return {"status": "success", "ticket_id": ticket_id}


@router_support.post("/add-response")
async def add_response(request: TicketResponseRequest):
    """Añade una respuesta a un ticket."""
    response_id = add_ticket_response(
        request.ticket_id, request.responder_username, request.response_text,
        request.is_internal_note
    )
    
    return {"status": "success", "response_id": response_id}


@router_support.post("/update-status")
async def update_status(
    ticket_id: int = Body(...),
    status: str = Body(...),
    assigned_to: Optional[str] = None
):
    """Actualiza el estado de un ticket."""
    success = update_ticket_status(ticket_id, status, assigned_to)
    if not success:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    
    return {"status": "success"}


@router_support.get("/my-tickets")
async def get_my_tickets(username: str = Query(...), status: Optional[str] = None):
    """Obtiene los tickets del usuario."""
    user = madre_db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    tickets = get_user_tickets(user['id'], status)
    return {"status": "success", "tickets": tickets}


@router_support.get("/ticket-responses")
async def get_responses(ticket_id: int = Query(...), include_internal: bool = False):
    """Obtiene las respuestas de un ticket."""
    responses = get_ticket_responses(ticket_id, include_internal)
    return {"status": "success", "responses": responses}


@router_support.get("/faq")
async def get_faq(category: Optional[str] = None):
    """Obtiene items de la FAQ."""
    faq_items = get_faq_items(category)
    return {"status": "success", "faq_items": faq_items}


@router_support.get("/search-knowledge-base")
async def search_kb(search_term: str = Query(...), category: Optional[str] = None):
    """Busca en la base de conocimientos."""
    articles = search_knowledge_base(search_term, category)
    return {"status": "success", "articles": articles}


# ============================================================================
# FEATURE 11: Trainer Feedback
# ============================================================================

router_trainer_feedback = APIRouter(prefix="/api/v1/trainer-feedback", tags=["Trainer Feedback"])


class TrainerFeedbackRequest(BaseModel):
    username: str
    trainer_username: str
    feedback_type: str
    feedback_text: str
    workout_session_id: Optional[int] = None
    media_path: Optional[str] = None


class TechniqueCorrectionRequest(BaseModel):
    username: str
    exercise_name: str
    correction_text: str
    trainer_username: str
    video_path: Optional[str] = None
    annotated_media_path: Optional[str] = None


class ImprovementSuggestionRequest(BaseModel):
    username: str
    suggestion_type: str
    suggestion_text: str
    trainer_username: str
    priority: str = "normal"


@router_trainer_feedback.post("/add-feedback")
async def add_feedback(request: TrainerFeedbackRequest):
    """Añade feedback del entrenador."""
    user = madre_db.get_user(request.username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    feedback_id = add_trainer_feedback(
        user['id'], request.trainer_username, request.feedback_type,
        request.feedback_text, request.workout_session_id, request.media_path
    )
    
    return {"status": "success", "feedback_id": feedback_id}


@router_trainer_feedback.get("/get-feedback")
async def get_feedback(username: str = Query(...), feedback_type: Optional[str] = None, limit: int = 50):
    """Obtiene el feedback del usuario."""
    user = madre_db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    feedback = get_user_feedback(user['id'], feedback_type, limit)
    return {"status": "success", "feedback": feedback}


@router_trainer_feedback.post("/add-correction")
async def add_correction(request: TechniqueCorrectionRequest):
    """Añade una corrección de técnica."""
    user = madre_db.get_user(request.username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    correction_id = add_technique_correction(
        user['id'], request.exercise_name, request.correction_text,
        request.trainer_username, request.video_path, request.annotated_media_path
    )
    
    return {"status": "success", "correction_id": correction_id}


@router_trainer_feedback.get("/get-corrections")
async def get_corrections(username: str = Query(...), exercise_name: Optional[str] = None):
    """Obtiene las correcciones de técnica."""
    user = madre_db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    corrections = get_technique_corrections(user['id'], exercise_name)
    return {"status": "success", "corrections": corrections}


@router_trainer_feedback.post("/add-suggestion")
async def add_suggestion(request: ImprovementSuggestionRequest):
    """Añade una sugerencia de mejora."""
    user = madre_db.get_user(request.username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    suggestion_id = add_improvement_suggestion(
        user['id'], request.suggestion_type, request.suggestion_text,
        request.trainer_username, request.priority
    )
    
    return {"status": "success", "suggestion_id": suggestion_id}


@router_trainer_feedback.get("/get-suggestions")
async def get_suggestions(username: str = Query(...), acknowledged: Optional[bool] = None):
    """Obtiene las sugerencias de mejora."""
    user = madre_db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    suggestions = get_improvement_suggestions(user['id'], acknowledged)
    return {"status": "success", "suggestions": suggestions}


# ============================================================================
# FEATURE 12: Session Booking
# ============================================================================

router_booking = APIRouter(prefix="/api/v1/booking", tags=["Session Booking"])


class SessionBookingRequest(BaseModel):
    username: str
    trainer_username: str
    booking_date: str
    start_time: str
    end_time: str
    session_type: str
    notes: Optional[str] = ""


@router_booking.get("/trainer-availability")
async def get_availability(trainer_username: str = Query(...), day_of_week: Optional[str] = None):
    """Obtiene la disponibilidad del entrenador."""
    availability = get_trainer_availability(trainer_username, day_of_week)
    return {"status": "success", "availability": availability}


@router_booking.post("/create-booking")
async def create_booking(request: SessionBookingRequest):
    """Crea una reserva de sesión."""
    user = madre_db.get_user(request.username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    booking_id = create_session_booking(
        user['id'], request.trainer_username, request.booking_date,
        request.start_time, request.end_time, request.session_type, request.notes
    )
    
    return {"status": "success", "booking_id": booking_id}


@router_booking.post("/cancel-booking")
async def cancel_booking(booking_id: int = Body(...), reason: str = Body("")):
    """Cancela una reserva de sesión."""
    success = cancel_session_booking(booking_id, reason)
    if not success:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    
    return {"status": "success"}


@router_booking.get("/my-bookings")
async def get_my_bookings(username: str = Query(...), status: Optional[str] = None):
    """Obtiene las reservas del usuario."""
    user = madre_db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    bookings = get_user_bookings(user['id'], status)
    return {"status": "success", "bookings": bookings}


# ============================================================================
# FEATURE 13: Group Classes
# ============================================================================

router_group_classes = APIRouter(prefix="/api/v1/group-classes", tags=["Group Classes"])


@router_group_classes.get("/available-classes")
async def get_classes(start_date: Optional[str] = None):
    """Obtiene las clases grupales disponibles."""
    classes = get_available_group_classes(start_date)
    return {"status": "success", "classes": classes}


@router_group_classes.post("/enroll")
async def enroll_class(username: str = Body(...), class_schedule_id: int = Body(...)):
    """Inscribe al usuario en una clase grupal."""
    user = madre_db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    success = enroll_in_group_class(class_schedule_id, user['id'])
    if not success:
        raise HTTPException(status_code=409, detail="No se puede inscribir (clase llena o ya inscrito)")
    
    return {"status": "success"}


@router_group_classes.post("/cancel-enrollment")
async def cancel_enrollment(username: str = Body(...), class_schedule_id: int = Body(...)):
    """Cancela la inscripción en una clase grupal."""
    user = madre_db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    success = cancel_group_class_enrollment(class_schedule_id, user['id'])
    if not success:
        raise HTTPException(status_code=404, detail="Inscripción no encontrada")
    
    return {"status": "success"}


@router_group_classes.get("/my-enrollments")
async def get_my_enrollments(username: str = Query(...)):
    """Obtiene las inscripciones a clases grupales del usuario."""
    user = madre_db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    enrollments = get_user_group_class_enrollments(user['id'])
    return {"status": "success", "enrollments": enrollments}


# ============================================================================
# FEATURE 14: Goal Setting
# ============================================================================

router_goals = APIRouter(prefix="/api/v1/goals", tags=["Goals"])


class UserGoalRequest(BaseModel):
    username: str
    goal_type: str
    goal_description: str
    target_value: float
    unit: str
    timeframe: str
    start_date: str
    target_date: str


@router_goals.post("/create-goal")
async def create_goal(request: UserGoalRequest):
    """Crea un objetivo para el usuario."""
    user = madre_db.get_user(request.username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    goal_id = create_user_goal(
        user['id'], request.goal_type, request.goal_description, request.target_value,
        request.unit, request.timeframe, request.start_date, request.target_date
    )
    
    return {"status": "success", "goal_id": goal_id}


@router_goals.post("/update-progress")
async def update_progress(goal_id: int = Body(...), current_value: float = Body(...)):
    """Actualiza el progreso de un objetivo."""
    success = update_goal_progress(goal_id, current_value)
    if not success:
        raise HTTPException(status_code=404, detail="Objetivo no encontrado")
    
    return {"status": "success"}


@router_goals.get("/my-goals")
async def get_my_goals(username: str = Query(...), status: Optional[str] = None):
    """Obtiene los objetivos del usuario."""
    user = madre_db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    goals = get_user_goals(user['id'], status)
    return {"status": "success", "goals": goals}


# ============================================================================
# FEATURE 15: Transformation Programs
# ============================================================================

router_transformation = APIRouter(prefix="/api/v1/transformation", tags=["Transformation Programs"])


class TransformationEvaluationRequest(BaseModel):
    transformation_id: int
    evaluation_week: int
    weight_kg: Optional[float] = None
    body_fat_percentage: Optional[float] = None
    notes: Optional[str] = ""
    photo_front: Optional[str] = None
    photo_side: Optional[str] = None
    photo_back: Optional[str] = None


@router_transformation.post("/enroll")
async def enroll_transformation(
    username: str = Body(...),
    program_id: int = Body(...),
    start_date: str = Body(...)
):
    """Inscribe al usuario en un programa de transformación."""
    user = madre_db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    transformation_id = enroll_user_in_transformation(user['id'], program_id, start_date)
    if not transformation_id:
        raise HTTPException(status_code=404, detail="Programa no encontrado")
    
    return {"status": "success", "transformation_id": transformation_id}


@router_transformation.post("/add-evaluation")
async def add_evaluation(request: TransformationEvaluationRequest):
    """Añade una evaluación al programa de transformación."""
    evaluation_id = add_transformation_evaluation(
        request.transformation_id, request.evaluation_week, request.weight_kg,
        request.body_fat_percentage, request.notes, request.photo_front,
        request.photo_side, request.photo_back
    )
    
    return {"status": "success", "evaluation_id": evaluation_id}


@router_transformation.get("/my-program")
async def get_my_program(username: str = Query(...)):
    """Obtiene el programa de transformación activo del usuario."""
    user = madre_db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    program = get_user_transformation(user['id'])
    if not program:
        return {"status": "success", "program": None}
    
    # Get evaluations
    evaluations = get_transformation_evaluations(program['id'])
    program['evaluations'] = evaluations
    
    return {"status": "success", "program": program}


# ============================================================================
# FEATURE 16: Reminder System
# ============================================================================

router_reminders = APIRouter(prefix="/api/v1/reminders", tags=["Reminders"])


class ReminderRequest(BaseModel):
    username: str
    reminder_type: str
    reminder_time: str
    days_of_week: Optional[str] = None
    custom_message: Optional[str] = None
    enabled: bool = True


@router_reminders.post("/create-reminder")
async def create_reminder(request: ReminderRequest):
    """Crea un recordatorio para el usuario."""
    user = madre_db.get_user(request.username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    reminder_id = create_user_reminder(
        user['id'], request.reminder_type, request.reminder_time,
        request.days_of_week, request.custom_message, request.enabled
    )
    
    return {"status": "success", "reminder_id": reminder_id}


@router_reminders.get("/my-reminders")
async def get_my_reminders(username: str = Query(...), enabled_only: bool = True):
    """Obtiene los recordatorios del usuario."""
    user = madre_db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    reminders = get_user_reminders(user['id'], enabled_only)
    return {"status": "success", "reminders": reminders}


@router_reminders.post("/toggle-reminder")
async def toggle_reminder(reminder_id: int = Body(...), enabled: bool = Body(...)):
    """Activa/desactiva un recordatorio."""
    success = update_reminder_enabled(reminder_id, enabled)
    if not success:
        raise HTTPException(status_code=404, detail="Recordatorio no encontrado")
    
    return {"status": "success"}


@router_reminders.get("/history")
async def get_history_reminders(username: str = Query(...), reminder_type: Optional[str] = None, limit: int = 50):
    """Obtiene el historial de recordatorios."""
    user = madre_db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    history = get_reminder_history(user['id'], reminder_type, limit)
    return {"status": "success", "history": history}


# ============================================================================
# Create Combined Router
# ============================================================================

def get_extended_api_router2():
    """Returns the secondary API router with features 10-16 endpoints."""
    main_router = APIRouter()
    
    main_router.include_router(router_support)
    main_router.include_router(router_trainer_feedback)
    main_router.include_router(router_booking)
    main_router.include_router(router_group_classes)
    main_router.include_router(router_goals)
    main_router.include_router(router_transformation)
    main_router.include_router(router_reminders)
    
    logger.info("Extended API router 2 created with features 10-16 endpoints")
    return main_router
