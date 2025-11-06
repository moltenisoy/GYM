# madre_main.py
#
# Punto de entrada principal para la Aplicación Madre.
# Este script orquesta el lanzamiento de los dos componentes principales:
# 1. El servidor FastAPI (en un hilo de fondo).
# 2. La aplicación GUI de CustomTkinter (en el hilo principal).

import threading
import uvicorn
import logging
from madre_gui import AppMadre
from madre_server import app as app_servidor
from config.settings import get_madre_settings
from shared.logger import setup_logger

# Initialize logger
logger = setup_logger(__name__, log_file="madre_main.log")

# Load configuration from environment
settings = get_madre_settings()

def iniciar_servidor() -> None:
    """
    Función objetivo para el hilo del servidor.
    Inicia el servidor uvicorn. Esta es una llamada BLOQUEANTE
    que se ejecutará dentro de su propio hilo.
    
    Raises:
        Exception: Si el servidor no puede iniciarse
    """
    logger.info(f"Iniciando servidor FastAPI/uvicorn en http://{settings.HOST}:{settings.PORT}")
    try:
        # Convert log level string to uvicorn log level
        uvicorn_log_level = settings.LOG_LEVEL.lower()
        if uvicorn_log_level not in ['critical', 'error', 'warning', 'info', 'debug', 'trace']:
            uvicorn_log_level = 'info'
        
        uvicorn.run(app_servidor, host=settings.HOST, port=settings.PORT, log_level=uvicorn_log_level)
    except Exception as e:
        logger.error(f"Error al iniciar el servidor uvicorn: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    logger.info("=== Iniciando Aplicación Madre ===")
    logger.info(f"Configuración: {settings}")
    
    try:
        # 1. Configurar el hilo del servidor
        # Creamos un hilo que tendrá como objetivo la función 'iniciar_servidor'.
        hilo_servidor = threading.Thread(target=iniciar_servidor, name="ServerThread")
        
        # Establecer como 'daemon=True'.
        # Esto significa que el hilo del servidor se cerrará automáticamente
        # cuando el hilo principal (la GUI) termine.
        hilo_servidor.daemon = True
        
        # 2. Iniciar el hilo del servidor
        # El servidor comenzará a escuchar peticiones en segundo plano.
        hilo_servidor.start()
        logger.info("Hilo del servidor iniciado en segundo plano")
        
        # 3. Iniciar la aplicación GUI
        # Creamos la instancia de la aplicación GUI.
        logger.info("Iniciando GUI de la aplicación...")
        app_gui = AppMadre()
        
        # Iniciamos el bucle principal de la GUI.
        # Esta es una llamada BLOQUEANTE que se ejecutará en el hilo principal.
        # La aplicación permanecerá aquí hasta que el usuario cierre la ventana.
        app_gui.mainloop()
        
        # Cuando el usuario cierra la ventana, app.mainloop() termina.
        # El programa principal finaliza, y como 'hilo_servidor' es un daemon,
        # se detendrá automáticamente.
        logger.info("Aplicación Madre cerrada. Deteniendo el servidor...")
        
    except KeyboardInterrupt:
        logger.info("Interrupción de teclado recibida. Cerrando aplicación...")
    except Exception as e:
        logger.critical(f"Error fatal en la aplicación: {e}", exc_info=True)
        raise
    finally:
        logger.info("=== Aplicación Madre finalizada ===")
