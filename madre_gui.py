# madre_gui.py
#
# Define la Interfaz Gráfica de Usuario (GUI) para la Aplicación Madre
# (Panel de Administración del Gimnasio) usando CustomTkinter.
# Esta GUI permite al personal administrativo gestionar socios, membresías,
# permisos de acceso y contenido de sincronización.

import customtkinter
import requests

# Importar la base de datos
import madre_db

# Configuración inicial de apariencia
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")


class UserDetailWindow(customtkinter.CTkToplevel):
    """
    Ventana emergente para ver detalles individuales de un usuario.
    """

    def __init__(self, master, username: str, **kwargs):
        super().__init__(master, **kwargs)

        self.username = username
        self.title(f"Detalles del Socio: {username}")
        self.geometry("700x600")

        # Obtener datos del usuario
        user = madre_db.get_user(username)
        if not user:
            self.destroy()
            return

        user_id = user['id']

        # Frame principal con scroll
        main_frame = customtkinter.CTkScrollableFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Información personal
        lbl_titulo = customtkinter.CTkLabel(
            main_frame,
            text="Información Personal",
            font=customtkinter.CTkFont(size=18, weight="bold")
        )
        lbl_titulo.pack(pady=(10, 5), anchor="w")

        info_frame = customtkinter.CTkFrame(main_frame)
        info_frame.pack(fill="x", padx=5, pady=5)

        info_data = [
            ("Usuario:", user['username']),
            ("Nombre Completo:", user['nombre_completo']),
            ("Email:", user['email'] or "N/A"),
            ("Teléfono:", user['telefono'] or "N/A"),
            ("Equipo:", user['equipo'] or "N/A"),
            ("Fecha Registro:", user['fecha_registro']),
            ("Última Sync:", user['last_sync'] or "Nunca"),
            ("Permiso Acceso:", "✓ Habilitado" if user['permiso_acceso'] else "✗ Deshabilitado")
        ]

        for i, (label, value) in enumerate(info_data):
            lbl = customtkinter.CTkLabel(info_frame, text=label, font=customtkinter.CTkFont(weight="bold"))
            lbl.grid(row=i, column=0, padx=10, pady=3, sticky="w")
            val = customtkinter.CTkLabel(info_frame, text=str(value))
            val.grid(row=i, column=1, padx=10, pady=3, sticky="w")

        # Cronograma de entrenamiento
        lbl_schedule = customtkinter.CTkLabel(
            main_frame,
            text="Cronograma de Entrenamiento",
            font=customtkinter.CTkFont(size=16, weight="bold")
        )
        lbl_schedule.pack(pady=(15, 5), anchor="w")

        schedule = madre_db.get_training_schedule(user_id)

        schedule_frame = customtkinter.CTkFrame(main_frame)
        schedule_frame.pack(fill="both", expand=True, padx=5, pady=5)

        if schedule:
            schedule_text = customtkinter.CTkTextbox(schedule_frame, height=200)
            schedule_text.pack(fill="both", expand=True, padx=5, pady=5)

            # Formatear cronograma
            content = f"Mes: {schedule['mes']} {schedule['ano']}\n"
            content += f"Objetivo: {schedule['schedule_data'].get('objetivo', 'N/A')}\n"
            content += f"Notas: {schedule['schedule_data'].get('notas', 'N/A')}\n\n"

            dias = schedule['schedule_data'].get('dias', {})
            for dia, info in dias.items():
                content += f"=== {dia.upper()} ===\n"
                content += f"Ejercicios: {', '.join(info.get('ejercicios', []))}\n"
                content += f"Descripción: {info.get('descripcion', 'N/A')}\n"
                content += f"Duración: {info.get('duracion_minutos', 0)} min\n\n"

            schedule_text.insert("1.0", content)
            schedule_text.configure(state="disabled")
        else:
            lbl_no_schedule = customtkinter.CTkLabel(schedule_frame, text="Sin cronograma asignado")
            lbl_no_schedule.pack(pady=10)

        # Galería de fotos
        lbl_gallery = customtkinter.CTkLabel(
            main_frame,
            text="Galería de Fotos",
            font=customtkinter.CTkFont(size=16, weight="bold")
        )
        lbl_gallery.pack(pady=(15, 5), anchor="w")

        gallery = madre_db.get_photo_gallery(user_id)

        gallery_frame = customtkinter.CTkFrame(main_frame)
        gallery_frame.pack(fill="x", padx=5, pady=5)

        if gallery:
            for i, photo in enumerate(gallery):
                photo_item = customtkinter.CTkFrame(gallery_frame)
                photo_item.pack(fill="x", padx=5, pady=2)

                lbl_photo = customtkinter.CTkLabel(
                    photo_item,
                    text=f"📷 {photo['photo_path'].split('/')[-1]}",
                    anchor="w"
                )
                lbl_photo.pack(side="left", padx=5, pady=3)

                if photo['descripcion']:
                    lbl_desc = customtkinter.CTkLabel(
                        photo_item,
                        text=f"- {photo['descripcion']}",
                        text_color="gray"
                    )
                    lbl_desc.pack(side="left", padx=5, pady=3)
        else:
            lbl_no_gallery = customtkinter.CTkLabel(gallery_frame, text="Sin fotos en la galería")
            lbl_no_gallery.pack(pady=10)

        # Botón cerrar
        btn_close = customtkinter.CTkButton(
            main_frame,
            text="Cerrar",
            command=self.destroy
        )
        btn_close.pack(pady=10)


class MessageDetailWindow(customtkinter.CTkToplevel):
    """
    Ventana emergente para ver detalles de un mensaje.
    """

    def __init__(self, master, message: dict, **kwargs):
        super().__init__(master, **kwargs)

        self.message = message
        self.title(f"Mensaje de {message.get('from_user', 'Desconocido')}")
        self.geometry("700x500")

        # Frame principal con scroll
        main_frame = customtkinter.CTkScrollableFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Información del mensaje
        lbl_from = customtkinter.CTkLabel(
            main_frame,
            text=f"De: {message.get('from_user', 'Desconocido')}",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        lbl_from.pack(fill="x", pady=3)

        lbl_to = customtkinter.CTkLabel(
            main_frame,
            text=f"Para: {message.get('to_user', 'Desconocido')}",
            anchor="w"
        )
        lbl_to.pack(fill="x", pady=3)

        lbl_date = customtkinter.CTkLabel(
            main_frame,
            text=f"Fecha: {message.get('sent_date', 'N/A')}",
            anchor="w"
        )
        lbl_date.pack(fill="x", pady=3)

        lbl_subject = customtkinter.CTkLabel(
            main_frame,
            text=f"Asunto: {message.get('subject', 'Sin asunto')}",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        lbl_subject.pack(fill="x", pady=10)

        # Cuerpo del mensaje
        textbox = customtkinter.CTkTextbox(main_frame, height=250)
        textbox.pack(fill="both", expand=True, pady=10)
        textbox.insert("1.0", message.get('body', ''))
        textbox.configure(state="disabled")

        # Adjuntos
        attachments = madre_db.get_message_attachments(message['id'])
        if attachments:
            lbl_attachments = customtkinter.CTkLabel(
                main_frame,
                text=f"📎 Adjuntos ({len(attachments)}):",
                font=customtkinter.CTkFont(weight="bold"),
                anchor="w"
            )
            lbl_attachments.pack(fill="x", pady=5)

            for att in attachments:
                att_frame = customtkinter.CTkFrame(main_frame)
                att_frame.pack(fill="x", padx=5, pady=2)

                lbl_att = customtkinter.CTkLabel(
                    att_frame,
                    text=f"📄 {att['filename']} ({att['file_size']} bytes)",
                    anchor="w"
                )
                lbl_att.pack(side="left", padx=10, pady=5)

        # Botón cerrar
        btn_close = customtkinter.CTkButton(
            main_frame,
            text="Cerrar",
            command=self.destroy
        )
        btn_close.pack(pady=10)


class Dashboard(customtkinter.CTkTabview):
    """
    Panel de control principal, implementado como un CTkTabview.
    Crea pestañas separadas para la gestión de usuarios y la sincronización.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Crear y añadir pestañas
        self.add("Gestión de Usuarios")
        self.add("Sincronización de Contenido")
        self.add("Sincronización Masiva")
        self.add("Buzón de Mensajes")

        # Poblar cada pestaña
        self._crear_pestaña_usuarios()
        self._crear_pestaña_sincronizacion()
        self._crear_pestaña_sync_masiva()
        self._crear_pestaña_mensajes()

    def _crear_pestaña_usuarios(self):
        """Puebla la pestaña 'Gestión de Usuarios'."""
        tab_usuarios = self.tab("Gestión de Usuarios")
        tab_usuarios.grid_columnconfigure(0, weight=1)

        lbl_titulo = customtkinter.CTkLabel(
            tab_usuarios,
            text="Gestión de Permisos de Usuarios",
            font=customtkinter.CTkFont(
                size=16,
                weight="bold"))
        lbl_titulo.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")

        lbl_desc = customtkinter.CTkLabel(tab_usuarios,
                                          text="Habilite o deshabilite el acceso para las Aplicaciones Hijas.")
        lbl_desc.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")

        # El CTkScrollableFrame es esencial para listas largas de usuarios.
        self.scrollable_frame_usuarios = customtkinter.CTkScrollableFrame(tab_usuarios, height=300)
        self.scrollable_frame_usuarios.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.scrollable_frame_usuarios.grid_columnconfigure(0, weight=1)

        btn_actualizar = customtkinter.CTkButton(
            tab_usuarios,
            text="Actualizar Lista",
            command=self._actualizar_vista_usuarios)
        btn_actualizar.grid(row=3, column=0, padx=20, pady=10)

        # Poblar la lista por primera vez
        self._actualizar_vista_usuarios()

    def _actualizar_vista_usuarios(self):
        """
        Limpia y vuelve a poblar el frame desplazable con los usuarios de madre_db.
        """
        # Limpiar widgets antiguos
        for widget in self.scrollable_frame_usuarios.winfo_children():
            widget.destroy()

        # Volver a poblar con datos frescos de la base de datos
        usuarios = madre_db.get_all_users()

        for i, user in enumerate(usuarios):
            username = user['username']
            permiso_actual = bool(user['permiso_acceso'])

            # Crear un frame para cada fila de usuario
            user_frame = customtkinter.CTkFrame(self.scrollable_frame_usuarios)
            user_frame.grid(row=i, column=0, padx=10, pady=5, sticky="ew")
            user_frame.grid_columnconfigure(1, weight=1)

            lbl_user = customtkinter.CTkLabel(
                user_frame,
                text=username,
                font=customtkinter.CTkFont(weight="bold")
            )
            lbl_user.grid(row=0, column=0, padx=10, pady=5, sticky="w")

            nombre_completo = user.get('nombre_completo', 'N/A')
            equipo = user.get('equipo', 'N/A')
            lbl_datos = customtkinter.CTkLabel(
                user_frame,
                text=f"{nombre_completo} - {equipo}",
                text_color="gray"
            )
            lbl_datos.grid(row=0, column=1, padx=10, pady=5, sticky="w")

            # Botón para ver detalles
            btn_detalles = customtkinter.CTkButton(
                user_frame,
                text="Ver Detalles",
                width=100,
                command=lambda u=username: self._ver_detalles_usuario(u)
            )
            btn_detalles.grid(row=0, column=2, padx=5, pady=5)

            # Switch de permisos
            switch_permiso = customtkinter.CTkSwitch(
                user_frame,
                text="Acceso Habilitado",
                command=lambda u=username: self._conmutar_permiso(u)
            )
            if permiso_actual:
                switch_permiso.select()

            switch_permiso.grid(row=0, column=3, padx=10, pady=5)

    def _ver_detalles_usuario(self, username: str):
        """
        Abre una ventana con los detalles completos del usuario.
        """
        UserDetailWindow(self, username)

    def _conmutar_permiso(self, username: str):
        """
        Invierte el estado de 'permiso_acceso' para un usuario en madre_db.
        """
        user = madre_db.get_user(username)
        if user:
            nuevo_estado = not bool(user.get("permiso_acceso", False))
            madre_db.update_user_permission(username, nuevo_estado)
            print(f"Permiso para '{username}' actualizado a: {nuevo_estado}")

            # Notificar al servidor (si está corriendo localmente)
            try:
                requests.post(
                    "http://localhost:8000/actualizar_permiso",
                    json={"username": username, "permiso_acceso": nuevo_estado},
                    timeout=1
                )
            except BaseException:
                pass  # El servidor actualizará desde la BD compartida

    def _crear_pestaña_sincronizacion(self):
        """Puebla la pestaña 'Sincronización de Contenido'."""
        tab_sync = self.tab("Sincronización de Contenido")
        tab_sync.grid_columnconfigure(0, weight=1)
        tab_sync.grid_rowconfigure(1, weight=1)

        lbl_titulo = customtkinter.CTkLabel(
            tab_sync,
            text="Publicar Contenido para Sincronización",
            font=customtkinter.CTkFont(size=16, weight="bold")
        )
        lbl_titulo.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")

        self.textbox_sync = customtkinter.CTkTextbox(tab_sync)
        self.textbox_sync.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        # Cargar contenido actual
        sync_data = madre_db.get_sync_data()
        self.textbox_sync.insert("1.0", sync_data.get("contenido", ""))

        # Label de versión
        self.lbl_version = customtkinter.CTkLabel(
            tab_sync,
            text=f"Versión actual: {sync_data.get('metadatos_version', '1.0.0')}",
            text_color="gray"
        )
        self.lbl_version.grid(row=2, column=0, padx=20, pady=5, sticky="w")

        btn_publicar = customtkinter.CTkButton(
            tab_sync,
            text="Publicar Nuevo Contenido",
            command=self._publicar_sync_data
        )
        btn_publicar.grid(row=3, column=0, padx=20, pady=10)

    def _crear_pestaña_sync_masiva(self):
        """Puebla la pestaña 'Sincronización Masiva'."""
        tab_masiva = self.tab("Sincronización Masiva")
        tab_masiva.grid_columnconfigure(0, weight=1)

        lbl_titulo = customtkinter.CTkLabel(
            tab_masiva,
            text="Actualización Masiva de Usuarios",
            font=customtkinter.CTkFont(size=16, weight="bold")
        )
        lbl_titulo.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")

        lbl_desc = customtkinter.CTkLabel(
            tab_masiva,
            text="Forzar sincronización para múltiples usuarios simultáneamente"
        )
        lbl_desc.grid(row=1, column=0, padx=20, pady=5, sticky="w")

        # Lista de usuarios con checkboxes
        self.scrollable_frame_masiva = customtkinter.CTkScrollableFrame(tab_masiva, height=300)
        self.scrollable_frame_masiva.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")

        # Botones de acción
        btn_frame = customtkinter.CTkFrame(tab_masiva, fg_color="transparent")
        btn_frame.grid(row=3, column=0, padx=20, pady=10)

        btn_seleccionar_todos = customtkinter.CTkButton(
            btn_frame,
            text="Seleccionar Todos",
            command=self._seleccionar_todos_usuarios
        )
        btn_seleccionar_todos.pack(side="left", padx=5)

        btn_deseleccionar = customtkinter.CTkButton(
            btn_frame,
            text="Deseleccionar Todos",
            command=self._deseleccionar_todos_usuarios
        )
        btn_deseleccionar.pack(side="left", padx=5)

        btn_sincronizar = customtkinter.CTkButton(
            btn_frame,
            text="Sincronizar Seleccionados",
            command=self._sincronizar_usuarios_masiva,
            fg_color="green"
        )
        btn_sincronizar.pack(side="left", padx=5)

        # Status label
        self.lbl_status_masiva = customtkinter.CTkLabel(
            tab_masiva,
            text="",
            text_color="gray"
        )
        self.lbl_status_masiva.grid(row=4, column=0, padx=20, pady=5)

        # Poblar lista de usuarios
        self._actualizar_lista_sync_masiva()

    def _actualizar_lista_sync_masiva(self):
        """Actualiza la lista de usuarios para sincronización masiva."""
        for widget in self.scrollable_frame_masiva.winfo_children():
            widget.destroy()

        self.checkboxes_usuarios = {}
        usuarios = madre_db.get_all_users()

        for i, user in enumerate(usuarios):
            username = user['username']

            checkbox = customtkinter.CTkCheckBox(
                self.scrollable_frame_masiva,
                text=f"{username} ({user.get('nombre_completo', 'N/A')})"
            )
            checkbox.grid(row=i, column=0, padx=10, pady=5, sticky="w")

            self.checkboxes_usuarios[username] = checkbox

    def _seleccionar_todos_usuarios(self):
        """Selecciona todos los checkboxes de usuarios."""
        for checkbox in self.checkboxes_usuarios.values():
            checkbox.select()

    def _deseleccionar_todos_usuarios(self):
        """Deselecciona todos los checkboxes de usuarios."""
        for checkbox in self.checkboxes_usuarios.values():
            checkbox.deselect()

    def _sincronizar_usuarios_masiva(self):
        """Realiza sincronización masiva de usuarios seleccionados."""
        usuarios_seleccionados = [
            username for username, checkbox in self.checkboxes_usuarios.items()
            if checkbox.get()
        ]

        if not usuarios_seleccionados:
            self.lbl_status_masiva.configure(
                text="No hay usuarios seleccionados",
                text_color="orange"
            )
            return

        # Actualizar timestamp de sincronización para cada usuario
        exitosos = 0
        for username in usuarios_seleccionados:
            if madre_db.update_user_sync(username):
                exitosos += 1

        # Notificar al servidor si está disponible
        try:
            response = requests.post(
                "http://localhost:8000/sincronizar_masiva",
                json=usuarios_seleccionados,
                timeout=2
            )
            if response.status_code == 200:
                self.lbl_status_masiva.configure(
                    text=f"✓ Sincronización masiva exitosa: {exitosos}/{len(usuarios_seleccionados)} usuarios",
                    text_color="green"
                )
            else:
                self.lbl_status_masiva.configure(
                    text=f"Advertencia: Actualizado localmente ({exitosos} usuarios), servidor no respondió",
                    text_color="orange"
                )
        except BaseException:
            self.lbl_status_masiva.configure(
                text=f"✓ Actualizado localmente: {exitosos} usuarios (servidor no disponible)",
                text_color="green"
            )

        print(f"Sincronización masiva: {exitosos} usuarios actualizados")

    def _publicar_sync_data(self):
        """
        Toma el texto del CTkTextbox y lo guarda en la base de datos.
        """
        nuevo_contenido = self.textbox_sync.get("1.0", "end-1c")

        # Actualizar en la base de datos (auto-incrementa versión)
        madre_db.update_sync_data(nuevo_contenido)

        # Obtener nueva versión
        sync_data = madre_db.get_sync_data()
        nueva_version = sync_data.get("metadatos_version", "1.0.0")

        # Actualizar label de versión
        self.lbl_version.configure(text=f"Versión actual: {nueva_version}")

        print(f"Nuevos datos de sincronización publicados. Versión: {nueva_version}")

    def _crear_pestaña_mensajes(self):
        """Puebla la pestaña 'Buzón de Mensajes'."""
        tab_mensajes = self.tab("Buzón de Mensajes")
        tab_mensajes.grid_columnconfigure(0, weight=1)
        tab_mensajes.grid_rowconfigure(1, weight=1)

        # Header con contador de no leídos
        header_frame = customtkinter.CTkFrame(tab_mensajes)
        header_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        lbl_titulo = customtkinter.CTkLabel(
            header_frame,
            text="✉️ Buzón de Mensajes",
            font=customtkinter.CTkFont(size=16, weight="bold")
        )
        lbl_titulo.pack(side="left", padx=10)

        self.lbl_unread_count = customtkinter.CTkLabel(
            header_frame,
            text="📬 0 no leídos",
            font=customtkinter.CTkFont(size=14),
            text_color="orange"
        )
        self.lbl_unread_count.pack(side="left", padx=20)

        btn_actualizar = customtkinter.CTkButton(
            header_frame,
            text="🔄 Actualizar",
            command=self._actualizar_mensajes,
            width=120
        )
        btn_actualizar.pack(side="right", padx=10)

        # Lista de mensajes
        self.scrollable_mensajes = customtkinter.CTkScrollableFrame(tab_mensajes)
        self.scrollable_mensajes.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        # Cargar mensajes inicial
        self._actualizar_mensajes()

    def _actualizar_mensajes(self):
        """Actualiza la lista de mensajes del admin."""
        for widget in self.scrollable_mensajes.winfo_children():
            widget.destroy()

        # Obtener mensajes para "admin"
        messages = madre_db.get_user_messages("admin", include_read=True)
        unread_count = madre_db.count_unread_messages("admin")

        # Actualizar contador
        self.lbl_unread_count.configure(text=f"📬 {unread_count} no leídos")

        if not messages:
            lbl_no_msg = customtkinter.CTkLabel(
                self.scrollable_mensajes,
                text="No hay mensajes en el buzón"
            )
            lbl_no_msg.pack(pady=20)
            return

        for msg in messages:
            msg_frame = customtkinter.CTkFrame(self.scrollable_mensajes)
            msg_frame.grid_columnconfigure(1, weight=1)
            msg_frame.pack(fill="x", padx=5, pady=5)

            # Indicador de leído/no leído
            indicator = "●" if not msg.get('is_read') else "○"
            color = "#2563eb" if not msg.get('is_read') else "gray"

            lbl_indicator = customtkinter.CTkLabel(
                msg_frame,
                text=indicator,
                text_color=color,
                width=20
            )
            lbl_indicator.grid(row=0, column=0, padx=5, pady=5)

            # Info del mensaje
            info_frame = customtkinter.CTkFrame(msg_frame, fg_color="transparent")
            info_frame.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

            lbl_from = customtkinter.CTkLabel(
                info_frame,
                text=f"De: {msg.get('from_user', 'Desconocido')} - {msg.get('subject', 'Sin asunto')}",
                font=customtkinter.CTkFont(weight="bold" if not msg.get('is_read') else "normal"),
                anchor="w"
            )
            lbl_from.pack(side="left", fill="x", expand=True)

            lbl_date = customtkinter.CTkLabel(
                info_frame,
                text=msg.get('sent_date', '')[:16],
                text_color="gray"
            )
            lbl_date.pack(side="right", padx=5)

            # Botones de acción
            btn_frame = customtkinter.CTkFrame(msg_frame, fg_color="transparent")
            btn_frame.grid(row=0, column=2, padx=5, pady=5)

            btn_ver = customtkinter.CTkButton(
                btn_frame,
                text="Ver",
                width=60,
                command=lambda m=msg: self._ver_mensaje(m)
            )
            btn_ver.pack(side="left", padx=2)

            btn_responder = customtkinter.CTkButton(
                btn_frame,
                text="Responder",
                width=80,
                command=lambda m=msg: self._responder_mensaje(m),
                fg_color="green"
            )
            btn_responder.pack(side="left", padx=2)

            btn_exportar = customtkinter.CTkButton(
                btn_frame,
                text="Exportar",
                width=80,
                command=lambda m=msg: self._exportar_mensaje(m),
                fg_color="orange"
            )
            btn_exportar.pack(side="left", padx=2)

            btn_eliminar = customtkinter.CTkButton(
                btn_frame,
                text="Eliminar",
                width=70,
                command=lambda m=msg: self._eliminar_mensaje(m),
                fg_color="red"
            )
            btn_eliminar.pack(side="left", padx=2)

    def _ver_mensaje(self, msg: dict):
        """Muestra los detalles de un mensaje en una ventana emergente."""
        # Marcar como leído
        madre_db.mark_message_read(msg['id'])

        # Crear ventana emergente
        dialog = MessageDetailWindow(self, msg)

        # Actualizar lista después de cerrar
        dialog.protocol("WM_DELETE_WINDOW", lambda: self._cerrar_mensaje_dialog(dialog))

    def _cerrar_mensaje_dialog(self, dialog):
        """Cierra el diálogo y actualiza la lista de mensajes."""
        dialog.destroy()
        self._actualizar_mensajes()

    def _responder_mensaje(self, msg: dict):
        """Abre un diálogo para responder un mensaje."""
        dialog = customtkinter.CTkToplevel(self)
        dialog.title(f"Responder a {msg.get('from_user', 'Desconocido')}")
        dialog.geometry("600x400")

        # Frame de contenido
        content_frame = customtkinter.CTkFrame(dialog)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(2, weight=1)

        lbl_to = customtkinter.CTkLabel(
            content_frame,
            text=f"Para: {msg.get('from_user', 'Desconocido')}",
            font=customtkinter.CTkFont(weight="bold")
        )
        lbl_to.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        entry_subject = customtkinter.CTkEntry(
            content_frame,
            placeholder_text="Asunto"
        )
        entry_subject.insert(0, f"Re: {msg.get('subject', '')}")
        entry_subject.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        textbox_body = customtkinter.CTkTextbox(content_frame)
        textbox_body.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

        btn_enviar = customtkinter.CTkButton(
            content_frame,
            text="Enviar Respuesta",
            command=lambda: self._enviar_respuesta(
                dialog,
                msg.get('from_user', ''),
                entry_subject.get(),
                textbox_body.get("1.0", "end-1c"),
                msg.get('id')
            ),
            fg_color="green"
        )
        btn_enviar.grid(row=3, column=0, padx=10, pady=10)

    def _enviar_respuesta(self, dialog, to_user, subject, body, parent_id):
        """Envía una respuesta a un mensaje."""
        if not to_user or not body.strip():
            return

        # Enviar mensaje
        madre_db.send_message("admin", to_user, subject, body, parent_id)

        dialog.destroy()
        self._actualizar_mensajes()

    def _exportar_mensaje(self, msg: dict):
        """Exporta un mensaje a archivo .txt."""
        import tkinter.filedialog as filedialog

        # Pedir ruta de archivo
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"mensaje_{msg['id']}.txt"
        )

        if filename:
            success = madre_db.export_message_to_txt(msg['id'], filename)
            if success:
                # Mostrar confirmación
                print(f"Mensaje exportado a: {filename}")

    def _eliminar_mensaje(self, msg: dict):
        """Elimina un mensaje."""
        # Confirmar eliminación (simple - en producción usar un diálogo)
        madre_db.delete_message(msg['id'])
        self._actualizar_mensajes()


class AppMadre(customtkinter.CTk):
    """
    Clase principal de la aplicación GUI.
    Contiene la ventana raíz y el Dashboard.
    """

    def __init__(self):
        super().__init__()

        self.title("Sistema de Gestión del Gimnasio - Panel Administrativo")
        self.geometry("800x600")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.dashboard = Dashboard(self, width=780, height=580)
        self.dashboard.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
