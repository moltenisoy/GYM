import threading
import uvicorn
from madre_gui import AppMadre
from madre_server import app as app_servidor
from config.settings import get_madre_settings
from shared.logger import setup_logger

logger = setup_logger(__name__, log_file="madre_main.log")

settings = get_madre_settings()

def iniciar_servidor() -> None:
    logger.info("Iniciando servidor FastAPI/uvicorn en http://%s:%s", settings.HOST, settings.PORT)
    try:
        uvicorn_log_level = settings.LOG_LEVEL.lower()
        if uvicorn_log_level not in ['critical', 'error', 'warning', 'info', 'debug', 'trace']:
            uvicorn_log_level = 'info'

        uvicorn.run(app_servidor, host=settings.HOST, port=settings.PORT, log_level=uvicorn_log_level)
    except Exception as e:
        logger.error("Error al iniciar el servidor uvicorn: %s", e, exc_info=True)
        raise

if __name__ == "__main__":
    logger.info("=== Iniciando Sistema de Gestión del Gimnasio (Aplicación Madre) ===")
    logger.info("Configuración: %s", settings)

    try:
        hilo_servidor = threading.Thread(target=iniciar_servidor, name="ServerThread")

        hilo_servidor.daemon = True

        hilo_servidor.start()
        logger.info("Hilo del servidor iniciado en segundo plano")

        logger.info("Iniciando GUI de la aplicación...")
        app_gui = AppMadre()

        app_gui.mainloop()

        logger.info("Aplicación Madre cerrada. Deteniendo el servidor...")

    except KeyboardInterrupt:
        logger.info("Interrupción de teclado recibida. Cerrando aplicación...")
    except Exception as e:
        logger.critical("Error fatal en la aplicación: %s", e, exc_info=True)
        raise
    finally:
        logger.info("=== Aplicación Madre finalizada ===")
