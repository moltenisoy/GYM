

import madre_db


def create_sample_users():
    """Crea usuarios de ejemplo con datos completos."""

    print("Creando usuarios de ejemplo...")

    if madre_db.create_user(
        username="admin",
        password="admin123",
        nombre_completo="Administrador del Sistema",
        email="admin@gym.example.com",
        telefono="+34 600 000 000",
        equipo="Administración",
        permiso_acceso=True
    ):
        print("✓ Usuario 'admin' creado")

    if madre_db.create_user(
        username="juan_perez",
        password="gym2024",
        nombre_completo="Juan Pérez García",
        email="juan.perez@example.com",
        telefono="+34 612 345 678",
        equipo="Equipo A - Fitness Avanzado",
        permiso_acceso=True
    ):
        print("✓ Usuario 'juan_perez' creado")

        user = madre_db.get_user("juan_perez")
        user_id = user['id']

        madre_db.set_user_profile_photo(
            user_id,
            "data/users/profile_photos/juan_perez.jpg"
        )
        print("  - Foto de perfil añadida")

        schedule_data = {
            "dias": {
                "lunes": {
                    "ejercicios": ["Pecho", "Tríceps"],
                    "descripcion": "Press banca 4x12, Fondos 3x15, Press inclinado 3x12",
                    "duracion_minutos": 60
                },
                "martes": {
                    "ejercicios": ["Cardio"],
                    "descripcion": "Running 30 min, Bicicleta 20 min",
                    "duracion_minutos": 50
                },
                "miercoles": {
                    "ejercicios": ["Espalda", "Bíceps"],
                    "descripcion": "Dominadas 4x10, Remo 4x12, Curl barra 3x12",
                    "duracion_minutos": 60
                },
                "jueves": {
                    "ejercicios": ["Descanso activo"],
                    "descripcion": "Estiramientos y yoga",
                    "duracion_minutos": 30
                },
                "viernes": {
                    "ejercicios": ["Piernas"],
                    "descripcion": "Sentadillas 4x15, Prensa 4x12, Zancadas 3x15",
                    "duracion_minutos": 70
                },
                "sabado": {
                    "ejercicios": ["Cardio intenso"],
                    "descripcion": "HIIT 25 min, Abs 15 min",
                    "duracion_minutos": 40
                },
                "domingo": {
                    "ejercicios": ["Descanso"],
                    "descripcion": "Día de recuperación completa",
                    "duracion_minutos": 0
                }
            },
            "objetivo": "Ganancia muscular y definición",
            "notas": "Aumentar progresivamente la carga cada semana"
        }

        madre_db.save_training_schedule(user_id, "Diciembre", 2024, schedule_data)
        print("  - Cronograma de entrenamiento añadido")

        gallery_photos = [
            ("data/users/gallery/juan_perez_progress_1.jpg", "Progreso mes 1 - Peso inicial"),
            ("data/users/gallery/juan_perez_progress_2.jpg", "Progreso mes 2 - Definición"),
            ("data/users/gallery/juan_perez_training_1.jpg", "Entrenamiento de piernas")
        ]

        for photo_path, descripcion in gallery_photos:
            madre_db.add_photo_to_gallery(user_id, photo_path, descripcion)
        print(f"  - {len(gallery_photos)} fotos añadidas a la galería")

    if madre_db.create_user(
        username="maria_lopez",
        password="fit2024",
        nombre_completo="María López Martínez",
        email="maria.lopez@example.com",
        telefono="+34 623 456 789",
        equipo="Equipo B - Cardio y Resistencia",
        permiso_acceso=True
    ):
        print("✓ Usuario 'maria_lopez' creado")

        user = madre_db.get_user("maria_lopez")
        user_id = user['id']

        madre_db.set_user_profile_photo(
            user_id,
            "data/users/profile_photos/maria_lopez.jpg"
        )
        print("  - Foto de perfil añadida")

        schedule_data = {
            "dias": {
                "lunes": {
                    "ejercicios": ["Running", "Core"],
                    "descripcion": "5km running pace, Plancha 3x1min, Abdominales 3x20",
                    "duracion_minutos": 45
                },
                "martes": {
                    "ejercicios": ["Spinning", "Estiramientos"],
                    "descripcion": "Clase de spinning 45 min, Yoga 15 min",
                    "duracion_minutos": 60
                },
                "miercoles": {
                    "ejercicios": ["Natación"],
                    "descripcion": "1500m estilo libre, técnica de brazada",
                    "duracion_minutos": 50
                },
                "jueves": {
                    "ejercicios": ["Running intervals"],
                    "descripcion": "Intervalos: 8x400m con descanso 90seg",
                    "duracion_minutos": 40
                },
                "viernes": {
                    "ejercicios": ["Circuito funcional"],
                    "descripcion": "Burpees, Box jumps, Battle ropes - 3 rondas",
                    "duracion_minutos": 50
                },
                "sabado": {
                    "ejercicios": ["Carrera larga"],
                    "descripcion": "10km ritmo cómodo",
                    "duracion_minutos": 60
                },
                "domingo": {
                    "ejercicios": ["Descanso"],
                    "descripcion": "Recuperación y estiramientos suaves",
                    "duracion_minutos": 0
                }
            },
            "objetivo": "Mejorar resistencia cardiovascular y pérdida de grasa",
            "notas": "Mantener frecuencia cardíaca entre 140-160 bpm"
        }

        madre_db.save_training_schedule(user_id, "Diciembre", 2024, schedule_data)
        print("  - Cronograma de entrenamiento añadido")

        gallery_photos = [
            ("data/users/gallery/maria_lopez_running.jpg", "Media maratón completada"),
            ("data/users/gallery/maria_lopez_yoga.jpg", "Sesión de yoga matutina")
        ]

        for photo_path, descripcion in gallery_photos:
            madre_db.add_photo_to_gallery(user_id, photo_path, descripcion)
        print(f"  - {len(gallery_photos)} fotos añadidas a la galería")

    if madre_db.create_user(
        username="carlos_rodriguez",
        password="trainer123",
        nombre_completo="Carlos Rodríguez Sánchez",
        email="carlos.rodriguez@example.com",
        telefono="+34 634 567 890",
        equipo="Equipo C - Principiantes",
        permiso_acceso=False
    ):
        print("✓ Usuario 'carlos_rodriguez' creado (sin permiso de acceso)")

        user = madre_db.get_user("carlos_rodriguez")
        user_id = user['id']

        madre_db.set_user_profile_photo(
            user_id,
            "data/users/profile_photos/carlos_rodriguez.jpg"
        )
        print("  - Foto de perfil añadida")

        schedule_data = {
            "dias": {
                "lunes": {
                    "ejercicios": ["Introducción al gimnasio"],
                    "descripcion": "Tour de equipos, ejercicios básicos con peso corporal",
                    "duracion_minutos": 30
                },
                "martes": {
                    "ejercicios": ["Cardio ligero"],
                    "descripcion": "Caminata rápida 20 min, bicicleta estática 15 min",
                    "duracion_minutos": 35
                },
                "miercoles": {
                    "ejercicios": ["Descanso"],
                    "descripcion": "Día de recuperación",
                    "duracion_minutos": 0
                },
                "jueves": {
                    "ejercicios": ["Fuerza básica"],
                    "descripcion": "Máquinas guiadas: Pecho, espalda, piernas - 2x12 cada una",
                    "duracion_minutos": 40
                },
                "viernes": {
                    "ejercicios": ["Cardio"],
                    "descripcion": "Elíptica 25 min a ritmo moderado",
                    "duracion_minutos": 30
                },
                "sabado": {
                    "ejercicios": ["Descanso"],
                    "descripcion": "Recuperación",
                    "duracion_minutos": 0
                },
                "domingo": {
                    "ejercicios": ["Descanso"],
                    "descripcion": "Recuperación",
                    "duracion_minutos": 0
                }
            },
            "objetivo": "Adaptación inicial al entrenamiento",
            "notas": "Enfocarse en la técnica correcta antes de aumentar peso"
        }

        madre_db.save_training_schedule(user_id, "Diciembre", 2024, schedule_data)
        print("  - Cronograma de entrenamiento añadido")

        gallery_photos = [
            ("data/users/gallery/carlos_rodriguez_inicio.jpg", "Primer día en el gimnasio")
        ]

        for photo_path, descripcion in gallery_photos:
            madre_db.add_photo_to_gallery(user_id, photo_path, descripcion)
        print(f"  - {len(gallery_photos)} fotos añadidas a la galería")


def create_initial_sync_data():
    """Crea el contenido inicial de sincronización."""
    print("\nCreando contenido de sincronización global...")

    contenido = """Bienvenido al Sistema de Gestión de Gimnasio

Este sistema te permite:
- Consultar tu cronograma de entrenamiento personalizado
- Ver tu progreso a través de fotos
- Recibir actualizaciones de tus entrenadores
- Sincronizar tus datos automáticamente

¡Mantente activo y alcanza tus objetivos!
"""

    madre_db.update_sync_data(contenido, "1.0.0")
    print("✓ Contenido de sincronización creado")


def main():
    """Función principal."""
    print("=" * 60)
    print("POBLANDO BASE DE DATOS DEL SISTEMA GYM")
    print("=" * 60)
    print()

    create_sample_users()
    create_initial_sync_data()
    populate_classes_and_schedules()
    populate_exercises()
    populate_equipment_zones()

    print()
    print("=" * 60)
    print("BASE DE DATOS POBLADA EXITOSAMENTE")
    print("=" * 60)
    print()
    print("Usuarios creados:")
    print("  1. juan_perez / gym2024 (acceso habilitado)")
    print("  2. maria_lopez / fit2024 (acceso habilitado)")
    print("  3. carlos_rodriguez / trainer123 (acceso DESHABILITADO)")
    print()
    print("Cada usuario tiene:")
    print("  - Foto de perfil")
    print("  - Datos personales completos")
    print("  - Cronograma de entrenamiento mensual")
    print("  - Galería de fotos personal")
    print()
    print("Clases y horarios creados:")
    print("  - Spinning, Yoga, CrossFit, Pilates, Zumba, Boxing")
    print("  - Horarios semanales configurados")
    print()
    print("Ejercicios disponibles:")
    print("  - 20+ ejercicios comunes de gimnasio")
    print()
    print("Equipos y zonas reservables:")
    print("  - Racks de sentadillas, Pistas de pádel, Carriles de piscina")
    print()


def populate_classes_and_schedules():
    """Crea clases grupales y sus horarios."""
    print("\nCreando clases grupales y horarios...")

    from datetime import datetime, timedelta

    today = datetime.now()
    days_until_monday = (today.weekday()) % 7
    monday = (today - timedelta(days=days_until_monday)).date().isoformat()

    classes_data = [
        {
            "nombre": "Spinning",
            "descripcion": "Clase de ciclismo indoor de alta intensidad",
            "instructor": "Carlos Ruiz",
            "duracion": 45,
            "capacidad_maxima": 20,
            "intensidad": "alta",
            "tipo": "cardio",
            "horarios": [
                {"dia_semana": "Lunes", "hora_inicio": "07:00", "sala": "Sala Cardio 1"},
                {"dia_semana": "Miércoles", "hora_inicio": "07:00", "sala": "Sala Cardio 1"},
                {"dia_semana": "Viernes", "hora_inicio": "07:00", "sala": "Sala Cardio 1"},
            ]
        },
        {
            "nombre": "Yoga",
            "descripcion": "Clase de yoga para todos los niveles",
            "instructor": "Ana Martínez",
            "duracion": 60,
            "capacidad_maxima": 15,
            "intensidad": "baja",
            "tipo": "flexibilidad",
            "horarios": [
                {"dia_semana": "Lunes", "hora_inicio": "18:00", "sala": "Sala Zen"},
                {"dia_semana": "Miércoles", "hora_inicio": "18:00", "sala": "Sala Zen"},
                {"dia_semana": "Sábado", "hora_inicio": "10:00", "sala": "Sala Zen"},
            ]
        },
        {
            "nombre": "CrossFit",
            "descripcion": "Entrenamiento funcional de alta intensidad",
            "instructor": "Miguel Torres",
            "duracion": 60,
            "capacidad_maxima": 12,
            "intensidad": "alta",
            "tipo": "funcional",
            "horarios": [
                {"dia_semana": "Martes", "hora_inicio": "19:00", "sala": "Box CrossFit"},
                {"dia_semana": "Jueves", "hora_inicio": "19:00", "sala": "Box CrossFit"},
                {"dia_semana": "Sábado", "hora_inicio": "09:00", "sala": "Box CrossFit"},
            ]
        },
        {
            "nombre": "Pilates",
            "descripcion": "Método Pilates para fortalecer core y mejorar postura",
            "instructor": "Laura Sánchez",
            "duracion": 50,
            "capacidad_maxima": 12,
            "intensidad": "media",
            "tipo": "fortalecimiento",
            "horarios": [
                {"dia_semana": "Martes", "hora_inicio": "10:00", "sala": "Sala Pilates"},
                {"dia_semana": "Jueves", "hora_inicio": "10:00", "sala": "Sala Pilates"},
            ]
        },
        {
            "nombre": "Zumba",
            "descripcion": "Baile fitness con ritmos latinos",
            "instructor": "Carmen Díaz",
            "duracion": 55,
            "capacidad_maxima": 25,
            "intensidad": "media",
            "tipo": "cardio",
            "horarios": [
                {"dia_semana": "Lunes", "hora_inicio": "20:00", "sala": "Sala Multiusos"},
                {"dia_semana": "Miércoles", "hora_inicio": "20:00", "sala": "Sala Multiusos"},
                {"dia_semana": "Viernes", "hora_inicio": "20:00", "sala": "Sala Multiusos"},
            ]
        },
        {
            "nombre": "Boxing",
            "descripcion": "Clase de boxeo y entrenamiento de combate",
            "instructor": "Javier Moreno",
            "duracion": 60,
            "capacidad_maxima": 16,
            "intensidad": "alta",
            "tipo": "combate",
            "horarios": [
                {"dia_semana": "Martes", "hora_inicio": "18:00", "sala": "Sala Combat"},
                {"dia_semana": "Jueves", "hora_inicio": "18:00", "sala": "Sala Combat"},
            ]
        },
    ]

    for class_info in classes_data:
        class_id = madre_db.create_class(
            nombre=class_info["nombre"],
            descripcion=class_info["descripcion"],
            instructor=class_info["instructor"],
            duracion=class_info["duracion"],
            capacidad_maxima=class_info["capacidad_maxima"],
            intensidad=class_info["intensidad"],
            tipo=class_info["tipo"]
        )

        if class_id:
            print(f"✓ Clase '{class_info['nombre']}' creada (ID: {class_id})")

            for horario in class_info["horarios"]:
                schedule_id = madre_db.create_class_schedule(
                    class_id=class_id,
                    instructor=class_info["instructor"],
                    dia_semana=horario["dia_semana"],
                    hora_inicio=horario["hora_inicio"],
                    fecha_inicio=monday,
                    recurrente=True,
                    sala=horario["sala"]
                )
                if schedule_id:
                    print(f"  - Horario {horario['dia_semana']} {horario['hora_inicio']} en {horario['sala']}")


def populate_exercises():
    """Crea ejercicios comunes de gimnasio."""
    print("\nCreando ejercicios...")

    exercises = [
        {"nombre": "Press de Banca", "categoria": "pecho", "equipo": "barra", "descripcion": "Ejercicio básico de empuje para pecho"},
        {"nombre": "Sentadillas", "categoria": "piernas", "equipo": "barra", "descripcion": "Ejercicio compuesto de piernas"},
        {"nombre": "Peso Muerto", "categoria": "espalda", "equipo": "barra", "descripcion": "Ejercicio compuesto de cadena posterior"},
        {"nombre": "Press Militar", "categoria": "hombros", "equipo": "barra", "descripcion": "Press vertical para hombros"},
        {"nombre": "Dominadas", "categoria": "espalda", "equipo": "barra_fija", "descripcion": "Ejercicio de tracción vertical"},
        {"nombre": "Remo con Barra", "categoria": "espalda", "equipo": "barra", "descripcion": "Ejercicio de tracción horizontal"},
        {"nombre": "Curl de Bíceps", "categoria": "brazos", "equipo": "barra", "descripcion": "Ejercicio de aislamiento para bíceps"},
        {"nombre": "Extensiones de Tríceps", "categoria": "brazos", "equipo": "polea", "descripcion": "Ejercicio de aislamiento para tríceps"},
        {"nombre": "Press Inclinado", "categoria": "pecho", "equipo": "barra", "descripcion": "Press de banca en banco inclinado"},
        {"nombre": "Zancadas", "categoria": "piernas", "equipo": "mancuernas", "descripcion": "Ejercicio unilateral de piernas"},
        {"nombre": "Prensa de Piernas", "categoria": "piernas", "equipo": "máquina", "descripcion": "Ejercicio de empuje de piernas"},
        {"nombre": "Elevaciones Laterales", "categoria": "hombros", "equipo": "mancuernas", "descripcion": "Aislamiento de deltoides laterales"},
        {"nombre": "Fondos en Paralelas", "categoria": "pecho", "equipo": "paralelas", "descripcion": "Ejercicio de empuje con peso corporal"},
        {"nombre": "Hip Thrust", "categoria": "glúteos", "equipo": "barra", "descripcion": "Ejercicio de extensión de cadera"},
        {"nombre": "Face Pull", "categoria": "hombros", "equipo": "polea", "descripcion": "Tracción para deltoides posteriores"},
        {"nombre": "Plancha", "categoria": "core", "equipo": "ninguno", "descripcion": "Ejercicio isométrico de core"},
        {"nombre": "Crunch Abdominal", "categoria": "core", "equipo": "ninguno", "descripcion": "Ejercicio de flexión abdominal"},
        {"nombre": "Burpees", "categoria": "cardio", "equipo": "ninguno", "descripcion": "Ejercicio de cuerpo completo de alta intensidad"},
        {"nombre": "Peso Muerto Rumano", "categoria": "piernas", "equipo": "barra", "descripcion": "Variante de peso muerto para isquiotibiales"},
        {"nombre": "Pullover", "categoria": "pecho", "equipo": "mancuerna", "descripcion": "Ejercicio para pecho y dorsales"},
    ]

    for exercise in exercises:
        exercise_id = madre_db.create_exercise(
            nombre=exercise["nombre"],
            descripcion=exercise["descripcion"],
            categoria=exercise["categoria"],
            equipo_necesario=exercise["equipo"]
        )
        if exercise_id:
            print(f"✓ Ejercicio '{exercise['nombre']}' creado")


def populate_equipment_zones():
    """Crea equipos y zonas reservables."""
    print("\nCreando equipos y zonas reservables...")

    equipment_zones = [
        {"nombre": "Rack de Sentadillas 1", "tipo": "rack", "descripcion": "Rack de sentadillas con barra olímpica", "cantidad": 1, "duracion_slot": 60},
        {"nombre": "Rack de Sentadillas 2", "tipo": "rack", "descripcion": "Rack de sentadillas con barra olímpica", "cantidad": 1, "duracion_slot": 60},
        {"nombre": "Rack de Sentadillas 3", "tipo": "rack", "descripcion": "Rack de sentadillas con barra olímpica", "cantidad": 1, "duracion_slot": 60},
        {"nombre": "Plataforma de Peso Muerto 1", "tipo": "plataforma", "descripcion": "Plataforma para levantamientos olímpicos", "cantidad": 1, "duracion_slot": 60},
        {"nombre": "Plataforma de Peso Muerto 2", "tipo": "plataforma", "descripcion": "Plataforma para levantamientos olímpicos", "cantidad": 1, "duracion_slot": 60},
        {"nombre": "Pista de Pádel 1", "tipo": "pista_padel", "descripcion": "Pista de pádel interior", "cantidad": 1, "duracion_slot": 90},
        {"nombre": "Pista de Pádel 2", "tipo": "pista_padel", "descripcion": "Pista de pádel interior", "cantidad": 1, "duracion_slot": 90},
        {"nombre": "Carril de Piscina 1", "tipo": "piscina", "descripcion": "Carril de piscina de 25m", "cantidad": 1, "duracion_slot": 45},
        {"nombre": "Carril de Piscina 2", "tipo": "piscina", "descripcion": "Carril de piscina de 25m", "cantidad": 1, "duracion_slot": 45},
        {"nombre": "Carril de Piscina 3", "tipo": "piscina", "descripcion": "Carril de piscina de 25m", "cantidad": 1, "duracion_slot": 45},
        {"nombre": "Cancha de Squash", "tipo": "cancha", "descripcion": "Cancha de squash techada", "cantidad": 1, "duracion_slot": 60},
        {"nombre": "Sala de Spinning", "tipo": "sala", "descripcion": "Sala dedicada con 20 bicicletas", "cantidad": 1, "duracion_slot": 60},
    ]

    for equipment in equipment_zones:
        equipment_id = madre_db.create_equipment_zone(
            nombre=equipment["nombre"],
            tipo=equipment["tipo"],
            descripcion=equipment["descripcion"],
            cantidad=equipment["cantidad"],
            duracion_slot=equipment["duracion_slot"]
        )
        if equipment_id:
            print(f"✓ Equipo/Zona '{equipment['nombre']}' creado")


if __name__ == "__main__":
    main()
