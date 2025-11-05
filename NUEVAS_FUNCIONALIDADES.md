# Nuevas Funcionalidades - Sistema GYM v2.0

## Resumen de Cambios

Este documento describe las nuevas funcionalidades implementadas en el sistema de gestión de gimnasio Madre-Hija.

---

## 1. Base de Datos Real SQLite

### ✨ Característica Principal
Se ha reemplazado la simulación en memoria con una **base de datos SQLite persistente** que mantiene toda la información entre sesiones.

### 📊 Estructura de Tablas

#### `users` - Usuarios del sistema
- `id`: ID único
- `username`: Nombre de usuario (único)
- `password_hash`: Contraseña hasheada (SHA256)
- `permiso_acceso`: Permiso de acceso (0/1)
- `nombre_completo`: Nombre completo del usuario
- `email`: Correo electrónico
- `telefono`: Teléfono de contacto
- `fecha_registro`: Fecha de registro
- `equipo`: Equipo asignado
- `last_sync`: Última fecha de sincronización

#### `profile_photos` - Fotos de perfil
- `id`: ID único
- `user_id`: ID del usuario
- `photo_path`: Ruta de la foto
- `upload_date`: Fecha de carga

#### `training_schedules` - Cronogramas de entrenamiento
- `id`: ID único
- `user_id`: ID del usuario
- `mes`: Mes del cronograma
- `ano`: Año del cronograma
- `schedule_data`: Datos del cronograma (JSON)
- `created_date`: Fecha de creación
- `modified_date`: Fecha de modificación

#### `photo_gallery` - Galería de fotos personal
- `id`: ID único
- `user_id`: ID del usuario
- `photo_path`: Ruta de la foto
- `descripcion`: Descripción de la foto
- `upload_date`: Fecha de carga

#### `sync_data` - Datos de sincronización global
- `id`: ID único
- `contenido`: Contenido del mensaje
- `metadatos_version`: Versión del contenido
- `update_date`: Fecha de actualización

### 🔒 Thread-Safety
Todas las operaciones de base de datos están protegidas con `threading.Lock` para garantizar seguridad en entornos multi-hilo (GUI + Servidor API).

---

## 2. Usuarios de Prueba

Se han creado **3 usuarios de ejemplo** con datos completos:

### 👤 Juan Pérez (`juan_perez` / `gym2024`)
- **Equipo**: Equipo A - Fitness Avanzado
- **Permiso**: ✅ Habilitado
- **Cronograma**: Programa de ganancia muscular y definición
  - 6 días de entrenamiento: Pecho/Tríceps, Cardio, Espalda/Bíceps, Descanso activo, Piernas, HIIT
  - 1 día de descanso completo
- **Galería**: 3 fotos de progreso y entrenamiento

### 👤 María López (`maria_lopez` / `fit2024`)
- **Equipo**: Equipo B - Cardio y Resistencia
- **Permiso**: ✅ Habilitado
- **Cronograma**: Programa de resistencia cardiovascular
  - Running, Spinning, Natación, Intervalos, Circuito funcional, Carrera larga
- **Galería**: 2 fotos (media maratón, yoga)

### 👤 Carlos Rodríguez (`carlos_rodriguez` / `trainer123`)
- **Equipo**: Equipo C - Principiantes
- **Permiso**: ❌ **DESHABILITADO**
- **Cronograma**: Programa de adaptación inicial
  - Rutina básica para principiantes
- **Galería**: 1 foto (primer día)

---

## 3. Aplicación Madre - Nuevas Funcionalidades

### 🎯 Gestión Individual de Usuarios

#### Botón "Ver Detalles"
Cada usuario ahora tiene un botón que abre una ventana emergente con:
- **Información Personal Completa**
  - Usuario, Nombre, Email, Teléfono
  - Equipo, Fecha de registro
  - Última sincronización, Estado del permiso
  
- **Cronograma de Entrenamiento**
  - Vista completa del cronograma mensual
  - Desglose por día: ejercicios, descripción, duración
  - Objetivo y notas del entrenador

- **Galería de Fotos**
  - Lista de todas las fotos con descripciones
  - Fechas de carga

### 📋 Sincronización Masiva (Nueva Pestaña)

#### Funcionalidades
- **Selección de Usuarios**: Checkboxes para cada usuario
- **Botones de Control**:
  - "Seleccionar Todos": Marca todos los usuarios
  - "Deseleccionar Todos": Desmarca todos
  - "Sincronizar Seleccionados": Fuerza sync para usuarios marcados

#### Comportamiento
- Actualiza el timestamp de sincronización para todos los usuarios seleccionados
- Permite sincronización masiva en un solo clic
- Muestra contador de usuarios sincronizados exitosamente

### 🔄 Actualización de Permisos en Tiempo Real
- Los cambios de permisos se reflejan inmediatamente en la base de datos
- La API del servidor accede a los mismos datos actualizados

---

## 4. Aplicación Hija - Nuevas Funcionalidades

### 🔐 Autenticación con Contraseña

#### Login Mejorado
- Campo de **usuario** y **contraseña**
- Validación contra base de datos con hash SHA256
- Credenciales almacenadas localmente para auto-login

#### Auto-Login
- La aplicación guarda credenciales en el primer login exitoso
- En próximas ejecuciones, intenta auto-login automáticamente
- Si falla la validación de 72 horas, solicita nuevo login

### ⏰ Validación de Sincronización (72 horas)

#### Regla de Negocio
- Los usuarios **DEBEN** sincronizar al menos una vez cada 72 horas
- Si pasan más de 72 horas sin sincronización:
  - El login queda **BLOQUEADO**
  - Se fuerza nuevo login para validar credenciales
  - Se requiere conexión con la Madre para desbloquear

#### Implementación
- Validación automática al iniciar la aplicación
- Verificación en el servidor mediante endpoint `/validar_sync`
- Contador de horas desde última sincronización

### 🔄 Sincronización Automática en Segundo Plano

#### Comportamiento Adaptativo
1. **Inicio de sesión**: Sincronización inmediata
2. **Primeros intentos**: Cada **5 minutos**
3. **Después de primera sync exitosa**: Cada **30 minutos**

#### Características Técnicas
- Ejecuta en **hilo daemon separado**
- **Prioridad baja** (`os.nice(10)` en Unix)
- No bloquea la interfaz de usuario
- Detención automática al cerrar la aplicación

#### Manejo de Errores
- Si falla una sincronización, continúa intentando
- Los errores no detienen el loop de sincronización
- Mensajes de error visibles en la UI

### 📱 Interfaz Mejorada con Pestañas

#### Pestaña "Perfil"
- Información personal completa del usuario
- Usuario, Nombre, Email, Teléfono
- Equipo asignado, Fecha de registro

#### Pestaña "Cronograma"
- Cronograma de entrenamiento mensual completo
- Desglose día por día:
  - Ejercicios planificados
  - Descripción detallada
  - Duración en minutos
- Objetivo del programa
- Notas del entrenador

#### Pestaña "Galería"
- Todas las fotos personales del usuario
- Descripción de cada foto
- Fecha de carga
- Visualización en lista ordenada

#### Pestaña "Mensajes"
- Contenido global de sincronización
- Mensajes del gimnasio/entrenadores
- Versión del contenido
- Actualizaciones importantes

---

## 5. Endpoints de API (Servidor)

### 🆕 Nuevos Endpoints

#### `POST /autorizar`
**Autenticación con contraseña**
```json
Request:
{
  "username": "juan_perez",
  "password": "gym2024"
}

Response (200 OK):
{
  "status": "aprobado",
  "usuario": "juan_perez",
  "nombre_completo": "Juan Pérez García",
  "equipo": "Equipo A - Fitness Avanzado",
  "last_sync": "2025-11-05T15:00:00"
}

Response (401 Unauthorized):
{
  "detail": "Credenciales inválidas."
}

Response (403 Forbidden):
{
  "detail": "Permiso de acceso denegado por el administrador."
}
```

#### `GET /validar_sync?usuario={username}`
**Validación de sincronización (72 horas)**
```json
Response (OK - Sincronizado):
{
  "requiere_sync": false,
  "bloqueado": false,
  "mensaje": "Sincronización actual",
  "horas_desde_sync": 12.5
}

Response (Bloqueado):
{
  "requiere_sync": true,
  "bloqueado": true,
  "mensaje": "Sincronización requerida. Última sync: 75.2 horas atrás",
  "horas_desde_sync": 75.2
}
```

#### `GET /sincronizar_datos?usuario={username}`
**Sincronización completa de datos**
```json
Response:
{
  "status": "sincronizacion_exitosa",
  "timestamp": "2025-11-05T15:00:00",
  "usuario": {
    "username": "juan_perez",
    "nombre_completo": "Juan Pérez García",
    "email": "juan.perez@example.com",
    "telefono": "+34 612 345 678",
    "equipo": "Equipo A - Fitness Avanzado",
    "fecha_registro": "2025-11-05"
  },
  "profile_photo": "data/users/profile_photos/juan_perez.jpg",
  "training_schedule": {
    "mes": "Diciembre",
    "ano": 2024,
    "schedule_data": {
      "dias": { ... },
      "objetivo": "Ganancia muscular y definición",
      "notas": "Aumentar progresivamente la carga"
    }
  },
  "photo_gallery": [
    {
      "photo_path": "data/users/gallery/juan_perez_progress_1.jpg",
      "descripcion": "Progreso mes 1",
      "upload_date": "2025-11-05"
    }
  ],
  "sync_content": {
    "contenido": "Mensajes del gimnasio...",
    "metadatos_version": "1.0.0"
  }
}
```

#### `POST /actualizar_permiso`
**Actualizar permiso de acceso**
```json
Request:
{
  "username": "juan_perez",
  "permiso_acceso": false
}

Response:
{
  "status": "actualizado",
  "usuario": "juan_perez",
  "permiso_acceso": false
}
```

#### `POST /sincronizar_masiva`
**Sincronización masiva**
```json
Request:
["juan_perez", "maria_lopez"]

Response:
{
  "status": "sincronizacion_masiva_completada",
  "total": 2,
  "resultados": [
    {"usuario": "juan_perez", "actualizado": true},
    {"usuario": "maria_lopez", "actualizado": true}
  ]
}
```

#### `GET /usuarios`
**Obtener lista de todos los usuarios**
```json
Response:
{
  "total": 3,
  "usuarios": [
    {
      "id": 1,
      "username": "juan_perez",
      "nombre_completo": "Juan Pérez García",
      "email": "juan.perez@example.com",
      "permiso_acceso": 1,
      "equipo": "Equipo A - Fitness Avanzado",
      "last_sync": "2025-11-05T15:00:00"
    },
    ...
  ]
}
```

---

## 6. Credenciales de Acceso

### Usuarios de Prueba

| Usuario | Contraseña | Acceso | Equipo |
|---------|-----------|--------|--------|
| `juan_perez` | `gym2024` | ✅ Habilitado | Equipo A - Fitness Avanzado |
| `maria_lopez` | `fit2024` | ✅ Habilitado | Equipo B - Cardio y Resistencia |
| `carlos_rodriguez` | `trainer123` | ❌ **BLOQUEADO** | Equipo C - Principiantes |

---

## 7. Archivos Modificados

### Nuevos Archivos
- `populate_db.py` - Script para poblar la base de datos con datos de prueba
- `data/gym_database.db` - Base de datos SQLite
- `NUEVAS_FUNCIONALIDADES.md` - Este documento

### Archivos Modificados
- `madre_db.py` - Completamente reescrito con SQLite
- `madre_server.py` - Nuevos endpoints y autenticación
- `madre_gui.py` - Nueva pestaña de sync masiva y detalles de usuario
- `hija_comms.py` - Gestión de credenciales y nuevas validaciones
- `hija_views.py` - Interfaz con pestañas y contraseña
- `hija_main.py` - Auto-login y sincronización en segundo plano

---

## 8. Flujo de Uso Completo

### Primera Vez - Usuario Nuevo

1. **Iniciar Aplicación Hija**
   - Se muestra pantalla de login
   - No hay credenciales guardadas

2. **Ingresar Credenciales**
   - Usuario: `juan_perez`
   - Contraseña: `gym2024`
   - Click en "Conectar a la Madre"

3. **Validación**
   - El servidor valida usuario y contraseña
   - Verifica permiso de acceso
   - Registra timestamp de sincronización

4. **Auto-Login**
   - Credenciales se guardan localmente
   - Próximas veces: auto-login automático

5. **Sincronización Inicial**
   - Se descarga toda la información del usuario
   - Se muestra en las 4 pestañas
   - Comienza sync automática cada 5 minutos

6. **Primera Sync Exitosa**
   - El intervalo cambia a 30 minutos
   - Continúa sincronizando en segundo plano

### Uso Regular

1. **Iniciar Aplicación**
   - Auto-login automático
   - Validación de 72 horas
   - Si está actualizado: acceso directo

2. **Navegación**
   - Ver Perfil
   - Revisar Cronograma del día
   - Ver progreso en Galería
   - Leer Mensajes del gimnasio

3. **Sync Manual**
   - Click en "Sincronizar Ahora"
   - Actualiza inmediatamente todos los datos

4. **Sync Automática**
   - Cada 30 minutos en segundo plano
   - Sin interrumpir el uso de la app
   - Prioridad baja de sistema

### Si Pasan 72 Horas Sin Sincronizar

1. **Intentar Iniciar Aplicación**
   - Validación de 72 horas falla
   - Se borra auto-login

2. **Pantalla de Login Forzado**
   - Debe ingresar credenciales nuevamente
   - Requiere conexión con la Madre

3. **Tras Login Exitoso**
   - Se restablece el contador de 72 horas
   - Se puede volver a usar la app

---

## 9. Gestión desde Aplicación Madre

### Gestión Individual

1. **Iniciar Aplicación Madre**
   - `python madre_main.py`
   - Se inicia GUI y servidor API simultáneamente

2. **Pestaña "Gestión de Usuarios"**
   - Ver lista completa de usuarios
   - Click en "Ver Detalles" de cualquier usuario
   - Ver toda su información: perfil, cronograma, galería

3. **Modificar Permisos**
   - Toggle del switch "Acceso Habilitado"
   - Cambio inmediato en base de datos
   - El usuario afectado se bloqueará/desbloqueará en próximo intento de login

### Sincronización Masiva

1. **Pestaña "Sincronización Masiva"**
   - Ver lista de todos los usuarios con checkboxes

2. **Seleccionar Usuarios**
   - Marcar usuarios individuales, o
   - Click en "Seleccionar Todos"

3. **Ejecutar Sincronización**
   - Click en "Sincronizar Seleccionados"
   - Se actualiza timestamp para todos los seleccionados
   - Mensaje de confirmación con contador

### Publicar Contenido Global

1. **Pestaña "Sincronización de Contenido"**
   - Editar el contenido en el campo de texto
   - Escribir mensajes, anuncios, actualizaciones

2. **Publicar**
   - Click en "Publicar Nuevo Contenido"
   - Se incrementa versión automáticamente
   - Todos los usuarios recibirán el contenido en próxima sync

---

## 10. Consideraciones Técnicas

### Seguridad
- ⚠️ Las contraseñas usan hash SHA256 (mejorar a bcrypt en producción)
- ⚠️ Credenciales locales cifradas básicamente (usar keyring en producción)
- ✅ Validación de permisos en servidor
- ✅ Thread-safety en operaciones de BD

### Rendimiento
- ✅ Sincronización en segundo plano no bloquea UI
- ✅ Prioridad baja de proceso (`nice +10`)
- ✅ Intervalo adaptativo (5 min → 30 min)
- ✅ Timeouts configurados en requests HTTP

### Escalabilidad
- ✅ Base de datos SQLite (migrable a PostgreSQL)
- ✅ API REST estándar
- ✅ Arquitectura modular
- ✅ Separación de responsabilidades

### Mantenibilidad
- ✅ Código documentado
- ✅ Funciones claramente nombradas
- ✅ Estructura de BD normalizada
- ✅ Logs y mensajes de debug

---

## 11. Próximos Pasos Sugeridos

### Corto Plazo
- [ ] Añadir carga real de imágenes (actualmente son rutas)
- [ ] Implementar edición de cronogramas desde Madre
- [ ] Agregar notificaciones push

### Mediano Plazo
- [ ] Migrar a bcrypt para contraseñas
- [ ] Implementar JWT para sesiones
- [ ] Añadir HTTPS/SSL
- [ ] Sistema de backup automático

### Largo Plazo
- [ ] Migrar a PostgreSQL
- [ ] App móvil (React Native / Flutter)
- [ ] Dashboard con métricas
- [ ] Sistema de mensajería en tiempo real

---

## 12. Comandos Útiles

### Poblar Base de Datos
```bash
python populate_db.py
```

### Iniciar Aplicación Madre
```bash
python madre_main.py
```

### Iniciar Aplicación Hija
```bash
python hija_main.py
```

### Verificar Base de Datos
```bash
sqlite3 data/gym_database.db
.tables
SELECT * FROM users;
.quit
```

### Borrar Base de Datos (Reset)
```bash
rm data/gym_database.db
python populate_db.py
```

---

## 📞 Soporte

Para preguntas o problemas, consultar:
- `README.md` - Documentación general
- `ESTRUCTURA_PROYECTO.md` - Arquitectura del sistema
- Este documento - Nuevas funcionalidades

---

**Sistema GYM v2.0** - Sistema completo de gestión de gimnasio con sincronización automática y base de datos persistente.
