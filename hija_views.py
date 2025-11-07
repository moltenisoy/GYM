# hija_views.py
#
# Define las "vistas" o "páginas" de la Aplicación de Socios (Aplicación Hija).
# Estas clases son componentes puros de GUI (CustomTkinter) que permiten a los
# socios del gimnasio acceder a su información, reservar clases, y gestionar su membresía.
# No contienen lógica de negocio o de red.
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
            text="Portal del Socio",
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

    def _handle_login_event(self, _event=None):
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
    GUI mejorada para la aplicación principal con sidebar y diseño profesional.
    Incluye animaciones, transiciones, mensajería y chat en vivo.
    """

    def __init__(self, master, username: str, user_data: dict, on_sync_attempt,
                 on_send_message=None, on_send_chat=None, **kwargs):
        super().__init__(master, **kwargs)

        self.username = username
        self.user_data = user_data
        self.on_sync_attempt = on_sync_attempt
        self.on_send_message = on_send_message
        self.on_send_chat = on_send_chat

        # Configurar grid principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ===============================
        # BARRA SUPERIOR - Perfil de Usuario
        # ===============================
        self._crear_barra_superior()

        # ===============================
        # SIDEBAR IZQUIERDA - Navegación
        # ===============================
        self._crear_sidebar()

        # ===============================
        # ÁREA DE CONTENIDO PRINCIPAL
        # ===============================
        self.content_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Variable para trackear la vista actual
        self.current_view = None

        # Mostrar vista inicial
        self._mostrar_perfil()

        # ===============================
        # BARRA DE ESTADO INFERIOR
        # ===============================
        self.status_frame = customtkinter.CTkFrame(self, height=30)
        self.status_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        self.lbl_status = customtkinter.CTkLabel(
            self.status_frame,
            text="● Conectado - Sincronización automática activa",
            anchor="w"
        )
        self.lbl_status.pack(side="left", padx=10, pady=5)

    def _crear_barra_superior(self):
        """Crea la barra superior con información del usuario."""
        header_frame = customtkinter.CTkFrame(self, height=80, corner_radius=10)
        header_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        header_frame.grid_propagate(False)

        # Nombre y equipo del usuario
        nombre_completo = self.user_data.get('nombre_completo', self.username)
        equipo = self.user_data.get('equipo', 'Sin equipo')

        info_frame = customtkinter.CTkFrame(header_frame, fg_color="transparent")
        info_frame.pack(side="left", padx=20, pady=10, fill="both", expand=True)

        lbl_nombre = customtkinter.CTkLabel(
            info_frame,
            text=nombre_completo,
            font=customtkinter.CTkFont(size=20, weight="bold"),
            anchor="w"
        )
        lbl_nombre.pack(anchor="w")

        lbl_equipo = customtkinter.CTkLabel(
            info_frame,
            text=f"👥 {equipo}",
            font=customtkinter.CTkFont(size=14),
            text_color="gray",
            anchor="w"
        )
        lbl_equipo.pack(anchor="w")

        email = self.user_data.get('email', '')
        if email:
            lbl_email = customtkinter.CTkLabel(
                info_frame,
                text=f"📧 {email}",
                font=customtkinter.CTkFont(size=12),
                text_color="gray",
                anchor="w"
            )
            lbl_email.pack(anchor="w")

        # Botón de sincronización
        self.btn_sync = customtkinter.CTkButton(
            header_frame,
            text="⟳ Sincronizar",
            width=120,
            command=self._handle_sync_event,
            fg_color="#2563eb",
            hover_color="#1d4ed8"
        )
        self.btn_sync.pack(side="right", padx=20, pady=10)

    def _crear_sidebar(self):
        """Crea la barra lateral de navegación."""
        sidebar_frame = customtkinter.CTkFrame(self, width=220, corner_radius=10)
        sidebar_frame.grid(row=1, column=0, padx=(10, 0), pady=(0, 10), sticky="nsew")
        sidebar_frame.grid_propagate(False)

        # Título del sidebar
        lbl_menu = customtkinter.CTkLabel(
            sidebar_frame,
            text="📋 MENÚ PRINCIPAL",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        lbl_menu.pack(padx=15, pady=(20, 10), anchor="w")

        # Botones de navegación
        self.nav_buttons = {}

        nav_items = [
            ("home", "🏠 Perfil", self._mostrar_perfil),
            ("schedule", "📅 Cronograma", self._mostrar_cronograma),
            ("exercise", "💪 Ejercicios", self._mostrar_ejercicios),
            ("training", "🏋️ Plan Entrenamiento", self._mostrar_plan_entrenamiento),
            ("measurements", "📏 Medidas", self._mostrar_medidas),
            ("nutrition", "🍎 Nutrición", self._mostrar_nutricion),
            ("dashboard", "📊 Dashboard", self._mostrar_dashboard),
            ("gallery", "🖼️ Galería", self._mostrar_galeria),
            ("messages", "✉️ Mensajes", self._mostrar_mensajes),
            ("chat", "💬 Chat en Vivo", self._mostrar_chat),
        ]

        for key, text, command in nav_items:
            btn = customtkinter.CTkButton(
                sidebar_frame,
                text=text,
                command=command,
                anchor="w",
                height=40,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
                corner_radius=8
            )
            btn.pack(padx=10, pady=5, fill="x")
            self.nav_buttons[key] = btn

        # Separador
        separator = customtkinter.CTkFrame(sidebar_frame, height=2, fg_color="gray30")
        separator.pack(padx=10, pady=20, fill="x")

        # Info adicional
        info_label = customtkinter.CTkLabel(
            sidebar_frame,
            text="Sistema GYM v3.0\nConexión segura activa",
            font=customtkinter.CTkFont(size=10),
            text_color="gray",
            justify="center"
        )
        info_label.pack(side="bottom", padx=10, pady=20)

    def _limpiar_contenido(self):
        """Limpia el área de contenido principal."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _activar_boton_nav(self, key: str):
        """Activa visualmente un botón de navegación."""
        for btn_key, btn in self.nav_buttons.items():
            if btn_key == key:
                btn.configure(fg_color="#2563eb", hover_color="#1d4ed8")
            else:
                btn.configure(fg_color="transparent", hover_color=("gray70", "gray30"))

    def _mostrar_perfil(self):
        """Muestra la vista de perfil del usuario."""
        self._limpiar_contenido()
        self._activar_boton_nav("home")
        self.current_view = "perfil"

        # Crear frame scrollable para perfil
        profile_scroll = customtkinter.CTkScrollableFrame(
            self.content_frame,
            label_text="👤 PERFIL DE USUARIO"
        )
        profile_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # Información del usuario
        info_data = [
            ("Usuario:", self.user_data.get('username', 'N/A')),
            ("Nombre Completo:", self.user_data.get('nombre_completo', 'N/A')),
            ("Email:", self.user_data.get('email', 'N/A')),
            ("Teléfono:", self.user_data.get('telefono', 'N/A')),
            ("Equipo:", self.user_data.get('equipo', 'N/A')),
            ("Fecha Registro:", self.user_data.get('fecha_registro', 'N/A'))
        ]

        for label, value in info_data:
            row_frame = customtkinter.CTkFrame(profile_scroll)
            row_frame.pack(fill="x", pady=8, padx=5)

            lbl = customtkinter.CTkLabel(
                row_frame,
                text=label,
                font=customtkinter.CTkFont(weight="bold", size=14),
                width=180,
                anchor="w"
            )
            lbl.pack(side="left", padx=10)

            val = customtkinter.CTkLabel(
                row_frame,
                text=str(value),
                anchor="w"
            )
            val.pack(side="left", padx=10, fill="x", expand=True)

    def _mostrar_cronograma(self):
        """Muestra la vista del cronograma de entrenamiento."""
        self._limpiar_contenido()
        self._activar_boton_nav("schedule")
        self.current_view = "cronograma"

        frame_container = customtkinter.CTkFrame(self.content_frame)
        frame_container.pack(fill="both", expand=True, padx=10, pady=10)

        lbl_title = customtkinter.CTkLabel(
            frame_container,
            text="📅 CRONOGRAMA DE ENTRENAMIENTO",
            font=customtkinter.CTkFont(size=16, weight="bold")
        )
        lbl_title.pack(padx=10, pady=10)

        self.textbox_cronograma = customtkinter.CTkTextbox(frame_container)
        self.textbox_cronograma.pack(fill="both", expand=True, padx=10, pady=10)
        self.textbox_cronograma.insert("1.0", "Sin cronograma cargado. Sincronice para obtener datos.")
        self.textbox_cronograma.configure(state="disabled")

    def _mostrar_galeria(self):
        """Muestra la vista de galería de fotos."""
        self._limpiar_contenido()
        self._activar_boton_nav("gallery")
        self.current_view = "galeria"

        self.scrollable_galeria = customtkinter.CTkScrollableFrame(
            self.content_frame,
            label_text="🖼️ GALERÍA DE FOTOS"
        )
        self.scrollable_galeria.pack(fill="both", expand=True, padx=10, pady=10)

        lbl_inicial = customtkinter.CTkLabel(
            self.scrollable_galeria,
            text="Sin fotos cargadas. Sincronice para obtener su galería."
        )
        lbl_inicial.pack(pady=20)

    def _mostrar_mensajes(self):
        """Muestra la vista de mensajes."""
        self._limpiar_contenido()
        self._activar_boton_nav("messages")
        self.current_view = "mensajes"

        msg_frame = customtkinter.CTkFrame(self.content_frame)
        msg_frame.pack(fill="both", expand=True, padx=10, pady=10)
        msg_frame.grid_columnconfigure(0, weight=1)
        msg_frame.grid_rowconfigure(1, weight=1)

        # Header con botón de nuevo mensaje
        header = customtkinter.CTkFrame(msg_frame)
        header.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        lbl_title = customtkinter.CTkLabel(
            header,
            text="✉️ BUZÓN DE MENSAJES",
            font=customtkinter.CTkFont(size=16, weight="bold")
        )
        lbl_title.pack(side="left", padx=10)

        btn_nuevo = customtkinter.CTkButton(
            header,
            text="✏️ Nuevo Mensaje",
            command=self._abrir_nuevo_mensaje,
            width=140
        )
        btn_nuevo.pack(side="right", padx=10)

        # Lista de mensajes
        self.scrollable_mensajes = customtkinter.CTkScrollableFrame(msg_frame)
        self.scrollable_mensajes.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        lbl_inicial = customtkinter.CTkLabel(
            self.scrollable_mensajes,
            text="Sin mensajes. Sincronice para cargar."
        )
        lbl_inicial.pack(pady=20)

    def _mostrar_chat(self):
        """Muestra la vista de chat en vivo."""
        self._limpiar_contenido()
        self._activar_boton_nav("chat")
        self.current_view = "chat"

        chat_frame = customtkinter.CTkFrame(self.content_frame)
        chat_frame.pack(fill="both", expand=True, padx=10, pady=10)
        chat_frame.grid_columnconfigure(0, weight=1)
        chat_frame.grid_rowconfigure(1, weight=1)

        # Header
        header = customtkinter.CTkFrame(chat_frame)
        header.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        lbl_title = customtkinter.CTkLabel(
            header,
            text="💬 CHAT EN VIVO CON ADMINISTRACIÓN",
            font=customtkinter.CTkFont(size=16, weight="bold")
        )
        lbl_title.pack(side="left", padx=10)

        # Área de mensajes de chat
        self.scrollable_chat = customtkinter.CTkScrollableFrame(chat_frame)
        self.scrollable_chat.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Input de mensaje
        input_frame = customtkinter.CTkFrame(chat_frame)
        input_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)

        self.entry_chat = customtkinter.CTkEntry(
            input_frame,
            placeholder_text="Escribe tu mensaje..."
        )
        self.entry_chat.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.entry_chat.bind("<Return>", lambda e: self._enviar_chat())

        btn_enviar = customtkinter.CTkButton(
            input_frame,
            text="Enviar",
            width=80,
            command=self._enviar_chat
        )
        btn_enviar.grid(row=0, column=1, padx=5, pady=5)

        # Mensaje inicial
        lbl_inicial = customtkinter.CTkLabel(
            self.scrollable_chat,
            text="Inicia una conversación con la administración.\nEscribe un mensaje abajo para comenzar.",
            justify="center",
            text_color="gray"
        )
        lbl_inicial.pack(pady=30)

    def _abrir_nuevo_mensaje(self):
        """Abre un diálogo para enviar un nuevo mensaje."""
        dialog = customtkinter.CTkInputDialog(
            text="Ingrese el destinatario (admin para administración):",
            title="Nuevo Mensaje"
        )
        destinatario = dialog.get_input()

        if destinatario and self.on_send_message:
            # Aquí se podría abrir un diálogo más completo
            # Por ahora solo mostramos un mensaje de info
            self.lbl_status.configure(
                text=f"📝 Preparando mensaje para {destinatario}..."
            )

    def _enviar_chat(self):
        """Envía un mensaje de chat."""
        mensaje = self.entry_chat.get()
        if mensaje and self.on_send_chat:
            self.on_send_chat("admin", mensaje)  # Enviar a admin
            self.entry_chat.delete(0, "end")

            # Añadir mensaje a la vista
            msg_frame = customtkinter.CTkFrame(self.scrollable_chat)
            msg_frame.pack(fill="x", padx=5, pady=3, anchor="e")

            lbl_msg = customtkinter.CTkLabel(
                msg_frame,
                text=f"Tú: {mensaje}",
                anchor="w",
                wraplength=400
            )
            lbl_msg.pack(padx=10, pady=5)

        # --- Pie de Página de Estado ---
        self.lbl_status = customtkinter.CTkLabel(
            self,
            text="Aplicación iniciada. Sincronización automática activa.",
            height=20
        )
        self.lbl_status.grid(row=2, column=0, padx=20, pady=5, sticky="w")

    def _handle_sync_event(self):
        """Manejador interno para el botón de sincronización."""
        self.btn_sync.configure(text="⟳ Sincronizando...", state="disabled")
        self.lbl_status.configure(text="⟳ Contactando a la Madre...")

        # Llamar al callback del controlador (en hija_main.py)
        self.on_sync_attempt()

    def update_content(self, sync_data: dict):
        """Actualiza todos los datos sincronizados en la vista activa."""
        # Actualizar cronograma si la vista está activa
        training_schedule = sync_data.get('training_schedule')
        if training_schedule and self.current_view == "cronograma":
            self.textbox_cronograma.configure(state="normal")
            self.textbox_cronograma.delete("1.0", "end")

            content = "=== CRONOGRAMA DE ENTRENAMIENTO ===\n\n"
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

        # Actualizar galería si la vista está activa
        photo_gallery = sync_data.get('photo_gallery', [])
        if self.current_view == "galeria":
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

        timestamp = sync_data.get('timestamp', '')[:19] if sync_data.get('timestamp') else ''
        self.lbl_status.configure(
            text=f"● Conectado - Última sincronización: {timestamp}"
        )
        self.btn_sync.configure(text="⟳ Sincronizar", state="normal")

    def show_sync_error(self, message: str):
        """Muestra un error de sincronización."""
        self.lbl_status.configure(text=f"✗ Error: {message}")
        self.btn_sync.configure(text="⟳ Sincronizar", state="normal")

    def update_sync_status(self, message: str, is_syncing: bool = False):
        """Actualiza el mensaje de estado de sincronización."""
        if is_syncing:
            self.lbl_status.configure(text=f"⟳ {message}")
        else:
            self.lbl_status.configure(text=f"● {message}")

    def update_message_list(self, messages: list):
        """Actualiza la lista de mensajes."""
        if self.current_view != "mensajes":
            return

        for widget in self.scrollable_mensajes.winfo_children():
            widget.destroy()

        if not messages:
            lbl_no_msg = customtkinter.CTkLabel(
                self.scrollable_mensajes,
                text="No hay mensajes"
            )
            lbl_no_msg.pack(pady=20)
            return

        for msg in messages:
            msg_frame = customtkinter.CTkFrame(self.scrollable_mensajes)
            msg_frame.pack(fill="x", padx=5, pady=5)

            # Indicador de leído/no leído
            indicator = "●" if not msg.get('is_read') else "○"
            color = "#2563eb" if not msg.get('is_read') else "gray"

            header_frame = customtkinter.CTkFrame(msg_frame, fg_color="transparent")
            header_frame.pack(fill="x", padx=10, pady=5)

            lbl_from = customtkinter.CTkLabel(
                header_frame,
                text=f"{indicator} De: {msg.get('from_user', 'Desconocido')}",
                font=customtkinter.CTkFont(weight="bold"),
                text_color=color,
                anchor="w"
            )
            lbl_from.pack(side="left")

            lbl_date = customtkinter.CTkLabel(
                header_frame,
                text=msg.get('sent_date', '')[:16],
                text_color="gray",
                anchor="e"
            )
            lbl_date.pack(side="right")

            lbl_subject = customtkinter.CTkLabel(
                msg_frame,
                text=msg.get('subject', 'Sin asunto'),
                anchor="w"
            )
            lbl_subject.pack(fill="x", padx=10, pady=2)

            # Botón para ver mensaje
            btn_view = customtkinter.CTkButton(
                msg_frame,
                text="Ver Mensaje",
                width=100,
                height=25,
                command=lambda m=msg: self._ver_mensaje_detalle(m)
            )
            btn_view.pack(padx=10, pady=5, anchor="e")

    def _ver_mensaje_detalle(self, msg: dict):
        """Muestra los detalles de un mensaje."""
        # Crear ventana emergente para el mensaje
        dialog = customtkinter.CTkToplevel(self)
        dialog.title(f"Mensaje de {msg.get('from_user', 'Desconocido')}")
        dialog.geometry("600x400")

        # Contenido del mensaje
        content_frame = customtkinter.CTkScrollableFrame(dialog)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        lbl_from = customtkinter.CTkLabel(
            content_frame,
            text=f"De: {msg.get('from_user', 'Desconocido')}",
            font=customtkinter.CTkFont(weight="bold"),
            anchor="w"
        )
        lbl_from.pack(fill="x", pady=2)

        lbl_date = customtkinter.CTkLabel(
            content_frame,
            text=f"Fecha: {msg.get('sent_date', 'N/A')}",
            anchor="w"
        )
        lbl_date.pack(fill="x", pady=2)

        lbl_subject = customtkinter.CTkLabel(
            content_frame,
            text=f"Asunto: {msg.get('subject', 'Sin asunto')}",
            font=customtkinter.CTkFont(weight="bold"),
            anchor="w"
        )
        lbl_subject.pack(fill="x", pady=5)

        textbox = customtkinter.CTkTextbox(content_frame, height=200)
        textbox.pack(fill="both", expand=True, pady=10)
        textbox.insert("1.0", msg.get('body', ''))
        textbox.configure(state="disabled")

    def update_chat_history(self, messages: list):
        """Actualiza el historial de chat."""
        if self.current_view != "chat":
            return

        for widget in self.scrollable_chat.winfo_children():
            widget.destroy()

        if not messages:
            lbl_no_chat = customtkinter.CTkLabel(
                self.scrollable_chat,
                text="No hay mensajes de chat. Escribe uno para comenzar.",
                text_color="gray"
            )
            lbl_no_chat.pack(pady=20)
            return

        for chat in messages:
            is_me = chat.get('from_user') == self.username

            msg_frame = customtkinter.CTkFrame(
                self.scrollable_chat,
                fg_color=("#e3f2fd" if is_me else "#f5f5f5")
            )
            msg_frame.pack(
                fill="x",
                padx=(50 if is_me else 5, 5 if is_me else 50),
                pady=3,
                anchor="e" if is_me else "w"
            )

            sender = "Tú" if is_me else chat.get('from_user', 'Admin')
            lbl_msg = customtkinter.CTkLabel(
                msg_frame,
                text=f"{sender}: {chat.get('message', '')}",
                anchor="w",
                wraplength=400
            )
            lbl_msg.pack(padx=10, pady=5)

            lbl_time = customtkinter.CTkLabel(
                msg_frame,
                text=chat.get('timestamp', '')[:16],
                font=customtkinter.CTkFont(size=10),
                text_color="gray",
                anchor="e"
            )
            lbl_time.pack(padx=10, pady=(0, 5), anchor="e")
    
    def _mostrar_ejercicios(self):
        """Muestra la vista de seguimiento de ejercicios."""
        self._switch_view("exercise")
        self._clear_content()
        
        lbl_placeholder = customtkinter.CTkLabel(
            self.content_frame,
            text="💪 Seguimiento de Ejercicios\n\nEsta funcionalidad estará disponible próximamente.\n\nPodrás registrar tus ejercicios en tiempo real,\nver tu historial y seguir tu progreso.",
            font=customtkinter.CTkFont(size=16),
            justify="center"
        )
        lbl_placeholder.pack(expand=True)
    
    def _mostrar_plan_entrenamiento(self):
        """Muestra la vista del plan de entrenamiento interactivo."""
        self._switch_view("training")
        self._clear_content()
        
        lbl_placeholder = customtkinter.CTkLabel(
            self.content_frame,
            text="🏋️ Plan de Entrenamiento Interactivo\n\nEsta funcionalidad estará disponible próximamente.\n\nPodrás ver tu calendario de entrenamientos,\nmarcar ejercicios completados y recibir notificaciones.",
            font=customtkinter.CTkFont(size=16),
            justify="center"
        )
        lbl_placeholder.pack(expand=True)
    
    def _mostrar_medidas(self):
        """Muestra la vista de medidas corporales."""
        self._switch_view("measurements")
        self._clear_content()
        
        lbl_placeholder = customtkinter.CTkLabel(
            self.content_frame,
            text="📏 Seguimiento de Medidas Corporales\n\nEsta funcionalidad estará disponible próximamente.\n\nPodrás registrar tu peso, medidas, porcentaje de grasa,\nmasa muscular y fotos de progreso.",
            font=customtkinter.CTkFont(size=16),
            justify="center"
        )
        lbl_placeholder.pack(expand=True)
    
    def _mostrar_nutricion(self):
        """Muestra la vista del plan nutricional."""
        self._switch_view("nutrition")
        self._clear_content()
        
        lbl_placeholder = customtkinter.CTkLabel(
            self.content_frame,
            text="🍎 Plan Nutricional Personalizado\n\nEsta funcionalidad estará disponible próximamente.\n\nPodrás ver tu plan de alimentación, recetas,\nlista de compras y registrar tu ingesta de agua.",
            font=customtkinter.CTkFont(size=16),
            justify="center"
        )
        lbl_placeholder.pack(expand=True)
    
    def _mostrar_dashboard(self):
        """Muestra el dashboard personal con estadísticas."""
        self._switch_view("dashboard")
        self._clear_content()
        
        lbl_placeholder = customtkinter.CTkLabel(
            self.content_frame,
            text="📊 Dashboard Personal\n\nEsta funcionalidad estará disponible próximamente.\n\nPodrás ver resúmenes de entrenamientos, calorías quemadas,\ntu racha de días consecutivos y gráficos de progreso.",
            font=customtkinter.CTkFont(size=16),
            justify="center"
        )
        lbl_placeholder.pack(expand=True)
