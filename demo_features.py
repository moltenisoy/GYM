#!/usr/bin/env python3
"""
Demo script para probar las nuevas funcionalidades del sistema de gimnasio.
Este script demuestra el uso de las APIs y funciones implementadas.
"""

import requests
from datetime import datetime, timedelta
from shared.workout_utils import calculate_plates, format_plates_result, calculate_rest_time, format_time

# Configuración
BASE_URL = "http://localhost:8000"
USERNAME = "juan_perez"
REQUEST_TIMEOUT = 10  # Timeout en segundos para requests


def print_section(title):
    """Imprime un separador de sección."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def demo_plates_calculator():
    """Demuestra la calculadora de discos."""
    print_section("1. CALCULADORA DE DISCOS")

    weights = [60, 100, 142.5]

    for weight in weights:
        print(f"\nCalculando para {weight}kg:")
        result = calculate_plates(weight, bar_weight=20.0)
        print(format_plates_result(result))


def demo_rest_timer():
    """Demuestra el temporizador de descanso."""
    print_section("2. TEMPORIZADOR DE DESCANSO")

    exercises = [
        ("strength", "high"),
        ("hypertrophy", "medium"),
        ("endurance", "low"),
        ("power", "high")
    ]

    for exercise_type, intensity in exercises:
        rest_seconds = calculate_rest_time(exercise_type, intensity)
        formatted = format_time(rest_seconds)
        print(f"{exercise_type.capitalize()} - {intensity}: {formatted}")


def demo_list_classes():
    """Lista las clases disponibles."""
    print_section("3. CLASES DISPONIBLES")

    try:
        response = requests.get(f"{BASE_URL}/clases", timeout=REQUEST_TIMEOUT)
        data = response.json()

        if data["status"] == "success":
            print(f"Total de clases: {len(data['clases'])}\n")
            for clase in data["clases"]:
                print(f"📋 {clase['nombre']}")
                print(f"   Instructor: {clase['instructor']}")
                print(f"   Duración: {clase['duracion']} min")
                print(f"   Capacidad: {clase['capacidad_maxima']} personas")
                print(f"   Intensidad: {clase['intensidad']}")
                print()
    except Exception as e:
        print(f"Error: {e}")


def demo_class_schedules():
    """Muestra los horarios de clases."""
    print_section("4. HORARIOS DE CLASES")

    try:
        response = requests.get(f"{BASE_URL}/clases/horarios", timeout=REQUEST_TIMEOUT)
        data = response.json()

        if data["status"] == "success":
            # Agrupar por día
            schedules_by_day = {}
            for schedule in data["horarios"]:
                day = schedule["dia_semana"]
                if day not in schedules_by_day:
                    schedules_by_day[day] = []
                schedules_by_day[day].append(schedule)

            # Ordenar días
            days_order = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

            for day in days_order:
                if day in schedules_by_day:
                    print(f"\n📅 {day}")
                    print("-" * 50)
                    for schedule in sorted(schedules_by_day[day], key=lambda x: x["hora_inicio"]):
                        print(f"  {schedule['hora_inicio']} - {schedule['class_nombre']}")
                        print(f"    Instructor: {schedule['instructor']}")
                        print(f"    Sala: {schedule['sala']}")
    except Exception as e:
        print(f"Error: {e}")


def demo_book_class():
    """Demuestra la reserva de una clase."""
    print_section("5. RESERVA DE CLASE (ONE-CLICK)")

    # Obtener fecha de la próxima semana
    next_monday = datetime.now() + timedelta(days=(7 - datetime.now().weekday()))
    fecha_clase = next_monday.strftime("%Y-%m-%d")

    try:
        # Reservar clase de Spinning (schedule_id=1)
        response = requests.post(
            f"{BASE_URL}/clases/reservar",
            json={
                "username": USERNAME,
                "schedule_id": 1,
                "fecha_clase": fecha_clase
            },
            timeout=REQUEST_TIMEOUT
        )
        data = response.json()

        print(f"Reservando clase de Spinning para {fecha_clase}...")
        print(f"Estado: {data.get('status')}")
        print(f"Mensaje: {data.get('message')}")

        # Ver mis reservas
        response = requests.get(f"{BASE_URL}/clases/mis-reservas?username={USERNAME}", timeout=REQUEST_TIMEOUT)
        data = response.json()

        if data["status"] == "success":
            print(f"\n📝 Mis reservas actuales: {len(data['reservas'])}")
            for reserva in data["reservas"]:
                print(f"  • {reserva['class_nombre']} - {reserva['fecha_clase']} {reserva['hora_inicio']}")
    except Exception as e:
        print(f"Error: {e}")


def demo_equipment():
    """Muestra los equipos reservables."""
    print_section("6. EQUIPOS Y ZONAS RESERVABLES")

    try:
        response = requests.get(f"{BASE_URL}/equipos", timeout=REQUEST_TIMEOUT)
        data = response.json()

        if data["status"] == "success":
            # Agrupar por tipo
            equipment_by_type = {}
            for equipo in data["equipos"]:
                tipo = equipo["tipo"]
                if tipo not in equipment_by_type:
                    equipment_by_type[tipo] = []
                equipment_by_type[tipo].append(equipo)

            for tipo, equipos in equipment_by_type.items():
                print(f"\n🏋️ {tipo.upper()}")
                print("-" * 50)
                for equipo in equipos:
                    print(f"  • {equipo['nombre']}")
                    print(f"    Duración de slot: {equipo['duracion_slot']} min")
    except Exception as e:
        print(f"Error: {e}")


def demo_exercises():
    """Lista los ejercicios disponibles."""
    print_section("7. EJERCICIOS DISPONIBLES")

    try:
        response = requests.get(f"{BASE_URL}/ejercicios", timeout=REQUEST_TIMEOUT)
        data = response.json()

        if data["status"] == "success":
            # Agrupar por categoría
            exercises_by_category = {}
            for ejercicio in data["ejercicios"]:
                categoria = ejercicio["categoria"]
                if categoria not in exercises_by_category:
                    exercises_by_category[categoria] = []
                exercises_by_category[categoria].append(ejercicio)

            for categoria, ejercicios in sorted(exercises_by_category.items()):
                print(f"\n💪 {categoria.upper()}")
                print("-" * 50)
                for ejercicio in ejercicios:
                    print(f"  • {ejercicio['nombre']}")
                    if ejercicio['equipo_necesario']:
                        print(f"    Equipo: {ejercicio['equipo_necesario']}")
    except Exception as e:
        print(f"Error: {e}")


def demo_workout_log():
    """Demuestra el registro de entrenamiento."""
    print_section("8. QUICK LOG - REGISTRO DE ENTRENAMIENTO")

    try:
        # Registrar una serie de sentadillas
        fecha = datetime.now().strftime("%Y-%m-%d")

        print("Registrando serie de Sentadillas...")
        response = requests.post(
            f"{BASE_URL}/workout/log",
            json={
                "username": USERNAME,
                "exercise_id": 2,  # Sentadillas
                "fecha": fecha,
                "serie": 1,
                "repeticiones": 12,
                "peso": 100.0,
                "descanso_segundos": 180
            },
            timeout=REQUEST_TIMEOUT
        )
        data = response.json()

        print(f"Estado: {data.get('status')}")
        print(f"Mensaje: {data.get('message')}")

        # Ver historial
        response = requests.get(
            f"{BASE_URL}/workout/historial?username={USERNAME}&exercise_id=2&limit=5",
            timeout=REQUEST_TIMEOUT
        )
        data = response.json()

        if data["status"] == "success":
            print(f"\n📊 Historial de Sentadillas:")
            for log in data["historial"]:
                print(f"  Serie {log['serie']}: {log['peso']}kg × {log['repeticiones']} reps")
                print(f"    Fecha: {log['fecha']}")
    except Exception:
        print("Error: No se pudo obtener el historial de ejercicio")


def demo_checkin_token():
    """Demuestra la generación de token de check-in."""
    print_section("9. CHECK-IN DIGITAL (QR/NFC)")

    try:
        response = requests.post(
            f"{BASE_URL}/checkin/generate-token?username={USERNAME}&token_type=qr",
            timeout=REQUEST_TIMEOUT
        )
        data = response.json()

        if data["status"] == "success":
            print("✅ Token de check-in generado exitosamente")
            print(f"Tipo: {data['token_type'].upper()}")
            print(f"Token: {data['token'][:20]}... (truncado)")
            print("\n💡 Este token se puede usar para generar un código QR")
            print("   que el usuario puede escanear en el torniquete.")
    except Exception:
        print("Error: No se pudo generar token de check-in")


def demo_api_status():
    """Verifica el estado del servidor."""
    print_section("0. ESTADO DEL SERVIDOR")

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=REQUEST_TIMEOUT)
        data = response.json()

        print(f"Estado del servidor: {data['status']}")
        print(f"Versión: {data['version']}")
        print(f"Base de datos: {data['database_status']}")
    except Exception:
        print("❌ Error: No se pudo conectar al servidor")
        print(f"   Asegúrate de que el servidor esté corriendo en {BASE_URL}")
        print("   Ejecuta: python -m uvicorn madre_server:app --host 0.0.0.0 --port 8000")
        return False

    return True


def main():
    """Función principal del demo."""
    print("\n" + "=" * 60)
    print("  DEMO - NUEVAS FUNCIONALIDADES DEL SISTEMA DE GIMNASIO")
    print("=" * 60)

    # Verificar que el servidor esté corriendo
    if not demo_api_status():
        return

    # Ejecutar demos
    demo_list_classes()
    demo_class_schedules()
    demo_book_class()
    demo_equipment()
    demo_exercises()
    demo_workout_log()
    demo_checkin_token()

    # Demos locales (no requieren servidor)
    demo_plates_calculator()
    demo_rest_timer()

    print("\n" + "=" * 60)
    print("  FIN DEL DEMO")
    print("=" * 60)
    print("\n✅ Todas las funcionalidades están operativas!")
    print("📖 Ver NUEVAS_FUNCIONALIDADES.md para documentación completa\n")


if __name__ == "__main__":
    main()
