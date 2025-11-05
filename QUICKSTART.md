# Guía de Inicio Rápido - Sistema Madre-Hija

## 🚀 Inicio Rápido en 5 Pasos

### Paso 1: Preparar el Servidor (Aplicación Madre)

```bash
# Instalar dependencias
pip install -r requirements_madre.txt

# Ejecutar la aplicación
python madre_main.py
```

✅ **Resultado**: Se abrirá una ventana con dos pestañas y el servidor API estará corriendo en `http://0.0.0.0:8000`

### Paso 2: Gestionar Usuarios en la Madre

En la ventana de la Madre:
1. Ve a la pestaña **"Gestión de Usuarios"**
2. Verás 3 usuarios predefinidos:
   - `usuario_alfa` ✅ Acceso habilitado
   - `usuario_beta` ✅ Acceso habilitado
   - `usuario_gamma` ❌ Acceso deshabilitado

3. Usa los switches para habilitar/deshabilitar acceso

### Paso 3: Publicar Contenido

En la ventana de la Madre:
1. Ve a la pestaña **"Sincronización de Contenido"**
2. Edita el texto en el cuadro
3. Presiona **"Publicar Nuevo Contenido"**

### Paso 4: Configurar Cliente (Aplicación Hija)

Si el servidor Madre está en otra computadora:

```bash
# Editar hija_comms.py
# Cambiar la línea 12:
MADRE_BASE_URL = "http://127.0.0.1:8000"
# Por (ejemplo):
MADRE_BASE_URL = "http://192.168.1.100:8000"
```

Si está en la misma computadora, no hace falta cambiar nada.

### Paso 5: Ejecutar Cliente (Aplicación Hija)

```bash
# Instalar dependencias
pip install -r requirements_hija.txt

# Ejecutar la aplicación
python hija_main.py
```

✅ **Resultado**: Se abrirá la ventana de inicio de sesión

## 🎯 Probar el Sistema

### Probar Autenticación Exitosa

1. En la Hija, ingresa: `usuario_alfa`
2. Presiona **"Conectar a la Madre"**
3. ✅ Deberías ver la pantalla principal

### Probar Autenticación Fallida

1. Cierra la aplicación Hija y vuelve a abrirla
2. Ingresa: `usuario_gamma`
3. Presiona **"Conectar a la Madre"**
4. ❌ Deberías ver un error: "Permiso de acceso denegado"

### Probar Sincronización

1. Con un usuario autenticado en la Hija
2. Presiona **"Sincronizar con la Madre"**
3. ✅ El contenido publicado en la Madre aparecerá en el cuadro de texto

### Probar Gestión en Tiempo Real

1. Deja abierta la Hija con `usuario_beta` conectado
2. En la Madre, desactiva el permiso de `usuario_beta`
3. En la Hija, intenta sincronizar
4. ❌ Aunque ya esté conectado, la sincronización fallará (permiso revocado)

## 📝 Usuarios de Prueba

| Usuario | Contraseña | Estado Inicial | Equipo |
|---------|-----------|---------------|--------|
| usuario_alfa | N/A | ✅ Habilitado | Equipo A |
| usuario_beta | N/A | ✅ Habilitado | Equipo B |
| usuario_gamma | N/A | ❌ Deshabilitado | Equipo C |

**Nota**: Esta es una versión de prueba sin contraseñas. Solo se requiere el nombre de usuario.

## 🔧 Resolución de Problemas

### Error: "No se pudo alcanzar la Aplicación Madre"

**Causa**: La Hija no puede conectarse al servidor Madre

**Soluciones**:
1. Verifica que la Madre esté ejecutándose
2. Verifica la IP en `hija_comms.py` línea 12
3. Verifica que no haya firewall bloqueando el puerto 8000
4. Si es en la misma PC, usa `127.0.0.1:8000`
5. Si es en red local, usa la IP real (ej: `192.168.1.100:8000`)

### Error: "ModuleNotFoundError: No module named 'customtkinter'"

**Causa**: Falta instalar las dependencias

**Solución**:
```bash
pip install -r requirements_madre.txt  # Para Madre
# o
pip install -r requirements_hija.txt   # Para Hija
```

### Error: "Address already in use" al iniciar Madre

**Causa**: El puerto 8000 ya está en uso

**Solución**:
```bash
# Opción 1: Encontrar y matar el proceso
# Windows:
netstat -ano | findstr :8000
taskkill /PID <numero_pid> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9

# Opción 2: Cambiar puerto en madre_main.py línea 14
HOST_PORT = 8001  # Cambiar a otro puerto
```

### La GUI no se muestra

**Causa**: Falta servidor X en Linux o problema de display

**Solución en Linux**:
```bash
export DISPLAY=:0
# o si usas WSL:
export DISPLAY=:0.0
```

## 🌐 Obtener la IP del Servidor

### Windows
```cmd
ipconfig
# Buscar "IPv4 Address" en tu adaptador de red
```

### Linux/Mac
```bash
ifconfig
# o
ip addr show
# Buscar inet en tu interfaz de red (ej: eth0, wlan0)
```

## 🎨 Capturas de Pantalla de Referencia

### Ventana Madre - Gestión de Usuarios
```
┌─────────────────────────────────────────────┐
│ Aplicación Madre - Panel de Control         │
├─────────────────────────────────────────────┤
│ [Gestión de Usuarios] [Sincronización...]   │
│                                              │
│ Gestión de Permisos de Usuarios             │
│ Habilite o deshabilite el acceso...         │
│                                              │
│ ┌──────────────────────────────────────┐    │
│ │ usuario_alfa (Equipo A) [✓] Acceso   │    │
│ │ usuario_beta (Equipo B) [✓] Acceso   │    │
│ │ usuario_gamma (Equipo C) [ ] Acceso  │    │
│ └──────────────────────────────────────┘    │
│           [Actualizar Lista]                 │
└─────────────────────────────────────────────┘
```

### Ventana Hija - Login
```
┌─────────────────────────────────────┐
│ Aplicación Hija - Iniciar Sesión    │
├─────────────────────────────────────┤
│        ┌──────────────────────┐     │
│        │  Acceso de Cliente   │     │
│        │                      │     │
│        │ [nombre de usuario]  │     │
│        │                      │     │
│        │ [Conectar a la Madre]│     │
│        │                      │     │
│        └──────────────────────┘     │
└─────────────────────────────────────┘
```

### Ventana Hija - App Principal
```
┌────────────────────────────────────────────┐
│ Aplicación Hija - usuario_alfa             │
├────────────────────────────────────────────┤
│ Bienvenido, usuario_alfa                   │
│                 [Sincronizar con la Madre] │
│                                            │
│ Contenido Sincronizado de la Madre:       │
│ ┌────────────────────────────────────────┐ │
│ │ Este es el contenido inicial desde la  │ │
│ │ Madre.                                 │ │
│ │                                        │ │
│ │                                        │ │
│ └────────────────────────────────────────┘ │
│ Sincronización exitosa. Versión: 1.0.0    │
└────────────────────────────────────────────┘
```

## ✨ Características Probadas

- ✅ Autenticación de usuarios
- ✅ Control de permisos en tiempo real
- ✅ Sincronización de contenido
- ✅ Manejo de errores de conexión
- ✅ Validación de usuarios
- ✅ GUI responsiva y moderna
- ✅ Servidor concurrente (GUI + API)

## 📚 Más Información

- Ver `README.md` para documentación completa
- Ver `ESTRUCTURA_PROYECTO.md` para detalles técnicos
- Ver archivos `.txt` originales para arquitectura detallada

## 🚀 Siguiente Nivel

Una vez que todo funcione, puedes:

1. **Agregar más usuarios** editando `madre_db.py`
2. **Cambiar el contenido** desde la pestaña de sincronización
3. **Probar en red local** configurando IPs
4. **Crear un ejecutable** con PyInstaller:
   ```bash
   pip install pyinstaller
   pyinstaller --onefile --windowed hija_main.py
   ```

¡Disfruta del sistema Madre-Hija! 🎉
