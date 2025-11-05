# madre_main.py
#
# Punto de entrada principal para la Aplicación Madre.
# Este script orquesta el lanzamiento de los dos componentes principales:
# 1. El servidor FastAPI (en un hilo de fondo).
# 2. La aplicación GUI de CustomTkinter (en el hilo principal).

import threading
import uvicorn
from madre_gui import AppMadre
from madre_server import app as app_servidor

# Define la IP y el puerto para el servidor.
# '0.0.0.0' lo hace accesible desde cualquier IP en la red,
# no solo 'localhost'.
HOST_IP = "0.0.0.0"
HOST_PORT = 8000

def iniciar_servidor():
    """
    Función objetivo para el hilo del servidor.
    Inicia el servidor uvicorn. Esta es una llamada BLOQUEANTE
    que se ejecutará dentro de su propio hilo.
    """
    print(f"Iniciando servidor FastAPI/uvicorn en http://{HOST_IP}:{HOST_PORT}")
    try:
        uvicorn.run(app_servidor, host=HOST_IP, port=HOST_PORT, log_level="info")
    except Exception as e:
        print(f"Error al iniciar el servidor uvicorn: {e}")

if __name__ == "__main__":
    # 1. Configurar el hilo del servidor
    # Creamos un hilo que tendrá como objetivo la función 'iniciar_servidor'.
    hilo_servidor = threading.Thread(target=iniciar_servidor)
    
    # Establecer como 'daemon=True'.
    # Esto significa que el hilo del servidor se cerrará automáticamente
    # cuando el hilo principal (la GUI) termine.
    hilo_servidor.daemon = True
    
    # 2. Iniciar el hilo del servidor
    # El servidor comenzará a escuchar peticiones en segundo plano.
    hilo_servidor.start()
    
    # 3. Iniciar la aplicación GUI
    # Creamos la instancia de la aplicación GUI.
    app_gui = AppMadre()
    
    # Iniciamos el bucle principal de la GUI.
    # Esta es una llamada BLOQUEANTE que se ejecutará en el hilo principal.
    # La aplicación permanecerá aquí hasta que el usuario cierre la ventana.
    app_gui.mainloop()
    
    # Cuando el usuario cierra la ventana, app.mainloop() termina.
    # El programa principal finaliza, y como 'hilo_servidor' es un daemon,
    # se detendrá automáticamente.
    print("Aplicación Madre cerrada. Deteniendo el servidor...")
