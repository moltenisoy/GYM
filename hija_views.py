# hija_views.py
#
# Define las "vistas" o "páginas" de la aplicación Hija.
# Estas clases son componentes puros de GUI (CustomTkinter) que
# no contienen lógica de negocio o de red.
# Reciben un 'controlador' o 'comando' para notificar acciones del usuario.

import customtkinter

class LoginFrame(customtkinter.CTkFrame):
    """
    GUI para la pantalla de inicio de sesión.
    Presenta un campo de entrada para el nombre de usuario y un botón de conexión.
    """
    def __init__(self, master, on_login_attempt, **kwargs):
        super().__init__(master, **kwargs)
        
        self.on_login_attempt = on_login_attempt  # Callback al controlador
        
        # Frame interno para el efecto "tarjeta"
        card_frame = customtkinter.CTkFrame(self)
        card_frame.pack(pady=40, padx=40)

        lbl_title = customtkinter.CTkLabel(card_frame, text="Acceso de Cliente", font=customtkinter.CTkFont(size=20, weight="bold"))
        lbl_title.pack(pady=(20, 10), padx=30)

        self.entry_username = customtkinter.CTkEntry(card_frame, placeholder_text="Nombre de usuario", width=250)
        self.entry_username.pack(pady=12, padx=30)
        
        # Vincular la tecla "Enter" para que también intente el login
        self.entry_username.bind("<Return>", self._handle_login_event)

        self.btn_login = customtkinter.CTkButton(card_frame, text="Conectar a la Madre", command=self._handle_login_event)
        self.btn_login.pack(pady=12, padx=30)
        
        self.lbl_status = customtkinter.CTkLabel(card_frame, text="", text_color="red")
        self.lbl_status.pack(pady=(0, 20), padx=30)

    def _handle_login_event(self, event=None):
        """
        Manejador de eventos interno para el botón o la tecla Enter.
        Llama al callback del controlador.
        """
        username = self.entry_username.get()
        if not username:
            self.show_status("Por favor, ingrese un nombre de usuario.")
            return
            
        # Deshabilitar el botón para evitar clics múltiples
        self.btn_login.configure(text="Conectando...", state="disabled")
        self.lbl_status.configure(text="")
        
        # Llamar a la función del controlador (en hija_main.py)
        self.on_login_attempt(username)

    def show_status(self, message: str, is_error: bool = True):
        """Muestra un mensaje de estado (ej. un error) al usuario."""
        color = "red" if is_error else "green"
        self.lbl_status.configure(text=message, text_color=color)
        # Rehabilitar el botón
        self.btn_login.configure(text="Conectar a la Madre", state="normal")

    def get_username(self) -> str:
        """Devuelve el nombre de usuario ingresado."""
        return self.entry_username.get()


class MainAppFrame(customtkinter.CTkFrame):
    """
    GUI para la aplicación principal, mostrada después de un inicio de sesión exitoso.
    Esta es la interfaz "escalable y compleja" solicitada.
    Para el prototipo, contiene un área de bienvenida y la función de sincronización.
    """
    def __init__(self, master, username: str, on_sync_attempt, **kwargs):
        super().__init__(master, **kwargs)
        
        self.username = username
        self.on_sync_attempt = on_sync_attempt  # Callback al controlador
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # --- Cabecera de Bienvenida ---
        header_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        
        lbl_welcome = customtkinter.CTkLabel(header_frame, text=f"Bienvenido, {self.username}", font=customtkinter.CTkFont(size=18, weight="bold"))
        lbl_welcome.pack(side="left")
        
        self.btn_sync = customtkinter.CTkButton(header_frame, text="Sincronizar con la Madre", command=self._handle_sync_event)
        self.btn_sync.pack(side="right")

        # --- Área de Contenido Principal ---
        # Para cumplir con la escalabilidad, se podría insertar un CTkTabview aquí.
        # Por simplicidad, mostramos un cuadro de texto para los datos sincronizados.
        content_frame = customtkinter.CTkFrame(self)
        content_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)

        lbl_content_title = customtkinter.CTkLabel(content_frame, text="Contenido Sincronizado de la Madre:")
        lbl_content_title.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        self.textbox_content = customtkinter.CTkTextbox(content_frame, state="disabled")
        self.textbox_content.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        # --- Pie de Página de Estado ---
        self.lbl_status = customtkinter.CTkLabel(self, text="Aplicación iniciada. Listo para sincronizar.", height=20)
        self.lbl_status.grid(row=2, column=0, padx=20, pady=5, sticky="w")

    def _handle_sync_event(self):
        """Manejador interno para el botón de sincronización."""
        self.btn_sync.configure(text="Sincronizando...", state="disabled")
        self.lbl_status.configure(text="Contactando a la Madre...", text_color="gray")
        
        # Llamar al callback del controlador (en hija_main.py)
        self.on_sync_attempt()

    def update_content(self, content: str, version: str):
        """Actualiza el cuadro de texto con el nuevo contenido sincronizado."""
        self.textbox_content.configure(state="normal")  # Habilitar escritura
        self.textbox_content.delete("1.0", "end")
        self.textbox_content.insert("1.0", content)
        self.textbox_content.configure(state="disabled")  # Deshabilitar escritura
        
        self.lbl_status.configure(text=f"Sincronización exitosa. Versión: {version}", text_color="green")
        self.btn_sync.configure(text="Sincronizar con la Madre", state="normal")

    def show_sync_error(self, message: str):
        """Muestra un error de sincronización."""
        self.lbl_status.configure(text=message, text_color="red")
        self.btn_sync.configure(text="Sincronizar con la Madre", state="normal")
