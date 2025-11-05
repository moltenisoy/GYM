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
    Presenta campos para nombre de usuario y contraseña.
    """
    def __init__(self, master, on_login_attempt, **kwargs):
        super().__init__(master, **kwargs)
        
        self.on_login_attempt = on_login_attempt  # Callback al controlador
        
        # Frame interno para el efecto "tarjeta"
        card_frame = customtkinter.CTkFrame(self)
        card_frame.pack(pady=40, padx=40)

        lbl_title = customtkinter.CTkLabel(
            card_frame,
            text="Acceso de Cliente",
            font=customtkinter.CTkFont(size=20, weight="bold")
        )
        lbl_title.pack(pady=(20, 10), padx=30)

        self.entry_username = customtkinter.CTkEntry(
            card_frame,
            placeholder_text="Nombre de usuario",
            width=250
        )
        self.entry_username.pack(pady=12, padx=30)
        
        self.entry_password = customtkinter.CTkEntry(
            card_frame,
            placeholder_text="Contraseña",
            width=250,
            show="*"
        )
        self.entry_password.pack(pady=12, padx=30)
        
        # Vincular la tecla "Enter" para que también intente el login
        self.entry_username.bind("<Return>", lambda e: self.entry_password.focus())
        self.entry_password.bind("<Return>", self._handle_login_event)

        self.btn_login = customtkinter.CTkButton(
            card_frame,
            text="Conectar a la Madre",
            command=self._handle_login_event
        )
        self.btn_login.pack(pady=12, padx=30)
        
        self.lbl_status = customtkinter.CTkLabel(card_frame, text="", text_color="red")
        self.lbl_status.pack(pady=(0, 20), padx=30)

    def _handle_login_event(self, event=None):
        """
        Manejador de eventos interno para el botón o la tecla Enter.
        Llama al callback del controlador.
        """
        username = self.entry_username.get()
        password = self.entry_password.get()
        
        if not username:
            self.show_status("Por favor, ingrese un nombre de usuario.")
            return
        
        if not password:
            self.show_status("Por favor, ingrese una contraseña.")
            return
            
        # Deshabilitar el botón para evitar clics múltiples
        self.btn_login.configure(text="Conectando...", state="disabled")
        self.lbl_status.configure(text="")
        
        # Llamar a la función del controlador (en hija_main.py)
        self.on_login_attempt(username, password)

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
    Muestra datos completos del usuario: perfil, cronograma, galería.
    """
    def __init__(self, master, username: str, user_data: dict, on_sync_attempt, **kwargs):
        super().__init__(master, **kwargs)
        
        self.username = username
        self.user_data = user_data
        self.on_sync_attempt = on_sync_attempt  # Callback al controlador
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # --- Cabecera de Bienvenida ---
        header_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        
        nombre_completo = user_data.get('nombre_completo', username)
        lbl_welcome = customtkinter.CTkLabel(
            header_frame,
            text=f"Bienvenido, {nombre_completo}",
            font=customtkinter.CTkFont(size=18, weight="bold")
        )
        lbl_welcome.pack(side="left")
        
        self.btn_sync = customtkinter.CTkButton(
            header_frame,
            text="Sincronizar Ahora",
            command=self._handle_sync_event
        )
        self.btn_sync.pack(side="right")

        # --- Área de Contenido Principal con Pestañas ---
        self.tabview = customtkinter.CTkTabview(self)
        self.tabview.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        # Crear pestañas
        self.tabview.add("Perfil")
        self.tabview.add("Cronograma")
        self.tabview.add("Galería")
        self.tabview.add("Mensajes")
        
        # Poblar pestañas
        self._crear_pestaña_perfil()
        self._crear_pestaña_cronograma()
        self._crear_pestaña_galeria()
        self._crear_pestaña_mensajes()

        # --- Pie de Página de Estado ---
        self.lbl_status = customtkinter.CTkLabel(
            self,
            text="Aplicación iniciada. Sincronización automática activa.",
            height=20
        )
        self.lbl_status.grid(row=2, column=0, padx=20, pady=5, sticky="w")
    
    def _crear_pestaña_perfil(self):
        """Crea la pestaña de perfil del usuario."""
        tab = self.tabview.tab("Perfil")
        tab.grid_columnconfigure(0, weight=1)
        
        # Frame con scroll para el perfil
        profile_frame = customtkinter.CTkScrollableFrame(tab)
        profile_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Información básica
        info_data = [
            ("Usuario:", self.user_data.get('username', 'N/A')),
            ("Nombre Completo:", self.user_data.get('nombre_completo', 'N/A')),
            ("Email:", self.user_data.get('email', 'N/A')),
            ("Teléfono:", self.user_data.get('telefono', 'N/A')),
            ("Equipo:", self.user_data.get('equipo', 'N/A')),
            ("Fecha Registro:", self.user_data.get('fecha_registro', 'N/A'))
        ]
        
        for label, value in info_data:
            row_frame = customtkinter.CTkFrame(profile_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=3)
            
            lbl = customtkinter.CTkLabel(
                row_frame,
                text=label,
                font=customtkinter.CTkFont(weight="bold"),
                width=150,
                anchor="w"
            )
            lbl.pack(side="left", padx=5)
            
            val = customtkinter.CTkLabel(row_frame, text=str(value), anchor="w")
            val.pack(side="left", padx=5, fill="x", expand=True)
    
    def _crear_pestaña_cronograma(self):
        """Crea la pestaña del cronograma de entrenamiento."""
        tab = self.tabview.tab("Cronograma")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        self.textbox_cronograma = customtkinter.CTkTextbox(tab)
        self.textbox_cronograma.pack(fill="both", expand=True, padx=10, pady=10)
        self.textbox_cronograma.insert("1.0", "Sin cronograma cargado. Sincronice para obtener datos.")
        self.textbox_cronograma.configure(state="disabled")
    
    def _crear_pestaña_galeria(self):
        """Crea la pestaña de galería de fotos."""
        tab = self.tabview.tab("Galería")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        self.scrollable_galeria = customtkinter.CTkScrollableFrame(tab)
        self.scrollable_galeria.pack(fill="both", expand=True, padx=10, pady=10)
        
        lbl_inicial = customtkinter.CTkLabel(
            self.scrollable_galeria,
            text="Sin fotos cargadas. Sincronice para obtener su galería."
        )
        lbl_inicial.pack(pady=20)
    
    def _crear_pestaña_mensajes(self):
        """Crea la pestaña de mensajes de sincronización."""
        tab = self.tabview.tab("Mensajes")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        self.textbox_mensajes = customtkinter.CTkTextbox(tab)
        self.textbox_mensajes.pack(fill="both", expand=True, padx=10, pady=10)
        self.textbox_mensajes.insert("1.0", "Sin mensajes. Sincronice para obtener contenido global.")
        self.textbox_mensajes.configure(state="disabled")

    def _handle_sync_event(self):
        """Manejador interno para el botón de sincronización."""
        self.btn_sync.configure(text="Sincronizando...", state="disabled")
        self.lbl_status.configure(text="Contactando a la Madre...", text_color="gray")
        
        # Llamar al callback del controlador (en hija_main.py)
        self.on_sync_attempt()

    def update_content(self, sync_data: dict):
        """Actualiza todas las pestañas con los datos sincronizados."""
        # Actualizar cronograma
        training_schedule = sync_data.get('training_schedule')
        if training_schedule:
            self.textbox_cronograma.configure(state="normal")
            self.textbox_cronograma.delete("1.0", "end")
            
            content = f"=== CRONOGRAMA DE ENTRENAMIENTO ===\n\n"
            content += f"Mes: {training_schedule.get('mes')} {training_schedule.get('ano')}\n"
            
            schedule_data = training_schedule.get('schedule_data', {})
            content += f"Objetivo: {schedule_data.get('objetivo', 'N/A')}\n"
            content += f"Notas: {schedule_data.get('notas', 'N/A')}\n\n"
            
            dias = schedule_data.get('dias', {})
            for dia, info in dias.items():
                content += f"=== {dia.upper()} ===\n"
                ejercicios = info.get('ejercicios', [])
                content += f"Ejercicios: {', '.join(ejercicios)}\n"
                content += f"Descripción: {info.get('descripcion', 'N/A')}\n"
                content += f"Duración: {info.get('duracion_minutos', 0)} minutos\n\n"
            
            self.textbox_cronograma.insert("1.0", content)
            self.textbox_cronograma.configure(state="disabled")
        
        # Actualizar galería
        photo_gallery = sync_data.get('photo_gallery', [])
        for widget in self.scrollable_galeria.winfo_children():
            widget.destroy()
        
        if photo_gallery:
            for i, photo in enumerate(photo_gallery):
                photo_frame = customtkinter.CTkFrame(self.scrollable_galeria)
                photo_frame.pack(fill="x", padx=5, pady=5)
                
                lbl_photo = customtkinter.CTkLabel(
                    photo_frame,
                    text=f"📷 {photo.get('photo_path', '').split('/')[-1]}",
                    font=customtkinter.CTkFont(weight="bold"),
                    anchor="w"
                )
                lbl_photo.pack(side="left", padx=10, pady=5)
                
                if photo.get('descripcion'):
                    lbl_desc = customtkinter.CTkLabel(
                        photo_frame,
                        text=photo['descripcion'],
                        text_color="gray",
                        anchor="w"
                    )
                    lbl_desc.pack(side="left", padx=10, pady=5)
                
                lbl_fecha = customtkinter.CTkLabel(
                    photo_frame,
                    text=photo.get('upload_date', '')[:10],
                    text_color="gray",
                    anchor="e"
                )
                lbl_fecha.pack(side="right", padx=10, pady=5)
        else:
            lbl_no_photos = customtkinter.CTkLabel(
                self.scrollable_galeria,
                text="No hay fotos en la galería"
            )
            lbl_no_photos.pack(pady=20)
        
        # Actualizar mensajes globales
        sync_content = sync_data.get('sync_content', {})
        if sync_content:
            self.textbox_mensajes.configure(state="normal")
            self.textbox_mensajes.delete("1.0", "end")
            
            contenido = sync_content.get('contenido', 'Sin contenido')
            version = sync_content.get('metadatos_version', '1.0.0')
            
            mensaje = f"=== MENSAJES DEL GIMNASIO ===\n"
            mensaje += f"Versión: {version}\n\n"
            mensaje += contenido
            
            self.textbox_mensajes.insert("1.0", mensaje)
            self.textbox_mensajes.configure(state="disabled")
        
        timestamp = sync_data.get('timestamp', '')[:19] if sync_data.get('timestamp') else ''
        self.lbl_status.configure(
            text=f"✓ Última sincronización: {timestamp}",
            text_color="green"
        )
        self.btn_sync.configure(text="Sincronizar Ahora", state="normal")

    def show_sync_error(self, message: str):
        """Muestra un error de sincronización."""
        self.lbl_status.configure(text=f"✗ Error: {message}", text_color="red")
        self.btn_sync.configure(text="Sincronizar Ahora", state="normal")
    
    def update_sync_status(self, message: str, is_syncing: bool = False):
        """Actualiza el mensaje de estado de sincronización."""
        if is_syncing:
            self.lbl_status.configure(text=f"⟳ {message}", text_color="blue")
        else:
            self.lbl_status.configure(text=message, text_color="gray")
