# hija_views_extended.py
#
# Extended GUI views for Hija application - Features 1-16
# This module contains custom frames for all new functionalities

import customtkinter
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Callable


class ExerciseTrackingView(customtkinter.CTkScrollableFrame):
    """Vista para seguimiento de ejercicios en tiempo real (Feature 1)"""
    
    def __init__(self, master, on_log_exercise: Callable, **kwargs):
        super().__init__(master, **kwargs)
        self.on_log_exercise = on_log_exercise
        
        # Header
        lbl_title = customtkinter.CTkLabel(
            self,
            text="💪 Seguimiento de Ejercicios",
            font=customtkinter.CTkFont(size=24, weight="bold")
        )
        lbl_title.pack(pady=20)
        
        # Formulario de registro
        form_frame = customtkinter.CTkFrame(self)
        form_frame.pack(pady=10, padx=20, fill="x")
        
        # Exercise name
        customtkinter.CTkLabel(form_frame, text="Ejercicio:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.entry_exercise = customtkinter.CTkEntry(form_frame, width=300, placeholder_text="Nombre del ejercicio")
        self.entry_exercise.grid(row=0, column=1, padx=10, pady=5)
        
        # Sets
        customtkinter.CTkLabel(form_frame, text="Series:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.entry_sets = customtkinter.CTkEntry(form_frame, width=100, placeholder_text="3")
        self.entry_sets.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        # Reps
        customtkinter.CTkLabel(form_frame, text="Repeticiones:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.entry_reps = customtkinter.CTkEntry(form_frame, width=100, placeholder_text="12")
        self.entry_reps.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        # Weight
        customtkinter.CTkLabel(form_frame, text="Peso (kg):").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.entry_weight = customtkinter.CTkEntry(form_frame, width=100, placeholder_text="50")
        self.entry_weight.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        
        # Duration (timer display)
        customtkinter.CTkLabel(form_frame, text="Duración:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.lbl_duration = customtkinter.CTkLabel(form_frame, text="00:00", font=customtkinter.CTkFont(size=20))
        self.lbl_duration.grid(row=4, column=1, padx=10, pady=5, sticky="w")
        
        # Timer controls
        timer_frame = customtkinter.CTkFrame(form_frame, fg_color="transparent")
        timer_frame.grid(row=5, column=1, padx=10, pady=5, sticky="w")
        
        self.btn_start_timer = customtkinter.CTkButton(
            timer_frame,
            text="▶ Iniciar",
            width=80,
            command=self._start_timer
        )
        self.btn_start_timer.pack(side="left", padx=5)
        
        self.btn_stop_timer = customtkinter.CTkButton(
            timer_frame,
            text="⏸ Pausar",
            width=80,
            command=self._stop_timer,
            state="disabled"
        )
        self.btn_stop_timer.pack(side="left", padx=5)
        
        # Notes
        customtkinter.CTkLabel(form_frame, text="Notas:").grid(row=6, column=0, padx=10, pady=5, sticky="nw")
        self.txt_notes = customtkinter.CTkTextbox(form_frame, width=300, height=80)
        self.txt_notes.grid(row=6, column=1, padx=10, pady=5)
        
        # Save button
        self.btn_save = customtkinter.CTkButton(
            form_frame,
            text="💾 Guardar Sesión",
            command=self._save_session,
            fg_color="#10b981",
            hover_color="#059669"
        )
        self.btn_save.grid(row=7, column=0, columnspan=2, padx=10, pady=20)
        
        # Timer variables
        self.timer_running = False
        self.timer_seconds = 0
        self.timer_job = None
        
        # History display
        self.history_frame = customtkinter.CTkFrame(self)
        self.history_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        customtkinter.CTkLabel(
            self.history_frame,
            text="📊 Historial Reciente",
            font=customtkinter.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        self.history_list = customtkinter.CTkScrollableFrame(self.history_frame, height=200)
        self.history_list.pack(fill="both", expand=True, padx=10, pady=10)
    
    def _start_timer(self):
        """Inicia el cronómetro."""
        self.timer_running = True
        self.btn_start_timer.configure(state="disabled")
        self.btn_stop_timer.configure(state="normal")
        self._update_timer()
    
    def _stop_timer(self):
        """Detiene el cronómetro."""
        self.timer_running = False
        self.btn_start_timer.configure(state="normal")
        self.btn_stop_timer.configure(state="disabled")
        if self.timer_job:
            self.after_cancel(self.timer_job)
    
    def _update_timer(self):
        """Actualiza el cronómetro."""
        if self.timer_running:
            self.timer_seconds += 1
            minutes = self.timer_seconds // 60
            seconds = self.timer_seconds % 60
            self.lbl_duration.configure(text=f"{minutes:02d}:{seconds:02d}")
            self.timer_job = self.after(1000, self._update_timer)
    
    def _save_session(self):
        """Guarda la sesión de ejercicio."""
        try:
            exercise = self.entry_exercise.get()
            sets = int(self.entry_sets.get() or 0)
            reps = int(self.entry_reps.get() or 0)
            weight = float(self.entry_weight.get() or 0)
            notes = self.txt_notes.get("1.0", "end-1c")
            
            if not exercise:
                self._show_error("Por favor ingrese el nombre del ejercicio")
                return
            
            # Call the callback
            self.on_log_exercise({
                'exercise_name': exercise,
                'sets': sets,
                'reps': reps,
                'weight': weight,
                'duration_seconds': self.timer_seconds,
                'notes': notes
            })
            
            # Reset form
            self.entry_exercise.delete(0, "end")
            self.entry_sets.delete(0, "end")
            self.entry_reps.delete(0, "end")
            self.entry_weight.delete(0, "end")
            self.txt_notes.delete("1.0", "end")
            self.timer_seconds = 0
            self.lbl_duration.configure(text="00:00")
            
        except ValueError as e:
            self._show_error(f"Error en los valores ingresados: {e}")
    
    def _show_error(self, message: str):
        """Muestra un mensaje de error."""
        # TODO: Implement error display
        print(f"Error: {message}")
    
    def update_history(self, history: List[Dict[str, Any]]):
        """Actualiza el historial de ejercicios."""
        # Clear current history
        for widget in self.history_list.winfo_children():
            widget.destroy()
        
        # Add history items
        for item in history[:10]:  # Show last 10
            item_frame = customtkinter.CTkFrame(self.history_list)
            item_frame.pack(fill="x", padx=5, pady=2)
            
            date = item.get('session_date', '')[:10]
            exercise = item.get('exercise_name', '')
            sets = item.get('sets_completed', 0)
            reps = item.get('reps_completed', 0)
            weight = item.get('weight_used', 0)
            
            text = f"📅 {date} | {exercise} | {sets}x{reps} @ {weight}kg"
            customtkinter.CTkLabel(item_frame, text=text, anchor="w").pack(side="left", padx=10, pady=5)


class TrainingPlanView(customtkinter.CTkScrollableFrame):
    """Vista para plan de entrenamiento interactivo (Feature 3)"""
    
    def __init__(self, master, on_complete_workout: Callable, **kwargs):
        super().__init__(master, **kwargs)
        self.on_complete_workout = on_complete_workout
        self.current_plan = None
        
        # Header
        lbl_title = customtkinter.CTkLabel(
            self,
            text="📅 Plan de Entrenamiento",
            font=customtkinter.CTkFont(size=24, weight="bold")
        )
        lbl_title.pack(pady=20)
        
        # Plan info frame
        self.plan_info_frame = customtkinter.CTkFrame(self)
        self.plan_info_frame.pack(pady=10, padx=20, fill="x")
        
        # Workout calendar/list
        self.workouts_frame = customtkinter.CTkFrame(self)
        self.workouts_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        customtkinter.CTkLabel(
            self.workouts_frame,
            text="📋 Entrenamientos Programados",
            font=customtkinter.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        self.workouts_list = customtkinter.CTkScrollableFrame(self.workouts_frame)
        self.workouts_list.pack(fill="both", expand=True, padx=10, pady=10)
    
    def update_plan(self, plan_data: Optional[Dict[str, Any]]):
        """Actualiza la información del plan."""
        self.current_plan = plan_data
        
        # Clear plan info
        for widget in self.plan_info_frame.winfo_children():
            widget.destroy()
        
        if not plan_data:
            customtkinter.CTkLabel(
                self.plan_info_frame,
                text="No tienes un plan de entrenamiento activo",
                font=customtkinter.CTkFont(size=16)
            ).pack(pady=20)
            return
        
        # Display plan info
        info_text = f"Plan: {plan_data.get('plan_name', '')}\n"
        info_text += f"Objetivo: {plan_data.get('goal', 'No especificado')}\n"
        info_text += f"Inicio: {plan_data.get('start_date', '')[:10]}"
        
        customtkinter.CTkLabel(
            self.plan_info_frame,
            text=info_text,
            font=customtkinter.CTkFont(size=14),
            justify="left"
        ).pack(padx=20, pady=10)
        
        # Update workouts
        self._update_workouts(plan_data.get('workouts', []))
    
    def _update_workouts(self, workouts: List[Dict[str, Any]]):
        """Actualiza la lista de entrenamientos."""
        # Clear workouts list
        for widget in self.workouts_list.winfo_children():
            widget.destroy()
        
        if not workouts:
            customtkinter.CTkLabel(
                self.workouts_list,
                text="No hay entrenamientos programados",
                text_color="gray"
            ).pack(pady=20)
            return
        
        # Sort by date
        workouts_sorted = sorted(workouts, key=lambda x: x.get('scheduled_date', ''))
        
        for workout in workouts_sorted:
            self._create_workout_item(workout)
    
    def _create_workout_item(self, workout: Dict[str, Any]):
        """Crea un item de entrenamiento."""
        workout_frame = customtkinter.CTkFrame(self.workouts_list)
        workout_frame.pack(fill="x", padx=5, pady=5)
        
        # Date and name
        date = workout.get('scheduled_date', '')[:10]
        name = workout.get('workout_name', '')
        completed = workout.get('completed', 0)
        
        info_frame = customtkinter.CTkFrame(workout_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        status_icon = "✅" if completed else "⭕"
        lbl_name = customtkinter.CTkLabel(
            info_frame,
            text=f"{status_icon} {date} - {name}",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        lbl_name.pack(anchor="w")
        
        # Exercise count
        exercises = workout.get('exercises_json', [])
        if isinstance(exercises, list):
            lbl_exercises = customtkinter.CTkLabel(
                info_frame,
                text=f"{len(exercises)} ejercicios | {workout.get('duration_minutes', 0)} min",
                text_color="gray",
                anchor="w"
            )
            lbl_exercises.pack(anchor="w")
        
        # Complete button
        if not completed:
            btn_complete = customtkinter.CTkButton(
                workout_frame,
                text="Completar",
                width=100,
                command=lambda: self._complete_workout(workout['id']),
                fg_color="#10b981",
                hover_color="#059669"
            )
            btn_complete.pack(side="right", padx=10, pady=10)
    
    def _complete_workout(self, workout_id: int):
        """Marca un entrenamiento como completado."""
        if self.on_complete_workout:
            self.on_complete_workout(workout_id)


class BodyMeasurementsView(customtkinter.CTkScrollableFrame):
    """Vista para seguimiento de medidas corporales (Feature 4)"""
    
    def __init__(self, master, on_add_measurement: Callable, **kwargs):
        super().__init__(master, **kwargs)
        self.on_add_measurement = on_add_measurement
        
        # Header
        lbl_title = customtkinter.CTkLabel(
            self,
            text="📏 Medidas Corporales",
            font=customtkinter.CTkFont(size=24, weight="bold")
        )
        lbl_title.pack(pady=20)
        
        # Form frame
        form_frame = customtkinter.CTkFrame(self)
        form_frame.pack(pady=10, padx=20, fill="x")
        
        # Weight
        customtkinter.CTkLabel(form_frame, text="Peso (kg):").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.entry_weight = customtkinter.CTkEntry(form_frame, width=150)
        self.entry_weight.grid(row=0, column=1, padx=10, pady=5)
        
        # Height
        customtkinter.CTkLabel(form_frame, text="Altura (cm):").grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.entry_height = customtkinter.CTkEntry(form_frame, width=150)
        self.entry_height.grid(row=0, column=3, padx=10, pady=5)
        
        # Body fat
        customtkinter.CTkLabel(form_frame, text="Grasa Corporal (%):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.entry_body_fat = customtkinter.CTkEntry(form_frame, width=150)
        self.entry_body_fat.grid(row=1, column=1, padx=10, pady=5)
        
        # Muscle mass
        customtkinter.CTkLabel(form_frame, text="Masa Muscular (kg):").grid(row=1, column=2, padx=10, pady=5, sticky="w")
        self.entry_muscle_mass = customtkinter.CTkEntry(form_frame, width=150)
        self.entry_muscle_mass.grid(row=1, column=3, padx=10, pady=5)
        
        # Circumferences section
        circum_frame = customtkinter.CTkFrame(form_frame)
        circum_frame.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky="ew")
        
        customtkinter.CTkLabel(
            circum_frame,
            text="Circunferencias (cm):",
            font=customtkinter.CTkFont(weight="bold")
        ).grid(row=0, column=0, columnspan=4, padx=10, pady=5)
        
        # Chest, waist, hips
        customtkinter.CTkLabel(circum_frame, text="Pecho:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_chest = customtkinter.CTkEntry(circum_frame, width=100)
        self.entry_chest.grid(row=1, column=1, padx=5, pady=5)
        
        customtkinter.CTkLabel(circum_frame, text="Cintura:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.entry_waist = customtkinter.CTkEntry(circum_frame, width=100)
        self.entry_waist.grid(row=1, column=3, padx=5, pady=5)
        
        customtkinter.CTkLabel(circum_frame, text="Cadera:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entry_hips = customtkinter.CTkEntry(circum_frame, width=100)
        self.entry_hips.grid(row=2, column=1, padx=5, pady=5)
        
        # Arms
        customtkinter.CTkLabel(circum_frame, text="Brazo Izq:").grid(row=2, column=2, padx=5, pady=5, sticky="w")
        self.entry_left_arm = customtkinter.CTkEntry(circum_frame, width=100)
        self.entry_left_arm.grid(row=2, column=3, padx=5, pady=5)
        
        customtkinter.CTkLabel(circum_frame, text="Brazo Der:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.entry_right_arm = customtkinter.CTkEntry(circum_frame, width=100)
        self.entry_right_arm.grid(row=3, column=1, padx=5, pady=5)
        
        # Thighs
        customtkinter.CTkLabel(circum_frame, text="Pierna Izq:").grid(row=3, column=2, padx=5, pady=5, sticky="w")
        self.entry_left_thigh = customtkinter.CTkEntry(circum_frame, width=100)
        self.entry_left_thigh.grid(row=3, column=3, padx=5, pady=5)
        
        customtkinter.CTkLabel(circum_frame, text="Pierna Der:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.entry_right_thigh = customtkinter.CTkEntry(circum_frame, width=100)
        self.entry_right_thigh.grid(row=4, column=1, padx=5, pady=5)
        
        # Notes
        customtkinter.CTkLabel(form_frame, text="Notas:").grid(row=3, column=0, padx=10, pady=5, sticky="nw")
        self.txt_notes = customtkinter.CTkTextbox(form_frame, width=500, height=60)
        self.txt_notes.grid(row=3, column=1, columnspan=3, padx=10, pady=5)
        
        # Save button
        btn_save = customtkinter.CTkButton(
            form_frame,
            text="💾 Guardar Mediciones",
            command=self._save_measurements,
            fg_color="#10b981",
            hover_color="#059669"
        )
        btn_save.grid(row=4, column=0, columnspan=4, padx=10, pady=20)
        
        # History display
        self.history_frame = customtkinter.CTkFrame(self)
        self.history_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        customtkinter.CTkLabel(
            self.history_frame,
            text="📊 Historial de Mediciones",
            font=customtkinter.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        self.history_list = customtkinter.CTkScrollableFrame(self.history_frame, height=200)
        self.history_list.pack(fill="both", expand=True, padx=10, pady=10)
    
    def _save_measurements(self):
        """Guarda las mediciones."""
        try:
            def get_float(entry):
                val = entry.get().strip()
                return float(val) if val else None
            
            data = {
                'weight_kg': get_float(self.entry_weight),
                'height_cm': get_float(self.entry_height),
                'body_fat_percentage': get_float(self.entry_body_fat),
                'muscle_mass_kg': get_float(self.entry_muscle_mass),
                'chest_cm': get_float(self.entry_chest),
                'waist_cm': get_float(self.entry_waist),
                'hips_cm': get_float(self.entry_hips),
                'left_arm_cm': get_float(self.entry_left_arm),
                'right_arm_cm': get_float(self.entry_right_arm),
                'left_thigh_cm': get_float(self.entry_left_thigh),
                'right_thigh_cm': get_float(self.entry_right_thigh),
                'notes': self.txt_notes.get("1.0", "end-1c")
            }
            
            if self.on_add_measurement:
                self.on_add_measurement(data)
            
            # Clear form
            for entry in [self.entry_weight, self.entry_height, self.entry_body_fat, 
                         self.entry_muscle_mass, self.entry_chest, self.entry_waist,
                         self.entry_hips, self.entry_left_arm, self.entry_right_arm,
                         self.entry_left_thigh, self.entry_right_thigh]:
                entry.delete(0, "end")
            self.txt_notes.delete("1.0", "end")
            
        except ValueError as e:
            print(f"Error: {e}")
    
    def update_history(self, measurements: List[Dict[str, Any]]):
        """Actualiza el historial de mediciones."""
        # Clear history
        for widget in self.history_list.winfo_children():
            widget.destroy()
        
        # Add measurements
        for measure in measurements[:10]:
            item_frame = customtkinter.CTkFrame(self.history_list)
            item_frame.pack(fill="x", padx=5, pady=2)
            
            date = measure.get('measurement_date', '')[:10]
            weight = measure.get('weight_kg', 0)
            bmi = measure.get('bmi', 0)
            body_fat = measure.get('body_fat_percentage', 0)
            
            text = f"📅 {date} | Peso: {weight}kg | IMC: {bmi:.1f} | Grasa: {body_fat}%"
            customtkinter.CTkLabel(item_frame, text=text, anchor="w").pack(side="left", padx=10, pady=5)


class NutritionPlanView(customtkinter.CTkScrollableFrame):
    """Vista para plan nutricional (Feature 5)"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Header
        lbl_title = customtkinter.CTkLabel(
            self,
            text="🍎 Plan Nutricional",
            font=customtkinter.CTkFont(size=24, weight="bold")
        )
        lbl_title.pack(pady=20)
        
        # Plan info frame
        self.plan_info_frame = customtkinter.CTkFrame(self)
        self.plan_info_frame.pack(pady=10, padx=20, fill="x")
        
        # Water intake tracker
        water_frame = customtkinter.CTkFrame(self)
        water_frame.pack(pady=10, padx=20, fill="x")
        
        customtkinter.CTkLabel(
            water_frame,
            text="💧 Ingesta de Agua Diaria",
            font=customtkinter.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        self.lbl_water = customtkinter.CTkLabel(
            water_frame,
            text="0 ml / 2000 ml",
            font=customtkinter.CTkFont(size=18)
        )
        self.lbl_water.pack(pady=5)
        
        self.water_progress = customtkinter.CTkProgressBar(water_frame, width=400)
        self.water_progress.pack(pady=10)
        self.water_progress.set(0)
        
        # Meals frame
        self.meals_frame = customtkinter.CTkFrame(self)
        self.meals_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        customtkinter.CTkLabel(
            self.meals_frame,
            text="🍽️ Comidas del Plan",
            font=customtkinter.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        self.meals_list = customtkinter.CTkScrollableFrame(self.meals_frame)
        self.meals_list.pack(fill="both", expand=True, padx=10, pady=10)
    
    def update_plan(self, plan_data: Optional[Dict[str, Any]]):
        """Actualiza el plan nutricional."""
        # Clear plan info
        for widget in self.plan_info_frame.winfo_children():
            widget.destroy()
        
        if not plan_data:
            customtkinter.CTkLabel(
                self.plan_info_frame,
                text="No tienes un plan nutricional asignado",
                font=customtkinter.CTkFont(size=16)
            ).pack(pady=20)
            return
        
        # Display plan info
        info_text = f"Plan: {plan_data.get('plan_name', '')}\n"
        info_text += f"Calorías diarias: {plan_data.get('daily_calories', 0)} kcal\n"
        info_text += f"Proteínas: {plan_data.get('protein_grams', 0)}g | "
        info_text += f"Carbohidratos: {plan_data.get('carbs_grams', 0)}g | "
        info_text += f"Grasas: {plan_data.get('fats_grams', 0)}g"
        
        customtkinter.CTkLabel(
            self.plan_info_frame,
            text=info_text,
            font=customtkinter.CTkFont(size=14),
            justify="left"
        ).pack(padx=20, pady=10)
        
        # Update meals
        self._update_meals(plan_data.get('meals', []))
    
    def _update_meals(self, meals: List[Dict[str, Any]]):
        """Actualiza la lista de comidas."""
        # Clear meals list
        for widget in self.meals_list.winfo_children():
            widget.destroy()
        
        if not meals:
            customtkinter.CTkLabel(
                self.meals_list,
                text="No hay comidas programadas",
                text_color="gray"
            ).pack(pady=20)
            return
        
        # Group by day of week
        days_order = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        meals_by_day = {}
        for meal in meals:
            day = meal.get('day_of_week', '')
            if day not in meals_by_day:
                meals_by_day[day] = []
            meals_by_day[day].append(meal)
        
        # Display by day
        for day in days_order:
            if day in meals_by_day:
                day_frame = customtkinter.CTkFrame(self.meals_list)
                day_frame.pack(fill="x", padx=5, pady=10)
                
                customtkinter.CTkLabel(
                    day_frame,
                    text=day,
                    font=customtkinter.CTkFont(size=16, weight="bold")
                ).pack(anchor="w", padx=10, pady=5)
                
                for meal in meals_by_day[day]:
                    meal_time = meal.get('meal_time', '')
                    recipe_name = meal.get('recipe_name') or meal.get('custom_meal_description', '')
                    text = f"  {meal_time}: {recipe_name}"
                    customtkinter.CTkLabel(
                        day_frame,
                        text=text,
                        anchor="w"
                    ).pack(anchor="w", padx=20, pady=2)
    
    def update_water_intake(self, water_ml: int, goal_ml: int = 2000):
        """Actualiza el indicador de ingesta de agua."""
        self.lbl_water.configure(text=f"{water_ml} ml / {goal_ml} ml")
        progress = min(water_ml / goal_ml, 1.0)
        self.water_progress.set(progress)


class DashboardView(customtkinter.CTkScrollableFrame):
    """Vista del dashboard personal (Feature 7)"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Header
        lbl_title = customtkinter.CTkLabel(
            self,
            text="📊 Dashboard Personal",
            font=customtkinter.CTkFont(size=24, weight="bold")
        )
        lbl_title.pack(pady=20)
        
        # Stats grid
        stats_container = customtkinter.CTkFrame(self)
        stats_container.pack(pady=10, padx=20, fill="x")
        
        # Configure grid
        for i in range(3):
            stats_container.grid_columnconfigure(i, weight=1)
        
        # Stat cards
        self.card_workouts = self._create_stat_card(stats_container, "💪 Entrenamientos", "0", "esta semana")
        self.card_workouts.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.card_calories = self._create_stat_card(stats_container, "🔥 Calorías", "0", "quemadas hoy")
        self.card_calories.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        self.card_streak = self._create_stat_card(stats_container, "⚡ Racha", "0", "días consecutivos")
        self.card_streak.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        
        # Progress chart placeholder
        chart_frame = customtkinter.CTkFrame(self)
        chart_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        customtkinter.CTkLabel(
            chart_frame,
            text="📈 Progreso Semanal",
            font=customtkinter.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        self.chart_area = customtkinter.CTkFrame(chart_frame, height=200)
        self.chart_area.pack(fill="both", expand=True, padx=10, pady=10)
    
    def _create_stat_card(self, parent, title: str, value: str, subtitle: str):
        """Crea una tarjeta de estadística."""
        card = customtkinter.CTkFrame(parent)
        
        customtkinter.CTkLabel(
            card,
            text=title,
            font=customtkinter.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        lbl_value = customtkinter.CTkLabel(
            card,
            text=value,
            font=customtkinter.CTkFont(size=32, weight="bold")
        )
        lbl_value.pack(pady=5)
        
        customtkinter.CTkLabel(
            card,
            text=subtitle,
            font=customtkinter.CTkFont(size=12),
            text_color="gray"
        ).pack(pady=(5, 10))
        
        # Store reference to value label
        card.value_label = lbl_value
        
        return card
    
    def update_stats(self, stats_data: Dict[str, Any]):
        """Actualiza las estadísticas."""
        if 'workouts' in stats_data:
            self.card_workouts.value_label.configure(text=str(stats_data['workouts']))
        
        if 'calories' in stats_data:
            self.card_calories.value_label.configure(text=str(stats_data['calories']))
        
        if 'streak' in stats_data:
            self.card_streak.value_label.configure(text=str(stats_data['streak']))
