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
# 5. Implementar sincronización automática en segundo plano.
# 6. Validar sincronización cada 72 horas (bloqueo si no se cumple).

import customtkinter
import threading
import time
from datetime import datetime
from hija_comms import APICommunicator
from hija_views import LoginFrame, MainAppFrame

# Configuración inicial de apariencia
customtkinter.set_appearance_mode("system")
customtkinter.set_default_color_theme("blue")

class AppHija(customtkinter.CTk):
    """
    Clase principal de la aplicación Hija (Controlador).
    Hereda de CTk para ser la ventana raíz.
    Implementa sincronización automática en segundo plano.
    """
    def __init__(self):
        super().__init__()
        
        self.title("Aplicación Hija - Gimnasio")
        self.geometry("800x600")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # --- Inicialización del Controlador ---
        self.communicator = APICommunicator()
        self.current_username = None
        self.current_user_data = None
        
        # --- Control de sincronización ---
        self.sync_thread = None
        self.sync_running = False
        self.sync_interval = 300  # 5 minutos inicialmente (en segundos)
        self.first_sync_done = False
        
        # --- Almacenamiento de Vistas ---
        self._current_frame = None
        
        # Intentar auto-login si hay credenciales guardadas
        self._intentar_auto_login()

    def _limpiar_frames_actuales(self):
        """
        Destruye el frame actual para hacer espacio para el siguiente.
        """
        if self._current_frame:
            self._current_frame.pack_forget()
            self._current_frame.destroy()
            self._current_frame = None

    def _intentar_auto_login(self):
        """
        Intenta realizar auto-login con credenciales guardadas.
        Valida también que la sincronización esté al día (72 horas).
        """
        creds = self.communicator.load_credentials()
        if not creds:
            # No hay credenciales guardadas, mostrar login normal
            self._mostrar_login()
            return
        
        username = creds.get('username')
        
        # Validar estado de sincronización (72 horas)
        valid, validation_data = self.communicator.validate_sync_status(username)
        
        if not valid and validation_data.get('bloqueado'):
            # Necesita sincronizar antes de continuar
            # Limpiar credenciales y forzar nuevo login
            self.communicator.clear_credentials()
            self._mostrar_login()
            return
        
        # Auto-login exitoso
        self.current_username = username
        self.current_user_data = {
            'username': username,
            'nombre_completo': creds.get('nombre_completo', username)
        }
        self._mostrar_app_principal()
    
    def _mostrar_login(self):
        """
        Crea y muestra el LoginFrame.
        """
        self._limpiar_frames_actuales()
        
        self.title("Aplicación Hija - Iniciar Sesión")
        self.geometry("600x450")
        
        # Instanciar el LoginFrame
        self._current_frame = LoginFrame(master=self, on_login_attempt=self._intentar_login)
        self._current_frame.pack(padx=20, pady=20, fill="both", expand=True)

    def _intentar_login(self, username: str, password: str):
        """
        Callback de lógica de negocio. Es llamado por LoginFrame.
        Usa el 'communicator' para intentar el login con contraseña.
        """
        success, data = self.communicator.attempt_login(username, password)
        
        if success:
            self.current_username = username
            self.current_user_data = data
            # Transición a la aplicación principal
            self._mostrar_app_principal()
        else:
            # Mostrar el error en la GUI de Login
            if isinstance(self._current_frame, LoginFrame):
                self._current_frame.show_status(data, is_error=True)

    def _mostrar_app_principal(self):
        """
        Crea y muestra el MainAppFrame después de un login exitoso.
        Inicia la sincronización automática en segundo plano.
        """
        self._limpiar_frames_actuales()
        
        nombre = self.current_user_data.get('nombre_completo', self.current_username)
        self.title(f"Aplicación Hija - {nombre}")
        self.geometry("900x700")
        
        # Instanciar el MainAppFrame con callbacks para mensajería y chat
        self._current_frame = MainAppFrame(
            master=self,
            username=self.current_username,
            user_data=self.current_user_data,
            on_sync_attempt=self._intentar_sync,
            on_send_message=self._enviar_mensaje,
            on_send_chat=self._enviar_chat
        )
        self._current_frame.pack(fill="both", expand=True)
        
        # Cargar mensajes y chat inicial
        self._cargar_mensajes()
        self._cargar_chat()
        
        # Iniciar sincronización automática en segundo plano
        self._iniciar_sync_automatica()

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
                # Actualizar todas las pestañas con los datos sincronizados
                self._current_frame.update_content(data)
                
                # Marcar que la primera sincronización fue exitosa
                if not self.first_sync_done:
                    self.first_sync_done = True
                    # Cambiar intervalo a 30 minutos después de primera sync exitosa
                    self.sync_interval = 1800  # 30 minutos
                    print("Primera sincronización exitosa. Intervalo cambiado a 30 minutos.")
            else:
                # Si falla, 'data' es un diccionario con un error
                error_msg = data.get("error", "Error de sincronización desconocido.")
                self._current_frame.show_sync_error(error_msg)
    
    def _iniciar_sync_automatica(self):
        """
        Inicia un hilo de sincronización automática en segundo plano.
        Sincroniza cada 5 minutos inicialmente, luego cada 30 minutos tras la primera sync exitosa.
        """
        if self.sync_running:
            return  # Ya hay una sincronización en progreso
        
        self.sync_running = True
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        # Configurar prioridad más baja (en sistemas Unix)
        try:
            import os
            if hasattr(os, 'nice'):
                os.nice(10)  # Aumentar nice value = menor prioridad
        except:
            pass
        
        self.sync_thread.start()
        print("Sincronización automática iniciada en segundo plano")
    
    def _sync_loop(self):
        """
        Loop de sincronización que se ejecuta en segundo plano.
        Respeta el intervalo configurado (5 min inicial, 30 min después).
        """
        # Primera sincronización inmediata
        time.sleep(2)  # Pequeña espera para que la GUI se cargue
        self._sync_en_background()
        
        while self.sync_running:
            # Esperar el intervalo configurado
            time.sleep(self.sync_interval)
            
            if not self.sync_running:
                break
            
            # Realizar sincronización
            self._sync_en_background()
    
    def _sync_en_background(self):
        """
        Realiza una sincronización en segundo plano sin bloquear la GUI.
        """
        if not self.current_username:
            return
        
        try:
            # Actualizar status en la GUI
            if isinstance(self._current_frame, MainAppFrame):
                self.after(0, lambda: self._current_frame.update_sync_status(
                    "Sincronizando en segundo plano...", True
                ))
            
            success, data = self.communicator.fetch_sync_data(self.current_username)
            
            if success:
                # Actualizar GUI en el hilo principal
                if isinstance(self._current_frame, MainAppFrame):
                    self.after(0, lambda: self._current_frame.update_content(data))
                    self.after(0, lambda: self._current_frame.update_sync_status(
                        f"Sincronización automática activa (cada {self.sync_interval//60} min)"
                    ))
                
                # Marcar primera sync como exitosa
                if not self.first_sync_done:
                    self.first_sync_done = True
                    self.sync_interval = 1800  # Cambiar a 30 minutos
                    print("Primera sincronización automática exitosa. Intervalo -> 30 min")
            else:
                print(f"Error en sincronización automática: {data.get('error', 'Desconocido')}")
                
        except Exception as e:
            print(f"Excepción en sincronización automática: {e}")
    
    def _enviar_mensaje(self, to_user: str, subject: str, body: str):
        """Envía un mensaje a otro usuario."""
        if not isinstance(self._current_frame, MainAppFrame):
            return
        
        success, data = self.communicator.send_message(to_user, subject, body)
        
        if success:
            self._current_frame.lbl_status.configure(
                text=f"✓ Mensaje enviado a {to_user}"
            )
            # Recargar mensajes
            self._cargar_mensajes()
        else:
            error_msg = data.get("error", "Error desconocido")
            self._current_frame.lbl_status.configure(
                text=f"✗ Error enviando mensaje: {error_msg}"
            )
    
    def _enviar_chat(self, to_user: str, message: str):
        """Envía un mensaje de chat en vivo."""
        if not isinstance(self._current_frame, MainAppFrame):
            return
        
        success, data = self.communicator.send_chat_message(to_user, message)
        
        if success:
            # Recargar chat
            self._cargar_chat()
        else:
            error_msg = data.get("error", "Error desconocido")
            self._current_frame.lbl_status.configure(
                text=f"✗ Error enviando chat: {error_msg}"
            )
    
    def _cargar_mensajes(self):
        """Carga los mensajes del usuario."""
        if not isinstance(self._current_frame, MainAppFrame):
            return
        
        success, data = self.communicator.get_messages()
        
        if success:
            messages = data.get('mensajes', [])
            self._current_frame.update_message_list(messages)
        else:
            print(f"Error cargando mensajes: {data.get('error', 'Desconocido')}")
    
    def _cargar_chat(self):
        """Carga el historial de chat."""
        if not isinstance(self._current_frame, MainAppFrame):
            return
        
        success, data = self.communicator.get_chat_history("admin")
        
        if success:
            messages = data.get('mensajes', [])
            self._current_frame.update_chat_history(messages)
        else:
            print(f"Error cargando chat: {data.get('error', 'Desconocido')}")
    
    def destroy(self):
        """
        Override del método destroy para detener la sincronización al cerrar.
        """
        self.sync_running = False
        if self.sync_thread and self.sync_thread.is_alive():
            self.sync_thread.join(timeout=1)
        super().destroy()

# --- Punto de Entrada ---
if __name__ == "__main__":
    app = AppHija()
    app.mainloop()
