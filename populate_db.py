#!/usr/bin/env python3
# populate_db.py
#
# Script para poblar la base de datos con usuarios de prueba y datos de ejemplo.

import madre_db


def create_sample_users():
    """Crea usuarios de ejemplo con datos completos."""

    print("Creando usuarios de ejemplo...")

    # Usuario 1: Juan Pérez
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

        # Obtener ID del usuario
        user = madre_db.get_user("juan_perez")
        user_id = user['id']

        # Añadir foto de perfil (ruta simulada)
        madre_db.set_user_profile_photo(
            user_id,
            "data/users/profile_photos/juan_perez.jpg"
        )
        print("  - Foto de perfil añadida")

        # Crear cronograma de entrenamiento para diciembre 2024
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

        # Añadir fotos a la galería
        gallery_photos = [
            ("data/users/gallery/juan_perez_progress_1.jpg", "Progreso mes 1 - Peso inicial"),
            ("data/users/gallery/juan_perez_progress_2.jpg", "Progreso mes 2 - Definición"),
            ("data/users/gallery/juan_perez_training_1.jpg", "Entrenamiento de piernas")
        ]

        for photo_path, descripcion in gallery_photos:
            madre_db.add_photo_to_gallery(user_id, photo_path, descripcion)
        print(f"  - {len(gallery_photos)} fotos añadidas a la galería")

    # Usuario 2: María López
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

        # Cronograma enfocado en cardio
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

    # Usuario 3: Carlos Rodríguez (sin permisos)
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

        # Cronograma básico para principiantes
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


if __name__ == "__main__":
    main()
