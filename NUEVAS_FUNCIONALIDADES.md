# Nuevas Funcionalidades del Sistema de Gestión de Gimnasio

Este documento detalla las nuevas funcionalidades implementadas en el sistema de gestión de gimnasio, incluyendo reservas de clases, gestión de equipos, logging de entrenamientos, y más.

## 📋 Índice

1. [Reservas de Clases](#1-reservas-de-clases)
2. [Gestión de Lista de Espera](#2-gestión-de-lista-de-espera)
3. [Recordatorios de Clases](#3-recordatorios-de-clases)
4. [Calendario Personal Sincronizado](#4-calendario-personal-sincronizado)
5. [Check-in de Clase por Proximidad](#5-check-in-de-clase-por-proximidad)
6. [Calificación Rápida de Clases](#6-calificación-rápida-de-clases)
7. [Reservas de Equipos/Zonas](#7-reservas-de-equiposzonas)
8. [Filtro de Clases Inteligente](#8-filtro-de-clases-inteligente)
9. [Notificaciones de "Hora de Salir"](#9-notificaciones-de-hora-de-salir)
10. [Botón "Cancelar" Fácil](#10-botón-cancelar-fácil)
11. [Check-in Digital (QR/NFC)](#11-check-in-digital-qrnfc)
12. [Modo "Entrenamiento Activo"](#12-modo-entrenamiento-activo)
13. [Mapa del Gimnasio con AR](#13-mapa-del-gimnasio-con-ar)
14. [Escáner de Máquinas](#14-escáner-de-máquinas)
15. [Quick Log de Series/Reps](#15-quick-log-de-seriesreps)
16. [Calculadora de Discos](#16-calculadora-de-discos)
17. [Temporizador de Descanso Avanzado](#17-temporizador-de-descanso-avanzado)

---

## 1. Reservas de Clases "One-Click"

### Descripción
Sistema de reserva de clases con un solo toque directamente desde el calendario de la aplicación.

### Implementación
- **Base de Datos**: Tabla `class_bookings` almacena todas las reservas
- **API Endpoint**: `POST /clases/reservar`
- **Función Backend**: `book_class()` en `madre_db.py`

### Características
- ✅ Reserva instantánea con un solo clic
- ✅ Verificación automática de capacidad
- ✅ Prevención de reservas duplicadas
- ✅ Agregado automático a lista de espera si la clase está llena

### Ejemplo de Uso (API)
```bash
curl -X POST 'http://localhost:8000/clases/reservar' \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "juan_perez",
    "schedule_id": 1,
    "fecha_clase": "2025-11-15"
  }'
```

### Respuesta Exitosa
```json
{
  "status": "success",
  "message": "Reserva confirmada exitosamente"
}
```

---

## 2. Gestión de Lista de Espera (Push)

### Descripción
Sistema automatizado de lista de espera con notificaciones push cuando se libera un cupo.

### Implementación
- **Base de Datos**: Tabla `class_waitlist` y `notifications`
- **API Endpoint**: Automático al cancelar reservas
- **Función Backend**: `notify_waitlist()` en `madre_db.py`

### Características
- ✅ Agregado automático a lista de espera cuando clase está llena
- ✅ Notificación instantánea cuando se libera un cupo
- ✅ Temporizador de 10 minutos para confirmar
- ✅ Gestión automática de prioridad (FIFO)

### Flujo
1. Usuario intenta reservar clase llena → Se agrega a waitlist
2. Otro usuario cancela → Sistema notifica al primero en waitlist
3. Usuario tiene 10 minutos para confirmar desde la notificación
4. Si no confirma, se notifica al siguiente en la lista

### Campos de Notificación
```json
{
  "tipo": "waitlist_spot_available",
  "titulo": "Cupo Disponible",
  "mensaje": "Se liberó un cupo en tu clase. Tienes 10 minutos para confirmar.",
  "expires_date": "2025-11-08T10:10:00",
  "data": {
    "schedule_id": 1,
    "fecha_clase": "2025-11-15"
  }
}
```

---

## 3. Recordatorios de Clases (Notificación Inteligente)

### Descripción
Sistema de recordatorios inteligentes que envía notificaciones 1 hora antes de la clase y 10 minutos antes si el usuario está en el gimnasio.

### Implementación
- **Base de Datos**: Tabla `notifications` y `user_preferences`
- **Función Backend**: `create_notification()` en `madre_db.py`
- **Configuración**: Campo `reminder_time_minutes` en preferencias de usuario

### Características
- ✅ Recordatorio 1 hora antes de la clase (configurable)
- ✅ Recordatorio "En 10 minutos" si está en el gimnasio (geofencing)
- ✅ Personalizable por usuario
- ✅ No envía recordatorios para clases ya registradas (checked-in)

### Preferencias de Usuario
```python
notification_class_reminder: bool = True  # Habilitar/deshabilitar
reminder_time_minutes: int = 60  # Minutos antes (default 60)
```

---

## 4. Calendario Personal Sincronizado

### Descripción
Preparación para sincronización con calendarios externos (Google Calendar, Outlook, iCal).

### Implementación
- **Base de Datos**: Tabla `user_preferences` con campos de configuración
- **Formato**: Exportación en formato iCalendar (.ics)

### Características
- ✅ Soporte para Google Calendar
- ✅ Soporte para Outlook Calendar
- ✅ Soporte para iCal (Apple Calendar)
- ✅ Exportación manual de reservas
- ✅ Actualización automática al hacer/cancelar reservas

### Configuración de Usuario
```python
calendar_sync_enabled: bool = False  # Habilitar sincronización
calendar_type: str = "google"  # Tipo: "google", "outlook", "ical"
```

### Formato de Exportación (iCalendar)
```ics
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//GYM Management//ES
BEGIN:VEVENT
UID:booking-1@gym.example.com
DTSTART:20251115T070000Z
DTEND:20251115T074500Z
SUMMARY:Spinning - Carlos Ruiz
LOCATION:Sala Cardio 1
DESCRIPTION:Clase de ciclismo indoor de alta intensidad
END:VEVENT
END:VCALENDAR
```

---

## 5. Check-in de Clase por Proximidad (Beacon/Geofencing)

### Descripción
Sistema de check-in automático basado en proximidad al entrar a la sala de clases.

### Implementación
- **Tecnología**: Requiere app móvil con soporte de Bluetooth/GPS
- **Base de Datos**: Tabla `checkin_history`
- **API Endpoint**: `POST /checkin`

### Características
- 🔄 Check-in automático al entrar a la sala (requiere app móvil)
- ✅ Check-in manual desde la app
- ✅ Registro de ubicación (sala específica)
- ✅ Historial completo de check-ins

### Estado Actual
- ✅ Backend implementado y funcional
- ⏳ Frontend móvil pendiente (requiere desarrollo de app móvil nativa)

### Ejemplo de Check-in Manual
```bash
curl -X POST 'http://localhost:8000/checkin?username=juan_perez&location=Sala%20Cardio%201'
```

---

## 6. Calificación Rápida de Clases (Pop-up Post-Clase)

### Descripción
Sistema de calificación inmediata después de terminar la clase con pop-up notification.

### Implementación
- **Base de Datos**: Tabla `class_ratings`
- **API Endpoint**: `POST /clases/calificar`
- **Función Backend**: `rate_class()` en `madre_db.py`

### Características
- ✅ Calificación de 1-5 estrellas para la clase
- ✅ Calificación separada para el instructor (opcional)
- ✅ Comentarios opcionales
- ✅ Notificación pop-up al finalizar la clase

### Ejemplo de Calificación
```bash
curl -X POST 'http://localhost:8000/clases/calificar' \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "juan_perez",
    "class_id": 1,
    "schedule_id": 1,
    "fecha_clase": "2025-11-15",
    "rating": 5,
    "instructor_rating": 5,
    "comentario": "Excelente clase, muy motivadora!"
  }'
```

---

## 7. Reservas de Equipos/Zonas

### Descripción
Sistema de reservas para equipos específicos (racks de sentadillas, pistas de pádel, carriles de piscina) por franjas horarias.

### Implementación
- **Base de Datos**: Tablas `equipment_zones` y `equipment_reservations`
- **API Endpoints**: 
  - `GET /equipos` - Listar equipos disponibles
  - `POST /equipos/reservar` - Reservar equipo
- **Función Backend**: `reserve_equipment()` en `madre_db.py`

### Características
- ✅ Reserva por franjas horarias (30/60/90 minutos)
- ✅ Verificación automática de conflictos
- ✅ Soporte para múltiples tipos de equipos/zonas
- ✅ Check-in al llegar al equipo

### Equipos Disponibles (Ejemplos)
- **Racks de Sentadillas**: 3 unidades, slots de 60 min
- **Pistas de Pádel**: 2 unidades, slots de 90 min
- **Carriles de Piscina**: 3 unidades, slots de 45 min
- **Plataformas de Peso Muerto**: 2 unidades, slots de 60 min
- **Cancha de Squash**: 1 unidad, slots de 60 min

### Ejemplo de Reserva
```bash
curl -X POST 'http://localhost:8000/equipos/reservar' \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "juan_perez",
    "equipment_id": 1,
    "fecha_reserva": "2025-11-15",
    "hora_inicio": "18:00",
    "hora_fin": "19:00"
  }'
```

---

## 8. Filtro de Clases (Inteligente)

### Descripción
Sistema avanzado de filtrado de clases por múltiples criterios.

### Implementación
- **Backend**: Funciones de filtrado en `madre_db.py`
- **API**: Parámetros de query en `GET /clases/horarios`

### Filtros Disponibles
- ✅ Por instructor
- ✅ Por intensidad (baja, media, alta)
- ✅ Por horario (mañana, tarde, noche)
- ✅ Por disponibilidad (cupos libres)
- ✅ Por tipo de clase (cardio, funcional, flexibilidad, etc.)
- 🔄 Por "recomendadas para ti" (IA - futuro)

### Ejemplo de Filtros (Query)
```bash
# Filtrar por instructor
GET /clases/horarios?instructor=Carlos%20Ruiz

# Filtrar por intensidad
GET /clases/horarios?intensidad=alta

# Filtrar por disponibilidad
GET /clases/horarios?disponible=true

# Múltiples filtros
GET /clases/horarios?intensidad=alta&disponible=true
```

---

## 9. Notificaciones de "Hora de Salir" (Integración Mapas)

### Descripción
Alertas basadas en tráfico en tiempo real que indican cuándo salir para llegar a tiempo a la clase.

### Implementación
- **Estado**: Documentado para implementación futura
- **Requiere**: Integración con Google Maps API o similar
- **Datos Necesarios**: 
  - Ubicación del usuario
  - Ubicación del gimnasio
  - Tráfico en tiempo real
  - Hora de inicio de la clase

### Características Planificadas
- 🔄 Cálculo de tiempo de viaje en tiempo real
- 🔄 Consideración de tráfico actual
- 🔄 Notificación personalizada por método de transporte
- 🔄 Recordatorio al momento óptimo de salida

### Ejemplo de Notificación
```
🚗 Hora de Salir!
Tu clase de Spinning comienza en 45 minutos.
Hay tráfico moderado. Sal ahora para llegar a tiempo.
Tiempo estimado: 25 minutos
```

---

## 10. Botón "Cancelar" Fácil

### Descripción
Cancelación de reservas sin penalización hasta un tiempo límite, directamente desde la pantalla de inicio.

### Implementación
- **API Endpoint**: `POST /clases/cancelar`
- **Función Backend**: `cancel_booking()` en `madre_db.py`

### Características
- ✅ Cancelación con un solo clic
- ✅ Notificación automática a lista de espera
- ✅ Historial de cancelaciones
- ✅ Política de cancelación configurable

### Política de Cancelación (Ejemplo)
- Sin penalización: hasta 2 horas antes de la clase
- Penalización 50%: 1-2 horas antes
- Penalización 100%: menos de 1 hora antes

### Ejemplo de Cancelación
```bash
curl -X POST 'http://localhost:8000/clases/cancelar?booking_id=1'
```

---

## 11. Check-in Digital (Código QR/NFC)

### Descripción
Sistema de acceso al gimnasio mediante código QR o NFC en el teléfono, eliminando tarjetas físicas.

### Implementación
- **Base de Datos**: Tabla `checkin_tokens`
- **API Endpoints**:
  - `POST /checkin/generate-token` - Generar token
  - `POST /checkin` - Registrar check-in
- **Función Backend**: `generate_checkin_token()` en `madre_db.py`

### Características
- ✅ Generación de tokens únicos por usuario
- ✅ Soporte para QR y NFC
- ✅ Tokens con expiración configurable
- ✅ Registro de historial de accesos
- ✅ Sin necesidad de tarjeta física

### Flujo de Uso
1. Usuario genera token desde la app
2. Se genera código QR único
3. Usuario escanea QR en el torniquete/lector
4. Sistema valida token y registra check-in
5. Puerta se abre automáticamente

### Ejemplo de Generación de Token
```bash
curl -X POST 'http://localhost:8000/checkin/generate-token?username=juan_perez&token_type=qr'
```

### Respuesta
```json
{
  "status": "success",
  "token": "AbCdEfGh12345678...",
  "token_type": "qr"
}
```

---

## 12. Modo "Entrenamiento Activo"

### Descripción
Interfaz simplificada que se activa al entrar al gimnasio, mostrando solo la rutina del día y temporizador.

### Implementación
- **Estado**: Pendiente de implementación en UI
- **Características Planificadas**:
  - 🔄 Activación automática al check-in
  - 🔄 Vista simplificada con botones grandes
  - 🔄 Rutina del día destacada
  - 🔄 Temporizador de descanso visible
  - 🔄 Registro rápido de series

### Vista Planificada
```
┌──────────────────────────────┐
│   ENTRENAMIENTO ACTIVO       │
├──────────────────────────────┤
│                              │
│   HOY: Pecho y Tríceps       │
│                              │
│   ▶ Press Banca: 4x12        │
│   ⏱ Descanso: 2:30           │
│                              │
│   [Registrar Serie]          │
│   [Siguiente Ejercicio]      │
│                              │
└──────────────────────────────┘
```

---

## 13. Mapa del Gimnasio con AR (Realidad Aumentada)

### Descripción
Función de realidad aumentada que guía al usuario a la máquina o estudio mediante la cámara.

### Implementación
- **Estado**: Requiere desarrollo de app móvil nativa con AR
- **Tecnología**: ARKit (iOS) / ARCore (Android)
- **Características Planificadas**:
  - 🔄 Mapa 3D del gimnasio
  - 🔄 Navegación con flechas AR
  - 🔄 Indicadores de disponibilidad de máquinas
  - 🔄 Información al apuntar a equipos

### Casos de Uso
- Nuevos usuarios que no conocen el gimnasio
- Buscar máquinas específicas rápidamente
- Ver disponibilidad de equipos en tiempo real
- Guías para rutinas específicas

---

## 14. Escáner de Máquinas (QR/NFC)

### Descripción
Sistema de escaneo de códigos en máquinas para ver tutoriales, registrar ejercicios y ver historial.

### Implementación
- **Base de Datos**: Campo `qr_code` en tabla `equipment_zones`
- **API**: Endpoints de ejercicios y workout logs
- **Estado**: Backend completo, requiere app móvil para escaneo

### Características
- ✅ Códigos QR únicos por máquina
- ✅ Acceso instantáneo a tutoriales en video
- ✅ Registro rápido del ejercicio
- ✅ Visualización de historial personal en esa máquina
- 🔄 Interfaz de escaneo (requiere app móvil)

### Información al Escanear
```json
{
  "equipo": "Rack de Sentadillas 1",
  "ejercicio_principal": "Sentadillas",
  "video_tutorial": "https://...",
  "mi_ultimo_entrenamiento": {
    "fecha": "2025-11-05",
    "series": 4,
    "peso": 100,
    "reps": 12
  },
  "recomendacion": "Última vez: 100kg. Intenta 105kg hoy."
}
```

---

## 15. "Quick Log" (Registro Rápido) de Series/Reps

### Descripción
Interfaz simplificada para registrar peso y repeticiones con botones grandes (+/-) y mínima escritura.

### Implementación
- **Base de Datos**: Tabla `workout_logs`
- **API Endpoint**: `POST /workout/log`
- **Función Backend**: `log_workout()` en `madre_db.py`

### Características
- ✅ Registro con 3 datos: ejercicio, peso, reps
- ✅ Botones +/- para incrementos rápidos
- ✅ Guardado automático de series consecutivas
- ✅ Temporizador de descanso automático
- ✅ Historial visible durante el ejercicio

### Interfaz Propuesta
```
┌─────────────────────────────┐
│  Sentadillas                │
├─────────────────────────────┤
│                             │
│  Peso:  [−]  100kg  [+]    │
│                             │
│  Reps:  [−]   12   [+]     │
│                             │
│  Serie: 2/4                 │
│                             │
│  [Registrar]                │
│                             │
│  Última: 100kg × 12         │
│  Hace 3 días                │
└─────────────────────────────┘
```

### Ejemplo de Registro
```bash
curl -X POST 'http://localhost:8000/workout/log' \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "juan_perez",
    "exercise_id": 2,
    "fecha": "2025-11-08",
    "serie": 1,
    "repeticiones": 12,
    "peso": 100.0,
    "descanso_segundos": 120
  }'
```

---

## 16. Calculadora de Discos (Plates Calculator)

### Descripción
Herramienta que calcula qué discos poner en la barra para alcanzar un peso específico.

### Implementación
- **Módulo**: `shared/workout_utils.py`
- **API Endpoint**: `POST /utilidades/calculadora-discos`
- **Función**: `calculate_plates()`

### Características
- ✅ Cálculo automático de configuración óptima
- ✅ Considera peso de la barra
- ✅ Muestra orden de colocación
- ✅ Soporte para diferentes tipos de barras
- ✅ Validación de disponibilidad de discos

### Discos Estándar Disponibles
- 25.0 kg, 20.0 kg, 15.0 kg, 10.0 kg
- 5.0 kg, 2.5 kg, 2.0 kg, 1.25 kg, 1.0 kg, 0.5 kg

### Tipos de Barras
- Barra Olímpica Estándar: 20 kg
- Barra Olímpica Mujer: 15 kg
- Barra EZ: 10 kg
- Barra Hexagonal (Trap Bar): 25 kg
- Barra Técnica: 5 kg

### Ejemplo de Uso
```bash
# Calcular para 100kg con barra olímpica (20kg)
curl -X POST 'http://localhost:8000/utilidades/calculadora-discos?target_weight=100&bar_weight=20'
```

### Respuesta
```json
{
  "status": "success",
  "resultado": {
    "success": true,
    "plates_per_side": [25.0, 15.0],
    "plate_counts": {
      "25.0": 1,
      "15.0": 1
    },
    "total_weight": 100.0,
    "message": "Configuración de discos calculada correctamente"
  }
}
```

### Visualización Formateada
```
✅ Peso objetivo: 100kg
📊 Barra: 20.0kg
⚖️  Peso total: 100.0kg

🔩 Discos por lado:
   • 25.0kg × 1
   • 15.0kg × 1

📝 Orden de colocación (por lado):
   1. 25.0kg
   2. 15.0kg
```

---

## 17. Temporizador de Descanso Avanzado (Automático)

### Descripción
Temporizador integrado que se inicia automáticamente después de registrar una serie.

### Implementación
- **Módulo**: `shared/workout_utils.py`
- **Función**: `calculate_rest_time()`
- **Campo DB**: `descanso_segundos` en `workout_logs`

### Características
- ✅ Inicio automático al registrar serie
- ✅ Tiempo calculado según tipo de ejercicio
- ✅ Notificaciones push al terminar
- ✅ Vibración del dispositivo
- ✅ Pausable y ajustable

### Tiempos Recomendados

| Tipo de Ejercicio | Intensidad Baja | Intensidad Media | Intensidad Alta |
|-------------------|-----------------|------------------|-----------------|
| Fuerza (Strength) | 2:00 min        | 3:00 min         | 4:00 min        |
| Potencia (Power)  | 3:00 min        | 4:00 min         | 5:00 min        |
| Hipertrofia       | 1:00 min        | 1:30 min         | 2:00 min        |
| Resistencia       | 0:30 min        | 0:45 min         | 1:00 min        |

### Ejemplo de Cálculo
```python
from shared.workout_utils import calculate_rest_time, format_time

rest_seconds = calculate_rest_time("strength", "high")
# Resultado: 240 segundos (4 minutos)

formatted = format_time(rest_seconds)
# Resultado: "4:00"
```

### Interfaz de Temporizador
```
┌──────────────────────────────┐
│   ⏱ DESCANSO                 │
├──────────────────────────────┤
│                              │
│         2:45                 │
│                              │
│   ████████████░░░░░░░░       │
│                              │
│   [Pausar]  [+30s]  [Listo] │
│                              │
└──────────────────────────────┘
```

---

## 📊 Resumen de Implementación

### ✅ Completamente Implementado (Backend)
1. ✅ Reservas de Clases "One-Click"
2. ✅ Gestión de Lista de Espera
3. ✅ Recordatorios de Clases (estructura)
4. ✅ Calendario Personal (preparación)
5. ✅ Calificación Rápida de Clases
6. ✅ Reservas de Equipos/Zonas
7. ✅ Filtro de Clases
8. ✅ Botón "Cancelar" Fácil
9. ✅ Check-in Digital (QR/NFC)
10. ✅ Quick Log de Series/Reps
11. ✅ Calculadora de Discos
12. ✅ Temporizador de Descanso

### 🔄 Requiere App Móvil
- Check-in por Proximidad (Beacon/Geofencing)
- Mapa del Gimnasio con AR
- Escáner de Máquinas (QR/NFC)
- Modo "Entrenamiento Activo"

### 🔄 Requiere Integración Externa
- Notificaciones de "Hora de Salir" (Google Maps API)
- Sincronización con Calendarios (OAuth con Google/Microsoft)

---

## 🚀 Datos de Prueba

El sistema incluye datos de prueba completos:

### Usuarios
- `juan_perez` / `gym2024`
- `maria_lopez` / `fit2024`

### Clases Disponibles
1. **Spinning** - Alta intensidad, 45 min (Lun/Mié/Vie 07:00)
2. **Yoga** - Baja intensidad, 60 min (Lun/Mié 18:00, Sáb 10:00)
3. **CrossFit** - Alta intensidad, 60 min (Mar/Jue 19:00, Sáb 09:00)
4. **Pilates** - Media intensidad, 50 min (Mar/Jue 10:00)
5. **Zumba** - Media intensidad, 55 min (Lun/Mié/Vie 20:00)
6. **Boxing** - Alta intensidad, 60 min (Mar/Jue 18:00)

### Ejercicios (20+)
Press de Banca, Sentadillas, Peso Muerto, Press Militar, Dominadas, Remo con Barra, Curl de Bíceps, y más...

### Equipos Reservables
- 3 Racks de Sentadillas
- 2 Plataformas de Peso Muerto
- 2 Pistas de Pádel
- 3 Carriles de Piscina
- 1 Cancha de Squash

---

## 📖 Documentación Técnica

### Estructura de Base de Datos

#### Nuevas Tablas
```sql
-- Clases
classes, class_schedules, class_bookings, class_waitlist, class_ratings

-- Equipos
equipment_zones, equipment_reservations

-- Entrenamientos
exercises, workout_logs

-- Check-in
checkin_tokens, checkin_history

-- Sistema
notifications, user_preferences
```

### API Endpoints

#### Clases
- `GET /clases` - Listar clases
- `GET /clases/horarios` - Listar horarios
- `POST /clases/reservar` - Reservar clase
- `GET /clases/mis-reservas` - Ver mis reservas
- `POST /clases/cancelar` - Cancelar reserva
- `POST /clases/calificar` - Calificar clase

#### Equipos
- `GET /equipos` - Listar equipos
- `POST /equipos/reservar` - Reservar equipo

#### Entrenamientos
- `GET /ejercicios` - Listar ejercicios
- `POST /workout/log` - Registrar serie
- `GET /workout/historial` - Ver historial

#### Check-in
- `POST /checkin/generate-token` - Generar token
- `POST /checkin` - Registrar check-in

#### Utilidades
- `POST /utilidades/calculadora-discos` - Calcular discos

#### Notificaciones
- `GET /notificaciones` - Ver notificaciones

---

## 🎯 Próximos Pasos

### UI Cliente (Fase Pendiente)
1. Crear vista de calendario de clases
2. Implementar interfaz de reserva one-click
3. Agregar vista de equipos reservables
4. Crear interfaz de workout logging
5. Implementar calculadora de discos en UI
6. Agregar vista de notificaciones

### Optimizaciones
1. Agregar caché para clases frecuentes
2. Implementar paginación en listas largas
3. Optimizar consultas de disponibilidad
4. Agregar índices a columnas frecuentes

### Funciones Avanzadas
1. Sistema de recomendaciones con IA
2. Análisis de patrones de entrenamiento
3. Integración con wearables
4. Estadísticas avanzadas de rendimiento

---

## 📞 Soporte

Para más información sobre el uso de estas funcionalidades, consultar:
- README.md - Información general del sistema
- GYM_MANAGEMENT_FEATURES.md - Características completas
- SETUP.md - Guía de instalación

---

**Versión**: 1.0  
**Fecha**: 2025-11-08  
**Estado**: Backend completo, UI pendiente
