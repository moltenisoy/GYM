# Sistema de Gestión Madre-Hija en Python

Este proyecto implementa una arquitectura de red "Madre-Hijo" (Servidor-Cliente) con aplicaciones de escritorio GUI modernas para Windows utilizando Python.

## Descripción General

El sistema consta de dos aplicaciones principales:

### Aplicación Madre (Servidor)
Una aplicación híbrida que funciona como:
- **Panel de gestión de escritorio** con GUI moderna (CustomTkinter)
- **Servidor API REST** (FastAPI) para comunicación con las aplicaciones Hija

**Archivos:**
- `madre_db.py` - Base de datos en memoria (simulación)
- `madre_server.py` - Servidor API con FastAPI
- `madre_gui.py` - Interfaz gráfica de gestión
- `madre_main.py` - Punto de entrada principal

### Aplicación Hija (Cliente)
Una aplicación de escritorio que requiere autenticación contra el servidor Madre antes de desbloquear su funcionalidad.

**Archivos:**
- `hija_comms.py` - Módulo de comunicaciones con la API Madre
- `hija_views.py` - Componentes de la interfaz gráfica
- `hija_main.py` - Punto de entrada y controlador principal

## Requisitos del Sistema

- Python 3.8 o superior
- Windows (recomendado) o Linux/macOS
- Conexión de red entre equipos Madre e Hija

## Instalación

### 1. Instalar Python
Descarga e instala Python desde [python.org](https://www.python.org/downloads/)

### 2. Clonar o descargar el repositorio
```bash
git clone <url-del-repositorio>
cd GYM
```

### 3. Instalar dependencias

**Para la Aplicación Madre:**
```bash
pip install -r requirements_madre.txt
```

**Para la Aplicación Hija:**
```bash
pip install -r requirements_hija.txt
```

## Uso

### Iniciar la Aplicación Madre

1. Ejecuta el archivo principal:
```bash
python madre_main.py
```

2. Se abrirá la ventana de gestión con dos pestañas:
   - **Gestión de Usuarios**: Habilita/deshabilita el acceso para usuarios
   - **Sincronización de Contenido**: Publica contenido para las aplicaciones Hija

3. El servidor API estará disponible en `http://0.0.0.0:8000`

### Iniciar la Aplicación Hija

1. **IMPORTANTE**: Antes de ejecutar, edita `hija_comms.py` y modifica la línea:
```python
MADRE_BASE_URL = "http://127.0.0.1:8000"
```
Reemplaza `127.0.0.1` con la dirección IP real de la máquina donde se ejecuta la Aplicación Madre.

2. Ejecuta el archivo principal:
```bash
python hija_main.py
```

3. Ingresa un nombre de usuario en la pantalla de inicio:
   - Usuarios predefinidos: `usuario_alfa`, `usuario_beta`, `usuario_gamma`
   - Por defecto, `usuario_alfa` y `usuario_beta` tienen acceso habilitado
   - `usuario_gamma` tiene acceso deshabilitado

4. Una vez autenticado, usa el botón "Sincronizar con la Madre" para obtener contenido actualizado

## Usuarios Predefinidos

La aplicación incluye tres usuarios de prueba:

| Usuario | Permiso de Acceso | Datos Adicionales |
|---------|-------------------|-------------------|
| usuario_alfa | ✓ Habilitado | Equipo A |
| usuario_beta | ✓ Habilitado | Equipo B |
| usuario_gamma | ✗ Deshabilitado | Equipo C |

## Características Principales

### Aplicación Madre
- ✅ Panel de gestión con pestañas
- ✅ Gestión de permisos de usuarios en tiempo real
- ✅ Publicación de contenido para sincronización
- ✅ Servidor API REST concurrente
- ✅ Interfaz gráfica moderna y responsiva

### Aplicación Hija
- ✅ Autenticación contra servidor Madre
- ✅ Interfaz de inicio de sesión intuitiva
- ✅ Sincronización de contenido desde la Madre
- ✅ Manejo robusto de errores de conexión
- ✅ Diseño modular y escalable

## Arquitectura Técnica

### Flujo de Autenticación
1. La Hija envía una petición POST a `/autorizar` con el nombre de usuario
2. La Madre verifica el usuario y su permiso de acceso
3. Si es aprobado, la Hija desbloquea su funcionalidad principal

### Flujo de Sincronización
1. La Hija envía una petición GET a `/sincronizar_datos` con su usuario
2. La Madre verifica el usuario y devuelve los datos de sincronización
3. La Hija actualiza su interfaz con el contenido recibido

### Tecnologías Utilizadas
- **GUI**: CustomTkinter (interfaz moderna sobre Tkinter)
- **API Server**: FastAPI (framework web de alto rendimiento)
- **HTTP Client**: requests (biblioteca estándar para peticiones HTTP)
- **Concurrencia**: threading (ejecución simultánea de GUI y servidor)
- **Validación**: Pydantic (modelos de datos con validación automática)

## Distribución

### Crear ejecutable para Windows
Para distribuir la aplicación Hija sin requerir Python:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed hija_main.py
```

El ejecutable estará en la carpeta `dist/`

## Extensiones Futuras

- 🔒 Implementar OAuth2 con JWT para autenticación segura
- 💾 Migrar de base de datos en memoria a SQLite/PostgreSQL
- 🔐 Añadir comunicación HTTPS/SSL
- 📦 Empaquetado con PyInstaller para distribución
- 🎨 Expansión de la GUI con más funcionalidades
- 📊 Dashboard con métricas y estadísticas

## Seguridad

⚠️ **ADVERTENCIA**: Este es un prototipo funcional (POC). No está listo para producción:
- Los usuarios están en texto plano
- No hay contraseñas
- La comunicación no está cifrada
- La base de datos es en memoria y se pierde al cerrar

Para uso en producción, implementa las extensiones de seguridad mencionadas.

## Soporte

Para problemas o preguntas sobre el sistema, consulta la documentación técnica completa en `Desarrollo Python Apps Madre-Hija Remotas.txt`

## Licencia

Este proyecto es un prototipo educativo y de demostración.
