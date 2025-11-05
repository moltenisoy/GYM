# madre_gui.py
#
# Define la Interfaz Gráfica de Usuario (GUI) para la Aplicación Madre
# usando CustomTkinter.
# Esta GUI permite al administrador gestionar los permisos de usuario y
# actualizar el contenido de sincronización.

import customtkinter
from typing import Dict, Any

# Importar la base de datos compartida
import madre_db

# Configuración inicial de apariencia (opcional, pero recomendada)
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

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
        
        # Poblar cada pestaña
        self._crear_pestaña_usuarios()
        self._crear_pestaña_sincronizacion()

    def _crear_pestaña_usuarios(self):
        """Puebla la pestaña 'Gestión de Usuarios'."""
        tab_usuarios = self.tab("Gestión de Usuarios")
        tab_usuarios.grid_columnconfigure(0, weight=1)
        
        lbl_titulo = customtkinter.CTkLabel(tab_usuarios, text="Gestión de Permisos de Usuarios", font=customtkinter.CTkFont(size=16, weight="bold"))
        lbl_titulo.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")
        
        lbl_desc = customtkinter.CTkLabel(tab_usuarios, text="Habilite o deshabilite el acceso para las Aplicaciones Hijas.")
        lbl_desc.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")

        # El CTkScrollableFrame es esencial para listas largas de usuarios.
        self.scrollable_frame_usuarios = customtkinter.CTkScrollableFrame(tab_usuarios, height=300)
        self.scrollable_frame_usuarios.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.scrollable_frame_usuarios.grid_columnconfigure(0, weight=1)

        btn_actualizar = customtkinter.CTkButton(tab_usuarios, text="Actualizar Lista", command=self._actualizar_vista_usuarios)
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
            
        # Volver a poblar con datos frescos de madre_db.USER_DB
        for i, (username, data) in enumerate(madre_db.USER_DB.items()):
            permiso_actual = data.get("permiso_acceso", False)
            
            # Crear un frame para cada fila de usuario
            user_frame = customtkinter.CTkFrame(self.scrollable_frame_usuarios)
            user_frame.grid(row=i, column=0, padx=10, pady=5, sticky="ew")
            user_frame.grid_columnconfigure(1, weight=1)
            
            lbl_user = customtkinter.CTkLabel(user_frame, text=username, font=customtkinter.CTkFont(weight="bold"))
            lbl_user.grid(row=0, column=0, padx=10, pady=5, sticky="w")
            
            lbl_datos = customtkinter.CTkLabel(user_frame, text=f"({data.get('datos_adicionales', 'N/A')})", text_color="gray")
            lbl_datos.grid(row=0, column=1, padx=10, pady=5, sticky="w")
            
            # El 'command' del switch modifica directamente la base de datos en memoria.
            # Usamos una lambda para pasar el 'username' al método de conmutación.
            switch_permiso = customtkinter.CTkSwitch(
                user_frame, 
                text="Acceso Habilitado",
                command=lambda u=username: self._conmutar_permiso(u)
            )
            if permiso_actual:
                switch_permiso.select()  # Marcar el switch si el permiso es True
                
            switch_permiso.grid(row=0, column=2, padx=10, pady=5)

    def _conmutar_permiso(self, username: str):
        """
        Invierte el estado de 'permiso_acceso' para un usuario en madre_db.
        """
        if username in madre_db.USER_DB:
            nuevo_estado = not madre_db.USER_DB[username].get("permiso_acceso", False)
            madre_db.USER_DB[username]["permiso_acceso"] = nuevo_estado
            print(f"Permiso para '{username}' actualizado a: {nuevo_estado}")
            # Se podría añadir un refresco automático de la lista si se desea
            # self._actualizar_vista_usuarios()
            
    def _crear_pestaña_sincronizacion(self):
        """Puebla la pestaña 'Sincronización de Contenido'."""
        tab_sync = self.tab("Sincronización de Contenido")
        tab_sync.grid_columnconfigure(0, weight=1)
        tab_sync.grid_rowconfigure(1, weight=1)
        
        lbl_titulo = customtkinter.CTkLabel(tab_sync, text="Publicar Contenido para Sincronización", font=customtkinter.CTkFont(size=16, weight="bold"))
        lbl_titulo.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")

        self.textbox_sync = customtkinter.CTkTextbox(tab_sync)
        self.textbox_sync.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.textbox_sync.insert("1.0", madre_db.SYNC_DATA.get("contenido", ""))
        
        btn_publicar = customtkinter.CTkButton(tab_sync, text="Publicar Nuevo Contenido", command=self._publicar_sync_data)
        btn_publicar.grid(row=2, column=0, padx=20, pady=10)

    def _publicar_sync_data(self):
        """
        Toma el texto del CTkTextbox y lo guarda en madre_db.SYNC_DATA.
        """
        nuevo_contenido = self.textbox_sync.get("1.0", "end-1c")  # Obtener todo el texto
        madre_db.SYNC_DATA["contenido"] = nuevo_contenido
        # Actualizar la versión (lógica simple de ejemplo)
        try:
            version_actual = float(madre_db.SYNC_DATA["metadatos_version"])
            nueva_version = version_actual + 0.1
            madre_db.SYNC_DATA["metadatos_version"] = f"{nueva_version:.1f}"
        except ValueError:
            madre_db.SYNC_DATA["metadatos_version"] = "1.0"
            
        print(f"Nuevos datos de sincronización publicados. Versión: {madre_db.SYNC_DATA['metadatos_version']}")
        

class AppMadre(customtkinter.CTk):
    """
    Clase principal de la aplicación GUI.
    Contiene la ventana raíz y el Dashboard.
    """
    def __init__(self):
        super().__init__()
        
        self.title("Aplicación Madre - Panel de Control")
        self.geometry("800x600")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.dashboard = Dashboard(self, width=780, height=580)
        self.dashboard.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
