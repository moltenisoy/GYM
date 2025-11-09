import customtkinter
import threading
import time
from hija_comms import APICommunicator
from hija_views import LoginFrame, MainAppFrame
from config.settings import get_hija_settings
from shared.logger import setup_logger

logger = setup_logger(__name__, log_file="hija_main.log")

settings = get_hija_settings()

customtkinter.set_appearance_mode("system")
customtkinter.set_default_color_theme("blue")

logger.info("Hija application module loaded - Settings: %s", settings)

class AppHija(customtkinter.CTk):

    def __init__(self):
        super().__init__()

        logger.info("=== Initializing Hija Application ===")

        self.title("Portal del Socio - Gimnasio")
        self.geometry("800x600")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.communicator = APICommunicator()
        self.current_username = None
        self.current_user_data = None

        self.sync_thread = None
        self.sync_running = False
        self.sync_interval = settings.SYNC_INTERVAL_INITIAL
        self.first_sync_done = False

        self._current_frame = None

        logger.info("Hija application initialized, attempting auto-login...")

        self._intentar_auto_login()

    def _limpiar_frames_actuales(self):
        if self._current_frame:
            self._current_frame.pack_forget()
            self._current_frame.destroy()
            self._current_frame = None

    def _intentar_auto_login(self):
        creds = self.communicator.load_credentials()
        if not creds:
            self._mostrar_login()
            return

        username = creds.get('username')

        valid, validation_data = self.communicator.validate_sync_status(username)

        if not valid and validation_data.get('bloqueado'):
            self.communicator.clear_credentials()
            self._mostrar_login()
            return

        self.current_username = username
        self.current_user_data = {
            'username': username,
            'nombre_completo': creds.get('nombre_completo', username)
        }
        self._mostrar_app_principal()

    def _mostrar_login(self):
        self._limpiar_frames_actuales()

        self.title("Aplicación Hija - Iniciar Sesión")
        self.geometry("600x450")

        self._current_frame = LoginFrame(master=self, on_login_attempt=self._intentar_login)
        self._current_frame.pack(padx=20, pady=20, fill="both", expand=True)

    def _intentar_login(self, username: str, password: str):
        success, data = self.communicator.attempt_login(username, password)

        if success:
            self.current_username = username
            self.current_user_data = data
            self._mostrar_app_principal()
        else:
            if isinstance(self._current_frame, LoginFrame):
                self._current_frame.show_status(data, is_error=True)

    def _mostrar_app_principal(self):
        self._limpiar_frames_actuales()

        nombre = self.current_user_data.get('nombre_completo', self.current_username)
        self.title(f"Aplicación Hija - {nombre}")
        self.geometry("900x700")

        self._current_frame = MainAppFrame(
            master=self,
            username=self.current_username,
            user_data=self.current_user_data,
            on_sync_attempt=self._intentar_sync,
            on_send_message=self._enviar_mensaje,
            on_send_chat=self._enviar_chat
        )
        self._current_frame.pack(fill="both", expand=True)

        self._cargar_mensajes()
        self._cargar_chat()

        self._iniciar_sync_automatica()

    def _intentar_sync(self):
        if not self.current_username:
            if isinstance(self._current_frame, MainAppFrame):
                self._current_frame.show_sync_error("Error: No hay usuario autenticado.")
            return

        success, data = self.communicator.fetch_sync_data(self.current_username)

        if isinstance(self._current_frame, MainAppFrame):
            if success:
                self._current_frame.update_content(data)

                if not self.first_sync_done:
                    self.first_sync_done = True
                    self.sync_interval = settings.SYNC_INTERVAL_NORMAL
                    logger.info(
                        "Primera sincronización exitosa. Intervalo cambiado a %d minutos.",
                        self.sync_interval // 60)
            else:
                error_msg = data.get("error", "Error de sincronización desconocido.")
                self._current_frame.show_sync_error(error_msg)

    def _iniciar_sync_automatica(self):
        if self.sync_running:
            return

        self.sync_running = True
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True, name="SyncThread")

        self.sync_thread.start()
        logger.info("Sincronización automática iniciada (intervalo: %ds)", self.sync_interval)

    def _sync_loop(self):
        time.sleep(2)
        self._sync_en_background()

        while self.sync_running:
            time.sleep(self.sync_interval)

            if not self.sync_running:
                break

            self._sync_en_background()

    def _sync_en_background(self):
        if not self.current_username:
            return

        try:
            if isinstance(self._current_frame, MainAppFrame):
                self.after(0, lambda: self._current_frame.update_sync_status(
                    "Sincronizando en segundo plano...", True
                ))

            success, data = self.communicator.fetch_sync_data(self.current_username)

            if success:
                if isinstance(self._current_frame, MainAppFrame):
                    self.after(0, lambda: self._current_frame.update_content(data))
                    self.after(0, lambda: self._current_frame.update_sync_status(
                        f"Sincronización automática activa (cada {self.sync_interval // 60} min)"
                    ))

                if not self.first_sync_done:
                    self.first_sync_done = True
                    self.sync_interval = settings.SYNC_INTERVAL_NORMAL
                    logger.info(
                        "Primera sincronización automática exitosa. Intervalo -> %d min",
                        self.sync_interval // 60)
            else:
                logger.warning("Error en sincronización automática: %s", data.get('error', 'Desconocido'))

        except Exception as e:
            logger.error("Excepción en sincronización automática: %s", e, exc_info=True)

    def _enviar_mensaje(self, to_user: str, subject: str, body: str):
        if not isinstance(self._current_frame, MainAppFrame):
            return

        success, data = self.communicator.send_message(to_user, subject, body)

        if success:
            self._current_frame.lbl_status.configure(
                text=f"✓ Mensaje enviado a {to_user}"
            )
            self._cargar_mensajes()
        else:
            error_msg = data.get("error", "Error desconocido")
            self._current_frame.lbl_status.configure(
                text=f"✗ Error enviando mensaje: {error_msg}"
            )

    def _enviar_chat(self, to_user: str, message: str):
        if not isinstance(self._current_frame, MainAppFrame):
            return

        success, data = self.communicator.send_chat_message(to_user, message)

        if success:
            self._cargar_chat()
        else:
            error_msg = data.get("error", "Error desconocido")
            self._current_frame.lbl_status.configure(
                text=f"✗ Error enviando chat: {error_msg}"
            )

    def _cargar_mensajes(self):
        if not isinstance(self._current_frame, MainAppFrame):
            return

        success, data = self.communicator.get_messages()

        if success:
            messages = data.get('mensajes', [])
            self._current_frame.update_message_list(messages)
        else:
            logger.error("Error cargando mensajes: %s", data.get('error', 'Desconocido'))

    def _cargar_chat(self):
        if not isinstance(self._current_frame, MainAppFrame):
            return

        success, data = self.communicator.get_chat_history("admin")

        if success:
            messages = data.get('mensajes', [])
            self._current_frame.update_chat_history(messages)
        else:
            logger.error("Error cargando chat: %s", data.get('error', 'Desconocido'))

    def destroy(self):
        logger.info("Shutting down Hija application...")
        self.sync_running = False
        if self.sync_thread and self.sync_thread.is_alive():
            logger.debug("Waiting for sync thread to finish...")
            self.sync_thread.join(timeout=1)
        super().destroy()
        logger.info("Hija application closed")

if __name__ == "__main__":
    logger.info("=== Starting Hija Application ===")
    try:
        app = AppHija()
        app.mainloop()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.critical("Fatal error in Hija application: %s", e, exc_info=True)
        raise
    finally:
        logger.info("=== Hija Application Finished ===")
