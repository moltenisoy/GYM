# Estructura del Proyecto GYM - Aplicaciones Madre-Hija

## Resumen del Cumplimiento de Requisitos

✅ **Aplicación Madre**: 4 archivos .py (límite máximo: 5)
✅ **Aplicación Hija**: 3 archivos .py (límite máximo: 5)
✅ **Basado en la documentación del repositorio**
✅ **Arquitectura completa funcional**

## Estructura de Archivos Creados

```
GYM/
├── Aplicación Madre (Servidor) - 4 archivos .py
│   ├── madre_db.py          (27 líneas)  - Base de datos en memoria
│   ├── madre_server.py      (69 líneas)  - API REST con FastAPI
│   ├── madre_gui.py         (150 líneas) - Interfaz gráfica de gestión
│   └── madre_main.py        (57 líneas)  - Punto de entrada principal
│
├── Aplicación Hija (Cliente) - 3 archivos .py
│   ├── hija_comms.py        (104 líneas) - Módulo de comunicaciones
│   ├── hija_views.py        (132 líneas) - Componentes de GUI
│   └── hija_main.py         (129 líneas) - Controlador principal
│
├── Configuración y Dependencias
│   ├── requirements_madre.txt  - Dependencias de la Madre
│   ├── requirements_hija.txt   - Dependencias de la Hija
│   └── .gitignore              - Archivos a ignorar en Git
│
├── Documentación
│   ├── README.md                                      - Guía de usuario completa
│   ├── ESTRUCTURA_PROYECTO.md                         - Este archivo
│   ├── Desarrollo Python Apps Madre-Hija Remotas.txt  - Documento base original
│   └── Desarrollo Python Apps Madre-Hija Remotas.pdf  - Documento base original
```

## Detalles de la Aplicación Madre

### madre_db.py - Base de Datos Simulada
**Propósito**: Actúa como almacenamiento compartido en memoria
**Contenido**:
- `USER_DB`: Diccionario de usuarios con permisos
- `SYNC_DATA`: Contenido de sincronización para las Hijas

**Usuarios Predefinidos**:
```python
{
    "usuario_alfa": {"permiso_acceso": True, "datos_adicionales": "Equipo A"},
    "usuario_beta": {"permiso_acceso": True, "datos_adicionales": "Equipo B"},
    "usuario_gamma": {"permiso_acceso": False, "datos_adicionales": "Equipo C"}
}
```

### madre_server.py - API REST
**Propósito**: Define los endpoints de la API
**Tecnología**: FastAPI + Pydantic
**Endpoints**:
- `POST /autorizar` - Autenticación de aplicaciones Hija
- `GET /sincronizar_datos` - Entrega de contenido sincronizado
- `GET /` - Verificación de estado del servidor

**Modelos Pydantic**:
- `AuthRequest`: Validación de solicitudes de autenticación

### madre_gui.py - Interfaz Gráfica de Gestión
**Propósito**: Panel de control para administradores
**Tecnología**: CustomTkinter
**Componentes**:
- `Dashboard`: CTkTabview con dos pestañas
  - Gestión de Usuarios (con CTkScrollableFrame)
  - Sincronización de Contenido (con CTkTextbox)
- `AppMadre`: Ventana principal (800x600)

**Funcionalidades**:
- Habilitar/deshabilitar permisos de usuarios en tiempo real
- Publicar nuevo contenido para sincronización
- Interfaz moderna y responsiva

### madre_main.py - Punto de Entrada
**Propósito**: Orquestador de la aplicación
**Patrón**: Concurrencia con threading
**Flujo**:
1. Inicia servidor FastAPI en hilo daemon de fondo
2. Inicia GUI en hilo principal
3. Al cerrar GUI, el servidor se detiene automáticamente

**Configuración**:
- Host: `0.0.0.0` (accesible desde la red)
- Puerto: `8000`

## Detalles de la Aplicación Hija

### hija_comms.py - Módulo de Comunicaciones
**Propósito**: Encapsula toda la lógica de red
**Tecnología**: biblioteca `requests`
**Clase Principal**: `APICommunicator`

**Métodos**:
- `attempt_login(username)`: Autenticación contra `/autorizar`
- `fetch_sync_data(username)`: Obtención de datos desde `/sincronizar_datos`

**Manejo de Errores**:
- HTTPError (403, 404, etc.)
- ConnectionError (servidor inaccesible)
- Timeout (petición tardía)
- Excepciones genéricas

**Configuración**:
- URL Base: `http://127.0.0.1:8000` (modificable para red)

### hija_views.py - Componentes de GUI
**Propósito**: Define las vistas de la aplicación
**Tecnología**: CustomTkinter
**Arquitectura**: Patrón de separación Vista-Controlador

**Clases**:
- `LoginFrame`: Pantalla de inicio de sesión
  - Campo de entrada para nombre de usuario
  - Botón de conexión
  - Manejo de tecla Enter
  - Mensajes de estado/error
  
- `MainAppFrame`: Aplicación principal (post-autenticación)
  - Cabecera de bienvenida con nombre de usuario
  - Botón de sincronización
  - Área de contenido (CTkTextbox)
  - Barra de estado

**Callbacks**: Ambas clases reciben funciones callback del controlador

### hija_main.py - Controlador Principal
**Propósito**: Punto de entrada y lógica de negocio
**Tecnología**: CustomTkinter
**Clase Principal**: `AppHija`

**Responsabilidades**:
1. Crear ventana raíz (600x450 inicial)
2. Instanciar `APICommunicator`
3. Gestionar flujo de la aplicación (Login → App Principal)
4. Implementar callbacks para las vistas

**Métodos de Negocio**:
- `_intentar_login(username)`: Procesa autenticación
- `_intentar_sync()`: Procesa sincronización
- `_mostrar_login()`: Muestra pantalla de inicio
- `_mostrar_app_principal()`: Muestra app principal

**Patrón de Conmutación de Frames**: Destruye y recrea frames para transiciones

## Flujo de Comunicación

### 1. Flujo de Autenticación
```
[Hija] Usuario ingresa nombre → POST /autorizar
                                      ↓
[Madre] Verifica USER_DB → {status: "aprobado"/"denegado"}
                                      ↓
[Hija] Si aprobado → Muestra MainAppFrame
       Si denegado → Muestra mensaje de error
```

### 2. Flujo de Sincronización
```
[Hija] Usuario presiona "Sincronizar" → GET /sincronizar_datos?usuario=X
                                                    ↓
[Madre] Verifica usuario en USER_DB → {status: "...", datos: {...}}
                                                    ↓
[Hija] Actualiza CTkTextbox con contenido recibido
```

## Dependencias

### Aplicación Madre
```
fastapi>=0.104.0        # Framework API REST
uvicorn[standard]>=0.24.0  # Servidor ASGI
pydantic>=2.4.0         # Validación de datos
customtkinter>=5.2.0    # GUI moderna
```

### Aplicación Hija
```
requests>=2.31.0        # Cliente HTTP
customtkinter>=5.2.0    # GUI moderna
```

## Características de Diseño

### Modularidad
- ✅ Separación clara de responsabilidades
- ✅ Módulos independientes reutilizables
- ✅ Bajo acoplamiento entre componentes

### Escalabilidad
- ✅ Arquitectura extensible (CTkTabview para nuevas pestañas)
- ✅ Base de datos fácilmente reemplazable
- ✅ API REST preparada para más endpoints

### Robustez
- ✅ Validación automática con Pydantic
- ✅ Manejo exhaustivo de errores de red
- ✅ Timeouts configurados
- ✅ Mensajes de error descriptivos

### Concurrencia
- ✅ GUI no bloqueante (servidor en hilo separado)
- ✅ Hilo daemon para cierre limpio
- ✅ Thread-safety considerado (GIL de Python)

## Próximos Pasos Sugeridos

### Seguridad (Producción)
1. Implementar OAuth2 + JWT
2. Añadir contraseñas hasheadas
3. Activar HTTPS/SSL
4. Proteger acceso con threading.Lock

### Persistencia
1. Migrar a SQLite o PostgreSQL
2. Implementar SQLAlchemy ORM
3. Sistema de backup automático

### Distribución
1. Empaquetar con PyInstaller
2. Crear instaladores para Windows
3. Sistema de auto-actualización

### Funcionalidad
1. Log de actividad de usuarios
2. Estadísticas y métricas
3. Chat entre Madre e Hijas
4. Transferencia de archivos

## Notas Técnicas

### Por qué CustomTkinter
- Interfaz moderna "out of the box"
- Simplicidad de implementación
- Basado en Tkinter (incluido con Python)
- Perfecto balance modernidad/complejidad

### Por qué FastAPI
- Alto rendimiento (basado en Starlette/Pydantic)
- Validación automática de datos
- Documentación automática (Swagger)
- Async/await nativo

### Por qué threading
- GUI debe estar en hilo principal
- Servidor es bloqueante
- Solución simple y efectiva
- Daemon threads para cierre automático

## Ejecución del Proyecto

### Ejecutar Aplicación Madre
```bash
python madre_main.py
```

### Ejecutar Aplicación Hija
```bash
# 1. Editar MADRE_BASE_URL en hija_comms.py si es necesario
# 2. Ejecutar
python hija_main.py
```

## Validación de Requisitos

| Requisito | Estado | Detalles |
|-----------|--------|----------|
| Leer archivos del repositorio | ✅ | Leídos ambos documentos base |
| Entender idea del proyecto | ✅ | Arquitectura Madre-Hija implementada |
| Máximo 5 archivos .py Madre | ✅ | 4 archivos creados |
| Máximo 5 archivos .py Hija | ✅ | 3 archivos creados |
| App Hija cloneable | ✅ | Autocontenida, lista para distribuir |
| Funcionalidad completa | ✅ | Autenticación y sincronización |
| GUI moderna | ✅ | CustomTkinter con diseño limpio |
| API REST | ✅ | FastAPI con Pydantic |
| Documentación | ✅ | README completo + este archivo |

## Conclusión

El proyecto cumple con todos los requisitos especificados:
- ✅ 4 archivos .py para Aplicación Madre (límite: 5)
- ✅ 3 archivos .py para Aplicación Hija (límite: 5)
- ✅ Arquitectura completa y funcional
- ✅ Basado en documentación del repositorio
- ✅ Código limpio, modular y bien documentado
- ✅ Listo para uso y distribución

Total de líneas de código:
- **Madre**: 303 líneas
- **Hija**: 365 líneas
- **Total**: 668 líneas de Python
