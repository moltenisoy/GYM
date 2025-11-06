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

### 4. Configuración (Opcional)

El sistema utiliza variables de entorno para su configuración. Puedes crear un archivo `.env` para personalizar los valores:

```bash
# Copiar el archivo de ejemplo
cp config/.env.example .env

# Editar con tus valores personalizados
nano .env  # o usa tu editor preferido
```

**Variables de configuración principales:**

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `MADRE_HOST` | Host del servidor Madre | `0.0.0.0` |
| `MADRE_PORT` | Puerto del servidor Madre | `8000` |
| `MADRE_BASE_URL` | URL del servidor (para Hija) | `http://127.0.0.1:8000` |
| `DB_PATH` | Ruta de la base de datos | `data/gym_database.db` |
| `LOG_LEVEL` | Nivel de logging | `INFO` |

> 💡 **Nota**: Si no creas un archivo `.env`, el sistema usará los valores por defecto.

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

1. **IMPORTANTE**: Antes de ejecutar, configura la URL del servidor Madre:

**Opción A (Recomendada): Usar variables de entorno**
```bash
# Crear archivo .env
echo "MADRE_BASE_URL=http://192.168.1.100:8000" > .env
```

**Opción B: Editar directamente (no recomendado)**
Edita `hija_comms.py` y modifica la línea:
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

La aplicación incluye tres usuarios de prueba con **datos completos**:

| Usuario | Contraseña | Permiso | Equipo |
|---------|-----------|---------|--------|
| `juan_perez` | `gym2024` | ✅ Habilitado | Equipo A - Fitness Avanzado |
| `maria_lopez` | `fit2024` | ✅ Habilitado | Equipo B - Cardio y Resistencia |
| `carlos_rodriguez` | `trainer123` | ❌ **BLOQUEADO** | Equipo C - Principiantes |

**Cada usuario incluye:**
- Foto de perfil
- Datos personales completos (email, teléfono, equipo)
- Cronograma de entrenamiento mensual detallado
- Galería de fotos personal con descripciones

> 💡 **Nota**: Para crear los usuarios y poblar la base de datos, ejecutar: `python populate_db.py`

## Características Principales

### Aplicación Madre
- ✅ Panel de gestión con pestañas
- ✅ **Base de datos SQLite persistente** (NUEVO)
- ✅ Gestión de permisos de usuarios en tiempo real
- ✅ **Gestión individual de usuarios con detalles completos** (NUEVO)
- ✅ **Sincronización masiva de múltiples usuarios** (NUEVO)
- ✅ Publicación de contenido para sincronización
- ✅ Servidor API REST concurrente
- ✅ Interfaz gráfica moderna y responsiva
- ✅ **Logging estructurado con rotación de archivos** (NUEVO v3.1)
- ✅ **Configuración mediante variables de entorno** (NUEVO v3.1)
- ✅ **Health check endpoint para monitoreo** (NUEVO v3.1)

### Aplicación Hija
- ✅ **Autenticación con contraseña** (NUEVO)
- ✅ **Auto-login con credenciales guardadas** (NUEVO)
- ✅ **Validación de sincronización cada 72 horas** (NUEVO)
- ✅ **Sincronización automática en segundo plano** (NUEVO)
  - Cada 5 minutos inicialmente
  - Cada 30 minutos tras primera sync exitosa
- ✅ **Interfaz con pestañas**: Perfil, Cronograma, Galería, Mensajes (NUEVO)
- ✅ Interfaz de inicio de sesión intuitiva
- ✅ Sincronización de contenido desde la Madre
- ✅ Manejo robusto de errores de conexión
- ✅ Diseño modular y escalable
- ✅ **Retry logic con exponential backoff** (NUEVO v3.1)
- ✅ **Logging estructurado** (NUEVO v3.1)
- ✅ **Configuración centralizada** (NUEVO v3.1)

> 📖 **Ver documentación completa de nuevas funcionalidades en** [`NUEVAS_FUNCIONALIDADES.md`](NUEVAS_FUNCIONALIDADES.md)

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
- **Logging**: Python logging module con RotatingFileHandler
- **Database**: SQLite3 con thread-safety
- **Configuration**: Environment variables con fallback a defaults

### Estructura del Proyecto (v3.1)

```
GYM/
├── madre_main.py           # Punto de entrada Madre
├── madre_server.py         # API REST con FastAPI
├── madre_gui.py            # Interfaz gráfica Madre
├── madre_db.py             # Capa de base de datos
├── hija_main.py            # Punto de entrada Hija
├── hija_comms.py           # Comunicaciones HTTP
├── hija_views.py           # Componentes GUI Hija
├── shared/                 # Módulos compartidos
│   ├── constants.py        # Constantes centralizadas
│   └── logger.py           # Configuración de logging
├── config/                 # Configuración
│   ├── .env.example        # Plantilla de configuración
│   └── settings.py         # Carga de variables de entorno
├── data/                   # Datos persistentes
│   ├── gym_database.db     # Base de datos SQLite
│   └── hija_local/         # Datos locales de Hija
├── logs/                   # Archivos de log
│   ├── madre_main.log
│   ├── madre_server.log
│   ├── madre_db.log
│   ├── hija_main.log
│   └── hija_comms.log
└── requirements_*.txt      # Dependencias
```

### Logs y Monitoreo (v3.1)

El sistema ahora incluye logging estructurado con:
- **Niveles**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Rotación**: Archivos de 10MB con 5 backups
- **Ubicación**: Directorio `logs/` (creado automáticamente)
- **Formato**: `[timestamp] - [module] - [level] - [message]`

**Ver logs en tiempo real:**
```bash
# Linux/macOS
tail -f logs/madre_server.log

# Windows PowerShell
Get-Content logs/madre_server.log -Wait -Tail 10
```

**Health Check Endpoint:**
```bash
curl http://localhost:8000/health
```
Respuesta:
```json
{
  "status": "online",
  "version": "3.1.0",
  "database_status": "healthy"
}
```

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

### Implementaciones Actuales ✅
- ✅ Contraseñas con hash SHA256
- ✅ Base de datos persistente (SQLite)
- ✅ Validación de permisos en servidor
- ✅ Validación de sincronización (72 horas)
- ✅ Thread-safety en operaciones de BD

### Mejoras Recomendadas para Producción ⚠️
- 🔒 Migrar a bcrypt/argon2 para contraseñas
- 🔒 Implementar JWT para sesiones
- 🔐 Añadir comunicación HTTPS/SSL
- 🔐 Usar keyring para credenciales locales
- 🔒 Implementar rate limiting en API
- 🔐 Migrar a PostgreSQL con SSL

> ⚠️ **ADVERTENCIA**: Si bien el sistema incluye seguridad básica, se recomienda implementar las mejoras listadas antes de usar en producción.

## Soporte

Para problemas o preguntas sobre el sistema, consulta la documentación técnica completa en `Desarrollo Python Apps Madre-Hija Remotas.txt`

## Licencia

Este proyecto es un prototipo educativo y de demostración.
