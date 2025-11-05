# hija_main.py
#
# Punto de entrada principal y CONTROLADOR de la Aplicación Hija.
#
# Responsabilidades:
# 1. Crear la ventana raíz de CustomTkinter.
# 2. Instanciar el módulo de comunicaciones ('hija_comms').
# 3. Gestionar el estado de la aplicación, mostrando el 'LoginFrame'
#    o el 'MainAppFrame' según corresponda (Conmutación de Frames).
# 4. Proveer las funciones de callback que la GUI ('hija_views') ejecutará.

import customtkinter
from hija_comms import APICommunicator
from hija_views import LoginFrame, MainAppFrame

# Configuración inicial de apariencia
customtkinter.set_appearance_mode("system")
customtkinter.set_default_color_theme("blue")

class AppHija(customtkinter.CTk):
    """
    Clase principal de la aplicación Hija (Controlador).
    Hereda de CTk para ser la ventana raíz.
    """
    def __init__(self):
        super().__init__()
        
        self.title("Aplicación Hija")
        self.geometry("600x450")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # --- Inicialización del Controlador ---
        self.communicator = APICommunicator()
        self.current_username = None
        
        # --- Almacenamiento de Vistas ---
        # El patrón de "conmutación de frames" implica destruir y crear
        # los frames principales.
        self._current_frame = None
        
        # Iniciar el flujo de la aplicación mostrando el Login
        self._mostrar_login()

    def _limpiar_frames_actuales(self):
        """
        Destruye el frame actual para hacer espacio para el siguiente.
        """
        if self._current_frame:
            self._current_frame.pack_forget()
            self._current_frame.destroy()
            self._current_frame = None

    def _mostrar_login(self):
        """
        Crea y muestra el LoginFrame.
        """
        self._limpiar_frames_actuales()
        
        self.title("Aplicación Hija - Iniciar Sesión")
        self.geometry("600x450")
        
        # Instanciar el LoginFrame, pasándole '_intentar_login' como
        # el callback 'on_login_attempt'.
        self._current_frame = LoginFrame(master=self, on_login_attempt=self._intentar_login)
        self._current_frame.pack(padx=20, pady=20, fill="both", expand=True)

    def _intentar_login(self, username: str):
        """
        Callback de lógica de negocio. Es llamado por LoginFrame.
        Usa el 'communicator' para intentar el login.
        """
        success, message = self.communicator.attempt_login(username)
        
        if success:
            self.current_username = message  # El mensaje de éxito es el nombre de usuario
            # Transición a la aplicación principal
            self._mostrar_app_principal()
        else:
            # Mostrar el error en la GUI de Login
            # Necesitamos acceder al método 'show_status' del frame de login
            if isinstance(self._current_frame, LoginFrame):
                self._current_frame.show_status(message, is_error=True)

    def _mostrar_app_principal(self):
        """
        Crea y muestra el MainAppFrame después de un login exitoso.
        """
        self._limpiar_frames_actuales()
        
        self.title(f"Aplicación Hija - {self.current_username}")
        self.geometry("700x500")
        
        # Instanciar el MainAppFrame, pasando el nombre de usuario
        # y el callback de sincronización.
        self._current_frame = MainAppFrame(
            master=self,
            username=self.current_username,
            on_sync_attempt=self._intentar_sync
        )
        self._current_frame.pack(fill="both", expand=True)

    def _intentar_sync(self):
        """
        Callback de lógica de negocio. Es llamado por MainAppFrame.
        Usa el 'communicator' para obtener datos de sincronización.
        """
        if not self.current_username:
            if isinstance(self._current_frame, MainAppFrame):
                self._current_frame.show_sync_error("Error: No hay usuario autenticado.")
            return
            
        success, data = self.communicator.fetch_sync_data(self.current_username)
        
        if isinstance(self._current_frame, MainAppFrame):
            if success:
                # Si es exitoso, 'data' es un diccionario con el contenido
                contenido = data.get("contenido", "No se recibió contenido.")
                version = data.get("metadatos_version", "N/A")
                self._current_frame.update_content(contenido, version)
            else:
                # Si falla, 'data' es un diccionario con un error
                error_msg = data.get("error", "Error de sincronización desconocido.")
                self._current_frame.show_sync_error(error_msg)

# --- Punto de Entrada ---
if __name__ == "__main__":
    app = AppHija()
    app.mainloop()
