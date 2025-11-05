# Setup Rápido - Sistema GYM v2.0

## 🚀 Instalación en 3 Pasos

### Paso 1: Instalar Dependencias

```bash
# Para Aplicación Madre
pip install -r requirements_madre.txt

# Para Aplicación Hija (si en otra máquina)
pip install -r requirements_hija.txt
```

### Paso 2: Crear Base de Datos

```bash
python populate_db.py
```

**Output esperado:**
```
============================================================
POBLANDO BASE DE DATOS DEL SISTEMA GYM
============================================================

Creando usuarios de ejemplo...
✓ Usuario 'juan_perez' creado
  - Foto de perfil añadida
  - Cronograma de entrenamiento añadido
  - 3 fotos añadidas a la galería
✓ Usuario 'maria_lopez' creado
  - Foto de perfil añadida
  - Cronograma de entrenamiento añadido
  - 2 fotos añadidas a la galería
✓ Usuario 'carlos_rodriguez' creado (sin permiso de acceso)
  - Foto de perfil añadida
  - Cronograma de entrenamiento añadido
  - 1 fotos añadidas a la galería

BASE DE DATOS POBLADA EXITOSAMENTE
```

### Paso 3: Verificar Instalación

```bash
python test_system.py
```

**Output esperado:**
```
✓ ALL TESTS PASSED (3/3)
  Sistema funcionando correctamente!
```

---

## 🎮 Uso del Sistema

### Iniciar Aplicación Madre (Servidor)

```bash
python madre_main.py
```

Se abrirá:
- 🖥️ Ventana GUI de gestión
- 🌐 Servidor API en http://localhost:8000

**Funcionalidades:**
- Gestión de Usuarios (ver detalles, cambiar permisos)
- Sincronización de Contenido (mensajes globales)
- Sincronización Masiva (actualizar múltiples usuarios)

### Iniciar Aplicación Hija (Cliente)

```bash
python hija_main.py
```

**Primera vez**: Se muestra pantalla de login

**Credenciales de prueba:**
```
Usuario: juan_perez
Contraseña: gym2024

Usuario: maria_lopez
Contraseña: fit2024

Usuario: carlos_rodriguez (BLOQUEADO)
Contraseña: trainer123
```

**Próximas veces**: Auto-login automático

---

## 📱 Características Disponibles

### En la Aplicación Madre

#### Pestaña "Gestión de Usuarios"
- Lista de todos los usuarios
- Botón "Ver Detalles" → Ventana emergente con:
  - Información personal completa
  - Cronograma de entrenamiento mensual
  - Galería de fotos personal
- Switch "Acceso Habilitado" → Cambio inmediato de permisos

#### Pestaña "Sincronización de Contenido"
- Editor de texto para mensajes globales
- Botón "Publicar Nuevo Contenido"
- Auto-incremento de versión

#### Pestaña "Sincronización Masiva"
- Lista de usuarios con checkboxes
- Botones:
  - "Seleccionar Todos"
  - "Deseleccionar Todos"
  - "Sincronizar Seleccionados"

### En la Aplicación Hija

#### Pestaña "Perfil"
- Información personal del usuario
- Email, teléfono, equipo
- Fecha de registro

#### Pestaña "Cronograma"
- Programa de entrenamiento mensual
- Desglose día por día:
  - Ejercicios
  - Descripción detallada
  - Duración en minutos
- Objetivo del programa
- Notas del entrenador

#### Pestaña "Galería"
- Fotos personales
- Descripciones
- Fechas de carga

#### Pestaña "Mensajes"
- Mensajes del gimnasio
- Anuncios importantes
- Actualizaciones

#### Barra de Estado
- Muestra estado de sincronización
- Sincronización automática cada 5→30 minutos
- No interrumpe el uso de la app

---

## 🔧 Configuración de Red

### Mismo Equipo (por defecto)
No requiere configuración. Funciona con `127.0.0.1:8000`

### Equipos Diferentes en Red Local

#### 1. Obtener IP del equipo Madre

**Windows:**
```cmd
ipconfig
```
Buscar "IPv4 Address" (ej: 192.168.1.100)

**Linux/Mac:**
```bash
ifconfig
# o
ip addr show
```
Buscar "inet" (ej: 192.168.1.100)

#### 2. Configurar IP en Hija

Editar `hija_comms.py`, línea 13:
```python
MADRE_BASE_URL = "http://192.168.1.100:8000"  # Usar IP real
```

#### 3. Verificar Firewall
Asegurarse que el puerto 8000 esté abierto en el equipo Madre.

**Windows:**
```
Panel de Control → Firewall → Configuración Avanzada
→ Reglas de Entrada → Nueva Regla → Puerto 8000
```

**Linux:**
```bash
sudo ufw allow 8000
```

---

## 🧪 Verificación de Funcionamiento

### Test 1: Autenticación
1. Iniciar Madre y Hija
2. Login con `juan_perez` / `gym2024`
3. ✅ Debe entrar a la app

### Test 2: Sincronización
1. Estando logueado en Hija
2. Click en "Sincronizar Ahora"
3. ✅ Debe actualizar todas las pestañas

### Test 3: Bloqueo de Usuario
1. En Madre, desactivar permiso de `juan_perez`
2. En Hija (ya logueada), intentar sincronizar
3. ✅ Debe mostrar error de permisos

### Test 4: Auto-Login
1. Cerrar y reabrir Hija (con credenciales guardadas)
2. ✅ Debe entrar automáticamente

### Test 5: Sincronización Automática
1. Observar la barra de estado en Hija
2. ✅ Debe sincronizar cada 5→30 minutos automáticamente

---

## 📊 Datos de los Usuarios

### Juan Pérez (juan_perez / gym2024)
- **Equipo**: Fitness Avanzado
- **Objetivo**: Ganancia muscular y definición
- **Entrenamiento**: 6 días/semana
  - Lunes: Pecho/Tríceps
  - Martes: Cardio
  - Miércoles: Espalda/Bíceps
  - Jueves: Descanso activo
  - Viernes: Piernas
  - Sábado: HIIT
  - Domingo: Descanso
- **Galería**: 3 fotos de progreso

### María López (maria_lopez / fit2024)
- **Equipo**: Cardio y Resistencia
- **Objetivo**: Resistencia cardiovascular
- **Entrenamiento**: 6 días/semana
  - Lunes: Running + Core
  - Martes: Spinning
  - Miércoles: Natación
  - Jueves: Running intervals
  - Viernes: Circuito funcional
  - Sábado: Carrera larga
  - Domingo: Descanso
- **Galería**: 2 fotos (media maratón, yoga)

### Carlos Rodríguez (carlos_rodriguez / trainer123) ❌ BLOQUEADO
- **Equipo**: Principiantes
- **Objetivo**: Adaptación inicial
- **Entrenamiento**: 3 días/semana
- **Galería**: 1 foto (primer día)

---

## 🛠️ Solución de Problemas

### Error: "No se pudo alcanzar la Aplicación Madre"
**Solución:**
1. Verificar que Madre esté ejecutándose
2. Verificar IP en `hija_comms.py`
3. Verificar firewall
4. Verificar que ambos estén en la misma red

### Error: "Address already in use"
**Solución:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Error: "ModuleNotFoundError"
**Solución:**
```bash
pip install -r requirements_madre.txt
pip install -r requirements_hija.txt
```

### La GUI no se muestra (Linux)
**Solución:**
```bash
export DISPLAY=:0
```

### Base de Datos Corrupta
**Solución:**
```bash
rm data/gym_database.db
python populate_db.py
```

---

## 📚 Documentación Adicional

- **README.md** - Visión general del proyecto
- **NUEVAS_FUNCIONALIDADES.md** - Documentación completa de features
- **SECURITY_SUMMARY.md** - Estado de seguridad y recomendaciones
- **QUICKSTART.md** - Guía rápida de inicio
- **ESTRUCTURA_PROYECTO.md** - Arquitectura técnica

---

## ✨ Próximos Pasos

### Empezar a Usar
1. ✅ Instalar dependencias
2. ✅ Crear base de datos
3. ✅ Ejecutar tests
4. 🎯 **¡Listo para usar!**

### Personalizar
- Añadir más usuarios en `populate_db.py`
- Modificar cronogramas de entrenamiento
- Cambiar mensajes de sincronización
- Ajustar intervalos de sync

### Para Producción
- Ver **SECURITY_SUMMARY.md** para mejoras de seguridad
- Migrar a bcrypt para contraseñas
- Implementar HTTPS/SSL
- Configurar backups automáticos

---

## 🎉 ¡Sistema Listo!

El sistema está **100% funcional** con:
- ✅ 3 usuarios de ejemplo con datos completos
- ✅ Base de datos persistente
- ✅ Autenticación con contraseñas
- ✅ Sincronización automática
- ✅ Gestión individual y masiva
- ✅ Interfaz moderna y responsiva

**¡Disfruta del sistema GYM v2.0!** 💪
