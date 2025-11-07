# Sistema de Gestión de Gimnasio

Sistema integral de gestión administrativa para gimnasios que permite gestionar socios, membresías, clases, instalaciones y operaciones del día a día.

## 📋 Descripción General

Este sistema está diseñado para gimnasios que necesitan una solución completa de gestión administrativa y comunicación con sus socios. El sistema consta de dos aplicaciones principales:

### 🏢 Aplicación Madre (Administración)
Aplicación de escritorio para el personal administrativo del gimnasio que funciona como:
- **Panel de Administración**: Gestión completa de socios, membresías, pagos y clases
- **Servidor API REST**: Comunicación con las aplicaciones de los socios
- **Sistema de Reportes**: Análisis de negocio y KPIs

**Funcionalidades Principales:**
- Gestión de socios y membresías
- Control de pagos y facturación
- Programación de clases grupales
- Gestión de instalaciones y equipamiento
- Reportes financieros y operativos
- Comunicación masiva con socios
- CRM para prospectos

### 📱 Aplicación Hija (Socios)
Aplicación de escritorio para los socios del gimnasio que permite:
- Ver y gestionar su membresía
- Reservar clases grupales
- Consultar horarios y disponibilidad
- Comunicarse con el gimnasio
- Seguimiento de asistencia y progreso
- Acceso a contenido de entrenamiento general

## 🎯 Enfoque del Sistema

### ✅ El Sistema ES:
- Sistema de gestión administrativa de gimnasio
- Plataforma de venta de paquetes de servicios (membresías)
- Herramienta de control de asistencia y reservas
- Sistema de comunicación gimnasio-socios
- Plataforma de análisis de negocio

### ❌ El Sistema NO ES:
- Plataforma de entrenamiento personalizado 1-a-1
- Sistema de coaching personal intensivo
- App centrada en entrenadores personales individuales

El gimnasio vende **paquetes de servicios** que incluyen acceso a instalaciones, clases grupales, y servicios adicionales opcionales (spa, nutrición, etc.). Los socios pueden seguir programas de entrenamiento generales sugeridos, pero el enfoque principal es la **gestión eficiente del gimnasio como negocio**.

## 🚀 Inicio Rápido

### Requisitos
- Python 3.8 o superior
- Windows (recomendado) o Linux/macOS
- Conexión de red entre servidor y clientes

### Instalación

#### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd GYM
```

#### 2. Instalar dependencias

**Para la Aplicación Madre (Administración):**
```bash
pip install -r requirements_madre.txt
```

**Para la Aplicación Hija (Socios):**
```bash
pip install -r requirements_hija.txt
```

#### 3. Configuración (Opcional)
```bash
cp config/.env.example .env
# Editar .env con tu configuración
```

**Variables principales:**
- `MADRE_HOST`: Host del servidor (default: 0.0.0.0)
- `MADRE_PORT`: Puerto del servidor (default: 8000)
- `DB_PATH`: Ruta de la base de datos (default: data/gym_database.db)

### Uso

#### Iniciar Aplicación Madre (Administración)
```bash
python madre_main.py
```

La interfaz administrativa se abrirá con acceso a:
- Gestión de socios
- Control de membresías y pagos
- Programación de clases
- Reportes y estadísticas

El servidor API estará disponible en `http://0.0.0.0:8000`

#### Iniciar Aplicación Hija (Socios)
```bash
# Configurar URL del servidor
echo "MADRE_BASE_URL=http://IP_DEL_SERVIDOR:8000" > .env

# Ejecutar aplicación
python hija_main.py
```

Los socios pueden autenticarse con sus credenciales para:
- Ver su información de membresía
- Reservar clases
- Consultar horarios
- Comunicarse con el gimnasio

## 👥 Usuarios de Prueba

Para poblar la base de datos con usuarios de prueba:
```bash
python populate_db.py
```

**Usuarios predefinidos:**
| Usuario | Contraseña | Tipo | Estado |
|---------|-----------|------|--------|
| `admin_gym` | `admin123` | Administrador | Activo |
| `juan_perez` | `gym2024` | Socio | Activo |
| `maria_lopez` | `fit2024` | Socio | Activo |
| `carlos_rodriguez` | `trainer123` | Socio | Bloqueado |

## 🏗️ Arquitectura Técnica

### Tecnologías Utilizadas
- **GUI**: CustomTkinter (interfaz moderna)
- **API Server**: FastAPI (REST API de alto rendimiento)
- **Database**: SQLite (persistencia de datos)
- **HTTP Client**: requests
- **Logging**: Python logging con rotación de archivos
- **Concurrencia**: threading para servidor y GUI

### Estructura del Proyecto
```
GYM/
├── madre_main.py              # Punto de entrada administración
├── madre_server.py            # API REST
├── madre_gui.py               # Interfaz administrativa
├── madre_db.py                # Capa de base de datos
├── hija_main.py               # Punto de entrada socios
├── hija_comms.py              # Comunicaciones HTTP
├── hija_views.py              # Interfaz de socios
├── shared/                    # Módulos compartidos
│   ├── constants.py
│   └── logger.py
├── config/                    # Configuración
│   ├── .env.example
│   └── settings.py
├── data/                      # Base de datos
│   └── gym_database.db
└── requirements_*.txt         # Dependencias
```

## 🔐 Seguridad

### Implementaciones Actuales
- ✅ Contraseñas con hash SHA256
- ✅ Base de datos SQLite persistente
- ✅ Validación de permisos en servidor
- ✅ Thread-safety en operaciones de BD
- ✅ Logging de auditoría

### Recomendaciones para Producción
- 🔒 Migrar a bcrypt/argon2 para contraseñas
- 🔐 Implementar JWT para sesiones
- 🔒 Añadir comunicación HTTPS/SSL
- 🔒 Rate limiting en API
- 🔐 Migrar a PostgreSQL con SSL

## 📊 Funcionalidades Principales

### Para Administración
- ✅ Gestión completa de socios
- ✅ Control de membresías y pagos
- ✅ Programación de clases grupales
- ✅ Gestión de instalaciones
- ✅ Reportes financieros
- ✅ Comunicación masiva
- ✅ Sistema de reservas
- ✅ CRM para prospectos

### Para Socios
- ✅ Autenticación segura
- ✅ Perfil personal
- ✅ Reserva de clases
- ✅ Seguimiento de asistencia
- ✅ Comunicación con gimnasio
- ✅ Sincronización automática
- ✅ Información de membresía

## 📈 Roadmap

Ver el archivo `GYM_MANAGEMENT_FEATURES.md` para una lista completa de funcionalidades planificadas, incluyendo:
- Control de acceso físico con torniquetes
- Integración con pasarelas de pago
- App móvil para socios
- Sistema de análisis predictivo
- Integración con wearables
- Reportes avanzados de negocio

## 🔧 Desarrollo

### Testing
```bash
python test_system.py
python test_messaging.py
```

### Logging
Los logs se guardan en el directorio `logs/`:
- `madre_main.log` - Aplicación madre
- `madre_server.log` - Servidor API
- `hija_main.log` - Aplicación hija

### Health Check
```bash
curl http://localhost:8000/health
```

## 📚 Documentación Adicional

- `GYM_MANAGEMENT_FEATURES.md` - Funcionalidades detalladas del sistema
- `SETUP.md` - Guía de instalación paso a paso
- `config/.env.example` - Variables de configuración disponibles

## 📄 Licencia

Este proyecto es un sistema de gestión de gimnasios.

## 🤝 Soporte

Para problemas o preguntas, consulta la documentación o abre un issue en el repositorio.
