SISTEMA DE GESTION DE GIMNASIO

ESTRUCTURA DEL PROYECTO:

APLICACION MADRE (Administración):
- madre_main.py: Punto de entrada principal
- madre_server.py: Servidor API FastAPI
- madre_gui.py: Interfaz gráfica de administración
- madre_db.py: Base de datos y operaciones
- requirements_madre.txt: Dependencias necesarias

APLICACION HIJA (Socios):
- hija_main.py: Punto de entrada principal
- hija_views.py: Interfaz gráfica de usuario
- hija_comms.py: Comunicación con servidor
- requirements_hija.txt: Dependencias necesarias

MODULOS COMPARTIDOS:
- config/: Configuración del sistema
- shared/: Utilidades compartidas (logger, constantes, workout_utils)

UTILIDADES:
- populate_db.py: Script para poblar base de datos con datos de prueba
- demo_features.py: Demostración de funcionalidades
- test_messaging.py: Pruebas de mensajería
- test_system.py: Pruebas del sistema

SUGERENCIAS Y MEJORAS:
- SUGERENCIAS_MADRE_APP.txt: Mejoras y nuevas características para app madre
- SUGERENCIAS_HIJA_APP.txt: Mejoras y nuevas características para app hija

INSTALACION:
pip install -r requirements_madre.txt
pip install -r requirements_hija.txt

EJECUCION:
Madre: python madre_main.py
Hija: python hija_main.py
